"""
Example Usage Script
Demonstrates how to use the AI Operations Assistant programmatically
This shows the agent flow without the Streamlit UI
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our agents
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from llm.groq_client import GroqLLMClient

def main():
    """
    Example of using the multi-agent system programmatically
    This demonstrates the complete flow from user input to final result
    """
    
    # Step 1: Initialize the LLM client
    # We use Groq with Llama 3 70B for all agent reasoning
    print("Initializing LLM client...")
    llm_client = GroqLLMClient()
    
    # Step 2: Create our three agents
    # Each agent has a specific responsibility in the pipeline
    print("Creating agents...")
    planner = PlannerAgent(llm_client)
    executor = ExecutorAgent(llm_client)
    verifier = VerifierAgent(llm_client)
    
    # Step 3: Define the user's task
    # This is what the user wants to accomplish
    user_task = "Get latest tech news and summarize it"
    print(f"\nUser Task: {user_task}")
    print("=" * 60)
    
    # Step 4: Planner Agent creates execution plan
    # The planner analyzes the task and breaks it into steps
    # It decides which tools to use (GitHub, News, or LLM)
    print("\n[PLANNER AGENT] Creating execution plan...")
    plan = planner.create_plan(user_task)
    
    print(f"\nPlan created with {len(plan.steps)} steps:")
    for step in plan.steps:
        print(f"  Step {step.step_number}: {step.action}")
        print(f"    Tool: {step.tool}")
        print(f"    Reasoning: {step.reasoning}")
    
    # Step 5: Executor Agent runs the plan
    # The executor calls the actual APIs and collects data
    # It handles errors gracefully and continues even if one step fails
    print("\n[EXECUTOR AGENT] Executing plan...")
    execution_result = executor.execute_plan(plan)
    
    print(f"\nExecution Status: {execution_result.overall_status}")
    for step_result in execution_result.step_results:
        status_icon = "✅" if step_result.status == "success" else "❌"
        print(f"  {status_icon} Step {step_result.step_number}: {step_result.status}")
        if step_result.error_message:
            print(f"    Error: {step_result.error_message}")
    
    # Step 6: Verifier Agent validates results
    # The verifier checks if we got all the data we need
    # It generates a human-readable summary using the LLM
    print("\n[VERIFIER AGENT] Validating results...")
    final_result = verifier.verify_and_format(
        original_task=user_task,
        plan=plan,
        execution_result=execution_result
    )
    
    # Step 7: Display final results
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(f"\nTask Complete: {final_result.is_complete}")
    print(f"Confidence Score: {final_result.confidence_score:.2f}")
    
    if final_result.issues:
        print(f"\nIssues Encountered:")
        for issue in final_result.issues:
            print(f"  - {issue}")
    
    print(f"\nSummary:")
    print(final_result.summary)
    
    # Optional: Show raw data
    print(f"\n[DEBUG] Raw data collected:")
    for key, value in final_result.data.items():
        print(f"  {key}: {type(value)}")

if __name__ == "__main__":
    # Check if environment variables are set
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not found in environment")
        print("Please create a .env file with your API keys")
        exit(1)
    
    if not os.getenv("NEWS_API_KEY"):
        print("Error: NEWS_API_KEY not found in environment")
        print("Please create a .env file with your API keys")
        exit(1)
    
    # Run the example
    try:
        main()
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("Please check your API keys and internet connection")
