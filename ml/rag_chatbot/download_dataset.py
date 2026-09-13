from datasets import load_dataset

# Hugging Face se dataset load karo
dataset = load_dataset("KisanVaani/agriculture-qa-english-only")

# Pandas DataFrame me convert karo
df = dataset["train"].to_pandas()

print(f"Total rows: {len(df)}")
print(df.head())

# CSV me save karo
df.to_csv("data/agriculture_qa_raw.csv", index=False)
print("Saved: data/agriculture_qa_raw.csv")