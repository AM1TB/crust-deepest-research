# CrewAI Deep Research Agent with Recruitment Functionality

A powerful multi-agent system built with CrewAI that performs comprehensive research and specialized recruitment research using the People Discovery API. The system orchestrates multiple agents to conduct deep research and source high-quality candidates through disciplined API exploration.

## Features

- 🤖 **Deep Research Agent**: Specialized in comprehensive research with systematic methodology
- 🎯 **Recruitment Research Agent**: AI-powered candidate sourcing using People Discovery API
- 🔌 **REST API Integration**: Custom tools for fetching data from multiple APIs
- 🌐 **Web Search Capabilities**: Optional integration with search engines (requires API keys)
- 📊 **Advanced Data Analysis**: Multi-phase analysis with ranking and scoring algorithms
- 🏗️ **Multi-Agent Orchestration**: Coordinated workflow across specialized agents
- ⚡ **Disciplined Exploration**: Capped API usage with quality-focused search strategies

## Project Structure

```
crust-deepest-research/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── main.py               # Main script to run the agent
├── agent.py              # Main CrewAI agent implementation
├── tools.py              # Basic REST API tools (todo examples)
├── recruitment_agent.py  # Specialized recruitment research agent
├── recruitment_tools.py  # People Discovery API tools
├── prompt.py             # Original system prompt and tool schema
├── utils/
│   └── api_client.py     # API utility functions
├── api-docs/
│   └── people-api-docs.md # People Discovery API documentation
└── env_example.txt       # Environment variables example
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**:
   - Copy `env_example.txt` to `.env`
   - Add your Anthropic API key (required)
   - Add optional API keys for enhanced functionality

3. **Run the Agent**:
   ```bash
   python main.py
   ```

## API Integration

The system includes multiple specialized API tools:

### Basic Research Tools
- **TodoAPITool**: Fetches individual todo items from JSONPlaceholder API
- **MultiTodoAPITool**: Fetches multiple todo items with filtering

### Recruitment Research Tools
- **PeopleSearchTool**: Advanced candidate search using People Discovery API
- **FilterBuilderTool**: Constructs complex search filters for recruitment queries
- **CandidateRankerTool**: Scores and ranks candidates based on job requirements

### People Discovery API Features
- Complex nested filters with AND/OR logic
- Fuzzy text matching using '(.)' operator
- Pagination with cursor-based navigation
- Rate limiting (60 RPM) and credit management
- Advanced post-processing exclusions

### Sample Recruitment API Response
```json
{
  "profiles": [
    {
      "person_id": "12345",
      "name": "John Doe",
      "headline": "Senior Software Engineer",
      "region": "San Francisco, CA",
      "years_of_experience_raw": 7,
      "skills": ["Python", "AWS", "React"],
      "current_employers": [{
        "title": "Senior Software Engineer",
        "name": "Tech Startup Inc",
        "company_headcount_latest": 75,
        "company_industries": ["Technology", "Financial Services"]
      }]
    }
  ],
  "next_cursor": "eyJ0aW1lc3RhbXAiOiIyMDI0LTEwLTE1VDE2OjMwOjAwWiJ9"
}
```

## Usage Examples

### Interactive Mode
Run `python main.py` and choose from the menu:
1. Conduct research on a custom topic
2. Run demo research (AI in Software Development)
3. Conduct recruitment research
4. Run demo recruitment research
5. Test API tools only
6. Exit

### Programmatic Usage

#### General Research
```python
from agent import DeepResearchAgent

# Create agent
agent = DeepResearchAgent()

# Conduct research
result = agent.conduct_research("Machine Learning Trends 2024")
print(result)

# Test API functionality
agent.demo_api_functionality()
```

#### Recruitment Research
```python
from agent import DeepResearchAgent

# Create agent with recruitment capabilities
agent = DeepResearchAgent()

# Define recruitment brief
brief = """
We're looking for a Senior Software Engineer with Python experience 
for our growing tech startup in San Francisco. The ideal candidate should have 
5-8 years of experience, strong background in web development, and experience 
with cloud platforms like AWS or GCP.
"""

