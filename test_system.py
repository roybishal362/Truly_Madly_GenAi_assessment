"""
Simple test script to verify system components
Run this before submitting to ensure everything works
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("Testing environment variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["GROQ_API_KEY", "NEWS_API_KEY"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Please check your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_imports():
    """Test if all modules can be imported"""
    print("\nTesting imports...")
    
    try:
        from llm.groq_client import GroqLLMClient
        from tools.github_tool import GitHubTool
        from tools.news_tool import NewsTool
        from agents.planner import PlannerAgent
        from agents.executor import ExecutorAgent
        from agents.verifier import VerifierAgent
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_github_api():
    """Test GitHub API connection"""
    print("\nTesting GitHub API...")
    
    try:
        from tools.github_tool import GitHubTool
        
        github = GitHubTool()
        repos = github.search_repositories(query="python", limit=2)
        
        if repos and len(repos) > 0 and "error" not in repos[0]:
            print(f"✅ GitHub API working - Found {len(repos)} repositories")
            return True
        else:
            print("❌ GitHub API returned no results or error")
            return False
    except Exception as e:
        print(f"❌ GitHub API error: {e}")
        return False

def test_news_api():
    """Test News API connection"""
    print("\nTesting News API...")
    
    try:
        from tools.news_tool import NewsTool
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("NEWS_API_KEY")
        news = NewsTool(api_key)
        articles = news.get_tech_news(limit=2)
        
        if articles and len(articles) > 0 and "error" not in articles[0]:
            print(f"✅ News API working - Found {len(articles)} articles")
            return True
        else:
            print("❌ News API returned no results or error")
            print(f"   Response: {articles}")
            return False
    except Exception as e:
        print(f"❌ News API error: {e}")
        return False

def test_groq_llm():
    """Test Groq LLM connection"""
    print("\nTesting Groq LLM...")
    
    try:
        from llm.groq_client import GroqLLMClient
        from dotenv import load_dotenv
        load_dotenv()
        
        llm = GroqLLMClient()
        response = llm.generate_text("Say 'Hello' in one word")
        
        if response and len(response) > 0:
            print(f"✅ Groq LLM working - Response: {response[:50]}")
            return True
        else:
            print("❌ Groq LLM returned empty response")
            return False
    except Exception as e:
        print(f"❌ Groq LLM error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("AI Operations Assistant - System Test")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("Module Imports", test_imports()))
    results.append(("GitHub API", test_github_api()))
    results.append(("News API", test_news_api()))
    results.append(("Groq LLM", test_groq_llm()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("Run: python -m streamlit run main.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
