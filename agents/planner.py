"""
Planner Agent
Converts user input into structured execution plan with tool selection
"""
from typing import List
from pydantic import BaseModel, Field
from llm.groq_client import GroqLLMClient

class PlanStep(BaseModel):
    """Single step in execution plan"""
    step_number: int = Field(description="Step sequence number")
    action: str = Field(description="Action to perform")
    tool: str = Field(description="Tool to use (GitHubTool, NewsTool, or LLM)")
    parameters: dict = Field(default_factory=dict, description="Parameters for the tool")
    reasoning: str = Field(description="Why this step is needed")

class ExecutionPlan(BaseModel):
    """Complete execution plan"""
    task_description: str = Field(description="Original user task")
    steps: List[PlanStep] = Field(description="List of execution steps")
    expected_outcome: str = Field(description="What the final result should contain")

class PlannerAgent:
    """Agent responsible for creating execution plans"""
    
    def __init__(self, llm_client: GroqLLMClient):
        """
        Initialize planner agent
        
        Args:
            llm_client: Groq LLM client instance
        """
        self.llm = llm_client
    
    def create_plan(self, user_query: str) -> ExecutionPlan:
        """
        Create execution plan from user query
        
        Args:
            user_query: Natural language task description
            
        Returns:
            Structured execution plan
        """
        system_message = """You are a planning agent that breaks down user tasks into executable steps.

Available tools:
1. GitHubTool - Search repositories, get trending repos, fetch repo details
   Methods: search_repositories(query, sort, limit), get_trending_repos(language, limit)
   Example parameters: {{"query": "python machine learning", "limit": 5}}
   
2. NewsTool - Fetch tech news and headlines
   Methods: get_tech_news(query, limit), get_top_headlines(category, country, limit)
   Example parameters: {{"query": "artificial intelligence", "limit": 5}}
   IMPORTANT: Always provide a non-empty query string for news searches
   
3. LLM - Summarize, analyze, or format data
   Example parameters: {{"prompt": "Summarize these articles"}}

Your job is to:
- Analyze the user's request
- Break it into logical steps
- Select appropriate tools for each step
- Specify parameters for each tool call (ensure query strings are not empty)
- Plan a final summarization step if needed

Create a clear, executable plan with specific, non-empty parameters."""

        prompt = f"""User task: {user_query}

Create a detailed execution plan with steps that will accomplish this task.
Each step should specify which tool to use and what parameters to pass.
Include a final step to summarize or format the results if needed."""

        plan = self.llm.generate_structured_output(
            prompt=prompt,
            output_model=ExecutionPlan,
            system_message=system_message
        )
        
        return plan
