import pandas as pd

# Har topic ke liye keywords - inse hum decide karenge ki
# ek QA pair kaunse topic me aata hai
TOPIC_KEYWORDS = {
    "crops": ["cultivation", "variety", "sowing", "harvest", "crop", "planting", "seed"],
    "disease": ["disease", "blight", "wilt", "spot", "rot", "fungus", "infection", "virus"],
    "pests": ["pest", "insect", "worm", "aphid", "infestation", "caterpillar", "bug"],
    "fertilizer": ["fertilizer", "npk", "urea", "nutrient", "manure", "compost", "nitrogen", "phosphorus", "potassium"],
    "irrigation": ["irrigation", "water", "drip", "sprinkler", "watering"],
    "soil": ["soil", "ph", "testing", "erosion", "loam", "clay"],
    "weather": ["weather", "rain", "season", "climate", "monsoon", "temperature", "humidity"],
    "schemes": ["pm kisan", "scheme", "subsidy", "loan", "kcc", "insurance", "government", "yojana"]
}


def load_and_clean(filepath: str) -> pd.DataFrame:
    """
    Raw dataset load karke clean karta hai
    """
    df = pd.read_csv(filepath)
    print(f"Raw rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")

    before = len(df)
    df = df.dropna()
    df = df.drop_duplicates()
    after = len(df)
    print(f"After cleaning: {after} rows ({before - after} removed)")

    return df


def tag_topic(question: str, answer: str) -> str:
    """
    Question + answer ke text me keywords dhundh ke topic assign karta hai.
    Agar koi keyword match nahi hota to 'general' tag lagta hai.
    """
    text = f"{question} {answer}".lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return topic

    return "general"


def add_topic_tags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Har row ko uska topic tag deta hai - ek naya column 'topic' banta hai
    """
    df["topic"] = df.apply(
        lambda row: tag_topic(row["question"], row["answers"]), axis=1
    )

    print("\nTopic distribution (before sampling):")
    print(df["topic"].value_counts())

    return df


def balanced_sample(df: pd.DataFrame, per_topic: int = 200) -> pd.DataFrame:
    """
    Har topic se max 'per_topic' rows leta hai, taaki koi bhi
    ek topic dataset pe hawi na ho jaaye (balanced representation).
    Agar kisi topic me kam rows hain to jitni hain utni le lega.
    """
    samples = []
    for topic, group in df.groupby("topic"):
        n = min(len(group), per_topic)
        samples.append(group.sample(n=n, random_state=42))

    balanced_df = pd.concat(samples).reset_index(drop=True)

    print("\nTopic distribution (after balanced sampling):")
    print(balanced_df["topic"].value_counts())
    print(f"\nTotal rows after balancing: {len(balanced_df)}")

    return balanced_df


if __name__ == "__main__":
    # Step 1: Load + clean
    df = load_and_clean("data/agriculture_qa_raw.csv")

    # Step 2: Topic tagging
    df = add_topic_tags(df)

    # Step 3: Balanced sampling - har topic se ~200 rows (max ~1600 total)
    final_df = balanced_sample(df, per_topic=200)

    # Step 4: Save
    final_df.to_csv("data/processed_qa.csv", index=False)
    print("\nSaved: data/processed_qa.csv")

    print("\nSample rows:")
    print(final_df[["topic", "question", "answers"]].head(5))
