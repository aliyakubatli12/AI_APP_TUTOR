from prompts.reviewer import question_reviewer


# good_response = """
# {
#   "questions": [
#     {
#       "title": "BST Search Path",
#       "question_text": "In a binary search tree with root 8, left child 3, and right child 10, explain how the search proceeds when looking for value 10."
#     },
#     {
#       "title": "BST Insertion Rule",
#       "question_text": "A binary search tree has root 5, left child 2, and right child 9. Where would value 7 be inserted?"
#     },
#     {
#       "title": "BST Traversal Reasoning",
#       "question_text": "Given a binary search tree with root 6, left subtree containing 2 and 4, and right subtree containing 8 and 9, what sequence is produced by an in-order traversal?"
#     }
#   ]
# }
# """
# bad_json_response = """
# {
#   "questions": [
#     {
#       "title": "Tree Traversal",
#       "question_text": "Consider this tree: \n 4 \n / \ \n 2 6"
#     }
#   ]
# }
# """

# print(question_reviewer(bad_json_response, "Binary Search Trees", "hard"))

off_topic_response = """
{
  "questions": [
    {
      "title": "Merge Sort Split Step",
      "question_text": "Explain how merge sort recursively divides an array into smaller parts."
    }
  ]
}
"""

print(question_reviewer(off_topic_response, "Binary Search Trees", "medium"))


# print(question_reviewer(good_response, "Binary Search Trees", "medium"))