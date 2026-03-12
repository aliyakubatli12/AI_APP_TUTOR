import json
from typing import Any, cast

with open("/Users/aliyakubatli/ai_module/topics/topic_tree.json", "r") as f:
    topic_tree: dict[str, dict[str, Any]] = cast(dict[str, dict[str, Any]], json.load(f))

rename_map = {
    "Audio Filters":           "Audio Filter Algorithms",
    "Backtracking":            "Backtracking Algorithms",
    "Bit Manipulation":        "Bit Manipulation",
    "Blockchain":              "Blockchain Algorithms",
    "Boolean Algebra":         "Boolean Algebra",
    "Cellular Automata":       "Cellular Automata",
    "Ciphers":                 "Cipher Algorithms",
    "Computer Vision":         "Computer Vision",
    "Conversions":             "Conversion Algorithms",
    "Data Compression":        "Data Compression Algorithms",
    "Data Structures":         "Data Structures",
    "Digital Image Processing":"Digital Image Processing",
    "Divide And Conquer":      "Divide And Conquer Algorithms",
    "Docs":                    None,  # silinecek
    "Dynamic Programming":     "Dynamic Programming",
    "Electronics":             "Electronics",
    "File Transfer":           "File Transfer",
    "Financial":               "Financial Algorithms",
    "Fractals":                "Fractals",
    "Fuzzy Logic":             "Fuzzy Logic",
    "Genetic Algorithm":       "Genetic Algorithms",
    "Geodesy":                 "Geodesy Algorithms",
    "Geometry":                "Geometry Algorithms",
    "Graphics":                "Graphics Algorithms",
    "Graphs":                  "Graph Algorithms",
    "Greedy Methods":          "Greedy Algorithms",
    "Hashes":                  "Hashing Algorithms",
    "Knapsack":                "Knapsack Problems",
    "Linear Algebra":          "Linear Algebra",
    "Linear Programming":      "Linear Programming",
    "Machine Learning":        "Machine Learning",
    "Maths":                   "Mathematics",
    "Matrix":                  "Matrix Algorithms",
    "Networking Flow":         "Network Flow Algorithms",
    "Neural Network":          "Neural Networks",
    "Other":                   "Other Algorithms",
    "Physics":                 "Physics",
    "Project Euler":           "Project Euler",
    "Quantum":                 "Quantum Algorithms",
    "Scheduling":              "Scheduling Algorithms",
    "Searches":                "Search Algorithms",
    "Sorts":                   "Sorting Algorithms",
    "Strings":                 "String Algorithms",
    "Web Programming":         "Web Programming",
}

# normalize edilmiş tree
normalized_tree = {}
for old_key, specifics in topic_tree.items():
    new_key = rename_map.get(old_key, old_key)
    if new_key is None:  # None ise atla (Docs gibi)
        continue
    normalized_tree[new_key] = specifics

# specific → general mapping
mapping = {}
for general, specifics in normalized_tree.items():
    for specific in specifics.keys():
        mapping[specific] = general

with open("/Users/aliyakubatli/ai_module/topics/topic_tree.json", "w") as f:
    json.dump(normalized_tree, f, indent=4)

with open("/Users/aliyakubatli/ai_module/topics/topic_mapping.json", "w") as f:
    json.dump(mapping, f, indent=4)

print(f"Kategoriler: {len(normalized_tree)}")
print(f"Specific topics: {len(mapping)}")

# Shown mistakes are in red because  of the pylance extension
# Not an issue to run the code