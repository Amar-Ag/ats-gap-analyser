import json

import pytest
from dotenv import load_dotenv

from src.agent.agent import client

load_dotenv(override=True)

@pytest.fixture
def sample_cv():
    sample_cv = """
    John Smith
    Data Analyst | john@email.com

    EXPERIENCE
    Senior Data Analyst - ABC Corp (2021-Present, 3 years)
    - Built SQL queries to analyse customer data
    - Created Power BI dashboards for operations team
    - Used Python and pandas for data cleaning

    Junior Analyst - XYZ Ltd (2019-2021)
    - Supported reporting using Excel and SQL

    SKILLS
    SQL, Python, pandas, Excel, Power BI, data visualisation

    EDUCATION
    BSc Statistics - University of Manchester (2019)
    """
    return sample_cv

@pytest.fixture
def sample_jd():
    sample_jd = """
    Data Analyst at a Logistics Company

    We are looking for a Data Analyst with 3+ years of experience.

    Required:
    - Strong SQL skills
    - Python for data analysis (pandas, numpy)
    - Power BI or Tableau for dashboards
    - Experience with logistics or supply chain data

    Nice to have:
    - dbt experience
    - Azure or AWS
    - Freight industry knowledge
    """
    return sample_jd

def test_tool_call_order(sample_cv, sample_jd):
    """Agent must call all four tools in the correct sequence"""
    called_tools = []

    import src.agent.agent as agent_module
    original_run_tool = agent_module.run_tool

    def tracking_run_tool(name, args):
        called_tools.append(name)
        return original_run_tool(name, args)

    agent_module.run_tool = tracking_run_tool

    try:
        agent_module.run_agent(
            f"Analyse my CV against this job description.\nCV:\n{sample_cv}\nJD:\n{sample_jd}"
        )
    finally:
        agent_module.run_tool = original_run_tool

    assert "extract_job_requirements" in called_tools
    assert "score_cv" in called_tools
    assert "suggest_improvements" in called_tools
    assert "generate_cover_letter" in called_tools

    assert called_tools.index("extract_job_requirements") < called_tools.index("score_cv")
    assert called_tools.index("score_cv") < called_tools.index("suggest_improvements")


def assert_criteria(result: str, criteria: list[str]):
    criteria_text = "\n".join(f"- {c}" for c in criteria)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict evaluator for an ATS Gap Analyser agent. "
                    "Given the agent output and a list of criteria, check if ALL criteria are met. "
                    "Return a JSON object with exactly these fields: "
                    "'passed' (boolean, true only if ALL criteria pass), "
                    "'reasoning' (string, overall explanation), "
                    "'failed_criteria' (list of strings, the exact criteria that failed, empty if all passed)."
                )
            },
            {
                "role": "user", 
                "content": criteria_text + "\n\nAgent Output:\n" + result
            }
        ]
    )
    
    judgment = json.loads(response.choices[0].message.content)
    
    if not judgment["passed"]:
        pytest.fail(f"Output did not meet criteria: {judgment['failed_criteria']}. Reasoning: {judgment['reasoning']}")


def test_criteria(sample_cv, sample_jd):
    """Agent will be checked by LLM against a given criteria"""

    import src.agent.agent as agent_module
    result = agent_module.run_agent(
        f"Analyse my CV against this job description.\nCV:\n{sample_cv}\nJD:\n{sample_jd}"
    )

    criteria = [
        "the response includes a numeric match score between 0 and 100",
        "the response lists at least one specific missing keyword from the job description",
        "the response includes a cover letter addressed to the specific role not a generic template",
        "the suggestions mention specific skills from the job description such as Tableau or numpy not generic advice"
    ]

    assert_criteria(result, criteria)
