from tools.topic_extractor import extract_topics


def run_pipeline(raw_text: str) -> dict[str, list[str]]:
    return extract_topics(raw_text)


if __name__ == "__main__":
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

    

    result = run_pipeline(raw_text)
    print(result)