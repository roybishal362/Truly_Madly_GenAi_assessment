# 🏗️ Architecture Deep Dive

## System Design Philosophy

This AI Operations Assistant follows a **multi-agent architecture** where specialized agents collaborate to accomplish complex tasks. Each agent has a single responsibility, making the system modular, testable, and maintainable.

## Agent Communication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                          │
│              "Get latest tech news and summarize it"        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PLANNER AGENT                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Analyze user intent                               │  │
│  │ 2. Break down into steps                             │  │
│  │ 3. Select tools (GitHub/News/LLM)                    │  │
│  │ 4. Generate structured plan (Pydantic)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Output: ExecutionPlan (JSON)                               │
│  {                                                          │
│    "steps": [                                               │
│      {"tool": "NewsTool", "action": "fetch_tech_news"},    │
│      {"tool": "LLM", "action": "summarize"}                │
│    ]                                                        │
│  }                                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXECUTOR AGENT                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Receive execution plan                            │  │
│  │ 2. Initialize tools (GitHub, News)                   │  │
│  │ 3. Execute steps sequentially                        │  │
│  │ 4. Call APIs with error handling                     │  │
│  │ 5. Collect results from each step                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Step 1: NewsTool.get_tech_news()                          │
│    → Calls NewsAPI                                          │
│    → Returns 5 articles                                     │
│                                                             │
│  Step 2: LLM.summarize()                                   │
│    → Sends articles to Groq                                 │
│    → Returns summary                                        │
│                                                             │
│  Output: ExecutionResult (JSON)                             │
│  {                                                          │
│    "step_results": [...],                                   │
│    "overall_status": "success"                              │
│  }                                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    VERIFIER AGENT                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Validate execution results                        │  │
│  │ 2. Check data completeness                           │  │
│  │ 3. Identify missing/incorrect outputs                │  │
│  │ 4. Calculate confidence score                        │  │
│  │ 5. Generate human-readable summary (LLM)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Validation:                                                │
│    ✓ All steps completed successfully                      │
│    ✓ Data collected from APIs                              │
│    ✓ No errors encountered                                 │
│                                                             │
│  Output: VerificationResult (JSON)                          │
│  {                                                          │
│    "is_complete": true,                                     │
│    "summary": "Found 5 tech articles...",                   │
│    "confidence_score": 1.0                                  │
│  }                                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Final Output                           │
│  • Structured data (JSON)                                   │
│  • Human-readable summary                                   │
│  • Confidence score                                         │
│  • Source links                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Planner Agent (`agents/planner.py`)

**Responsibility**: Task decomposition and tool selection

**Key Features**:
- Uses LLM to understand user intent
- Generates structured plans with Pydantic models
- Selects appropriate tools based on task requirements
- Provides reasoning for each step

**LLM Usage**:
```python
# Prompt engineering for structured output
system_message = "You are a planning agent..."
plan = llm.generate_structured_output(
    prompt=user_query,
    output_model=ExecutionPlan,  # Pydantic model
    system_message=system_message
)
```

**Output Schema**:
```python
class ExecutionPlan(BaseModel):
    task_description: str
    steps: List[PlanStep]
    expected_outcome: str
```

### 2. Executor Agent (`agents/executor.py`)

**Responsibility**: Execute plan and call APIs

**Key Features**:
- Initializes all tools (GitHub, News)
- Executes steps sequentially
- Handles API errors gracefully
- Collects results from each step

**Tool Routing**:
```python
if "github" in tool_name:
    data = self._call_github_tool(step)
elif "news" in tool_name:
    data = self._call_news_tool(step)
elif "llm" in tool_name:
    data = self._call_llm(step)
```

**Error Handling**:
- Try-catch around each step
- Returns error status if API fails
- Continues execution even if one step fails

### 3. Verifier Agent (`agents/verifier.py`)

**Responsibility**: Validate results and ensure quality

**Key Features**:
- Checks if all steps completed successfully
- Validates data completeness
- Calculates confidence score
- Generates human-readable summary using LLM

**Validation Logic**:
```python
success_rate = successful_steps / total_steps
confidence_score = success_rate

if execution_result.overall_status == "success":
    is_complete = True
```

**Summary Generation**:
- Uses LLM to create natural language summary
- Highlights key findings
- Mentions any issues or limitations

## Tool Integration

### GitHub Tool (`tools/github_tool.py`)

**API Endpoints Used**:
- `/search/repositories` - Search repos by query
- `/repos/{owner}/{repo}` - Get repo details

**Features**:
- No authentication required (optional token)
- Rate limiting handled
- Error handling with fallbacks

**Example Usage**:
```python
github = GitHubTool()
repos = github.search_repositories(
    query="language:python",
    sort="stars",
    limit=5
)
```

### News Tool (`tools/news_tool.py`)

**API Endpoints Used**:
- `/everything` - Search all articles
- `/top-headlines` - Get top headlines by category

