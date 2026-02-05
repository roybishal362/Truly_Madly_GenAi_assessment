"""
Verifier Agent
Validates execution results and ensures completeness
"""
from typing import Dict, Any
from pydantic import BaseModel, Field
from llm.groq_client import GroqLLMClient
from agents.planner import ExecutionPlan
from agents.executor import ExecutionResult

class VerificationResult(BaseModel):
    """Final verified result"""
    original_task: str = Field(description="Original user task")
    is_complete: bool = Field(description="Whether task was completed successfully")
    summary: str = Field(description="Human-readable summary of results")
    data: Dict[str, Any] = Field(description="Structured data from execution")
    issues: list = Field(default_factory=list, description="Any issues or missing data")
    confidence_score: float = Field(description="Confidence in result quality (0-1)")

class VerifierAgent:
    """Agent responsible for verifying and formatting results"""
    
    def __init__(self, llm_client: GroqLLMClient):
        """
        Initialize verifier agent
        
        Args:
            llm_client: Groq LLM client instance
        """
        self.llm = llm_client
    
    def verify_and_format(
        self, 
        original_task: str,
        plan: ExecutionPlan,
        execution_result: ExecutionResult
    ) -> VerificationResult:
        """
        Verify execution results and create final output
        
        Args:
            original_task: Original user query
            plan: Execution plan that was used
            execution_result: Results from executor
            
        Returns:
            Verified and formatted result
        """
        # Check if execution was successful
        is_complete = execution_result.overall_status == "success"
        
        # Collect all data
        collected_data = {}
        issues = []
        
        for step_result in execution_result.step_results:
            if step_result.status == "success":
                collected_data[f"step_{step_result.step_number}"] = step_result.data
            else:
                issues.append(f"Step {step_result.step_number} failed: {step_result.error_message}")
        
        # Calculate confidence score
        success_rate = sum(1 for r in execution_result.step_results if r.status == "success") / len(execution_result.step_results)
        confidence_score = success_rate
        
        # Generate summary using LLM
        summary = self._generate_summary(original_task, collected_data, issues)
        
        return VerificationResult(
            original_task=original_task,
            is_complete=is_complete,
            summary=summary,
            data=collected_data,
            issues=issues,
            confidence_score=confidence_score
        )
    
    def _generate_summary(self, task: str, data: Dict[str, Any], issues: list) -> str:
        """
        Generate human-readable summary using LLM
        
        Args:
            task: Original task
            data: Collected data
            issues: Any issues encountered
            
        Returns:
            Summary text
        """
        system_message = """You are a verification agent that creates clear, concise summaries.
Your job is to:
- Summarize the data collected from APIs
- Highlight key findings
- Mention any issues or limitations
- Keep it readable and informative"""

        prompt = f"""Original task: {task}

Data collected:
{self._format_data_for_prompt(data)}

Issues encountered: {issues if issues else "None"}

Create a clear, informative summary of the results. Include key highlights and insights."""

        summary = self.llm.generate_text(prompt, system_message)
        return summary
    
    def _format_data_for_prompt(self, data: Dict[str, Any]) -> str:
        """Format data dictionary for LLM prompt"""
        formatted = []
        for key, value in data.items():
            if isinstance(value, dict):
                if "repos" in value:
                    repos = value["repos"]
                    formatted.append(f"\nGitHub Repositories ({len(repos)} found):")
                    for repo in repos[:3]:  # Show first 3
                        if "error" not in repo:
                            formatted.append(f"  - {repo.get('name', 'Unknown')}: {repo.get('stars', 0)} stars")
                
                elif "articles" in value:
                    articles = value["articles"]
                    formatted.append(f"\nNews Articles ({len(articles)} found):")
                    for article in articles[:3]:  # Show first 3
                        if "error" not in article:
                            formatted.append(f"  - {article.get('title', 'Unknown')}")
                
                elif "summary" in value:
                    formatted.append(f"\nSummary: {value['summary']}")
        
        return "\n".join(formatted) if formatted else str(data)
