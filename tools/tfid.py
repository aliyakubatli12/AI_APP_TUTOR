from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Union
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "topics"))

from Category_canoncials import CATEGORY_CANONICALS as category_canon  # noqa: E402




def best_tfidf_match(query: str, candidates: list[str]) -> dict[str, Union[str, float]]:
    texts = candidates + [query]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(texts)

    candidate_matrix = matrix[:-1]
    query_vector = matrix[-1]

    sims = cosine_similarity(query_vector, candidate_matrix).flatten()
    best_idx = sims.argmax()

    return {
        "best_match": candidates[best_idx],
        "score": float(sims[best_idx]),
    }

if __name__ == "__main__":
    query = "minimum spanning tree dijkstra"
    candidates = category_canon["Graph Algorithms"]

    result = best_tfidf_match(query, candidates)
    print(result)