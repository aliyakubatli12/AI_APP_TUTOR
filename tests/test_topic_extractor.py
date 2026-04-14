from tools.topic_extractor.topic_extractor import extract_topics

"""
Runs multiple test inputs through the topic extraction pipeline.

Each string simulates a possible user input and the script prints:
- the test number
- the raw input
- the extracted specific and general topics
"""


tests = [


"BFS\nQuick Sort\nLinear Regression",
"dfs; bubble sort; knn",
"Bugün BFS ve Dijkstra çalıştım",
"Today I studied bfs, dfs and kmp algorithm",
"We covered sorting: bubble sort, merge sort, quick sort",
"rsa | morse | caesar cipher",
"Stack\nQueue By List\nCircular Queue",
"pca\nsvm\nrelu\nlstm",
"Minimum Spanning Tree\nKruskal\nPrim",
"I learned dynamic programming today, specifically knapsack and fibonacci",
"binary search | bst | avl tree",
"Graph algorithms: dijkstra, bellman ford, a*",
"n queens; sudoku; word search",
"matrix multiplication\nrotate matrix\nspiral print",
"We studied neural networks, cnn and backpropagation",



    
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