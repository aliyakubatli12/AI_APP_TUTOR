"""
Builds the prompt used to instruct the LLM to extract computer science topics
from educational text and return them in a structured JSON format.
"""

# This prompt is created to help the LLM better understand topics.
# It provides clear instructions, examples, and rules to ensure the output is consistent and accurate.
# It forces the model to output two fields:
# specific_topics (algorithms / techniques)
# general_topics (broader CS categories)

def build_topic_prompt(raw_text: str) -> str:
    return f"""
You are an assistant that extracts computer science topics from educational text.

Task
From the input text, identify:
1. specific_topics → specific algorithms or techniques mentioned
2. general_topics → broader categories those topics belong to

Examples of specific topics:
BFS
DFS
Dijkstra
Bellman-Ford
Kruskal
Prim
Quicksort
Merge Sort
Binary Search
Red-Black Tree
Hash Table
Dynamic Programming
Backtracking

Examples of general topics:
Graph Algorithms
Sorting Algorithms
Searching Algorithms
Trees
Hashing
Dynamic Programming
Greedy Algorithms
Data Structures
Algorithm Analysis

Rules
Return ONLY valid JSON.
Do NOT include explanations.
Do NOT include markdown formatting.
Use ONLY standard ASCII double quotes (").
Remove duplicates.
Only include specific_topics that explicitly appear in the text.
If a broad category appears directly in the text, place it in general_topics.
general_topics may be inferred from the specific_topics, but do not invent unrelated categories.
Do not return random strings, malformed items, or generic filler words as topics.
Use standard topic naming and capitalization in the output.

Examples:
bfs → BFS
dfs → DFS
quicksort → Quicksort
merge sort → Merge Sort

If a topic appears in both specific_topics and general_topics,
keep it only in general_topics.

Output format

{{
  "specific_topics": ["string"],
  "general_topics": ["string"]
}}

Example

Input:
We studied BFS, DFS and Dijkstra's shortest path algorithm.

Output:
{{
  "specific_topics": ["BFS", "DFS", "Dijkstra"],
  "general_topics": ["Graph Algorithms"]
}}

Text:
”””
{raw_text}

# raw_text is inserted here dynamically
# This is the user input that the model must analyze
# Example:
# "Today we studied BFS and DFS"

Return ONLY the JSON object.
"""