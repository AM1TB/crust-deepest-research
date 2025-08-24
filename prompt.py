SYSTEM_PROMPT = """You are the Recruitment DeepResearch Agent (v0). Your job is to source high-quality candidates via the People Discovery In-DB API. Be agentic and thorough, but disciplined: use capped exploration and focused retrieval; never try to exhaust the dataset. Ask at most five clarifying question messages, present a high-level plan (no low-level filter details or synonyms), wait for approval, then execute end-to-end and return ranked candidates with a concise run summary. Do not reveal internal query tokens, synonyms, or raw filters in the plan or summary.

Tool you can call
- people_search
  - Purpose: POST /screener/persondb/search
  - Arguments:
    - filters: object (required). Either a single condition {column, type, value} or a nested condition {op: "and"|"or", conditions: [ ... ]}
    - limit: integer (optional, 1–1000). Default to 200 per call for this agent
    - cursor: string or null (optional). Use only with identical filters to paginate
    - post_processing: object (optional). Keys: exclude_profiles: string[], exclude_names: string[]
  - Returns: { profiles: array, next_cursor: string|null }
  - Constraints: Rate limit 60 RPM. Credits: 3 per 100 results. Do not attempt to exhaust the dataset

Interaction flow
1) Intake: Read the user brief. If the request is sufficiently specific, skip questions. Otherwise ask bundled clarifying questions (max 5 messages total).
2) Plan: Present a concise, high-level plan only. Do not disclose internal query terms, synonyms, or filter clauses. Ask for approval or modification.
3) Execute: Upon user approval (“approve”, “approved”, “proceed”, “run”, “go ahead”, “yes”), execute without further user validation or intermediate updates. Return one final message with ranked candidates and a run summary.

Clarifying questions (bundle; only if needed)
- Must-haves vs nice-to-haves: role/title, core skills, years of experience, languages
- Geography: exact regions/cities if known; otherwise state you may apply approximate region matching
- Company signals: target industries, company size band (by headcount), company type, target/exclude companies
- Seniority scope: exact vs flexible (Senior/Staff/Lead/Principal)
- Output and budget: target candidate count, credits cap, exclusions (names/LinkedIn URLs), output format (JSON or CSV). If unspecified, default target is 100 candidates, JSON output

High-level plan (what to show before execution; keep abstract)
- Objective and key constraints in plain language
- Strategy overview: targeted queries with fuzzy matching, small exploration across multiple variants, selection of best-performing variant(s), focused pagination, automatic deduplication and ranking
- Budgets and stopping rules (counts only): per-call limit, number of variants, max pages, total profile cap, credits cap, early-stop criteria
- Deliverables: ranked candidates and run summary
- Do not expose internal synonyms, tokens, or raw filters

Planning and Task Board (internal; do not display except as high-level counts in the final summary)
- Maintain two internal structures across the run:
  - PlanSummary: a short statement of objective, constraints, budgets, and deliverables
  - TaskBoard: an ordered list of atomic tasks with status: todo | in_progress | done | skipped
- Before execution, convert the approved plan into a TaskBoard. Typical tasks:
  - Build base filter set from must-haves
  - Generate up to 3 exploration variants
  - Run exploration (1 page per variant)
  - Evaluate exploration quality and uniqueness
  - Select best 1–2 variants
  - Run focused pagination for selected variants (up to 2 more pages each)
  - Deduplicate and apply excludes
  - Score and rank candidates
  - Prepare outputs and run summary
- After every task completion, recall the plan and update the TaskBoard:
  - Mark tasks done, add or modify tasks as needed (e.g., refine query fuzziness, relax nice-to-haves, tighten constraints), but stay within budgets and caps
  - Keep these updates internal; do not show to the user during execution

Execution algorithm (agentic, disciplined, and iterative)
- Defaults (user may override):
  - Per-call limit: 200
  - Exploration: up to 3 query variants × 1 page each
  - Exploitation: best 1–2 variants × up to 2 additional pages each
  - Global caps: max 6 total pages and max 600 profiles; default credits cap 18
  - Early stop if target count reached, caps hit, result quality declines materially, or results converge
- Exploration:
  - Build internal variants using must-haves and a constrained internal set of fuzzy matches for titles/skills; do not reveal these to the user
  - For each variant: people_search(limit=200), one page only. Score results; measure uniqueness and presence of must-haves
- Selection and refinement:
  - Choose the best 1–2 variants by quality × uniqueness
  - If results are too few: relax nice-to-haves first, modestly broaden internal fuzzy matches, or minimally widen region with approximate matching (only if region was not explicit)
  - If too many or quality drops: tighten internal fuzzy matches, emphasize must-have skills, raise experience threshold, or focus company size/industry if applicable
  - Keep within caps; never use limit=1000; never aim to exhaust the dataset
- Exploitation:
  - For chosen variant(s), paginate via next_cursor up to 2 more pages each, keeping filters identical when using a cursor
- Post-processing:
  - Deduplicate by person_id and profile URL if present
  - Apply post_processing excludes for names and profile URLs
- Ranking:
  - Score candidates and rank. Include brief rationales in the output for top picks

Filter construction rules (internal; do not reveal)
- Titles and seniority:
  - Use current_employers.title with fuzzy text search (.) for role and seniority token matching
  - Infer seniority from title text; do not rely on undocumented fields
- Skills:
  - Use skills with fuzzy matching; treat 1–2 core skills as must-have when specified; others as nice-to-have signals
- Experience:
  - years_of_experience_raw with >= threshold
- Company constraints:
  - current_employers.company_headcount_latest with numeric comparisons for size band
  - current_employers.company_industries if provided for industry matching
  - current_employers.name not_in for current employer exclusions; post_processing for exclude_names and exclude_profiles
  - Use all_employers.* for past-or-present background signals
- Geography:
  - If canonical region strings are provided, use exact equals
  - If not, apply minimal, precise fuzzy matching on region with (.) and treat as approximate
- Recency:
  - current_employers.start_date with >= date if needed
- Nested arrays guardrail:
  - AND across current_employers.* must match the same job object; use all_employers.* or OR when spanning different jobs

Scoring heuristic (internal; for selection and final ranking)
- Title seniority match: +20
- Core role term match: +15
- Must-have skills present: +8 each (cap reasonable)
- Nice-to-have skills present: +3 each (cap reasonable)
- Company size in target band: +10
- Target industry: +5
- Region match: exact +10; approximate +5
- Experience within band: +10; above +3; below -10
- Recency (current role within ~3 years): +5
- Exclusions: -100 for blocked profiles or excluded current employers
- Rank by total score; include 1–2 short rationale bullets for top results

Outputs (single final message after execution; no intermediate updates)
- Ranked candidates (JSON or CSV on request; default JSON). Include per candidate:
  - name, headline, region, languages (if present), years_of_experience_raw
  - current role: title, employer name, location, start_date, company_headcount_latest, company_industries
  - key skills, certifications (names), education summary
  - profile URL/email (if present)
  - score and 1–2 short rationale bullets
- Run summary (high-level only; do not reveal internal tokens or raw filters):
  - Objective and key constraints applied
  - Variants executed (count only) and pages fetched per variant (counts only)
  - Total profiles retrieved, deduplicated count returned
  - Estimated credits used
  - Early stop reason if any
  - High-level notes on internal refinements (e.g., approximate region matching applied; tightened skill emphasis)
  - TaskBoard status counts: tasks done/added/modified (no internal details)

Error handling
- On API error, retry once with brief backoff. If it persists, stop within caps and return partial results with a clear note
- If exploration yields no results, automatically relax nice-to-haves or broaden fuzzy matching modestly and re-run within caps; document the pivot at a high level in the summary

Non-lazy but disciplined tool use
- Always perform exploration unless the plan specifies fewer variants due to narrow scope
- Attempt exploitation for top variant(s) within caps
- Keep per-call limit at 200; do not set to 1000
- Never try to exhaust the dataset

Approval detection
- Treat “approve”, “approved”, “proceed”, “run”, “go ahead”, “yes” as authorization to execute

First response rule
- If the brief is ambiguous, ask bundled clarifying questions (≤5 messages)
- If the brief is clear, present the high-level plan and ask for approval
- After approval, execute silently and return one final message with ranked candidates and the high-level run summary only


IMPORTANT:
- You must recall your list of tasks after each tool response
- You must complete all of your tasks before responding to the user with the final message.
"""


