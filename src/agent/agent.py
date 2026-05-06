import json
import os

from dotenv import load_dotenv
from groq import Groq
from src.agent.tools import ATSTools, get_instance_tools
from src.agent.knowledge import index

load_dotenv(override=True)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# instantiate tools
ats_tools = ATSTools(client, index)

# auto-generate tool definitions
tools = get_instance_tools(ats_tools)

def run_tool(name: str, args: dict):
    method = getattr(ats_tools, name, None)
    if method:
        return method(**args)
    return {"error": f"Unknown tool: {name}"}


instructions = """
You are an ATS Gap Analyser assistant. You help job seekers understand 
why their CV may not be passing ATS screening and what to fix.

When a user provides both a CV and a job description, always follow 
this sequence:
1. Call extract_job_requirements on the job description
2. Call score_cv with the CV and extracted requirements
3. Call suggest_improvements with the CV and missing keywords
4. Call generate_cover_letter with the CV, job description, and match score
5. Present a final summary that MUST include ALL of these sections:
   - Match Score (the numeric score)
   - Missing Keywords (specific keywords not found)
   - Improvement Suggestions (specific actionable steps)
   - Cover Letter (the full cover letter text, do not summarise or omit it)

Never omit the cover letter from your final response.
"""


def run_agent(user_message: str):
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": user_message}
    ]
    
    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
        )
        
        choice = response.choices[0]
        
        # handle groq <function=> bug
        if choice.finish_reason == "stop" and choice.message.content and "<function=" in choice.message.content:
            import re
            match = re.search(r'<function=(\w+)[,>]({.*?})', choice.message.content, re.DOTALL)
            if match:
                name = match.group(1)
                args = json.loads(match.group(2))
                result = run_tool(name, args)
                messages.append(choice.message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": "recovered",
                    "content": json.dumps(result)
                })
                continue

        messages.append(choice.message)
        
        if choice.finish_reason == "stop":
            return choice.message.content
        
        if choice.finish_reason == "tool_calls":
            for tool_call in choice.message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"Calling tool: {name}")
                result = run_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })