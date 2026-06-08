import os
import json
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
from rag.vectorstore import load_vectorstore, retrieve_relevant_documents, format_retrieved_context

load_dotenv()
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

def generate_quiz(topic, user_id, num_questions=5):
    """Generate MCQs from uploaded documents."""

    db = load_vectorstore(user_id)
    context = ""

    if db:
        docs = retrieve_relevant_documents(db, topic, k=6)
        context = format_retrieved_context(docs)

    if not context:
        raise ValueError("No relevant uploaded notes found for this topic. Upload notes or try a topic from your documents.")

    prompt = f"""
You are a quiz generator for students.

Topic: {topic}
Context from student's notes:
{context}

Generate {num_questions} multiple choice questions.
Use only the provided context. Do not add facts that are not in the notes.

Return ONLY a JSON array in this exact format:
[
  {{
    "question": "What is...?",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "A",
    "explanation": "Because..."
  }}
]

No extra text. Only the JSON array.
"""

    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )

    raw = response.choices[0].message.content.strip()

    # Clean JSON
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    questions = json.loads(raw)
    return questions
