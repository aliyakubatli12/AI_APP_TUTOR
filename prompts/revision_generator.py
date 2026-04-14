def build_revision_prompt(req, review):
    issues_text = "\n".join(f"- {issue}" for issue in review.get("issues", []))

    return f"""
The previous output was not accepted by the reviewer.

You must generate a corrected new version of the questions.

Reviewer feedback:
{issues_text}

Important revision rules:
- Fix all listed issues.
- Do not repeat the same mistakes.
- Keep the same topic.
- Keep the same general area.
- Keep the same difficulty level.
- Stay within the same algorithm or concept.
- Return only JSON in the required format.

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
{
  "questions": [
    {{
      "title": "...",
      "question_text": "..."
    }}
  ]
}

Output Requirements:
- Return strictly valid JSON only.
- Do not include any text before or after the JSON.
- Do not use markdown code blocks (no ```).
- Do not include trailing commas.
- All strings must be valid JSON strings.
- Do not use raw line breaks inside "question_text".
- If a line break is necessary, use \\n instead.
- Prefer describing graphs in sentence form instead of ASCII diagrams.
- Ensure the output can be parsed with json.loads() without errors.
- If unsure, prioritize valid JSON over formatting.
""".strip()