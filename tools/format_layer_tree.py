import json
from pathlib import Path
from .normalize_topic import normalize_topic

TOPIC_TREE_PATH = Path(__file__).resolve().parents[1] / "topics" / "topic_tree.json"

with open(TOPIC_TREE_PATH, "r", encoding="utf-8") as f:
    topic_tree = json.load(f)

first_layer_items = []

for category, items in topic_tree.items():
    for raw_name in items.keys():
        first_layer_items.append({ # type: ignore
            "raw_name": raw_name,
            "normalized_name": normalize_topic(raw_name),
            "category": category,
        })
with open("topic_tree_format.json", "w") as f:
    json.dump(first_layer_items, f, indent=4)

print(json.dumps(first_layer_items[:10], indent=2, ensure_ascii=False))