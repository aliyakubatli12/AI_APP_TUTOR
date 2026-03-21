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
You extract computer science topics from educational text.

From the input text, identify:
1. specific_topics → algorithms, techniques, or concrete CS concepts explicitly mentioned
2. general_topics → broader categories those topics belong to

Rules
Return ONLY valid JSON using double quotes (").
Remove duplicates.
Include a topic in specific_topics only if it appears explicitly in the text.
If a broad category appears directly in the text, include it in general_topics.
general_topics may be inferred from specific_topics if the relation is obvious.
If a topic appears in both lists, keep it only in general_topics.

Output format

{{
"specific_topics": ["string"],
"general_topics": ["string"]
}}

Example 1

Input:
We studied BFS, DFS and Dijkstra's shortest path algorithm.

Output:
{{
"specific_topics": ["BFS", "DFS", "Dijkstra"],
"general_topics": ["Graph Algorithms"]
}}

Example 2

Input:
This lecture covered quicksort and merge sort.

Output:
{{
"specific_topics": ["Quicksort", "Merge Sort"],
"general_topics": ["Sorting Algorithms"]
}}

Example 3

Input:
We implemented binary search in today's class.

Output:
{{
"specific_topics": ["Binary Search"],
"general_topics": ["Searching Algorithms"]
}}

Example 4

Input:
Today we discussed red-black trees and hash tables.

Output:
{{
"specific_topics": ["Red-Black Tree", "Hash Table"],
"general_topics": ["Trees", "Hashing", "Data Structures"]
}}

Example 5

Input:
The lecture introduced dynamic programming and backtracking techniques.

Output:
{{
"specific_topics": ["Dynamic Programming", "Backtracking"],
"general_topics": []
}}

Text:

{raw_text} 


Return ONLY the JSON object.
"""