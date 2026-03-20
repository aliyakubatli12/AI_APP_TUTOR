def generate_question_response(req):
    return f"""
You are an algorithm tutor.

Topic: {req['specific_topic']}
General Area: {req['general_topic']}
Difficulty: {req['difficulty']}

Generate {req['question_count']} practice questions.

Guidelines:
- Focus on problem-solving and reasoning rather than definition recall.
- Use small, concrete inputs that can be worked through step by step.
- Encourage intermediate reasoning and clear decision-making.
- Ensure all questions are logically correct and consistent with how the algorithm works.
- Stay strictly within the selected algorithm; do not introduce unrelated concepts or unnecessary tasks.
- Prefer concise, algorithm-focused questions; avoid unnecessary implementation details or programming-style formats.

Difficulty Guidelines:
- Easy:
  - Use small and simple inputs.
  - Require basic application of the algorithm (not just recall).
  - Include at least one meaningful decision (e.g., choosing between options or rejecting a step).
  - Avoid trivial questions that can be solved by a single obvious step.

- Medium:
  - Include multiple steps and decision points.
  - Require following the algorithm through several stages.
  - Combine execution with explanation when appropriate.

- Hard:
  - Include more complex or edge-case scenarios.
  - Require deeper reasoning and careful tracking of steps.
  - May include tricky but clearly stated situations (no hidden ambiguity).

Diversity Requirements:
- Maintain a balanced mix of question types:
  - full execution problems (end-to-end application),
  - step-based or partial questions (focused on specific decisions),
  - conceptual reasoning questions (explaining why a step is valid or invalid).
- The majority of questions should involve actual problem solving.
- Avoid generating questions that are structurally too similar to each other.

Style Guidance:
- Questions should be clear, precise, and unambiguous.
- Prefer practical scenarios over abstract definitions.
- Avoid unnecessary complexity unless explicitly required.



Return JSON in the following format:
{{
  "questions": [
    {{
      "title": "...",
      "question_text": "..."
    }}
  ]
}}
"""