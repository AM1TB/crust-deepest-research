#!/usr/bin/env python3
"""
Main script to run the CrewAI Deep Research Agent.
"""

import os
import sys
from agent import DeepResearchAgent


def check_api_keys():
    """Check if required API keys are set."""
    required_keys = ["OPENAI_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print("⚠️  Warning: Missing required API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease set your API keys in a .env file or as environment variables.")
        print("See env_example.txt for reference.")
        return False
    
    return True


def main():
    """Main function to run the research agent."""
    print("🤖 CrewAI Deep Research Agent")
    print("=" * 50)
    
    # Check API keys
    if not check_api_keys():
        print("\n❌ Cannot proceed without required API keys.")
        sys.exit(1)
    
    try:
        # Create the research agent
        agent = DeepResearchAgent()
        
        print("\n🔧 Testing API Tool Functionality...")
        print("-" * 40)
        
        # Demonstrate API functionality first
        agent.demo_api_functionality()
        
        print("\n" + "=" * 50)
        print("🔍 Starting Deep Research Session")
        print("=" * 50)
        
        # Interactive mode
        while True:
            print("\nOptions:")
            print("1. Conduct research on a custom topic")
            print("2. Run demo research (AI in Software Development)")
            print("3. Test API tools only")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                topic = input("\nEnter research topic: ").strip()
                if topic:
                    print(f"\n🔍 Researching: {topic}")
                    result = agent.conduct_research(topic)
                    print("\n" + "=" * 60)
                    print("📋 RESEARCH RESULT:")
                    print("=" * 60)
                    print(result)
                else:
                    print("❌ Please enter a valid topic.")
            
            elif choice == "2":
                topic = "Artificial Intelligence in Modern Software Development"
                print(f"\n🔍 Running demo research: {topic}")
                result = agent.conduct_research(topic)
                print("\n" + "=" * 60)
                print("📋 RESEARCH RESULT:")
                print("=" * 60)
                print(result)
            
            elif choice == "3":
                print("\n🔧 Testing API Tools...")
                agent.demo_api_functionality()
            
            elif choice == "4":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-4.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Research session interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your API keys and internet connection.")


if __name__ == "__main__":
    main()
