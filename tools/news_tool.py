"""
News API Tool
Fetches latest tech news articles
"""
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta

class NewsTool:
    """Tool for interacting with NewsAPI"""
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: str):
        """
        Initialize News tool
        
        Args:
            api_key: NewsAPI key
        """
        if not api_key:
            raise ValueError("NewsAPI key is required")
        self.api_key = api_key
    
    def get_tech_news(
        self, 
        query: str = "technology",
        limit: int = 5,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Get latest tech news articles
        
        Args:
            query: Search query or topic
            limit: Number of articles to return
            language: Language code (en, es, fr, etc.)
            
        Returns:
            List of news articles
        """
        try:
            url = f"{self.BASE_URL}/everything"
            
            # Get news from last 7 days
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            params = {
                "q": query,
                "apiKey": self.api_key,
                "language": language,
                "sortBy": "publishedAt",
                "from": from_date,
                "pageSize": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                return [{"error": f"NewsAPI error: {data.get('message', 'Unknown error')}"}]
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "title": article.get("title", "No title"),
                    "description": article.get("description", "No description"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author", "Unknown"),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "content": article.get("content", "")[:200]  # Truncate content
                })
            
            return articles
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"NewsAPI request failed: {str(e)}"}]
    
    def get_top_headlines(
        self,
        category: str = "technology",
        country: str = "us",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top headlines by category
        
        Args:
            category: News category (technology, business, science, etc.)
            country: Country code (us, gb, in, etc.)
            limit: Number of headlines
            
        Returns:
            List of top headlines
        """
        try:
            url = f"{self.BASE_URL}/top-headlines"
            params = {
                "apiKey": self.api_key,
                "category": category,
                "country": country,
                "pageSize": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                return [{"error": f"NewsAPI error: {data.get('message', 'Unknown error')}"}]
            
            headlines = []
            for article in data.get("articles", []):
                headlines.append({
                    "title": article.get("title", "No title"),
                    "description": article.get("description", "No description"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", "")
                })
            
            return headlines
        
        except requests.exceptions.RequestException as e:
            return [{"error": f"NewsAPI request failed: {str(e)}"}]
