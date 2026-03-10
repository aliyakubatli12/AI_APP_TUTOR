from tools.topic_extractor import extract_topics

# Test cases used to evaluate the topic extraction system
# Each string simulates a possible user input

tests = [

    "BFS\nDFS\nDynamic Programming",
    "Dijkstra",
    "Today we studied BFS, DFS, and Dijkstra's algorithm",
    "In this course we explore sorting algorithms like quicksort and mergesort",
    "abc\ndef\nghi",
    "Dynamic Programming",
    "BFS - Breadth First Search\nDFS - Depth First Search",
    "bfs, dfs, dijkstra",
    ",,, /// |||",
    "Algorithms and Data Structures are fundamental topics",
    "Quicksort\nMergesort\nHeapsort",
    "Dijkstra; Bellman-Ford; Floyd-Warshall",
    "Stack\nQueue\nLinked List",
    "Graph Algorithms",
    "BFS\nToday we studied DFS",
    "BFS, DFS and Dijkstra",
    "topics: BFS, DFS, Dijkstra",
    "I like BFS, but DFS is also useful",
    "We covered dynamic programming, greedy algorithms, and graph traversal",
    "Sorting\nSearching\nGraph Algorithms",
    "A*\nDijkstra\nBellman-Ford",
    "Binary Search Tree\nAVL Tree\nRed Black Tree",
    "Machine Learning\nDeep Learning\nReinforcement Learning",
    "This week we studied stacks, queues, and heaps"
]

# Print total number of test inputs
print("TOTAL TESTS:", len(tests))

# Iterate through all test cases
for i, raw_text in enumerate(tests, 1):

    # Show which test is running
    print(f"\n--- TEST {i} ---")

    # Show type of the input (should normally be str)
    print("TYPE:", type(raw_text))

    # Show the exact representation of the string
    # Useful for debugging newline characters (\n)
    print("INPUT REPR:", repr(raw_text))

    try:
        # Call the topic extraction pipeline
        result = extract_topics(raw_text)

        # Print extracted topics
        print("RESULT:", result)

    except Exception as e:
        # If an error occurs, print the error message
        print("ERROR:", e)