import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from .retriever import retrieve_context

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = Groq(api_key=os.environ["GROQ_API_KEY"])


def build_prompt(query: str, context_chunks: list) -> str:
    """
    Retrieved chunks ko ek clean prompt me format karta hai
    jo LLM ko diya jayega. Ye "prompt engineering" ka core part hai.
    """
    if not context_chunks:
        context_text = "No relevant context found."
    else:
        context_text = "\n\n".join([
            f"Q: {c['question']}\nA: {c['answer']}"
            for c in context_chunks
        ])

    prompt = f"""You are groWise, a helpful agriculture assistant for Indian farmers.
Use the context below as your primary source of information.
If the context does not exactly match the question but has related or
partially useful information, use it to give the best practical advice you can.
Only say you don't have enough information if the context is completely unrelated
to the question.

Formatting rules (very important):
- Keep the answer short and to the point - only include information relevant to the question.
- Do NOT use markdown tables.
- Use simple bullet points (starting with "-") for lists of tips or steps.
- Use **bold** only for key terms, not entire sentences.
- Avoid long introductions - get straight to the practical advice.

Context:
{context_text}

Farmer's Question: {query}

Answer:"""

    return prompt


def generate_answer(query: str, top_k: int = 8) -> dict:
    """
    Poora RAG flow: retrieve -> prompt build -> LLM se answer generate
    """
    context_chunks = retrieve_context(query, top_k=top_k)
    prompt = build_prompt(query, context_chunks)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",  # Groq ka fast, free model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # kam temperature = zyada factual, kam creative
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": [c["topic"] for c in context_chunks],
        "num_chunks_used": len(context_chunks)
    }


if __name__ == "__main__":
    test_query = "how to control pests in tomato plants"

    result = generate_answer(test_query)

    print(f"\nQuery: {test_query}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources used (topics): {result['sources']}")
