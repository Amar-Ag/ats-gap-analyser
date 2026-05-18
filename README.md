# ATS Gap Analyser

## Problem

Job seekers apply to roles and hear nothing back. They don't know if
their CV failed ATS screening, lacked the right keywords, or simply
didn't match the role — so they can't improve their applications.

## What It Does

The ATS Gap Analyser is an AI agent that takes a CV and a job description
and returns a full gap analysis. It uses RAG over an ATS best practices
knowledge base to ground its suggestions in real advice.

**Input:** CV text + job description text  
**Output:**
- Match score (0-100) showing how well the CV fits the role
- Missing keywords and skills the JD requires
- Specific, actionable CV improvement suggestions
- A tailored cover letter for the role

**Live demo:** https://ats-gap-analyser.streamlit.app/

## How It Works

The agent runs four tools in sequence:

1. `extract_job_requirements` — parses the JD into structured requirements including OR conditions
2. `score_cv` — scores the CV against requirements using an explicit rubric with OR condition and phrasing awareness
3. `suggest_improvements` — retrieves ATS best practices via RAG and generates specific fixes
4. `generate_cover_letter` — writes a tailored cover letter based on the CV and gaps

## Project Structure

src/
└── agent/
├── knowledge.py    # ATS knowledge base + minsearch index
├── tools.py        # ATSTools class with four tools
└── agent.py        # Agent loop, run_agent, Logfire monitoring
app.py              # Streamlit UI
tests/
└── test_agent.py       # Tool call order, LLM judge, out-of-scope tests
notebooks/
├── 01-setup.ipynb      # Environment verification
├── 02-rag.ipynb        # RAG pipeline prototype
├── 03-agent.ipynb      # Agent development
├── 04-monitoring-analysis.ipynb  # Logfire query analysis
└── 05-evaluation.ipynb # LLM judge evaluation
scripts/
├── batch_run.py        # Run 50 evaluation scenarios in batch
├── label_results.py    # Streamlit labeling tool
└── rerun_bad.py        # Rerun sessions labeled bad after agent fixes
data/
├── ats_knowledge.json          # ATS best practices knowledge base
├── eval_results.json           # Raw evaluation results
└── eval_results_results.json   # Labeled evaluation dataset


## Setup

### Prerequisites
- Docker Desktop
- VS Code with Dev Containers extension

### Run Locally

1. Clone the repo:
```bash
git clone https://github.com/Amar-Ag/ats-gap-analyser.git
cd ats-gap-analyser
```

2. Open in VS Code and click **Reopen in Container** when prompted

3. Copy `.env.example` to `.env` and add your keys:
```bash
cp .env.example .env
# add GROQ_API_KEY and LOGFIRE_TOKEN
```

4. Install dependencies:
```bash
make install
```

5. Run tests:
```bash
make test
```

6. Run the app:
```bash
make run
```

## Evaluation Results

Evaluated against 44 labeled sessions covering happy path, varied input,
edge cases, out of scope, and breaking scenarios.

| Metric | Value |
|---|---|
| Total labeled sessions | 44 |
| Good responses | 33 (75%) |
| Bad responses | 11 (25%) |
| Real agent logic failures | 9/42 (21%) |

**Failure breakdown:**
- Hallucination (6) — agent invents keywords not in JD
- Wrong score (2) — scoring inconsistency
- Missed key gap (1) — phrasing variation not matched

**LLM Judge performance (6 iterations):**

| Version | Sessions | Accuracy | Recall | Change |
|---|---|---|---|---|
| v1 baseline | 23 | 33% | 60% | initial |
| v2 step-by-step | 23 | 50% | 100% | added reasoning steps |
| v3 clarify suggestions | 23 | 66% | 100% | hallucination definition |
| v4 parenthetical rule | 23 | 75% | 100% | best on small dataset |
| v5 full dataset | 42 | 52% | 100% | larger dataset |
| v6 OR/refusal fixes | 42 | 64% | 89% | final |

**Key finding:** Judge achieves 89% recall (rarely misses real failures)
with 64% accuracy. Lower precision reflects the judge being stricter
than human labelers on edge cases and breaking scenarios.

## Known Limitations

- Match score has ±5 variance across runs despite `temperature=0`
- Groq occasionally produces malformed tool calls — handled with recovery handler
- OR conditions in JDs (e.g. "Power BI or Tableau") are handled but not always perfectly
- Knowledge base is static — expanding it will improve suggestion quality
- HuggingFace fallback available when Groq daily limit is reached

## Tech Stack

- **LLM:** Groq (`llama-3.3-70b-versatile`) with HuggingFace fallback
- **RAG:** minsearch over ATS best practices knowledge base
- **Agent:** Custom tool-calling loop with 4 tools and OR condition awareness
- **Monitoring:** Logfire (traces, token usage, match scores)
- **Testing:** pytest with monkey-patching and LLM-as-judge
- **Evaluation:** 44 labeled sessions, LLM judge with 6 iterations
- **UI:** Streamlit (deployed at ats-gap-analyser.streamlit.app)
- **Dependency management:** uv
- **Environment:** VS Code Dev Container + Docker

## Project Status

- ✅ Agent with 4 tools
- ✅ RAG over ATS knowledge base
- ✅ OR condition and phrasing matching in scoring
- ✅ Monitoring with Logfire
- ✅ 44 evaluation scenarios labeled
- ✅ LLM judge with 6 iterations
- ✅ Streamlit UI deployed
- ✅ Tests passing