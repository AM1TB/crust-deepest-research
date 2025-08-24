"""
Custom recruitment tools for CrewAI based on the People Discovery API.
"""

import os
import json
from typing import Dict, Any, Optional, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from utils.api_client import make_authenticated_request
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeopleSearchArgs(BaseModel):
    """Arguments for PeopleSearch tool."""
    filters: Dict[str, Any] = Field(description="Filter tree for the search")
    limit: int = Field(default=200, description="Results per page (1-1000)")
    cursor: Optional[str] = Field(default=None, description="Pagination cursor")
    post_processing: Optional[Dict[str, Any]] = Field(default=None, description="Post-processing exclusions")


class PeopleSearchTool(BaseTool):
    name: str = "people_search"
    description: str = """
    Query the People Discovery In-DB API to find and paginate candidates using complex, nested filters. 
    Keep filters identical when paginating with a cursor. Use disciplined limits (default 200 results per call).
    
    Parameters:
    - filters (required): Dict with column/type/value structure or nested conditions
    - limit (optional): Integer 1-1000, defaults to 200
    - cursor (optional): String for pagination or null for first page
    - post_processing (optional): Dict with exclusions or null
    
    This tool supports:
    - Complex nested filters with AND/OR logic
    - Fuzzy text matching using '(.)' operator
    - Pagination with cursor-based navigation
    - Post-processing exclusions for profiles and names
    - Rate limiting (60 RPM) and credit management (3 credits per 100 results)
    """
    args_schema: type[BaseModel] = PeopleSearchArgs

    def _run(
        self,
        filters: Dict[str, Any],
        limit: int = 200,
        cursor: Optional[str] = None,
        post_processing: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a people search query.
        
        Args:
            filters: Filter tree for the search. Each node is either a single condition 
                    {column, type, value} or a group {op, conditions:[...]}
            limit: Results per page (1-1000, default 200)
            cursor: Opaque cursor from previous response for pagination
            post_processing: Extra filtering with exclude_profiles and exclude_names arrays
            
        Returns:
            str: JSON string containing search results or error message
        """
        try:
            # Validate inputs
            if not isinstance(filters, dict):
                return json.dumps({"error": "Filters must be a dictionary object"})
            
            if not (1 <= limit <= 1000):
                return json.dumps({"error": "Limit must be between 1 and 1000"})
            
            # Build the request payload
            payload = {
                "filters": filters,
                "limit": limit
            }
            
            if cursor:
                payload["cursor"] = cursor
                
            if post_processing:
                payload["post_processing"] = post_processing
            
            # Get the API endpoint URL
            api_base_url = os.getenv('CRUSTDATA_API_BASE_URL', 'https://api.crustdata.com')
            url = f"{api_base_url}/screener/persondb/search"
            
            logger.info(f"Making People Search API call with limit={limit}")
            
            # Make the API call
            response_data = make_authenticated_request(url, payload, method="POST")
            
            # Format the response with truncated profiles to prevent context overflow
            profiles = response_data.get("profiles", [])
            
            # Truncate each profile to essential fields only to prevent context overflow
            truncated_profiles = []
            for profile in profiles:
                truncated_profile = {
                    "name": profile.get("name", ""),
                    "headline": profile.get("headline", ""),
                    "region": profile.get("region", ""),
                    "years_of_experience_raw": profile.get("years_of_experience_raw", 0),
                    "current_employers": profile.get("current_employers", [])[:1],  # Only first employer
                    "skills": profile.get("skills", [])[:10],  # Limit to first 10 skills
                    "person_id": profile.get("person_id", ""),
                    "profile_url": profile.get("profile_url", "")
                }
                # Further truncate current_employers data
                if truncated_profile["current_employers"]:
                    employer = truncated_profile["current_employers"][0]
                    truncated_profile["current_employers"] = [{
                        "name": employer.get("name", ""),
                        "title": employer.get("title", ""),
                        "start_date": employer.get("start_date", ""),
                        "company_headcount_latest": employer.get("company_headcount_latest", 0),
                        "company_industries": employer.get("company_industries", [])[:3]  # Limit industries
                    }]
                
                truncated_profiles.append(truncated_profile)
            
            # Further reduce context if we have too many profiles
            if len(truncated_profiles) > 50:
                # For large result sets, only return summary statistics and first 20 profiles
                result = {
                    "profiles": truncated_profiles[:20],
                    "next_cursor": response_data.get("next_cursor"),
                    "total_results": len(profiles),
                    "profiles_in_response": 20,
                    "profiles_truncated": len(profiles) - 20,
                    "api_credits_used": self._estimate_credits_used(len(profiles)),
                    "note": f"Context-optimized response: showing first 20 of {len(profiles)} profiles to prevent context overflow"
                }
            else:
                result = {
                    "profiles": truncated_profiles,
                    "next_cursor": response_data.get("next_cursor"),
                    "total_results": len(profiles),
                    "api_credits_used": self._estimate_credits_used(len(profiles)),
                    "note": "Profile data has been truncated to prevent context overflow"
                }
            
            logger.info(f"Search completed: {result['total_results']} profiles returned (context-optimized)")
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_msg = f"Error in people search: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    def _estimate_credits_used(self, result_count: int) -> float:
        """Estimate API credits used based on result count (3 credits per 100 results)."""
        return (result_count / 100) * 3


class FilterBuilderTool(BaseTool):
    name: str = "filter_builder"
    description: str = """
    Helper tool to build complex nested filters for the People Search API.
    Supports creating filters for titles, skills, experience, company constraints, geography, etc.
    Uses the proper column names and operators as defined in the API schema.
    
    Usage examples:
    - Title filter: filter_type="title", titles=["Software Engineer", "Developer"], fuzzy=True
    - Skills filter: filter_type="skills", skills=["Python", "JavaScript"], fuzzy=True  
    - Experience filter: filter_type="experience", min_years=3, max_years=10
    - Company filter: filter_type="company", company_size_min=100, company_size_max=1000, industries=["Technology"]
    - Region filter: filter_type="region", regions=["San Francisco Bay Area"], fuzzy=True
    - Combined filter: filter_type="combined", filter_components=[filter1, filter2]
    """
    
    def _run(
        self,
        filter_type: str,
        **kwargs
    ) -> str:
        """
        Build filters for common search patterns.
        
        Args:
            filter_type: Type of filter to build ('title', 'skills', 'experience', 'company', 'region', 'combined')
            **kwargs: Additional parameters specific to each filter type
            
        Returns:
            str: JSON string containing the constructed filter
        """
        try:
            if filter_type == "title":
                if 'titles' not in kwargs:
                    return json.dumps({
                        "error": "Missing required parameter 'titles' for title filter",
                        "usage": "filter_type='title', titles=['Software Engineer', 'Developer'], fuzzy=True"
                    })
                return self._build_title_filter(**kwargs)
            elif filter_type == "skills":
                if 'skills' not in kwargs:
                    return json.dumps({
                        "error": "Missing required parameter 'skills' for skills filter",
                        "usage": "filter_type='skills', skills=['Python', 'JavaScript'], fuzzy=True"
                    })
                return self._build_skills_filter(**kwargs)
            elif filter_type == "experience":
                if 'min_years' not in kwargs:
                    return json.dumps({
                        "error": "Missing required parameter 'min_years' for experience filter",
                        "usage": "filter_type='experience', min_years=3, max_years=10"
                    })
                return self._build_experience_filter(**kwargs)
            elif filter_type == "company":
                if not any(k in kwargs for k in ['company_size_min', 'company_size_max', 'industries', 'exclude_companies']):
                    return json.dumps({
                        "error": "Missing required parameters for company filter. Need at least one of: company_size_min, company_size_max, industries, exclude_companies",
                        "usage": "filter_type='company', company_size_min=100, company_size_max=1000, industries=['Technology']"
                    })
                return self._build_company_filter(**kwargs)
            elif filter_type == "region":
                if 'regions' not in kwargs:
                    return json.dumps({
                        "error": "Missing required parameter 'regions' for region filter",
                        "usage": "filter_type='region', regions=['San Francisco Bay Area'], fuzzy=True"
                    })
                return self._build_region_filter(**kwargs)
            elif filter_type == "combined":
                if 'filter_components' not in kwargs:
                    return json.dumps({
                        "error": "Missing required parameter 'filter_components' for combined filter",
                        "usage": "filter_type='combined', filter_components=[filter1, filter2]"
                    })
                return self._build_combined_filter(**kwargs)
            else:
                return json.dumps({
                    "error": f"Unknown filter type: {filter_type}",
                    "valid_types": ["title", "skills", "experience", "company", "region", "combined"]
                })
                
        except Exception as e:
            return json.dumps({"error": f"Error building filter: {str(e)}"})
    
    def _build_title_filter(self, titles: List[str], fuzzy: bool = True) -> str:
        """Build filter for job titles."""
        if not titles:
            return json.dumps({"error": "Titles list cannot be empty"})
            
        if len(titles) == 1:
            operator = "(.)" if fuzzy else "="
            filter_obj = {
                "column": "current_employers.title",
                "type": operator,
                "value": titles[0]
            }
        else:
            # Multiple titles with OR logic
            conditions = []
            for title in titles:
                operator = "(.)" if fuzzy else "="
                conditions.append({
                    "column": "current_employers.title",
                    "type": operator,
                    "value": title
                })
            filter_obj = {
                "op": "or",
                "conditions": conditions
            }
        
        return json.dumps(filter_obj, indent=2)
    
    def _build_skills_filter(self, skills: List[str], fuzzy: bool = True) -> str:
        """Build filter for skills."""
        if not skills:
            return json.dumps({"error": "Skills list cannot be empty"})
            
        conditions = []
        for skill in skills:
            operator = "(.)" if fuzzy else "="
            conditions.append({
                "column": "skills",
                "type": operator,
                "value": skill
            })
        
        # Use AND for multiple skills (person must have all skills)
        if len(conditions) == 1:
            filter_obj = conditions[0]
        else:
            filter_obj = {
                "op": "and",
                "conditions": conditions
            }
        
        return json.dumps(filter_obj, indent=2)
    
    def _build_experience_filter(self, min_years: int, max_years: Optional[int] = None) -> str:
        """Build filter for years of experience."""
        if min_years < 0:
            return json.dumps({"error": "Minimum years cannot be negative"})
            
        if max_years is None:
            # Only minimum requirement
            filter_obj = {
                "column": "years_of_experience_raw",
                "type": "=>",
                "value": min_years
            }
        else:
            # Range requirement
            if max_years < min_years:
                return json.dumps({"error": "Maximum years cannot be less than minimum years"})
                
            filter_obj = {
                "op": "and",
                "conditions": [
                    {
                        "column": "years_of_experience_raw",
                        "type": "=>",
                        "value": min_years
                    },
                    {
                        "column": "years_of_experience_raw",
                        "type": "=<",
                        "value": max_years
                    }
                ]
            }
        
        return json.dumps(filter_obj, indent=2)
    
    def _build_company_filter(
        self,
        company_size_min: Optional[int] = None,
        company_size_max: Optional[int] = None,
        industries: Optional[List[str]] = None,
        exclude_companies: Optional[List[str]] = None
    ) -> str:
        """Build filter for company constraints."""
        conditions = []
        
        # Company size constraints
        if company_size_min is not None:
            conditions.append({
                "column": "current_employers.company_headcount_latest",
                "type": "=>",
                "value": company_size_min
            })
            
        if company_size_max is not None:
            conditions.append({
                "column": "current_employers.company_headcount_latest",
                "type": "=<",
                "value": company_size_max
            })
        
        # Industry constraints
        if industries:
            if len(industries) == 1:
                conditions.append({
                    "column": "current_employers.company_industries",
                    "type": "(.)",
                    "value": industries[0]
                })
            else:
                industry_conditions = []
                for industry in industries:
                    industry_conditions.append({
                        "column": "current_employers.company_industries",
                        "type": "(.)",
                        "value": industry
                    })
                conditions.append({
                    "op": "or",
                    "conditions": industry_conditions
                })
        
        # Company exclusions
        if exclude_companies:
            conditions.append({
                "column": "current_employers.name",
                "type": "not_in",
                "value": exclude_companies
            })
        
        if not conditions:
            return json.dumps({"error": "At least one company constraint must be specified"})
        
        if len(conditions) == 1:
            filter_obj = conditions[0]
        else:
            filter_obj = {
                "op": "and",
                "conditions": conditions
            }
        
        return json.dumps(filter_obj, indent=2)
    
    def _build_region_filter(self, regions: List[str], fuzzy: bool = True) -> str:
        """Build filter for geographic regions."""
        if not regions:
            return json.dumps({"error": "Regions list cannot be empty"})
            
        if len(regions) == 1:
            operator = "(.)" if fuzzy else "="
            filter_obj = {
                "column": "region",
                "type": operator,
                "value": regions[0]
            }
        else:
            conditions = []
            for region in regions:
                operator = "(.)" if fuzzy else "="
                conditions.append({
                    "column": "region",
                    "type": operator,
                    "value": region
                })
            filter_obj = {
                "op": "or",
                "conditions": conditions
            }
        
        return json.dumps(filter_obj, indent=2)
    
    def _build_combined_filter(self, filter_components: List[Dict]) -> str:
        """Build a combined filter from multiple components."""
        if not filter_components:
            return json.dumps({"error": "Filter components list cannot be empty"})
            
        if len(filter_components) == 1:
            filter_obj = filter_components[0]
        else:
            filter_obj = {
                "op": "and",
                "conditions": filter_components
            }
        
        return json.dumps(filter_obj, indent=2)


class CandidateRankerTool(BaseTool):
    name: str = "candidate_ranker"
    description: str = """
    Rank and score candidates based on various criteria including title match, skills, experience, 
    company size, industry, and geographic preferences. Uses a weighted scoring system.
    """
    
    def _run(
        self,
        candidates: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> str:
        """
        Rank candidates based on job requirements.
        
        Args:
            candidates: List of candidate profiles from people search
            requirements: Dictionary containing job requirements and preferences
            
        Returns:
            str: JSON string containing ranked candidates with scores
        """
        try:
            if not candidates:
                return json.dumps({"ranked_candidates": [], "total_candidates": 0})
            
            scored_candidates = []
            
            for candidate in candidates:
                score = self._calculate_score(candidate, requirements)
                rationale = self._generate_rationale(candidate, requirements)
                
                scored_candidate = {
                    **candidate,
                    "score": score,
                    "rationale": rationale
                }
                scored_candidates.append(scored_candidate)
            
            # Sort by score (descending)
            ranked_candidates = sorted(scored_candidates, key=lambda x: x["score"], reverse=True)
            
            # Limit the number of candidates returned to prevent context overflow
            max_candidates = 25  # Limit to top 25 candidates
            limited_candidates = ranked_candidates[:max_candidates]
            
            result = {
                "ranked_candidates": limited_candidates,
                "total_candidates": len(ranked_candidates),
                "candidates_returned": len(limited_candidates),
                "top_score": ranked_candidates[0]["score"] if ranked_candidates else 0,
                "average_score": sum(c["score"] for c in ranked_candidates) / len(ranked_candidates) if ranked_candidates else 0,
                "note": f"Returning top {len(limited_candidates)} of {len(ranked_candidates)} candidates to optimize context usage"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": f"Error ranking candidates: {str(e)}"})
    
    def _calculate_score(self, candidate: Dict[str, Any], requirements: Dict[str, Any]) -> int:
        """Calculate score for a candidate based on requirements."""
        score = 0
        
        # Title/seniority match (+20)
        current_title = self._get_current_title(candidate)
        target_titles = requirements.get("titles", [])
        if any(title.lower() in current_title.lower() for title in target_titles):
            score += 20
        
        # Core skills match (+8 each, cap at reasonable number)
        candidate_skills = candidate.get("skills", [])
        must_have_skills = requirements.get("must_have_skills", [])
        for skill in must_have_skills[:10]:  # Cap at 10 skills
            if any(skill.lower() in cs.lower() for cs in candidate_skills):
                score += 8
        
        # Nice-to-have skills (+3 each, cap at reasonable number)
        nice_to_have_skills = requirements.get("nice_to_have_skills", [])
        for skill in nice_to_have_skills[:10]:  # Cap at 10 skills
            if any(skill.lower() in cs.lower() for cs in candidate_skills):
                score += 3
        
        # Experience match
        years_exp = candidate.get("years_of_experience_raw", 0)
        min_exp = requirements.get("min_experience", 0)
        max_exp = requirements.get("max_experience", 100)
        
        if min_exp <= years_exp <= max_exp:
            score += 10
        elif years_exp > max_exp:
            score += 3
        elif years_exp < min_exp:
            score -= 10
        
        # Company size match (+10)
        company_headcount = self._get_current_company_headcount(candidate)
        target_min_size = requirements.get("company_size_min", 0)
        target_max_size = requirements.get("company_size_max", float('inf'))
        
        if target_min_size <= company_headcount <= target_max_size:
            score += 10
        
        # Industry match (+5)
        current_industries = self._get_current_company_industries(candidate)
        target_industries = requirements.get("target_industries", [])
        if any(industry.lower() in ci.lower() for industry in target_industries for ci in current_industries):
            score += 5
        
        # Region match (+10 exact, +5 approximate)
        candidate_region = candidate.get("region", "")
        target_regions = requirements.get("target_regions", [])
        if any(region.lower() == candidate_region.lower() for region in target_regions):
            score += 10
        elif any(region.lower() in candidate_region.lower() for region in target_regions):
            score += 5
        
        # Recency bonus (+5)
        current_start_date = self._get_current_job_start_date(candidate)
        if current_start_date and self._is_recent_role(current_start_date):
            score += 5
        
        return max(0, score)  # Ensure non-negative score
    
    def _generate_rationale(self, candidate: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """Generate rationale bullets for candidate score."""
        rationale = []
        
        # Title match
        current_title = self._get_current_title(candidate)
        target_titles = requirements.get("titles", [])
        if any(title.lower() in current_title.lower() for title in target_titles):
            rationale.append(f"Strong title match: {current_title}")
        
        # Skills match
        candidate_skills = candidate.get("skills", [])
        must_have_skills = requirements.get("must_have_skills", [])
        matched_skills = [skill for skill in must_have_skills 
                         if any(skill.lower() in cs.lower() for cs in candidate_skills)]
        if matched_skills:
            rationale.append(f"Key skills: {', '.join(matched_skills[:3])}")  # Show top 3
        
        # Experience
        years_exp = candidate.get("years_of_experience_raw", 0)
        rationale.append(f"{years_exp} years of experience")
        
        # Company context
        company_name = self._get_current_company_name(candidate)
        company_headcount = self._get_current_company_headcount(candidate)
        if company_name:
            rationale.append(f"Currently at {company_name} ({company_headcount:,} employees)")
        
        return rationale[:3]  # Return top 3 rationale points
    
    def _get_current_title(self, candidate: Dict[str, Any]) -> str:
        """Extract current job title from candidate."""
        current_employers = candidate.get("current_employers", [])
        if current_employers:
            return current_employers[0].get("title", "")
        return ""
    
    def _get_current_company_name(self, candidate: Dict[str, Any]) -> str:
        """Extract current company name from candidate."""
        current_employers = candidate.get("current_employers", [])
        if current_employers:
            return current_employers[0].get("name", "")
        return ""
    
    def _get_current_company_headcount(self, candidate: Dict[str, Any]) -> int:
        """Extract current company headcount from candidate."""
        current_employers = candidate.get("current_employers", [])
        if current_employers:
            return current_employers[0].get("company_headcount_latest", 0)
        return 0
    
    def _get_current_company_industries(self, candidate: Dict[str, Any]) -> List[str]:
        """Extract current company industries from candidate."""
        current_employers = candidate.get("current_employers", [])
        if current_employers:
            industries = current_employers[0].get("company_industries", [])
            return industries if isinstance(industries, list) else [industries] if industries else []
        return []
    
    def _get_current_job_start_date(self, candidate: Dict[str, Any]) -> str:
        """Extract current job start date from candidate."""
        current_employers = candidate.get("current_employers", [])
        if current_employers:
            return current_employers[0].get("start_date", "")
        return ""
    
    def _is_recent_role(self, start_date: str) -> bool:
        """Check if the role started within the last 3 years."""
        try:
            from datetime import datetime, timedelta
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            three_years_ago = datetime.now() - timedelta(days=3*365)
            return start_dt >= three_years_ago
        except (ValueError, TypeError):
            return False
