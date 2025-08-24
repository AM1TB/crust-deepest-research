#!/usr/bin/env python3
"""
Main script to run the CrewAI Deep Research Agent.
"""

import os
import sys
from agent import DeepResearchAgent


def check_api_keys():
    """Check if required API keys are set."""
    required_keys = ["ANTHROPIC_API_KEY"]
    optional_keys = ["CRUSTDATA_API_KEY", "SERPER_API_KEY"]
    missing_required = []
    missing_optional = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_required.append(key)
    
    for key in optional_keys:
        if not os.getenv(key):
            missing_optional.append(key)
    
    if missing_required:
        print("❌ Error: Missing required API keys:")
        for key in missing_required:
            print(f"   - {key}")
        print("\nPlease set your API keys in a .env file or as environment variables.")
        print("See env_example.txt for reference.")
        return False
    
    if missing_optional:
        print("⚠️  Warning: Missing optional API keys (some features may be limited):")
        for key in missing_optional:
            print(f"   - {key}")
        print()
    
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
        
        # Interactive mode
        while True:
            print("\nOptions:")
            print("1. Conduct research on a custom topic")
            print("2. Run demo research (AI in Software Development)")
            print("3. Conduct recruitment research")
            print("4. Run demo recruitment research")
            print("5. Test API tools only")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
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
                recruitment_brief = input("\nEnter recruitment brief (describe the position and requirements): ").strip()
                if recruitment_brief:
                    print("\n🎯 Conducting recruitment research...")
                    result = agent.conduct_recruitment_research(recruitment_brief)
                    print("\n" + "=" * 60)
                    print("📋 RECRUITMENT RESULT:")
                    print("=" * 60)
                    print(result)
                else:
                    print("❌ Please enter a valid recruitment brief.")
            
            elif choice == "4":
                recruitment_brief = """
                We're looking for a Senior Software Engineer with Python experience 
                for our growing tech startup in San Francisco. The ideal candidate should have 
                5-8 years of experience, strong background in web development, and experience 
                with cloud platforms like AWS or GCP. We're a 50-100 person company in the 
                fintech space.
                """
                print("\n🎯 Running demo recruitment research...")
                print(f"Brief: {recruitment_brief.strip()}")
                result = agent.conduct_recruitment_research(recruitment_brief)
                print("\n" + "=" * 60)
                print("📋 RECRUITMENT RESULT:")
                print("=" * 60)
                print(result)
            
            elif choice == "5":
                print("\n🔧 Testing API Tools...")
                agent.demo_api_functionality()
            
            elif choice == "6":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-6.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Research session interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please check your API keys and internet connection.")


if __name__ == "__main__":
    main()
