"""
GitHub API Tool
Fetches trending repositories and project information
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class GitHubTool:
    """Tool for interacting with GitHub API"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub tool
        
        Args:
            token: Optional GitHub personal access token for higher rate limits
        """
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def search_repositories(
        self, 
        query: str = "language:python", 
        sort: str = "stars",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search GitHub repositories
        
        Args:
            query: Search query (default: Python repos)
            sort: Sort by (stars, forks, updated)
            limit: Number of results to return
            
        Returns:
            List of repository information
        """
        try:
            url = f"{self.BASE_URL}/search/repositories"
            params = {
                "q": query,
                "sort": sort,
                "order": "desc",
                "per_page": limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            repos = []
            
            for item in data.get("items", []):
                repos.append({
                    "name": item["name"],
                    "full_name": item["full_name"],
                    "description": item.get("description", "No description"),
                    "stars": item["stargazers_count"],
                    "forks": item["forks_count"],
                    "language": item.get("language", "Unknown"),
                    "url": item["html_url"],
                    "topics": item.get("topics", [])
                })
            
            return repos
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"GitHub API error: {str(e)}"}]
    
    def get_trending_repos(self, language: str = "python", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get trending repositories (repos created in last 7 days with most stars)
        
        Args:
            language: Programming language filter
            limit: Number of results
            
        Returns:
            List of trending repositories
        """
        # Calculate date 7 days ago
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        query = f"language:{language} created:>{week_ago}"
        
        return self.search_repositories(query=query, sort="stars", limit=limit)
    
    def get_repo_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository details
        """
        try:
            url = f"{self.BASE_URL}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                "name": data["name"],
                "description": data.get("description", "No description"),
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "open_issues": data["open_issues_count"],
                "language": data.get("language", "Unknown"),
                "created_at": data["created_at"],
                "updated_at": data["updated_at"]
            }
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch repo details: {str(e)}"}
