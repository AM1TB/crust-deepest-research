# CrewAI Deep Research Agent

A powerful research agent built with CrewAI that performs comprehensive research and integrates REST API data sources. The agent can fetch and analyze data from external APIs while conducting deep research on any topic.

## Features

- 🤖 **Deep Research Agent**: Specialized in comprehensive research with systematic methodology
- 🔌 **REST API Integration**: Custom tools for fetching data from JSONPlaceholder API
- 🌐 **Web Search Capabilities**: Optional integration with search engines (requires API keys)
- 📊 **Data Analysis**: Analyzes and synthesizes information from multiple sources
- 🎯 **Flexible Research Topics**: Can research any topic provided by the user

## Project Structure

```
crust-deepest-research/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── main.py            # Main script to run the agent
├── agent.py           # CrewAI agent implementation
├── tools.py           # Custom REST API tools
└── env_example.txt    # Environment variables example
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**:
   - Copy `env_example.txt` to `.env`
   - Add your LLM API key (required)
   - Add optional API keys for enhanced functionality

3. **Run the Agent**:
   ```bash
   python main.py
   ```

## API Integration

The agent includes two custom REST API tools:

### TodoAPITool
- Fetches individual todo items from JSONPlaceholder API
- Demonstrates basic API integration
- Sample endpoint: `https://jsonplaceholder.typicode.com/todos/1`

### MultiTodoAPITool
- Fetches multiple todo items or user-specific todos
- Supports filtering and limiting results
- Useful for bulk data analysis

### Sample API Response
```json
{
  "userId": 1,
  "id": 1,
  "title": "delectus aut autem",
  "completed": false
}
```

## Usage Examples

### Interactive Mode
Run `python main.py` and choose from the menu:
1. Research custom topics
2. Run demo research
3. Test API tools
4. Exit

### Programmatic Usage
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

## Research Capabilities

The agent can research topics such as:
- Technology trends and developments
- Scientific concepts and theories
- Business strategies and markets
- Historical events and analysis
- Current events and news

## API Keys Required

### Required
- **OPENAI_API_KEY**: For CrewAI agent functionality

### Optional (for enhanced capabilities)
- **SERPER_API_KEY**: For web search functionality
- **GOOGLE_API_KEY**: For Google search integration
- **GOOGLE_CSE_ID**: For custom search engine

## Agent Configuration

The research agent is configured with:
- **Role**: Deep Research Specialist
- **Goal**: Comprehensive research with REST API integration
- **Tools**: Custom API tools + optional web search tools
- **Max Iterations**: 3
- **Max Execution Time**: 5 minutes

## Example Research Output

The agent provides structured research reports including:
- Executive summary
- Detailed findings by theme
- Data analysis (including API data)
- Conclusions and recommendations
- Sources and references

## Troubleshooting

1. **Missing API Keys**: Ensure OPENAI_API_KEY is set in your environment
2. **Network Issues**: Check internet connection for API calls
3. **Tool Errors**: Verify API endpoints are accessible
4. **Timeout Issues**: Large research tasks may take time to complete

## Contributing

Feel free to extend the agent with additional tools and capabilities:
- Add more REST API integrations
- Implement new research methodologies
- Enhance data analysis features
- Add export functionality for research results

## License

This project is for educational and research purposes.