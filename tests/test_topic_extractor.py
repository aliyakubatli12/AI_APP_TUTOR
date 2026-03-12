from tools.topic_extractor import extract_topics

"""
Runs multiple test inputs through the topic extraction pipeline.

Each string simulates a possible user input and the script prints:
- the test number
- the raw input
- the extracted specific and general topics
"""


tests = [

    
    "Graph Algorithms\nSorting Algorithms\nDynamic Programming",
    "Breadth First Search\nDepth First Search\nDijkstra Algorithm",
    "Bubble Sort\nQuick Sort\nMerge Sort\nSorting Algorithms",
    "Binary Search\nSearch Algorithms\nLinear Search",
    "Data Structures\nStack\nQueue\nLinked List",
    "Knapsack\nKnapsack Problems\nGreedy Knapsack",
    "Machine Learning\nLinear Regression\nLogistic Regression",
    "Neural Networks\nBack Propagation Neural Network\nConvolution Neural Network",
    "Graph Algorithms\nDijkstra\nBellman Ford\nA Star",
    "Sorting Algorithms\nBubble Sort",
    "Hash Table\nHash Map\nHashing Algorithms",
    "Dynamic Programming\nFibonacci\nKnapsack",
    "String Algorithms\nKnuth Morris Pratt\nRabin Karp",
    "Mathematics\nPrime Check\nGreatest Common Divisor",
    "Search Algorithms\nBinary Search\nJump Search",
    "Cipher Algorithms\nCaesar Cipher\nVigenere Cipher",
    "Data Structures\nAvl Tree\nRed Black Tree\nBinary Search Tree",
    "Greedy Algorithms\nFractional Knapsack\nGas Station",
    "Backtracking Algorithms\nN Queens\nSudoku\nHamiltonian Cycle",
    "Matrix Algorithms\nRotate Matrix\nSpiral Print",

    
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