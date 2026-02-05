"""
AI Operations Assistant - Main Entry Point
Streamlit UI for multi-agent system with Planner, Executor, and Verifier agents
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
import config

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from llm.groq_client import GroqLLMClient

def initialize_agents():
    """Initialize all three agents with shared LLM client"""
    llm_client = GroqLLMClient()
    
    planner = PlannerAgent(llm_client)
    executor = ExecutorAgent(llm_client)
    verifier = VerifierAgent(llm_client)
    
    return planner, executor, verifier

def main():
    st.set_page_config(
        page_title="AI Operations Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Operations Assistant")
    st.markdown("*Multi-agent system powered by Groq + Llama 3 70B*")
    
    # Initialize agents
    if 'agents_initialized' not in st.session_state:
        with st.spinner("Initializing agents..."):
            planner, executor, verifier = initialize_agents()
            st.session_state.planner = planner
            st.session_state.executor = executor
            st.session_state.verifier = verifier
            st.session_state.agents_initialized = True
    
    # User input
    user_query = st.text_area(
        "Enter your task:",
        placeholder="Example: Get latest tech news and summarize it",
        height=100
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        submit_button = st.button("🚀 Execute", type="primary")
    with col2:
        clear_button = st.button("🗑️ Clear")
    
    if clear_button:
        st.session_state.clear()
        st.rerun()
    
    if submit_button and user_query:
        # Step 1: Planning
        with st.expander("📋 Step 1: Planning", expanded=True):
            with st.spinner("Planner agent is creating execution plan..."):
                plan = st.session_state.planner.create_plan(user_query)
                st.json(plan.model_dump())
        
        # Step 2: Execution
        with st.expander("⚙️ Step 2: Execution", expanded=True):
            with st.spinner("Executor agent is running tasks..."):
                execution_result = st.session_state.executor.execute_plan(plan)
                st.json(execution_result.model_dump())
        
        # Step 3: Verification
        with st.expander("✅ Step 3: Verification", expanded=True):
            with st.spinner("Verifier agent is validating results..."):
                final_result = st.session_state.verifier.verify_and_format(
                    user_query, plan, execution_result
                )
                st.json(final_result.model_dump())
        
        # Final Output
        st.success("✨ Task Completed Successfully!")
        st.markdown("### 📊 Final Result")
        st.markdown(final_result.summary)
        
        if final_result.data:
            st.markdown("### 📈 Detailed Data")
            st.json(final_result.data)

if __name__ == "__main__":
    main()
