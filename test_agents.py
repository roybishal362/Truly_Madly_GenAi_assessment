"""
Quick test for agents to verify they work
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent))

load_dotenv()

from agents.planner import PlannerAgent
from llm.groq_client import GroqLLMClient

def test_planner():
    """Test planner agent"""
    print("Testing Planner Agent...")
    
    try:
        llm_client = GroqLLMClient()
        planner = PlannerAgent(llm_client)
        
        user_query = "Get latest tech news and summarize it"
        print(f"Query: {user_query}")
        
        plan = planner.create_plan(user_query)
        print(f"✅ Plan created with {len(plan.steps)} steps")
        
        for step in plan.steps:
            print(f"  Step {step.step_number}: {step.action} using {step.tool}")
            print(f"    Parameters: {step.parameters}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_planner()
    if success:
        print("\n✅ Planner test passed!")
    else:
        print("\n❌ Planner test failed!")
