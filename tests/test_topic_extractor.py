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
    "Bubble Sort; Quick Sort; Merge Sort",
    "Binary Search | Linear Search | Jump Search",
    "Stack / Queue / Linked List",
    "BFS\nMerge Sort; Dijkstra | Prime Check",
    "Today we studied BFS and DFS in class",
    "We covered sorting algorithms and discussed their complexity",
    "I learned about dynamic programming and it was hard",
    "He is studying graph algorithms these days",
    "The team was working on search algorithms yesterday",
    "Bubble Sort",
    "",
    "123\n456\n789",
    "BFS\nDFS",
    "We studied Bubble Sort\nQuick Sort\nMerge Sort\nDijkstra",
    "Today we studied the fundamentals of graph theory\nBFS\nDFS",
    "Breadth First Search Algorithm\nDepth First Search Algorithm\nBubble Sort",
    "BFS\nDFS\nDijkstra\nBellman Ford\nA Star\nFloyd Warshall\nPrim\nKruskal",


    
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