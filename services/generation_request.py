VALID_DIFFICULTIES = {"easy", "medium", "hard"}

def build_generation_request(result, selected_specific_topic, difficulty):
    if selected_specific_topic not in result["specific_topics"]:
        raise ValueError(f"Invalid topic: {selected_specific_topic}")

    difficulty = difficulty.lower()
    if difficulty not in VALID_DIFFICULTIES:
        raise ValueError(f"Invalid difficulty: {difficulty}")

    general_topics = result.get("general_topics", [])
    if not general_topics:
        raise ValueError("No general topic found")

    return {
        "general_topic": general_topics[0],   # MVP: ilkini al
        "specific_topic": selected_specific_topic,
        "difficulty": difficulty,
        "question_count": 3
    }

if __name__ == "__main__":
    result = {
        "specific_topics": ["Kruskal", "Fibonacci"],
        "general_topics": ["Dynamic Programming"]
    }

    request = build_generation_request(result, "Kruskal", "Easy")
    print(request) 