# ATS Gap Analyser

> **AI agent that tells job seekers exactly why their CV isn't getting interviews — and how to fix it.**

🔗 **[Live Demo](https://ats-gap-analyser.streamlit.app/)** | Built by [Amar Agrawal](https://www.linkedin.com/in/amar-agrawal-/)

---

## The Problem

Job seekers apply for roles and hear nothing back. They don't know if their CV failed ATS screening, lacked the right keywords, or simply didn't match the role — so they can't improve their applications.

**This tool solves that.** Paste your CV and a job description, get a match score, specific gaps, actionable fixes, and a tailored cover letter in under 30 seconds.

---

## What It Does

**Input:** CV (PDF upload or text paste) + Job Description (URL fetch or text paste)

**Output:**
- 🎯 **Match score** (0-100) with colour-coded visual indicator
- 🔍 **Missing keywords** — only genuinely absent required skills
- 💡 **Improvement suggestions** — grounded in a 50-document ATS best practices knowledge base
- ✉️ **Tailored cover letter** — downloadable as Word (.docx), available in 7 languages
- 🔒 **Privacy first** — your CV and JD are never stored or logged

---

## Architecture

The agent orchestrates four tools in sequence using a custom tool-calling loop:
```

User Input (CV + JD)
│
▼
extract_job_requirements  ──►  Structured requirements + OR conditions
│
▼
score_cv  ──────────────────►  Match score + matched/missing keywords
│                       (OR condition aware, phrasing flexible)
▼
suggest_improvements  ──────►  RAG over 50 ATS best practice documents
│
▼
generate_cover_letter  ─────►  Tailored 3-paragraph cover letter
│
▼
Final Summary
```

**Key engineering decisions:**
- OR conditions in JDs ("Power BI or Tableau") are extracted as alternatives and handled correctly in scoring
- Phrasing matching: "Managed £500k budget" satisfies "budget management"
- Groq malformed tool call recovery handler using regex
- HuggingFace fallback when Groq daily token limit is reached

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Groq `llama-3.3-70b-versatile` + HuggingFace fallback |
| RAG | minsearch over 50 ATS best practice documents |
| Agent | Custom tool-calling loop with 4 tools |
| Monitoring | Logfire (traces, token usage, match scores per session) |
| Testing | pytest — tool call order, LLM-as-judge, out-of-scope |
| UI | Streamlit (deployed on Streamlit Cloud) |
| Packaging | uv + pyproject.toml |
| Environment | VS Code Dev Container + Docker |
| CI/CD | GitHub Actions |

---

## Evaluation

Systematically evaluated using 50 hand-crafted scenarios across 5 categories: happy path, varied input, edge cases, out-of-scope, and breaking scenarios.

**Agent performance:**

| Metric | Value |
|---|---|
| Total labeled sessions | 50 |
| Good responses | 42 (84%) |
| Bad responses | 8 (16%) |
| Real logic failures (excl. API errors) | 6/48 = 12.5% |

**Failure breakdown:**
- Hallucination (4) — agent invents keywords not in JD
- Wrong score (2) — scoring inconsistency on edge cases
- Incorrect refusal (1) — agent declined a valid input
- Missed key gap (1) — phrasing variation not matched

**LLM Judge (6 iterations of prompt engineering):**

| Version | Sessions | Accuracy | Recall | What Changed |
|---|---|---|---|---|
| v1 | 23 | 33% | 60% | Baseline |
| v2 | 23 | 50% | 100% | Step-by-step reasoning |
| v3 | 23 | 66% | 100% | Hallucination definition |
| v4 | 23 | 75% | 100% | Parenthetical constraint rule |
| v5 | 42 | 52% | 100% | Scaled to larger dataset |
| v6 | 50 | 60% | 88% | OR condition + refusal clarifications |

**Key finding:** The judge achieves 88% recall — it rarely misses a real failure. Lower precision (60%) reflects the judge being stricter than human labelers on legitimate domain gaps and edge cases. The drop from 75% (23 sessions) to 60% (50 sessions) shows the judge generalises less well to edge cases — a known limitation of small evaluation sets.

---

## Project Structure

```
src/
└── agent/
├── knowledge.py              # 50-document ATS knowledge base + minsearch index
├── tools.py                  # ATSTools class with 4 tools and OR condition handling
└── agent.py                  # Agent loop, tool recovery, Logfire monitoring
app.py                        # Streamlit UI with PDF upload, URL fetch, history
tests/
└── test_agent.py                 # Tool call order, LLM judge, out-of-scope tests
notebooks/
├── 02-rag.ipynb                  # RAG pipeline prototype
├── 03-agent.ipynb                # Agent development
├── 04-monitoring-analysis.ipynb  # Logfire query analysis
└── 05-evaluation.ipynb           # LLM judge evaluation pipeline
scripts/
├── batch_run.py                  # 50-scenario batch evaluation runner
├── label_results.py              # Streamlit manual labeling tool
├── rerun_bad.py                  # Targeted rerun of failed sessions
└── generate_knowledge.py         # Generate ATS knowledge base with LLM
data/
├── ats_knowledge.json            # 50 ATS best practice documents
├── eval_results.json             # Raw batch evaluation results
└── eval_dataset.json             # Labeled dataset with judge results
```

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

# 2. Open in VS Code and click "Reopen in Container" when prompted

# 3. Add your keys
cp .env.example .env
# Edit .env with GROQ_API_KEY and LOGFIRE_TOKEN

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
- Cover letter language selector supports 7 languages — quality varies by language
- Some enterprise career portals (Oracle, Workday) block URL fetching — paste JD text directly

---

## About

Built as the capstone project for the [AI Engineering Buildcamp](https://maven.com/alexey-grigorev/from-rag-to-agents) by Alexey Grigorev.

The project demonstrates end-to-end AI engineering: problem identification, RAG pipeline, agent with tool calling, test-driven development, monitoring with Logfire, systematic evaluation with LLM-as-judge, and production deployment.
