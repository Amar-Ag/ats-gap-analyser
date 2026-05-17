import json
import os
import logfire
import re

from openai import OpenAI
from dotenv import load_dotenv
from groq import Groq, BadRequestError
from src.agent.tools import ATSTools, get_instance_tools
from src.agent.knowledge import index

load_dotenv(override=True)
logfire.configure()

# primary client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# fallback client
hf_client = OpenAI(
    api_key=os.getenv("HF_TOKEN"),
    base_url="https://router.huggingface.co/v1"
)

# start with groq
client = groq_client

# instantiate tools
ats_tools = ATSTools(client, index)

# auto-generate tool definitions
tools = get_instance_tools(ats_tools)

def run_tool(name: str, args: dict):
    with logfire.span(f"tool:{name}", args=str(args)[:200]):
        method = getattr(ats_tools, name, None)
        if method:
            result = method(**args)
            if name == "score_cv" and isinstance(result, dict):
                logfire.info("cv scored", match_score=result.get("match_score"))
            return result
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
    global client
    retry_count = 0
    
    with logfire.span("agent run", user_message=user_message[:100]):
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_message}
        ]
        
        while True:
            try:
                model = "llama-3.3-70b-versatile" if client == groq_client else "meta-llama/Llama-3.3-70B-Instruct:groq"
                
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tools,
                )
            except BadRequestError as e:
                if 'tool_use_failed' in str(e) and retry_count < 3:
                    retry_count += 1
                    messages.append({
                        "role": "user",
                        "content": "Please try again using the tools one at a time in the correct sequence."
                    })
                    continue
                raise
            except Exception as e:
                if '429' in str(e):
                    if client == groq_client:
                        print("Groq rate limit — switching to HuggingFace")
                        client = hf_client
                        ats_tools.client = hf_client  # switch tools client too
                        continue
                    else:
                        raise
                raise

            choice = response.choices[0]

            if hasattr(response, 'usage') and response.usage:
                logfire.info(
                    "token usage",
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens
                )
            
            # handle groq <function=> bug
            if choice.finish_reason == "stop" and choice.message.content and "<function=" in choice.message.content:
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
                logfire.info("agent completed", response_length=len(choice.message.content))
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

