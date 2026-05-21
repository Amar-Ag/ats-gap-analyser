---

## Setup

### Prerequisites
- Docker Desktop
- VS Code with Dev Containers extension
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Logfire token (free at [logfire.pydantic.dev](https://logfire.pydantic.dev))

### Run Locally

```bash
# 1. Clone
git clone https://github.com/Amar-Ag/ats-gap-analyser.git
cd ats-gap-analyser

# 2. Open in VS Code → click "Reopen in Container"

# 3. Add your keys
cp .env.example .env
# Edit .env: add GROQ_API_KEY and LOGFIRE_TOKEN

# 4. Install and run
make install
make run
```

### Other Commands

```bash
make test    # Run pytest suite
make batch   # Run evaluation batch
make label   # Open labeling tool
make merge   # Merge evaluation results
```

---

## Known Limitations

- Match score has ±5 variance across runs despite `temperature=0` — inherent LLM non-determinism
- Groq occasionally produces malformed tool calls — handled with a regex recovery handler
- Knowledge base is static — expanding it with domain-specific content will improve suggestion quality
- URL fetching works for direct career pages but not LinkedIn (blocked) or Indeed (rate limited)

---

## About

Built as the capstone project for the [AI Engineering Buildcamp](https://maven.com/p/buildcamp) by Alexey Grigorev.

The project demonstrates end-to-end AI engineering: problem identification, RAG pipeline, agent with tool calling, test-driven development, monitoring with Logfire, systematic evaluation with LLM-as-judge, and production deployment.