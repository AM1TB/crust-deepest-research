"""
CrewAI Deep Research Agent with REST API integration and Recruitment functionality.
"""

import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from tools import TodoAPITool, MultiTodoAPITool
from recruitment_agent import RecruitmentResearchAgent
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Load environment variables
load_dotenv()


class DeepResearchAgent:
    """A CrewAI agent specialized in performing deep research with REST API integration."""
    
    def __init__(self):
        # Initialize Claude LLM
        self.llm = ChatAnthropic(
            model="claude-3-7-sonnet-20250219",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0,
            max_tokens=4096
        )
        
        # Initialize custom tools
        self.todo_tool = TodoAPITool()
        self.multi_todo_tool = MultiTodoAPITool()
        
        # Initialize web search tools (optional - requires API keys)
        self.tools = [self.todo_tool, self.multi_todo_tool]
        
        # Add web search tools if API keys are available
        if os.getenv("SERPER_API_KEY"):
            self.tools.append(SerperDevTool())
        
        # Initialize recruitment research agent
        self.recruitment_agent = RecruitmentResearchAgent()
        
        # Create the research agent
        self.researcher = Agent(
            role='Deep Research Specialist',
            goal='Perform comprehensive and thorough research on any given topic, utilizing both web resources and REST API data sources to provide detailed insights and analysis.',
            backstory="""You are an expert researcher with a keen eye for detail and a passion for uncovering comprehensive information. 
            You excel at gathering data from multiple sources, including REST APIs, and synthesizing it into meaningful insights. 
            Your research methodology is thorough, systematic, and always aims to provide the most accurate and up-to-date information available.
            You have access to todo data through REST APIs which you can use to demonstrate data integration capabilities.""",
            verbose=True,
            allow_delegation=False,
            tools=self.tools,
            llm=self.llm,
            max_iter=3,
            max_execution_time=300  # 5 minutes max
        )

    def create_research_task(self, research_topic: str, include_api_demo: bool = True) -> Task:
        """
        Create a research task for the agent.
        
        Args:
            research_topic (str): The topic to research
            include_api_demo (bool): Whether to include API demonstration
            
        Returns:
            Task: Configured research task
        """
        task_description = f"""
        Conduct deep research on the topic: '{research_topic}'
        
        Your research should include:
        1. Comprehensive overview of the topic
        2. Key concepts, definitions, and terminology
        3. Current trends and developments
        4. Practical applications and use cases
        5. Potential challenges or limitations
        6. Future outlook and predictions
        """
        
        if include_api_demo:
            task_description += """
            
        Additionally, demonstrate REST API integration by:
        1. Fetching sample todo data using the Todo API Tool
        2. Analyzing the data structure and content
        3. Explaining how such API integration could be useful for research purposes
        """
        
        expected_output = """
        A comprehensive research report that includes:
        - Executive summary
        - Detailed findings organized by key themes
        - Data analysis (including API data if applicable)
        - Conclusions and recommendations
        - Sources and references used
        
        The report should be well-structured, informative, and demonstrate thorough research methodology.
        """
        
        return Task(
            description=task_description,
            expected_output=expected_output,
            agent=self.researcher
        )

    def conduct_research(self, research_topic: str, include_api_demo: bool = True) -> str:
        """
        Execute the research task.
        
        Args:
            research_topic (str): The topic to research
            include_api_demo (bool): Whether to include API demonstration
            
        Returns:
            str: Research results
        """
        # Create the research task
        research_task = self.create_research_task(research_topic, include_api_demo)
        
        # Create the crew
        crew = Crew(
            agents=[self.researcher],
            tasks=[research_task],
            verbose=2,
            process=Process.sequential,
            manager_llm=self.llm
        )
        
        # Execute the research
        print(f"🔍 Starting deep research on: {research_topic}")
        print("=" * 60)
        
        result = crew.kickoff()
        
        print("=" * 60)
        print("✅ Research completed!")
        
        return result

    def demo_api_functionality(self) -> str:
        """
        Demonstrate the API functionality independently.
        
        Returns:
            str: API demonstration results
        """
        print("🔧 Demonstrating API Tool Functionality")
        print("-" * 40)
        
        # Test single todo fetch
        print("Fetching single todo (ID: 1):")
        single_todo = self.todo_tool._run(1)
        print(single_todo)
        print()
        
        # Test multiple todos fetch
        print("Fetching multiple todos (limit: 5):")
        multiple_todos = self.multi_todo_tool._run(limit=5)
        print(multiple_todos)
        print()
        
        # Test user-specific todos
        print("Fetching todos for user 1 (limit: 3):")
        user_todos = self.multi_todo_tool._run(user_id=1, limit=3)
        print(user_todos)
        
        return "API demonstration completed successfully!"
    
    def conduct_recruitment_research(self, recruitment_brief: str) -> str:
        """
        Execute recruitment research using the specialized recruitment agent.
        
        Args:
            recruitment_brief (str): The recruitment brief describing the position and requirements
            
        Returns:
            str: Formatted recruitment research results
        """
        try:
            print(f"🎯 Starting recruitment research for: {recruitment_brief[:100]}...")
            print("=" * 60)
            
            # Execute recruitment research
            result = self.recruitment_agent.conduct_recruitment_research(recruitment_brief)
            
            if "error" in result:
                return f"❌ Recruitment research failed: {result['error']}"
            
            # Format the results for display
            formatted_result = self._format_recruitment_results(result)
            
            print("=" * 60)
            print("✅ Recruitment research completed!")
            
            return formatted_result
            
        except Exception as e:
            error_msg = f"Error in recruitment research: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def _format_recruitment_results(self, result: dict) -> str:
        """Format recruitment research results for display."""
        try:
            formatted = "🎯 RECRUITMENT RESEARCH RESULTS\n"
            formatted += "=" * 60 + "\n\n"
            
            # Requirements summary
            if "requirements" in result:
                formatted += "📋 REQUIREMENTS SUMMARY:\n"
                formatted += f"Original Brief: {result['requirements'].get('brief', 'N/A')}\n"
                formatted += f"Target Count: {result['requirements'].get('target_count', 100)} candidates\n"
                formatted += f"Credits Cap: {result['requirements'].get('credits_cap', 18)}\n\n"
            
            # Search strategy
            if "plan" in result:
                formatted += "🔍 SEARCH STRATEGY:\n"
                formatted += f"Objective: {result['plan'].get('objective', 'N/A')}\n"
                formatted += f"Strategy: {result['plan'].get('strategy', 'N/A')}\n"
                formatted += f"Exploration Variants: {result['plan'].get('exploration_variants', 3)}\n"
                formatted += f"Per-Call Limit: {result['plan'].get('per_call_limit', 200)}\n\n"
            
            # Results summary
            metadata = result.get("metadata", {})
            formatted += "📊 RESULTS SUMMARY:\n"
            formatted += f"Total Candidates Found: {metadata.get('total_candidates', 0)}\n"
            formatted += f"Estimated Credits Used: {metadata.get('estimated_credits_used', 0)}\n"
            formatted += f"Phases Completed: {metadata.get('phases_completed', 0)}/5\n\n"
            
            # Ranked candidates (if available)
            ranked_candidates = result.get("ranked_candidates", {})
            candidates = ranked_candidates.get("ranked_candidates", [])
            
            if candidates:
                formatted += "🏆 TOP CANDIDATES:\n"
                formatted += "-" * 40 + "\n"
                
                for i, candidate in enumerate(candidates[:5], 1):  # Show top 5
                    formatted += f"{i}. {candidate.get('name', 'N/A')}\n"
                    formatted += f"   Score: {candidate.get('score', 0)}\n"
                    formatted += f"   Title: {candidate.get('headline', 'N/A')}\n"
                    formatted += f"   Region: {candidate.get('region', 'N/A')}\n"
                    
                    rationale = candidate.get('rationale', [])
                    if rationale:
                        formatted += f"   Rationale: {'; '.join(rationale[:2])}\n"
                    
                    formatted += "\n"
            else:
                formatted += "No candidates found or ranking not completed.\n\n"
            
            # Run summary
            if "run_summary" in result:
                formatted += "📝 RUN SUMMARY:\n"
                formatted += "-" * 40 + "\n"
                summary_lines = str(result["run_summary"]).split('\n')
                for line in summary_lines[:10]:  # Show first 10 lines
                    if line.strip():
                        formatted += f"{line.strip()}\n"
                formatted += "\n"
            
            return formatted
            
        except Exception as e:
            return f"Error formatting results: {str(e)}\n\nRaw results:\n{result}"


if __name__ == "__main__":
    # Create the research agent
    agent = DeepResearchAgent()
    
    # Demonstrate API functionality
    agent.demo_api_functionality()
    
    # Conduct sample research
    research_topic = "Artificial Intelligence in Modern Software Development"
    result = agent.conduct_research(research_topic)
    
    print("\n" + "=" * 60)
    print("FINAL RESEARCH RESULT:")
    print("=" * 60)
    print(result)
