from striprtf.striprtf import rtf_to_text # type: ignore
from typing import cast
import re
import json

with open("/Users/aliyakubatli/ai_module/datas/raw_data_algorithms.txt.rtf", "r", encoding="utf-8") as f:
     raw = f.read()

plain_text: str = cast(str, rtf_to_text(raw))

lines = [l.strip() for l in plain_text.split("\n") if l.strip()]

tree = {}
current_category = None

for line in lines:

    if line.startswith("## "):
        current_category = line.replace("## ", "")
        tree[current_category] = {}

    elif line.startswith("* [") and current_category:
        match = re.search(r"\[(.*?)\]", line)
        if match:
            algo = match.group(1)
            tree[current_category][algo] = {}

with open("topic_tree.json", "w") as f:
    json.dump(tree, f, indent=4)