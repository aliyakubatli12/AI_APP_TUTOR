import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from tests.test_generation import test_generation
from services.generation_request import build_generation_request
from tools.topic_extractor.topic_extractor import extract_topics




st.title("Algorithm Tutor MVP")

if "result" not in st.session_state:
    st.session_state.result = None

input_text = st.text_area("Paste your notes / content here", height=200)

if st.button("Extract Topics"):
    try:
        if not input_text.strip():
            st.warning("Please enter some text first.")
        else:
            result = extract_topics(input_text)
            st.session_state.result = result
    except Exception as e:
        st.error(f"Error while extracting topics: {e}")

if st.session_state.result:
    result = st.session_state.result

    st.write("General Area:", result["general_topics"][0])

    selected_topic = st.selectbox("Choose a topic", result["specific_topics"])
    difficulty = st.selectbox("Choose difficulty", ["easy", "medium", "hard"])

    if st.button("Generate Questions"):
        try:
            questions = test_generation(result, selected_topic, difficulty)

            st.write(
                "Request:",
                {
                    "general_topic": result["general_topics"][0],
                    "specific_topic": selected_topic,
                    "difficulty": difficulty,
                    "question_count": 3
                }
            )

            for i, q in enumerate(questions, start=1):
                st.subheader(q.get("title", f"Question {i}"))
                st.write(q.get("question_text", ""))

        except Exception as e:
            st.error(f"Error while generating questions: {e}")