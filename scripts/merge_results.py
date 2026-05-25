import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

with open(ROOT / 'data/eval_results.json') as f:
    source = {s['name']: s for s in json.load(f)}

with open(ROOT / 'data/eval_dataset.json') as f:
    labeled = json.load(f)

updated = 0
for session in labeled:
    name = session['name']
    if name in source and not session.get('result'):
        session['result'] = source[name].get('result', '')
        session['status'] = source[name].get('status', 'error')
        updated += 1

with open(ROOT / 'data/eval_dataset.json', 'w') as f:
    json.dump(labeled, f, indent=2)

print(f"Updated {updated} sessions")