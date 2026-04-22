# ATS Gap Analyser

## Problem

Job seekers apply to roles and hear nothing back. They don't know if 
their CV failed ATS screening, lacked the right keywords, or simply 
didn't match the role — so they can't improve their applications.

## What It Does

The ATS Gap Analyser takes a CV (PDF) and a job description (text) 
and returns:

- A match score showing how well the CV fits the role
- A list of missing keywords and skills the JD requires
- Specific, actionable CV improvement suggestions
- A tailored cover letter for the role

## Typical Interaction

**Input:** Upload your CV as a PDF + paste a job description  
**Output:** Gap report with match score, missing skills, improvement 
suggestions, and a cover letter

## Setup

1. Clone the repo
2. Copy `.env.example` to `.env` and add your `GROQ_API_KEY`
3. Run `uv sync` to install dependencies
4. Open notebooks in Jupyter

## Notebooks

- `notebooks/01-setup.ipynb` — verify environment
- `notebooks/02-rag.ipynb` — RAG pipeline over ATS best practices data