# Conduct recruitment research
result = agent.conduct_recruitment_research(brief)
print(result)
```

#### Direct Recruitment Agent Usage
```python
from recruitment_agent import RecruitmentResearchAgent

# Create specialized recruitment agent
recruiter = RecruitmentResearchAgent()

# Conduct end-to-end recruitment research
result = recruiter.conduct_recruitment_research(brief)
print(result)
```

## Research Capabilities

### General Research
The agent can research topics such as:
- Technology trends and developments
- Scientific concepts and theories
- Business strategies and markets
- Historical events and analysis
- Current events and news

### Recruitment Research
The recruitment agent specializes in:
- **Disciplined Candidate Sourcing**: Multi-phase exploration and exploitation
- **Complex Filter Construction**: Nested conditions with fuzzy matching
- **Quality-Focused Search**: Emphasis on must-have vs nice-to-have criteria
- **Intelligent Ranking**: Weighted scoring across multiple dimensions
- **Budget-Conscious Operation**: Respects API rate limits and credit caps

### Recruitment Workflow
1. **Intake Phase**: Analyze recruitment brief and extract requirements
2. **Planning Phase**: Develop high-level search strategy with task breakdown
3. **Exploration Phase**: Test 3 search variants with 1 page each (200 results)
4. **Selection Phase**: Choose best 1-2 variants based on quality metrics
5. **Exploitation Phase**: Deep pagination on selected variants (2+ pages each)
6. **Analysis Phase**: Rank candidates using weighted scoring algorithm
7. **Summary Phase**: Generate comprehensive run report

## API Keys Required

### Required
- **ANTHROPIC_API_KEY**: For CrewAI agent functionality with Claude

### Optional (for enhanced capabilities)
- **CRUSTDATA_API_KEY**: For People Discovery API access (recruitment features)
- **SERPER_API_KEY**: For web search functionality
- **GOOGLE_API_KEY**: For Google search integration
- **GOOGLE_CSE_ID**: For custom search engine

## Agent Configuration

### General Research Agent
- **Role**: Deep Research Specialist
- **Goal**: Comprehensive research with REST API integration
- **Tools**: Custom API tools + optional web search tools
- **Max Iterations**: 3
- **Max Execution Time**: 5 minutes

### Recruitment Research Agents
The system orchestrates three specialized agents:

#### 1. Recruitment DeepResearch Agent
- **Role**: Recruitment DeepResearch Agent (v0)
- **Goal**: Source high-quality candidates via disciplined People Discovery API exploration
- **Tools**: PeopleSearchTool, FilterBuilderTool, CandidateRankerTool
- **Max Iterations**: 10
- **Max Execution Time**: 10 minutes

#### 2. Recruitment Strategy Planner
- **Role**: Develops high-level search strategies and manages task planning
- **Goal**: Translate recruitment briefs into actionable search strategies
- **Tools**: FilterBuilderTool
- **Max Iterations**: 3
- **Max Execution Time**: 3 minutes

#### 3. Candidate Quality Analyzer
- **Role**: Analyzes and ranks candidates based on job requirements
- **Goal**: Evaluate candidate fit and provide quality insights
- **Tools**: CandidateRankerTool
- **Max Iterations**: 3
- **Max Execution Time**: 3 minutes

## Example Outputs

### General Research Output
The agent provides structured research reports including:
- Executive summary
- Detailed findings by theme
- Data analysis (including API data)
- Conclusions and recommendations
- Sources and references

### Recruitment Research Output
The recruitment system provides:
- **Requirements Summary**: Extracted job requirements and constraints
- **Search Strategy**: High-level approach with budget allocations
- **Results Summary**: Total candidates found, credits used, phases completed
- **Top Candidates**: Ranked list with scores and rationales
- **Run Summary**: Execution statistics and process notes

### Sample Recruitment Output
```
🎯 RECRUITMENT RESEARCH RESULTS
============================================================

📋 REQUIREMENTS SUMMARY:
Original Brief: We're looking for a Senior Software Engineer...
Target Count: 100 candidates
Credits Cap: 18

