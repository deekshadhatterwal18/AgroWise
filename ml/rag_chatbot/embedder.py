import pandas as pd
import json
from sentence_transformers import SentenceTransformer

# Model sirf ek baar load hota hai - ye 384-dimension embeddings deta hai
# Isse deployment ke time bhi yahi model load hoga (server start pe ek baar)
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.")


def embed_texts(texts: list) -> list:
    """
    Ek list of texts leke unke embeddings return karta hai.
    Model internally batching handle karta hai, isliye hume
    manual batch loop banane ki zarurat nahi (jo API ke saath karni padti thi).
    """
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    return embeddings.tolist()


if __name__ == "__main__":
    df = pd.read_csv("data/chunks.csv")

    print(f"Generating embeddings for {len(df)} chunks (local model)...")
    embeddings = embed_texts(df["content"].tolist())

    df["embedding"] = [json.dumps(e) for e in embeddings]

    df.to_csv("data/chunks_with_embeddings.csv", index=False)
    print(f"\nDone. Saved: data/chunks_with_embeddings.csv")
    print(f"Embedding dimension: {len(embeddings[0])}")