**Features**:
- Requires API key
- Date filtering (last 7 days)
- Language and country filters

**Example Usage**:
```python
news = NewsTool(api_key="...")
articles = news.get_tech_news(
    query="technology",
    limit=5
)
```

## LLM Integration

### Groq Client (`llm/groq_client.py`)

**LangChain Integration**:
```python
from langchain_groq import ChatGroq
from langchain.output_parsers import PydanticOutputParser

llm = ChatGroq(
    model_name="llama-3.1-70b-versatile",
    temperature=0.1,  # Low for consistency
    max_tokens=2048
)
```

**Structured Output Generation**:
1. Define Pydantic model for output schema
2. Create output parser
3. Build prompt with format instructions
4. Execute chain: prompt → LLM → parser
5. Return validated Pydantic object

**Benefits**:
- Type-safe outputs
- Automatic validation
- Clear contracts between agents
- Easy to debug

## Data Flow Example

### Input: "Get latest tech news and summarize it"

**Step 1: Planner**
```json
{
  "task_description": "Get latest tech news and summarize it",
  "steps": [
    {
      "step_number": 1,
      "action": "fetch_tech_news",
      "tool": "NewsTool",
      "parameters": {"query": "technology", "limit": 5},
      "reasoning": "Need to fetch recent tech articles"
    },
    {
      "step_number": 2,
      "action": "summarize_articles",
      "tool": "LLM",
      "parameters": {"prompt": "Summarize these articles"},
      "reasoning": "User wants a summary of the news"
    }
  ],
  "expected_outcome": "Summary of latest tech news"
}
```

**Step 2: Executor**
```json
{
  "plan_description": "Get latest tech news and summarize it",
  "step_results": [
    {
      "step_number": 1,
      "action": "fetch_tech_news",
      "tool_used": "NewsTool",
      "status": "success",
      "data": {
        "articles": [
          {
            "title": "AI Breakthrough in 2024",
            "source": "TechCrunch",
            "url": "https://..."
          }
        ]
      }
    },
    {
      "step_number": 2,
      "action": "summarize_articles",
      "tool_used": "LLM",
      "status": "success",
      "data": {
        "summary": "Recent tech news highlights..."
      }
    }
  ],
  "overall_status": "success"
}
```

**Step 3: Verifier**
```json
{
  "original_task": "Get latest tech news and summarize it",
  "is_complete": true,
  "summary": "Successfully retrieved 5 tech articles from the past week. Key highlights include AI breakthroughs, new framework releases, and industry trends. All articles are from reputable sources like TechCrunch and Wired.",
  "data": {
    "step_1": {"articles": [...]},
    "step_2": {"summary": "..."}
  },
  "issues": [],
  "confidence_score": 1.0
}
```

## Design Patterns Used

### 1. Single Responsibility Principle
- Each agent has one clear purpose
- Tools are separated by API
- LLM client is isolated

### 2. Dependency Injection
- Agents receive LLM client as parameter
- Tools can be mocked for testing
- Easy to swap implementations

### 3. Strategy Pattern
- Executor routes to different tools
- Tool selection based on plan
- Flexible and extensible

### 4. Chain of Responsibility
- Planner → Executor → Verifier
- Each agent processes and passes forward
- Clear data flow

## Error Handling Strategy

### API Failures
- Wrapped in try-catch blocks
- Return error status with message
- Continue execution when possible

### LLM Failures
- Retry logic can be added
- Fallback to simpler prompts
- Log errors for debugging

### Validation Failures
- Pydantic catches schema errors
- Clear error messages
- Prevents invalid data propagation

## Performance Considerations

### Sequential Execution
- **Current**: Steps run one after another
- **Benefit**: Simple, predictable, easy to debug
- **Tradeoff**: Slower for independent steps

### No Caching
- **Current**: Every request hits APIs
- **Benefit**: Always fresh data
- **Tradeoff**: Uses rate limits quickly

### Future Optimizations
- Parallel execution for independent steps
- Redis cache for repeated queries
- Request batching for APIs
- Async/await for I/O operations

## Testing Strategy

### Unit Tests (Future)
- Test each agent independently
- Mock LLM and API responses
- Verify Pydantic schemas

### Integration Tests (Future)
- Test full agent pipeline
- Use test API keys
- Verify end-to-end flow

### Manual Testing (Current)
- `test_system.py` verifies components
- Example prompts in README
- Streamlit UI for interactive testing

## Scalability Considerations

### Current Limitations
- Single-user design
- No database or persistence
- Sequential execution only
- No authentication

### Production Improvements
- FastAPI backend with async
- PostgreSQL for user history
- Redis for caching
- JWT authentication
- Docker containerization
- Kubernetes deployment

---

**This architecture demonstrates production-ready patterns while maintaining simplicity for a 24-hour assignment.**
