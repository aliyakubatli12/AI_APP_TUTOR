from tools.topic_extractor import extract_topics


# Pipeline entry function
# Takes raw input text and returns extracted topics
# Output format:
# {
#   "specific_topics": [...],
#   "general_topics": [...]
# }
def run_pipeline(raw_text: str) -> dict[str, list[str]]:
    return extract_topics(raw_text)


# This block runs only when the file is executed directly
# (not when imported as a module)
if __name__ == "__main__":

    # Example input text containing general CS topics
    raw_text = """
    Algorithm Analysis
    Data Structures
    Sorting Algorithms
    Searching Algorithms
    Graph Algorithms
    Trees
    Hashing
    Recursion
    Divide and Conquer
    Greedy Algorithms
    Dynamic Programming
    Backtracking
    """

    # Run the topic extraction pipeline
    result = run_pipeline(raw_text)

    # Print the extracted topics
    print(result)