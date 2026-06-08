import os
import json
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
from rag.vectorstore import load_vectorstore, retrieve_relevant_documents, format_retrieved_context

load_dotenv()
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

def generate_flashcards(topic, user_id, num_cards=10):
    """Generate flashcards from uploaded documents."""

    db = load_vectorstore(user_id)
    context = ""

    if db:
        docs = retrieve_relevant_documents(db, topic, k=6)
        context = format_retrieved_context(docs)

    if not context:
        raise ValueError("No relevant uploaded notes found for this topic. Upload notes or try a topic from your documents.")

    prompt = f"""
You are a flashcard generator for students.

Topic: {topic}
Context from student's notes:
{context}

Generate {num_cards} flashcards for memorization.
Use only the provided context. Do not add facts that are not in the notes.

Return ONLY a JSON array in this exact format:
[
  {{
    "front": "What is TCP?",
    "back": "Transmission Control Protocol. A connection-oriented protocol that ensures reliable data delivery."
  }}
]

No extra text. Only the JSON array.
"""

    response = client.chat.completions.create(
        model="gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    raw = response.choices[0].message.content.strip()

    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    cards = json.loads(raw)
    return cards
