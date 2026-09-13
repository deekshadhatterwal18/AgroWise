import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv

# .env root (AgroWise) me hai - 2 folder upar
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# IMPORTANT: yahi model use karo jo embedder.py me use kiya tha.
# Agar model mismatch hua to vectors compare hi nahi honge sahi se.
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.")


def retrieve_context(query: str, top_k: int = 8, threshold: float = 0.2) -> list:
    """
    User ke query ko embed karta hai, fir Supabase me
    'match_documents' function call karke sabse similar
    chunks nikaalta hai.

    top_k: kitne chunks chahiye
    threshold: kitni minimum similarity honi chahiye (0 to 1)
               kam rakhoge to zyada results aayenge (kam relevant bhi)
    """
    query_embedding = model.encode(query).tolist()

    response = supabase.rpc("match_documents", {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": top_k
    }).execute()

    return response.data


if __name__ == "__main__":
    # Test karne ke liye - koi bhi sample query try karo
    test_query = "how to control pests in tomato plants"

    print(f"\nQuery: {test_query}\n")
    results = retrieve_context(test_query, top_k=3)

    if not results:
        print("Koi relevant chunk nahi mila. Threshold kam karke try karo.")
    else:
        for i, r in enumerate(results, 1):
            print(f"--- Result {i} (similarity: {r['similarity']:.3f}, topic: {r['topic']}) ---")
            print(f"Q: {r['question']}")
            print(f"A: {r['answer']}\n")
