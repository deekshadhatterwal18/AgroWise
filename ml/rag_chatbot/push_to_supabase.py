import pandas as pd
import json
import os
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

# .env file rag_chatbot se 2 folder upar (AgroWise root) me hai
# __file__ ka matlab hai "ye script khud kahan hai" - isse hum
# hamesha sahi path nikal lenge, chahe script kahin se bhi chalayi jaye
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)


def push_to_supabase(df: pd.DataFrame, batch_size: int = 50):
    """
    Har row ko Supabase 'documents' table me insert karta hai.
    Batch me insert karte hain taaki ek saath bahut saare
    requests na jaayein (rate limit + speed ke liye better).
    """
    total = len(df)
    inserted = 0

    for i in range(0, total, batch_size):
        batch = df.iloc[i:i + batch_size]

        records = []
        for _, row in batch.iterrows():
            records.append({
                "question": row["question"],
                "answer": row["answers"],
                "topic": row["topic"],
                "content": row["content"],
                "embedding": json.loads(row["embedding"])  # JSON string wapas list me
            })

        try:
            supabase.table("documents").insert(records).execute()
            inserted += len(records)
            print(f"Inserted {inserted}/{total} rows")
        except Exception as e:
            print(f"Error inserting batch starting at row {i}: {e}")

    print(f"\nDone. Total inserted: {inserted}")


if __name__ == "__main__":
    df = pd.read_csv("data/chunks_with_embeddings.csv")
    push_to_supabase(df, batch_size=50)
