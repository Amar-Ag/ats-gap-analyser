import json
import os
import inspect
from pydantic import BaseModel
from typing import List, get_type_hints
from src.agent.knowledge import index

class JobRequirements(BaseModel):
    job_title: str
    required_skills: List[str]
    nice_to_have_skills: List[str]
    experience_years: int
    keywords: List[str]


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
    
    def extract_job_requirements(self, job_description: str) -> dict:
        """Extracts structured requirements from a job description including required skills, experience level, and keywords"""
        schema = JobRequirements.model_json_schema()
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Extract structured requirements from a job description. Return only a JSON object matching this schema: {schema}. Return only the JSON, no other text."},
                {"role": "user", "content": job_description}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    
    def score_cv(self, cv_text: str, requirements: dict) -> dict:
        """Scores a CV against job requirements and identifies matched and missing keywords"""
        schema = CVScore.model_json_schema()
        
        rubric = """
    Score the CV using this exact rubric:
    - Start at 100
    - Subtract 10 points for each required skill missing from the CV
    - Subtract 15 points if experience years in CV is less than required
    - Subtract 5 points for each important keyword missing
    - Minimum score is 0

    Be strict and literal — only count a skill as present if it is 
    explicitly mentioned in the CV text. Do not infer or assume.
    """
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an ATS scoring system. {rubric}
    Return only a JSON object matching this schema: {schema}
    Return only the JSON, no other text."""
                },
                {
                    "role": "user",
                    "content": f"CV:\n{cv_text}\n\nRequirements:\n{json.dumps(requirements, indent=2)}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    
    def suggest_improvements(self, cv_text: str, missing_keywords: List[str]) -> dict:
        """Generates specific actionable CV improvement suggestions based on missing keywords using ATS best practices"""
        search_results = self.index.search(
            f"keywords missing skills {' '.join(missing_keywords[:3])}",
            num_results=3
        )
        context = json.dumps(search_results, indent=2)
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Generate specific actionable CV improvement suggestions. Return a JSON object with a single key 'suggestions' containing a list of strings. Be specific not generic."},
                {"role": "user", "content": f"Missing keywords: {missing_keywords}\n\nATS Best Practices:\n{context}\n\nCV:\n{cv_text}\n\nGenerate 4-5 specific suggestions."}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    
    def generate_cover_letter(self, cv_text: str, job_description: str, match_score: int) -> str:
        """Generates a tailored cover letter based on the CV, job description and match score"""
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Write a tailored 3-paragraph cover letter. Open with a specific reason for applying. Connect top achievements to job requirements. Close with a call to action. Under 250 words."},
                {"role": "user", "content": f"CV:\n{cv_text}\n\nJob Description:\n{job_description}\n\nMatch Score: {match_score}/100"}
            ]
        )
        return response.choices[0].message.content