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

## How It Works

The agent runs four tools in sequence:

1. `extract_job_requirements` — parses the JD into structured requirements
2. `score_cv` — scores the CV against requirements using an explicit rubric
3. `suggest_improvements` — retrieves ATS best practices via RAG and generates specific fixes
4. `generate_cover_letter` — writes a tailored cover letter based on the CV and gaps

## Project Structure

src/
└── agent/
├── knowledge.py    # ATS knowledge base + minsearch index
├── tools.py        # ATSTools class with four tools
└── agent.py        # Agent loop and run_agent function
tests/
└── test_agent.py       # Tool call order, LLM judge, and out-of-scope tests
data/
└── ats_knowledge.json  # ATS best practices knowledge base
notebooks/
├── 01-setup.ipynb      # Environment verification
├── 02-rag.ipynb        # RAG pipeline prototype
└── 03-agent.ipynb      # Agent development notebook

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

3. Copy `.env.example` to `.env` and add your Groq API key:
```bash
cp .env.example .env
# add GROQ_API_KEY=your_key_here
```

4. Install dependencies:
```bash
make install
```

5. Run tests to verify everything works:
```bash
make test
```

## Usage

```python
from src.agent.agent import run_agent

result = run_agent("""
Analyse my CV against this job description.

CV:
[paste your CV here]

Job Description:
[paste the job description here]
""")

print(result)
```

## Tech Stack

- **LLM:** Groq (`llama-3.3-70b-versatile`)
- **RAG:** minsearch over ATS best practices knowledge base
- **Agent:** Custom tool-calling loop with 4 tools
- **Testing:** pytest with monkey-patching and LLM-as-judge
- **Dependency management:** uv
- **Environment:** VS Code Dev Container + Docker

## Known Limitations

- Match score has ±5 variance across runs even with `temperature=0` due to LLM subjectivity
- Groq occasionally produces malformed tool calls — handled with a recovery handler
- Knowledge base is static — expanding it will improve suggestion quality