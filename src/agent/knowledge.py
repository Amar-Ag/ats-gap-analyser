import json
from pathlib import Path
from minsearch import Index

data_path = Path(__file__).parent.parent.parent / "data" / "ats_knowledge.json"

with open(data_path) as f:
    documents = json.load(f)

index = Index(
    text_fields=["title", "content"],
    keyword_fields=["category"]
)
index.fit(documents)