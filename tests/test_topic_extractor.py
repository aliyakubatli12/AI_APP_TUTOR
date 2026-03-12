from tools.topic_extractor import extract_topics

"""
Runs multiple test inputs through the topic extraction pipeline.

Each string simulates a possible user input and the script prints:
- the test number
- the raw input
- the extracted specific and general topics
"""


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
    
]


print("TOTAL TESTS:", len(tests))

for i, raw_text in enumerate(tests, 1):

    print(f"\n--- TEST {i} ---")
    print("TYPE:", type(raw_text))
    print("INPUT REPR:", repr(raw_text))

    try:
        result = extract_topics(raw_text)
        print("RESULT:", result)

    except Exception as e:
        print("ERROR:", e)