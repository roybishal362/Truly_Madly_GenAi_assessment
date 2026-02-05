# 🤖 AI Operations Assistant

A multi-agent AI system that accepts natural language tasks, creates execution plans, calls real APIs, and returns verified results. Built with LangChain, Groq (Llama 3.3 70B), and Streamlit.

## 📋 Architecture

### Multi-Agent System

The system uses three specialized agents that work together:

1. **Planner Agent**
   - Takes natural language input from user
   - Analyzes the task and breaks it into executable steps
   - Selects appropriate tools (GitHub API, News API, or LLM)
   - Generates structured execution plan with Pydantic models
   - Uses LLM to reason about task decomposition

2. **Executor Agent**
   - Receives execution plan from Planner
   - Iterates through each step sequentially
   - Calls appropriate APIs based on plan
   - Handles errors and retries
   - Collects results from all steps

3. **Verifier Agent**
   - Validates execution results for completeness
   - Checks if all required data was collected
   - Identifies missing or incorrect outputs
   - Generates human-readable summary using LLM
   - Calculates confidence score for results

### Tools Integration

**GitHub Tool** (`tools/github_tool.py`)
- Search repositories by query, language, stars
- Get trending repositories
- Fetch repository details
- No authentication required (optional token for higher limits)

**News Tool** (`tools/news_tool.py`)
- Fetch latest tech news articles
- Get top headlines by category
- Search news by keywords
- Requires NewsAPI key

**LLM Tool** (via Groq)
- Summarization and analysis
- Structured output generation
- Natural language understanding

## 🔧 Setup Instructions

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone or download this repository**

2. **Install dependencies**
```bash
cd ai_ops_assistant
pip install -r requirements.txt
```

3. **Configure environment variables**

Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

Edit `.env` and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
NEWS_API_KEY=your_news_api_key_here
GITHUB_TOKEN=your_github_token_here  # Optional
```

**Where to get API keys:**
- **Groq API**: https://console.groq.com/keys (Free tier available)
- **News API**: https://newsapi.org/register (Free: 100 requests/day)
- **GitHub Token**: https://github.com/settings/tokens (Optional, increases rate limit)

4. **Run the application**
```bash
python -m streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

## 🌐 Integrated APIs

### 1. GitHub API
- **Base URL**: `https://api.github.com`
- **Authentication**: Optional (token increases rate limit)
- **Rate Limits**: 60 requests/hour (no auth), 5000/hour (with token)
- **Used For**: Repository search, trending projects, tech insights

### 2. NewsAPI
- **Base URL**: `https://newsapi.org/v2`
- **Authentication**: Required (API key)
- **Rate Limits**: 100 requests/day (free tier)
- **Used For**: Latest tech news, headlines, article search

## 💡 Example Prompts

Try these prompts in the Streamlit UI:

1. **"Get latest tech news and summarize it"**
   - Fetches recent technology news articles
   - Summarizes key headlines and topics
   - Provides source links

2. **"Find trending Python repositories on GitHub"**
   - Searches for popular Python projects
   - Returns repo names, stars, descriptions
   - Shows recent trending projects

3. **"Get top tech headlines and find related GitHub projects"**
   - Fetches latest tech news headlines
   - Searches GitHub for related repositories
   - Combines insights from both sources

4. **"What are the latest AI and machine learning news?"**
   - Searches news for AI/ML topics
   - Summarizes recent developments
   - Provides article sources

5. **"Find popular JavaScript frameworks and get recent news about web development"**
   - Searches GitHub for JS frameworks
   - Fetches web development news
   - Creates comprehensive summary

## 🏗️ Project Structure

```
ai_ops_assistant/
├── agents/
│   ├── __init__.py
│   ├── planner.py       # Planner Agent - creates execution plans
│   ├── executor.py      # Executor Agent - runs API calls
│   └── verifier.py      # Verifier Agent - validates results
├── tools/
│   ├── __init__.py
│   ├── github_tool.py   # GitHub API integration
│   └── news_tool.py     # NewsAPI integration
├── llm/
│   ├── __init__.py
│   └── groq_client.py   # Groq LLM client with LangChain
├── main.py              # Streamlit UI entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## ⚙️ How It Works

### Execution Flow

```
User Input (Natural Language)
        ↓
