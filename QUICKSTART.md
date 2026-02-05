# 🚀 Quick Start Guide

## For Evaluators

This guide will help you run the AI Operations Assistant in under 5 minutes.

### Step 1: Install Dependencies (1 minute)

```bash
cd ai_ops_assistant
pip install -r requirements.txt
```

### Step 2: Configure API Keys (2 minutes)

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and add your API keys:
```env
GROQ_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
GITHUB_TOKEN=optional
```

**Get API Keys:**
- Groq: https://console.groq.com/keys (Free, instant)
- NewsAPI: https://newsapi.org/register (Free, instant)
- GitHub: https://github.com/settings/tokens (Optional)

### Step 3: Test System (1 minute)

```bash
python test_system.py
```

This will verify all components are working.

### Step 4: Run Application (1 minute)

```bash
python -m streamlit run main.py
```

The app opens at `http://localhost:8501`

### Step 5: Try Example Prompts

Copy-paste these into the UI:

1. **"Get latest tech news and summarize it"**
2. **"Find trending Python repositories on GitHub"**
3. **"Get top tech headlines and find related GitHub projects"**

---

## Expected Behavior

### Planner Agent
- Creates structured execution plan
- Selects appropriate tools
- Shows JSON output with steps

### Executor Agent
- Calls GitHub and News APIs
- Collects data from each step
- Shows execution results

### Verifier Agent
- Validates completeness
- Generates summary
- Shows final formatted output

---

## Troubleshooting

**"GROQ_API_KEY not found"**
- Check `.env` file exists
- Verify API key is correct
- No quotes around the key

**"NewsAPI error"**
- Verify API key is valid
- Check rate limit (100/day free tier)
- Try again in a few minutes

**"Module not found"**
- Run: `pip install -r requirements.txt`
- Ensure you're in `ai_ops_assistant/` directory

**Streamlit won't start**
- Check Python version (3.9+)
- Try: `python -m streamlit run main.py`
- Make sure streamlit is installed: `pip install streamlit`

---

## Architecture Verification

✅ **Multi-Agent Design**: 3 agents (Planner, Executor, Verifier)
✅ **LLM Integration**: Groq + Llama 3.3 70B via LangChain
✅ **Structured Outputs**: Pydantic models with JSON schema
✅ **API Integration**: GitHub API + NewsAPI (2 real APIs)
✅ **No Hardcoded Responses**: All data from live APIs
✅ **One Command Run**: `python -m streamlit run main.py`

---

## File Structure Check

```
ai_ops_assistant/
├── agents/          ✅ Planner, Executor, Verifier
├── tools/           ✅ GitHub, News API tools
├── llm/             ✅ Groq client with LangChain
├── main.py          ✅ Streamlit UI
├── requirements.txt ✅ Dependencies
├── .env.example     ✅ Environment template
└── README.md        ✅ Full documentation
```

---

**Total Setup Time: ~5 minutes**
**Ready for evaluation!** 🎉
