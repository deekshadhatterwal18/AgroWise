import pandas as pd


def create_chunks(filepath: str) -> pd.DataFrame:
    """
    processed_qa.csv se data leta hai aur har QA pair ko
    ek 'chunk' banata hai - jisme question + answer combine
    ho jaate hain ek single text block me.

    Isse RAG retrieval better hota hai kyunki jab user question
    poochega, to poora context (Q+A dono) match hoga, sirf answer nahi.
    """
    df = pd.read_csv(filepath)

    # Har row ka ek unique chunk_id banate hain
    df["chunk_id"] = [f"chunk_{i}" for i in range(len(df))]

    # Question + Answer ko ek "content" text me jodte hain
    # Ye wahi text hai jiska embedding banega
    df["content"] = "Question: " + df["question"] + "\nAnswer: " + df["answers"]

    print(f"Total chunks created: {len(df)}")
    print("\nSample chunk:")
    print(df["content"].iloc[0])

    return df


if __name__ == "__main__":
    df = create_chunks("data/processed_qa.csv")
    df.to_csv("data/chunks.csv", index=False)
    print("\nSaved: data/chunks.csv")
