from tools.topic_extractor import extract_topics

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