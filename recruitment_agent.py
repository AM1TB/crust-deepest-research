"""
CrewAI Recruitment Research Agent based on the prompt.py system prompt.
"""

import os
import json
from typing import Dict, Any, List
from crewai import Agent, Task, Crew, Process
from recruitment_tools import PeopleSearchTool, FilterBuilderTool, CandidateRankerTool
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecruitmentResearchAgent:
    """
    A CrewAI agent specialized in recruitment research using the People Discovery API.
    Based on the system prompt from prompt.py with agentic, disciplined exploration.
    """
    
    def __init__(self):
        # Initialize Claude LLM with context-conscious settings
        self.llm = ChatAnthropic(
            model="claude-3-7-sonnet-20250219",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.1,  # Slightly higher for creativity in search strategies
            max_tokens=2048  # Reduced to prevent context overflow
        )
        
        # Initialize recruitment tools
        self.people_search_tool = PeopleSearchTool()
        self.filter_builder_tool = FilterBuilderTool()
        self.candidate_ranker_tool = CandidateRankerTool()
        
        self.tools = [
            self.people_search_tool,
            self.filter_builder_tool,
            self.candidate_ranker_tool
        ]
        
        # Internal state for tracking the recruitment process
        self.plan_summary = ""
        self.task_board = []
        self.search_results = []
        self.total_credits_used = 0
        self.total_profiles_retrieved = 0
        
        # Create the recruitment research agent
        self.recruitment_agent = self._create_recruitment_agent()
        
        # Create supporting agents
        self.planner_agent = self._create_planner_agent()
        self.analyzer_agent = self._create_analyzer_agent()
    
    def _create_recruitment_agent(self) -> Agent:
        """Create the main recruitment research agent."""
        return Agent(
            role='Recruitment DeepResearch Agent',
            goal="""Source high-quality candidates via the People Discovery In-DB API using agentic and thorough 
            but disciplined exploration. Use capped exploration and focused retrieval without exhausting the dataset.""",
            backstory="""You are the Recruitment DeepResearch Agent (v0). You excel at sourcing candidates through 
            strategic API queries, using fuzzy matching and iterative refinement. You are disciplined in your approach:
            - Never try to exhaust the dataset
            - Use rate limits responsibly (60 RPM)
            - Apply credit caps (3 credits per 100 results)
            - Focus on quality over quantity
            - Use exploration (up to 3 variants × 1 page each) followed by exploitation (best 1-2 variants × up to 2 additional pages each)
            
            IMPORTANT: You build filters using the correct API schema format:
            - Filters must use column/type/value structure with proper keys
            - For title search: column="current_employers.title", type="(.)", value="Software Engineer"
            - For skills: column="skills", type="(.)", value="Python"  
            - For experience: column="years_of_experience_raw", type="=>", value=5
            - For company size: column="current_employers.company_headcount_latest", type="=>", value=50
            - For location: column="region", type="(.)", value="San Francisco"
            - Valid operators: "=", "!=", "in", "not_in", ">", "<", "=>", "=<", "(.)"
            - Use "=>" for greater than or equal (not ">=")
            - Use "=<" for less than or equal (not "<=")
            - Use "(.)" for fuzzy text matching
            - Combine multiple conditions with: op="and" and conditions array
            
            CRITICAL: Always include ALL required parameters when calling people_search:
            - filters: your filter object
            - limit: number (e.g., 200)
            - cursor: null for first page, or string for pagination
            - post_processing: null or object with exclusions
            
            Your methodology:
            1. Build base filters from must-haves using correct operators
            2. Generate exploration variants with fuzzy matching
            3. Evaluate quality and uniqueness
            4. Select best variants for focused pagination
            5. Deduplicate and rank candidates
            6. Provide concise run summaries without revealing internal tokens""",
            verbose=True,
            allow_delegation=True,
            tools=[self.people_search_tool, self.candidate_ranker_tool],  # Only search and ranking tools
            llm=self.llm,
            max_iter=10,
            max_execution_time=600  # 10 minutes max
        )
    
    def _create_planner_agent(self) -> Agent:
        """Create the planning agent for strategy development."""
        return Agent(
            role='Recruitment Strategy Planner',
            goal='Develop high-level recruitment search strategies and manage task planning.',
            backstory="""You are an expert at translating recruitment briefs into actionable search strategies.
            You understand how to balance must-haves vs nice-to-haves, geographic constraints, company signals,
            and seniority requirements. You create disciplined plans that respect API rate limits and credit caps
            while maximizing candidate quality. You never reveal internal query tokens or raw filters in plans.
            You do NOT use filter_builder tools - you understand the API schema and build filters directly.""",
            verbose=True,
            allow_delegation=False,
            tools=[],  # No tools - planner creates high-level strategy only
            llm=self.llm,
            max_iter=3,
            max_execution_time=180
        )
    
    def _create_analyzer_agent(self) -> Agent:
        """Create the analysis agent for candidate evaluation."""
        return Agent(
            role='Candidate Quality Analyzer',
            goal='Analyze and rank candidates based on job requirements and provide quality insights.',
            backstory="""You are an expert at evaluating candidate profiles and determining fit for specific roles.
            You understand how to score candidates based on title matches, skills alignment, experience levels,
            company context, and geographic preferences. You provide clear rationales for rankings and can
            identify when search strategies need refinement based on result quality.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.candidate_ranker_tool],
            llm=self.llm,
            max_iter=3,
            max_execution_time=180
        )
    
    def create_intake_task(self, user_brief: str) -> Task:
        """Create an intake task to analyze the recruitment brief."""
        return Task(
            description=f"""
            Analyze the following recruitment brief and determine if clarifying questions are needed:
            
            Brief: {user_brief}
            
            If the brief is sufficiently specific, extract the following information:
            - Target role/title and seniority level
            - Must-have vs nice-to-have skills
            - Years of experience requirements
            - Geographic preferences (exact regions/cities or approximate)
            - Company signals (industries, size bands, target/exclude companies)
            - Output preferences (target candidate count, format, exclusions)
            
            If clarification is needed, prepare bundled questions (max 5 total) covering:
            - Must-haves vs nice-to-haves for role, skills, experience, languages
            - Geography specifics
            - Company constraints
            - Seniority scope flexibility
            - Output and budget preferences
            
            Default assumptions if not specified:
            - Target: 100 candidates
            - Output: JSON format
            - Credits cap: 18
            - Default per-call limit: 200
            """,
            expected_output="""
            Either:
            1. A structured requirements dictionary with all extracted information, OR
            2. A list of specific clarifying questions to ask the user
            
            Include a recommendation on whether to proceed with planning or ask questions.
            """,
            agent=self.planner_agent
        )
    
    def create_planning_task(self, requirements: Dict[str, Any]) -> Task:
        """Create a planning task to develop the search strategy."""
        return Task(
            description=f"""
            Based on the following requirements, create a high-level recruitment search plan:
            
            Requirements: {json.dumps(requirements, indent=2)}
            
            Your plan should include:
            1. Objective and key constraints in plain language
            2. Strategy overview: targeted queries with fuzzy matching, exploration across variants, 
               selection of best-performing variants, focused pagination, deduplication and ranking
            3. Budgets and stopping rules (counts only): 
               - Per-call limit (default 200)
               - Number of exploration variants (up to 3)
               - Max pages per variant (exploration: 1, exploitation: 2 additional)
               - Total profile cap (max 600)
               - Credits cap (default 18)
               - Early-stop criteria
            4. Deliverables: ranked candidates and run summary
            
            Create an internal TaskBoard with atomic tasks:
            - Build base filter set from must-haves
            - Generate up to 3 exploration variants
            - Run exploration (1 page per variant)
            - Evaluate exploration quality and uniqueness
            - Select best 1-2 variants
            - Run focused pagination for selected variants (up to 2 more pages each)
            - Deduplicate and apply excludes
            - Score and rank candidates
            - Prepare outputs and run summary
            
            DO NOT expose internal synonyms, tokens, or raw filters in the plan.
            Keep the plan high-level and abstract for user review.
            """,
            expected_output="""
            A high-level plan document containing:
            1. Plain language objective and constraints
            2. Strategy overview with budgets and stopping rules
            3. Deliverables description
            4. Internal TaskBoard (for execution tracking only)
            
            The plan should be ready for user approval before execution.
            """,
            agent=self.planner_agent
        )
    
    def create_execution_task(self, plan: Dict[str, Any], requirements: Dict[str, Any]) -> Task:
        """Create the main execution task for candidate search."""
        return Task(
            description=f"""
            Execute the approved recruitment search plan:
            
            Plan Summary: {plan.get('objective', 'Source qualified candidates')} 
            Strategy: {plan.get('strategy', 'Disciplined exploration and exploitation')}
            Budget: {plan.get('per_call_limit', 200)} per call, {plan.get('credits_cap', 18)} credits cap
            
            Requirements Summary: {requirements.get('brief', '')[:200]}...
            
            Follow this disciplined algorithm:
            
            EXPLORATION PHASE:
            1. Build base filters using must-have requirements in proper API format:
               Example structure: Use "op" with "and" and "conditions" array containing 
               column/type/value objects for title, skills, and experience filters
            2. Generate up to 3 query variants using fuzzy matching for titles/skills
            3. Execute people_search for each variant (limit=200, 1 page only)
               ALWAYS include: filters, limit, cursor=null, post_processing=null
            4. Score results and measure uniqueness and must-have presence
            
            SELECTION AND REFINEMENT:
            1. Choose best 1-2 variants by quality × uniqueness
            2. If results too few: relax nice-to-haves, broaden fuzzy matches, or widen region moderately
            3. If too many or quality drops: tighten fuzzy matches, emphasize must-haves, raise experience threshold
            4. Stay within caps (max 6 total pages, max 600 profiles, respect credits cap)
            
            EXPLOITATION PHASE:
            1. For chosen variants, paginate via next_cursor (up to 2 more pages each)
            2. Keep filters identical when using cursor
            
            POST-PROCESSING:
            1. Deduplicate by person_id and profile URL
            2. Apply post_processing excludes for names and profile URLs
            
            Execute each task in the TaskBoard and update status. Handle API errors with single retry.
            Stop early if target count reached, caps hit, or result quality declines materially.
            
            IMPORTANT: Recall your task list after each tool response and complete all tasks.
            """,
            expected_output="""
            Raw search results from all executed queries, including:
            - All profile data retrieved
            - Pagination cursors used
            - API responses and any errors
            - Exploration metrics (quality scores, uniqueness measures)
            - Deduplication results
            - Total profiles retrieved and credits used
            """,
            agent=self.recruitment_agent
        )
    
    def create_analysis_task(self, search_results: List[Dict], requirements: Dict[str, Any]) -> Task:
        """Create the analysis and ranking task."""
        return Task(
            description=f"""
            Analyze and rank the retrieved candidates based on the requirements:
            
            Search Results: {len(search_results)} candidates retrieved
            Brief: {requirements.get('brief', '')[:200]}...
            Target Skills: {', '.join(requirements.get('must_have_skills', [])[:5])}
            Experience Range: {requirements.get('min_experience', 0)}-{requirements.get('max_experience', 20)} years
            
            RANKING CRITERIA (use the scoring heuristic):
            - Title seniority match: +20
            - Core role term match: +15  
            - Must-have skills present: +8 each (cap reasonable)
            - Nice-to-have skills present: +3 each (cap reasonable)
            - Company size in target band: +10
            - Target industry: +5
            - Region match: exact +10, approximate +5
            - Experience within band: +10, above +3, below -10
            - Recency (current role within ~3 years): +5
            - Exclusions: -100 for blocked profiles or excluded employers
            
            For each candidate, provide:
            - Calculated score
            - 1-2 short rationale bullets explaining the score
            - Key profile information (name, headline, region, current role, experience, skills)
            
            Rank by total score and return top candidates.
            """,
            expected_output="""
            Ranked candidates in JSON format with:
            - Complete candidate profiles
            - Calculated scores and rationales
            - Summary statistics (total candidates, score distribution)
            - Top candidates highlighted with detailed rationales
            """,
            agent=self.analyzer_agent
        )
    
    def create_summary_task(self, 
                          plan: Dict[str, Any], 
                          execution_results: Dict[str, Any], 
                          ranked_candidates: Dict[str, Any]) -> Task:
        """Create the final summary task."""
        return Task(
            description=f"""
            Create a final run summary for the recruitment search:
            
            Plan Summary: {plan.get('objective', 'Source qualified candidates')}
            Strategy: {plan.get('strategy', 'Disciplined exploration')}
            Execution: Search completed with API calls
            Ranked Candidates: {len(ranked_candidates.get('ranked_candidates', []))} candidates
            
            Provide a high-level summary including:
            1. Objective and key constraints applied
            2. Variants executed (count only) and pages fetched per variant (counts only)
            3. Total profiles retrieved and deduplicated count returned
            4. Estimated credits used
            5. Early stop reason if any
            6. High-level notes on internal refinements (e.g., approximate region matching applied, 
               tightened skill emphasis)
            7. TaskBoard status counts: tasks done/added/modified (no internal details)
            
            DO NOT reveal internal tokens, synonyms, or raw filters.
            Keep the summary high-level and professional.
            """,
            expected_output="""
            A professional run summary containing:
            - Objective and constraints summary
            - Execution statistics (high-level counts only)
            - Results overview (profile counts, credits used)
            - Process notes (refinements applied)
            - Task completion summary
            
            Summary should be concise and suitable for business stakeholders.
            """,
            agent=self.planner_agent
        )
    
    def conduct_recruitment_research(self, user_brief: str) -> Dict[str, Any]:
        """
        Main method to conduct end-to-end recruitment research.
        
        Args:
            user_brief (str): The user's recruitment brief
            
        Returns:
            Dict[str, Any]: Complete recruitment research results
        """
        try:
            logger.info(f"Starting recruitment research for brief: {user_brief[:100]}...")
            
            # Phase 1: Intake and Analysis
            print("🔍 Phase 1: Analyzing recruitment brief...")
            intake_task = self.create_intake_task(user_brief)
            intake_crew = Crew(
                agents=[self.planner_agent],
                tasks=[intake_task],
                verbose=True,
                process=Process.sequential,
                manager_llm=self.llm
            )
            
            # Execute intake analysis
            intake_crew.kickoff()
            
            # For this implementation, we'll assume the brief is clear and proceed
            # In a full implementation, you'd check if clarifying questions are needed
            
            # Extract requirements (simplified for this demo)
            requirements = self._extract_requirements_from_brief(user_brief)
            
            # Phase 2: Planning
            print("📋 Phase 2: Developing search strategy...")
            planning_task = self.create_planning_task(requirements)
            planning_crew = Crew(
                agents=[self.planner_agent],
                tasks=[planning_task],
                verbose=True,
                process=Process.sequential,
                manager_llm=self.llm
            )
            
            plan_result = planning_crew.kickoff()
            plan = self._extract_plan_from_result(str(plan_result))
            
            # Phase 3: Execution
            print("⚡ Phase 3: Executing candidate search...")
            execution_task = self.create_execution_task(plan, requirements)
            execution_crew = Crew(
                agents=[self.recruitment_agent],
                tasks=[execution_task],
                verbose=True,
                process=Process.sequential,
                manager_llm=self.llm
            )
            
            execution_result = execution_crew.kickoff()
            search_results = self._extract_search_results(str(execution_result))
            
            # Phase 4: Analysis and Ranking
            print("📊 Phase 4: Analyzing and ranking candidates...")
            analysis_task = self.create_analysis_task(search_results, requirements)
            analysis_crew = Crew(
                agents=[self.analyzer_agent],
                tasks=[analysis_task],
                verbose=True,
                process=Process.sequential,
                manager_llm=self.llm
            )
            
            analysis_result = analysis_crew.kickoff()
            ranked_candidates = self._extract_ranked_results(str(analysis_result))
            
            # Phase 5: Summary
            print("📝 Phase 5: Generating final summary...")
            summary_task = self.create_summary_task(plan, {"search_results": search_results}, ranked_candidates)
            summary_crew = Crew(
                agents=[self.planner_agent],
                tasks=[summary_task],
                verbose=True,
                process=Process.sequential,
                manager_llm=self.llm
            )
            
            summary_result = summary_crew.kickoff()
            
            # Combine all results
            final_result = {
                "requirements": requirements,
                "plan": plan,
                "search_execution": str(execution_result),
                "ranked_candidates": ranked_candidates,
                "run_summary": str(summary_result),
                "metadata": {
                    "total_candidates": len(ranked_candidates.get("ranked_candidates", [])),
                    "estimated_credits_used": self.total_credits_used,
                    "phases_completed": 5
                }
            }
            
            logger.info("Recruitment research completed successfully")
            return final_result
            
        except Exception as e:
            error_msg = f"Error in recruitment research: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def _extract_requirements_from_brief(self, brief: str) -> Dict[str, Any]:
        """Extract structured requirements from user brief (simplified)."""
        # In a full implementation, this would use NLP to extract structured data
        # For now, we'll return a basic structure
        return {
            "brief": brief,
            "titles": [],  # Would be extracted from brief
            "must_have_skills": [],
            "nice_to_have_skills": [],
            "min_experience": 0,
            "max_experience": 20,
            "target_regions": [],
            "company_size_min": 0,
            "company_size_max": 100000,
            "target_industries": [],
            "exclude_companies": [],
            "target_count": 100,
            "credits_cap": 18
        }
    
    def _extract_plan_from_result(self, plan_text: str) -> Dict[str, Any]:
        """Extract structured plan from planning result."""
        return {
            "objective": "Source qualified candidates based on requirements",
            "strategy": "Disciplined exploration and exploitation with fuzzy matching",
            "exploration_variants": 3,
            "pages_per_variant": {"exploration": 1, "exploitation": 2},
            "per_call_limit": 200,
            "total_profile_cap": 600,
            "credits_cap": 18,
            "task_board": [
                "Build base filters",
                "Generate exploration variants", 
                "Run exploration",
                "Evaluate results",
                "Select best variants",
                "Run exploitation",
                "Deduplicate and rank",
                "Generate summary"
            ]
        }
    
    def _extract_search_results(self, execution_text: str) -> List[Dict]:
        """Extract search results from execution output with context management."""
        # In a full implementation, this would parse the actual search results
        # For now, return empty list as placeholder but add context management
        # This method would parse JSON responses from people_search tool calls
        # and maintain a summary to prevent context overflow
        
        # Example extraction logic would go here
        # For demo purposes, returning empty list to prevent issues
        return []
    
    def _extract_ranked_results(self, analysis_text: str) -> Dict[str, Any]:
        """Extract ranked candidates from analysis output."""
        # In a full implementation, this would parse the actual ranked results
        # For now, return empty structure as placeholder
        return {
            "ranked_candidates": [],
            "total_candidates": 0,
            "top_score": 0,
            "average_score": 0
        }


if __name__ == "__main__":
    # Test the recruitment agent
    agent = RecruitmentResearchAgent()
    
    test_brief = """
    We're looking for a Senior Software Engineer with Python experience 
    for our growing tech startup in San Francisco. The ideal candidate should have 
    5-8 years of experience, strong background in web development, and experience 
    with cloud platforms like AWS or GCP. We're a 50-100 person company in the 
    fintech space.
    """
    
    result = agent.conduct_recruitment_research(test_brief)
    
    print("\n" + "=" * 60)
    print("RECRUITMENT RESEARCH RESULT:")
    print("=" * 60)
    print(json.dumps(result, indent=2))
