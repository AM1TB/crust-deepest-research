"""
CrewAI Deep Research Agent with REST API integration.
"""

import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from tools import TodoAPITool, MultiTodoAPITool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DeepResearchAgent:
    """A CrewAI agent specialized in performing deep research with REST API integration."""
    
    def __init__(self):
        # Initialize custom tools
        self.todo_tool = TodoAPITool()
        self.multi_todo_tool = MultiTodoAPITool()
        
        # Initialize web search tools (optional - requires API keys)
        self.tools = [self.todo_tool, self.multi_todo_tool]
        
        # Add web search tools if API keys are available
        if os.getenv("SERPER_API_KEY"):
            self.tools.append(SerperDevTool())
        
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
            process=Process.sequential
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
