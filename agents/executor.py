"""
Executor Agent
Executes the plan by calling appropriate tools and APIs
"""
import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from llm.groq_client import GroqLLMClient
from tools.github_tool import GitHubTool
from tools.news_tool import NewsTool
from agents.planner import ExecutionPlan

class StepResult(BaseModel):
    """Result of a single execution step"""
    step_number: int = Field(description="Step sequence number")
    action: str = Field(description="Action performed")
    tool_used: str = Field(description="Tool that was used")
    status: str = Field(description="success or error")
    data: Any = Field(description="Data returned from tool")
    error_message: str = Field(default="", description="Error message if failed")

class ExecutionResult(BaseModel):
    """Complete execution result"""
    plan_description: str = Field(description="Original plan description")
    step_results: List[StepResult] = Field(description="Results from each step")
    overall_status: str = Field(description="success or partial_failure or failure")

class ExecutorAgent:
    """Agent responsible for executing plans"""
    
    def __init__(self, llm_client: GroqLLMClient):
        """
        Initialize executor agent
        
        Args:
            llm_client: Groq LLM client instance
        """
        self.llm = llm_client
        
        # Initialize tools
        github_token = os.getenv("GITHUB_TOKEN")  # Optional
        self.github_tool = GitHubTool(token=github_token)
        
        news_api_key = os.getenv("NEWS_API_KEY")
        if not news_api_key:
            raise ValueError("NEWS_API_KEY not found in environment")
        self.news_tool = NewsTool(api_key=news_api_key)
    
    def execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        """
        Execute the complete plan
        
        Args:
            plan: Execution plan from planner agent
            
        Returns:
            Execution results
        """
        step_results = []
        
        for step in plan.steps:
            result = self._execute_step(step)
            step_results.append(result)
        
        # Determine overall status
        success_count = sum(1 for r in step_results if r.status == "success")
        if success_count == len(step_results):
            overall_status = "success"
        elif success_count > 0:
            overall_status = "partial_failure"
        else:
            overall_status = "failure"
        
        return ExecutionResult(
            plan_description=plan.task_description,
            step_results=step_results,
            overall_status=overall_status
        )
    
    def _execute_step(self, step) -> StepResult:
        """
        Execute a single step
        
        Args:
            step: PlanStep to execute
            
        Returns:
            Step execution result
        """
        try:
            tool_name = step.tool.lower()
            
            if "github" in tool_name:
                data = self._call_github_tool(step)
            elif "news" in tool_name:
                data = self._call_news_tool(step)
            elif "llm" in tool_name:
                data = self._call_llm(step)
            else:
                return StepResult(
                    step_number=step.step_number,
                    action=step.action,
                    tool_used=step.tool,
                    status="error",
                    data={},
                    error_message=f"Unknown tool: {step.tool}"
                )
            
            return StepResult(
                step_number=step.step_number,
                action=step.action,
                tool_used=step.tool,
                status="success",
                data=data
            )
        
        except Exception as e:
            return StepResult(
                step_number=step.step_number,
                action=step.action,
                tool_used=step.tool,
                status="error",
                data={},
                error_message=str(e)
            )
    
    def _call_github_tool(self, step) -> Dict[str, Any]:
        """Call GitHub tool based on step parameters"""
        params = step.parameters
        action = step.action.lower()
        
        if "trending" in action:
            language = params.get("language", "python")
            limit = params.get("limit", 5)
            return {"repos": self.github_tool.get_trending_repos(language, limit)}
        
        elif "search" in action:
            query = params.get("query", "language:python")
            sort = params.get("sort", "stars")
            limit = params.get("limit", 5)
            return {"repos": self.github_tool.search_repositories(query, sort, limit)}
        
        else:
            # Default to search
            return {"repos": self.github_tool.search_repositories(limit=5)}
    
    def _call_news_tool(self, step) -> Dict[str, Any]:
        """Call News tool based on step parameters"""
        params = step.parameters
        action = step.action.lower()
        
        if "headline" in action:
            category = params.get("category", "technology")
            country = params.get("country", "us")
            limit = params.get("limit", 5)
            return {"articles": self.news_tool.get_top_headlines(category, country, limit)}
        
        else:
            # Default to tech news - ensure query is not empty
            query = params.get("query", "technology")
            if not query or query.strip() == "":
                query = "technology"  # Fallback to technology if empty
            limit = params.get("limit", 5)
            return {"articles": self.news_tool.get_tech_news(query, limit)}
    
    def _call_llm(self, step) -> Dict[str, Any]:
        """Use LLM for summarization or analysis"""
        params = step.parameters
        prompt = params.get("prompt", "Summarize the data")
        
        response = self.llm.generate_text(prompt)
        return {"summary": response}