[Planner Agent]
- Analyzes task
- Creates step-by-step plan
- Selects tools (GitHub/News/LLM)
        ↓
[Executor Agent]
- Executes each step
- Calls GitHub API
- Calls News API
- Collects results
        ↓
[Verifier Agent]
- Validates completeness
- Checks for errors
- Generates summary
        ↓
Final Result (Structured + Summary)
```

### Example Execution

**Input**: "Get latest tech news and summarize it"

**Planner Output**:
```json
{
  "steps": [
    {
      "step_number": 1,
      "action": "fetch_tech_news",
      "tool": "NewsTool",
      "parameters": {"query": "technology", "limit": 5}
    },
    {
      "step_number": 2,
      "action": "summarize_news",
      "tool": "LLM",
      "parameters": {"prompt": "Summarize these tech articles"}
    }
  ]
}
```

**Executor Output**: Calls NewsAPI → Gets 5 articles → Passes to LLM

**Verifier Output**: Validates data → Generates summary → Returns final result

## 🚨 Known Limitations

### API Rate Limits
- **NewsAPI Free Tier**: 100 requests/day
- **GitHub (no auth)**: 60 requests/hour
- **Groq Free Tier**: Rate limits apply
- **Solution**: Use GitHub token, upgrade API plans if needed

### Data Freshness
- News articles limited to last 7 days (NewsAPI restriction)
- GitHub trending calculated from recent repos
- Real-time data not available

### Error Handling
- Partial failures are handled gracefully
- If one API fails, other steps may still succeed
- Verifier reports issues in final output

### LLM Limitations
- Llama 3 70B may occasionally produce verbose summaries
- Structured output parsing can fail with complex schemas
- Retry logic not implemented for LLM failures

### Scalability
- Sequential execution (no parallel API calls)
- No caching mechanism
- Single-user design (no database)

## 🔄 Tradeoffs

### Design Decisions

**Sequential vs Parallel Execution**
- **Current**: Steps execute sequentially
- **Tradeoff**: Slower but simpler, easier to debug
- **Future**: Parallel execution for independent steps

**No Caching**
- **Current**: Every request hits APIs
- **Tradeoff**: Always fresh data but uses rate limits
- **Future**: Redis/memory cache for repeated queries

**Streamlit UI**
- **Current**: Simple web interface
- **Tradeoff**: Easy to use but limited customization
- **Alternative**: FastAPI + React for production

**Pydantic Models**
- **Current**: Strict schema validation
- **Tradeoff**: Type safety but less flexible
- **Benefit**: Catches errors early, clear contracts

## 🧪 Testing

### Manual Testing
1. Start the app: `python -m streamlit run main.py`
2. Try example prompts listed above
3. Check that all three agents execute
4. Verify API data appears in results

### Debugging
- Check `.streamlit/` folder for logs
- Verify API keys in `.env` file
- Test APIs individually in Python shell
- Check rate limits if requests fail

## 📚 Dependencies

- **streamlit**: Web UI framework
- **langchain**: LLM orchestration framework
- **langchain-groq**: Groq provider for LangChain
- **pydantic**: Data validation and schemas
- **requests**: HTTP client for API calls
- **python-dotenv**: Environment variable management

## 🎓 Learning Resources

- **LangChain Docs**: https://python.langchain.com/docs/get_started/introduction
- **Groq API**: https://console.groq.com/docs/quickstart
- **NewsAPI Docs**: https://newsapi.org/docs
- **GitHub API**: https://docs.github.com/en/rest
- **Pydantic**: https://docs.pydantic.dev/

## 📝 Notes

- This project demonstrates multi-agent architecture for a GenAI internship assignment
- Built with production-ready patterns (error handling, validation, modularity)
- Code is documented with clear comments for readability
- Follows Python best practices and PEP 8 style guide

## 🚀 Future Improvements

With more time, these features could be added:
- Caching API responses (Redis/SQLite)
- Parallel tool execution for faster results
- Cost tracking per request
- User authentication and history
- More API integrations (Twitter, Reddit, etc.)
- Async execution with FastAPI
- Unit tests and integration tests
- Docker containerization
- CI/CD pipeline

---

**Built with ❤️ for TrulyMadly GenAI Internship Assignment**
