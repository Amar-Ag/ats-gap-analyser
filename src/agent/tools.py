import json
import os
import inspect
from pydantic import BaseModel
from typing import List, get_type_hints

class JobRequirements(BaseModel):
    job_title: str
    required_skills: List[str]
    nice_to_have_skills: List[str]
    experience_years: int
    keywords: List[str]
    or_conditions: List[str]  # e.g. ["Power BI or Tableau", "AWS or GCP"]


class CVScore(BaseModel):
    match_score: int
    matched_keywords: List[str]
    missing_keywords: List[str]
    experience_match: bool
    summary: str


def get_instance_tools(instance) -> list:
    tools = []
    
    for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
        if name.startswith('_'):
            continue
            
        sig = inspect.signature(method)
        hints = get_type_hints(method)
        doc = inspect.getdoc(method) or ""
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            hint = hints.get(param_name, str)
            
            if hint == str:
                param_type = "string"
            elif hint == int:
                param_type = "integer"
            elif hint == List[str]:
                param_type = "array"
            elif hint == dict:
                param_type = "object"
            else:
                param_type = "string"
            
            # these three blocks must be INSIDE the for loop
            prop = {"type": param_type, "description": f"Parameter '{param_name}': {param_name.replace('_', ' ')}"}
            if param_type == "array":
                prop["items"] = {"type": "string"}
            if param_type == "object":
                prop["description"] = f"Parameter '{param_name}': pass the complete output from the previous tool call as-is"
                prop["additionalProperties"] = True
            
            properties[param_name] = prop
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": doc,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        })
    
    return tools

class ATSTools:
    def __init__(self, client, index):
        self.client = client
        self.index = index
    
    @property
    def model(self):
        # check if using HuggingFace by looking at base_url
        base_url = str(getattr(self.client, 'base_url', ''))
        if 'huggingface' in base_url or 'router' in base_url:
            return "meta-llama/Llama-3.3-70B-Instruct:groq"
        return "llama-3.3-70b-versatile"
    
    def extract_job_requirements(self, job_description: str) -> dict:
        """Extracts structured requirements from a job description including required skills, experience level, and keywords"""
        schema = JobRequirements.model_json_schema()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"""Extract structured requirements from a job description.

                For OR conditions like "Power BI or Tableau" or "AWS or GCP":
                - Add BOTH individual skills to required_skills
                - Also add the full OR phrase to or_conditions (e.g. "Power BI or Tableau")

                This allows the scorer to know which skills are interchangeable alternatives.
                If experience years is not explicitly mentioned in the JD, set experience_years to 0.

                Return only a JSON object matching this schema: {schema}. Return only the JSON, no other text."""},
                {"role": "user", "content": job_description}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    
    def score_cv(self, cv_text: str, requirements: dict) -> dict:
        """Scores a CV against job requirements and identifies matched and missing keywords"""
        schema = CVScore.model_json_schema()
        
        or_conditions = requirements.get('or_conditions', [])
        or_conditions_text = "\n".join(f"- {c}" for c in or_conditions) if or_conditions else "None"
        or_conditions_warning = ""
        if or_conditions:
            or_conditions_warning = "\n\nCRITICAL - These are OR conditions. Do NOT list the alternative in missing_keywords:\n" + "\n".join(f"- {c}" for c in or_conditions)
        
        rubric = f"""
    Score the CV using this exact rubric:
    - Start at 100
    - Subtract 10 points for each required skill missing from the CV
    - Subtract 15 points if experience years in CV is less than required
    - Subtract 5 points for each important keyword missing
    - Minimum score is 0

    OR CONDITIONS (having EITHER option satisfies the requirement — do NOT penalise for the missing one):
    {or_conditions_text}

    PHRASING: Match skills conceptually not just literally:
    - "Managed £500k budget" satisfies "budget management"
    - "Created Power BI dashboards" satisfies "data visualisation"
    - "Python (basic)" satisfies "Python"
    - Match the concept, not the exact words.

    Be strict on required skills but flexible on phrasing variations.
    """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an ATS scoring system. {rubric}

    CRITICAL RULE FOR missing_keywords:
    Only include a keyword in missing_keywords if it is BOTH:
    1. Explicitly required in the JD (not nice-to-have)
    2. Genuinely absent from the CV (not just phrased differently)

    Do NOT include OR condition alternatives in missing_keywords.
    If JD says "Power BI or Tableau" and CV has Power BI, do NOT list Tableau as missing.

    Return only a JSON object matching this schema: {schema}
    Return only the JSON, no other text."""
                },
                {
                    "role": "user",
                    "content": f"CV:\n{cv_text}\n\nRequirements:\n{json.dumps(requirements, indent=2)}{or_conditions_warning}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    
    def suggest_improvements(self, cv_text: str, missing_keywords: List[str]) -> dict:
        """Generates specific actionable CV improvement suggestions based on missing keywords using ATS best practices"""
        # search more specifically based on the type of gaps
        search_query = " ".join(missing_keywords[:5]) if missing_keywords else "ATS keywords skills"
        search_results = self.index.search(search_query, num_results=5)  # increase from 3 to 5
        context = json.dumps(search_results, indent=2)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """Generate specific actionable CV improvement suggestions based on missing keywords.
                    Rules:
                    - Only suggest adding keywords that are genuinely missing from the CV
                    - If a skill is present in the CV but phrased differently (e.g. 'Managed £500k budget' covers 'budget management'), do NOT suggest adding it
                    - If the JD has OR conditions (e.g. 'Power BI or Tableau') and the CV has one of them, do NOT suggest adding the other
                    - Be specific not generic — reference actual keywords from the missing list
                    - Base suggestions on the ATS best practices context provided

                    Return a JSON object with a single key 'suggestions' containing a list of strings."""},
                {"role": "user", "content": f"Missing keywords: {missing_keywords}\n\nATS Best Practices:\n{context}\n\nCV:\n{cv_text}\n\nGenerate 4-5 specific suggestions."}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    
    def generate_cover_letter(self, cv_text: str, job_description: str, match_score: int) -> str:
        """Generates a tailored cover letter based on the CV, job description and match score"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": """Write a tailored 3-paragraph cover letter.
                    Open with a specific reason for applying to THIS role at THIS company.
                    Connect top 2-3 achievements directly to the job requirements.
                    If match score is below 70, honestly acknowledge the gap and explain 
                    how transferable skills compensate. Close with a call to action.
                    Under 250 words. Do not use placeholder text like [Company Name]."""},
                {"role": "user", "content": f"CV:\n{cv_text}\n\nJob Description:\n{job_description}\n\nMatch Score: {match_score}/100"}
            ]
        )
        return response.choices[0].message.content