🔍 SEARCH STRATEGY:
Objective: Source qualified candidates based on requirements
Strategy: Disciplined exploration and exploitation with fuzzy matching
Exploration Variants: 3
Per-Call Limit: 200

📊 RESULTS SUMMARY:
Total Candidates Found: 87
Estimated Credits Used: 12
Phases Completed: 5/5

🏆 TOP CANDIDATES:
----------------------------------------
1. Jane Smith
   Score: 95
   Title: Senior Software Engineer at TechCorp
   Region: San Francisco, CA
   Rationale: Strong title match; Key skills: Python, AWS, React

2. John Doe
   Score: 87
   Title: Lead Software Engineer at StartupInc
   Region: San Francisco Bay Area
   Rationale: 8 years of experience; Currently at StartupInc (75 employees)
```

## Troubleshooting

### General Issues
1. **Missing API Keys**: Ensure ANTHROPIC_API_KEY is set in your environment
2. **Network Issues**: Check internet connection for API calls
3. **Tool Errors**: Verify API endpoints are accessible
4. **Timeout Issues**: Large research tasks may take time to complete

### Recruitment-Specific Issues
1. **CRUSTDATA_API_KEY Missing**: Recruitment features require People Discovery API access
2. **Rate Limit Errors**: Respect 60 RPM limit; agent includes built-in throttling
3. **Credit Limit Reached**: Monitor usage (3 credits per 100 results)
4. **No Candidates Found**: Try broader search criteria or different filter combinations
5. **Low Quality Results**: Adjust must-have vs nice-to-have requirements

### Debug Tips
- Enable verbose mode for detailed execution logs
- Check agent iteration limits if tasks time out
- Verify filter syntax using FilterBuilderTool test mode
- Monitor API response formats for schema changes

## Architecture Overview

The system implements a sophisticated multi-agent orchestration pattern:

```
┌─────────────────────────────────────────────────────────┐
│                   Main Research Agent                   │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │ General Research│    │    Recruitment Research     │ │
│  │     Agent       │    │         System              │ │
│  └─────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
           ┌────────▼────────┐ ┌───▼────┐ ┌────────▼────────┐
           │ Strategy        │ │ Search │ │ Quality         │
           │ Planner         │ │ Agent  │ │ Analyzer        │
           │                 │ │        │ │                 │
           │ • Plan Creation │ │ • API  │ │ • Candidate     │
           │ • Task Breakdown│ │ • Calls│ │   Ranking       │
           │ • Requirements  │ │ • Multi│ │ • Score         │
           │   Extraction    │ │   Phase│ │   Calculation   │
           └─────────────────┘ └────────┘ └─────────────────┘
                    │               │               │
           ┌────────▼────────┐ ┌───▼────┐ ┌────────▼────────┐
           │ Filter Builder  │ │ People │ │ Candidate       │
           │ Tool            │ │ Search │ │ Ranker Tool     │
           │                 │ │ Tool   │ │                 │
           │ • Complex       │ │ • API  │ │ • Scoring       │
           │   Filters       │ │   Calls│ │ • Rationale     │
           │ • Fuzzy Match   │ │ • Cursor│ │ • Ranking       │
           │ • Nested Logic  │ │   Mgmt │ │ • Analysis      │
           └─────────────────┘ └────────┘ └─────────────────┘
```

## Contributing

Feel free to extend the system with additional capabilities:

### General Enhancements
- Add more REST API integrations
- Implement new research methodologies
- Enhance data analysis features
- Add export functionality for research results

### Recruitment-Specific Enhancements
- Add support for additional recruitment APIs
- Implement advanced candidate scoring algorithms
- Add candidate pipeline management features
- Create automated follow-up and outreach tools
- Add candidate diversity and bias analysis
- Implement real-time market intelligence features

### Technical Improvements
- Add comprehensive test coverage
- Implement async API calls for better performance
- Add result caching and persistence
- Create web interface for easier interaction
- Add monitoring and analytics dashboards

## License

This project is for educational and research purposes.