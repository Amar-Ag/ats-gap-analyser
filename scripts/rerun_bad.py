import json
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(override=True)

from src.agent.agent import run_agent

RESULTS_FILE = 'data/eval_dataset.json'

RERUN_CATEGORIES = ['wrong_score', 'missed_key_gap']

with open(RESULTS_FILE) as f:
    results = json.load(f)

to_rerun = [
    r for r in results
    if r.get('failure_category') in RERUN_CATEGORIES
    and r.get('status') == 'success'
    and not r.get('rerun')  # skip already rerun
]

print(f"Sessions to rerun: {len(to_rerun)}")
for r in to_rerun:
    print(f"  {r['name']} — {r['failure_category']}")

print("\nStarting reruns...\n")

for i, session in enumerate(to_rerun):
    print(f"--- [{i+1}/{len(to_rerun)}] {session['name']} ---")
    
    try:
        cv_text = session['cv'][:1500] if session['cv'] else ""
        jd_text = session['jd'][:800] if session['jd'] else ""
        
        message = f"Analyse my CV against this job description.\nCV:\n{cv_text}\nJD:\n{jd_text}"
        
        result = run_agent(message)
        
        # update result but preserve label and comments
        session['result'] = result
        session['status'] = 'success'
        session['rerun'] = True  # flag as rerun
        # clear old judge result so it gets re-evaluated
        session.pop('judge_result', None)
        
        print(f"Result preview: {result[:150]}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        if '429' in str(e):
            print("Rate limit hit — saving and stopping")
            with open(RESULTS_FILE, 'w') as f:
                json.dump(results, f, indent=2)
            break
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved. Sleeping 10s...")
    time.sleep(13)

print(f"\nDone. Check results and relabel as needed.")