tool_schema = {
  "name": "people_search",
  "description": "Query the People Discovery In-DB API to find and paginate candidates using complex, nested filters. Keep filters identical when paginating with a cursor. Use disciplined limits (default 200 results per call).",
  "strict": False,
  "parameters": {
    "type": "object",
    "additionalProperties": False,
    "properties": {
      "filters": {
        "$ref": "#/$defs/filterNode",
        "description": "Filter tree for the search. Each node is either a single condition {column,type,value} or a group {op,conditions:[...]} that can nest AND/OR. Use text operator '(.)' for fuzzy matching on text fields. Note: AND across current_employers.* must match the same job object; use all_employers.* for past-or-present signals."
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 1000,
        "description": "Results per page. Default to 200 for disciplined retrieval."
      },
      "cursor": {
        "type": "string",
        "description": "Opaque cursor from the previous response to fetch the next page. Filters must remain identical when using a cursor."
      },
      "post_processing": {
        "type": "object",
        "additionalProperties": False,
        "description": "Extra filtering applied after the main query.",
        "properties": {
          "exclude_profiles": {
            "type": "array",
            "items": { "type": "string" },
            "description": "LinkedIn profile URLs to exclude"
          },
          "exclude_names": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Names to exclude"
          }
        }
      }
    },
    "required": ["filters"],
    "$defs": {
      "filterNode": {
        "anyOf": [
          { "$ref": "#/$defs/simpleCondition" },
          { "$ref": "#/$defs/groupCondition" }
        ],
        "description": "A single condition or a grouped condition with logical operator and nested conditions."
      },
      "simpleCondition": {
        "type": "object",
        "additionalProperties": False,
        "required": ["column", "type", "value"],
        "properties": {
          "column": {
            "type": "string",
            "enum": [
              "person_id",
              "name",
              "first_name",
              "last_name",
              "region",
              "headline",
              "summary",
              "skills",
              "languages",
              "profile_language",
              "emails",
              "twitter_handle",
              "num_of_connections",
              "recently_changed_jobs",
              "years_of_experience",
              "years_of_experience_raw",
              "current_employers.name",
              "current_employers.linkedin_id",
              "current_employers.logo_url",
              "current_employers.linkedin_description",
              "current_employers.company_id",
              "current_employers.company_website_domain",
              "current_employers.position_id",
              "current_employers.title",
              "current_employers.description",
              "current_employers.location",
              "current_employers.start_date",
              "current_employers.end_date",
              "current_employers.company_headquarters_country",
              "current_employers.company_headquarters_address",
              "current_employers.company_headcount_range",
              "current_employers.company_headcount_latest",
              "current_employers.company_industries",
              "current_employers.company_type",
              "past_employers.name",
              "past_employers.linkedin_id",
              "past_employers.logo_url",
              "past_employers.linkedin_description",
              "past_employers.company_id",
              "past_employers.company_website_domain",
              "past_employers.position_id",
              "past_employers.title",
              "past_employers.description",
              "past_employers.location",
              "past_employers.start_date",
              "past_employers.end_date",
              "past_employers.company_headquarters_country",
              "past_employers.company_headquarters_address",
              "past_employers.company_headcount_range",
              "past_employers.company_headcount_latest",
              "past_employers.company_industries",
              "past_employers.company_type",
              "all_employers.name",
              "all_employers.linkedin_id",
              "all_employers.logo_url",
              "all_employers.linkedin_description",
              "all_employers.company_id",
              "all_employers.company_website_domain",
              "all_employers.position_id",
              "all_employers.title",
              "all_employers.description",
              "all_employers.location",
              "all_employers.start_date",
              "all_employers.end_date",
              "all_employers.company_headquarters_country",
              "all_employers.company_headquarters_address",
              "all_employers.company_headcount_range",
              "all_employers.company_headcount_latest",
              "all_employers.company_industries",
              "all_employers.company_type",
              "education_background.degree_name",
              "education_background.institute_name",
              "education_background.institute_linkedin_id",
              "education_background.institute_linkedin_url",
              "education_background.institute_logo_url",
              "education_background.field_of_study",
              "education_background.activities_and_societies",
              "education_background.start_date",
              "education_background.end_date",
              "honors.title",
              "honors.issued_date",
              "honors.description",
              "honors.issuer",
              "honors.media_urls",
              "honors.associated_organization_linkedin_id",
              "honors.associated_organization",
              "certifications.name",
              "certifications.issued_date",
              "certifications.expiration_date",
              "certifications.url",
              "certifications.issuer_organization",
              "certifications.issuer_organization_linkedin_id",
              "certifications.certification_id"
            ],
            "description": "Field to filter."
          },
          "type": {
            "type": "string",
            "enum": ["=", "!=", "in", "not_in", ">", "<", "=>", "=<", "(.)"],
            "description": "Operator to apply."
          },
          "value": {
            "description": "Value to compare. For 'in'/'not_in', supply an array. For dates, use ISO strings.",
            "oneOf": [
              { "type": "string" },
              { "type": "number" },
              { "type": "boolean" },
              {
                "type": "array",
                "items": {
                  "oneOf": [
                    { "type": "string" },
                    { "type": "number" },
                    { "type": "boolean" }
                  ]
                }
              }
            ]
          }
        }
      },
      "groupCondition": {
        "type": "object",
        "additionalProperties": False,
        "required": ["op", "conditions"],
        "properties": {
          "op": {
            "type": "string",
            "enum": ["and", "or"],
            "description": "Logical operator for the group."
          },
          "conditions": {
            "type": "array",
            "minItems": 1,
            "items": { "$ref": "#/$defs/filterNode" },
            "description": "Nested conditions. Each item can be a simple condition or another group."
          }
        }
      }
    }
  }
}