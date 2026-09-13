import os

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from xgboost import XGBClassifier


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "Crop_recommendation.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# Load dataset
df = pd.read_csv(DATASET_PATH)

print("=" * 50)
print("DATASET INFORMATION")
print("=" * 50)

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())


# Select features
features = [
    "N",
    "P",
    "K",
    "temperature",
    "humidity",
    "ph",
    "rainfall"
]

X = df[features]
y = df["label"]


# Encode crop labels
label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

print("\nNumber of crops:", len(label_encoder.classes_))

print("\nCrop classes:")
print(label_encoder.classes_)


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# Random Forest
rf_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

rf_predictions = rf_model.predict(X_test)

rf_accuracy = accuracy_score(
    y_test,
    rf_predictions
)

print("\n" + "=" * 50)
print("RANDOM FOREST")
print("=" * 50)

print(f"Accuracy: {rf_accuracy * 100:.2f}%")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        rf_predictions,
        target_names=label_encoder.classes_
    )
)


# XGBoost
xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)

xgb_model.fit(X_train, y_train)

xgb_predictions = xgb_model.predict(X_test)

xgb_accuracy = accuracy_score(
    y_test,
    xgb_predictions
)

print("\n" + "=" * 50)
print("XGBOOST")
print("=" * 50)

print(f"Accuracy: {xgb_accuracy * 100:.2f}%")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        xgb_predictions,
        target_names=label_encoder.classes_
    )
)


# Select best model
if rf_accuracy >= xgb_accuracy:

    best_model = rf_model
    best_model_name = "Random Forest"
    best_accuracy = rf_accuracy

else:

    best_model = xgb_model
    best_model_name = "XGBoost"
    best_accuracy = xgb_accuracy


# Save best model
model_path = os.path.join(
    MODEL_DIR,
    "crop_model.pkl"
)

joblib.dump(
    best_model,
    model_path
)


# Save label encoder
encoder_path = os.path.join(
    MODEL_DIR,
    "label_encoder.pkl"
)

joblib.dump(
    label_encoder,
    encoder_path
)


# Save model metadata
metadata = {
    "features": features,
    "model_name": best_model_name,
    "accuracy": best_accuracy
}

metadata_path = os.path.join(
    MODEL_DIR,
    "model_metadata.pkl"
)

joblib.dump(
    metadata,
    metadata_path
)


print("\n" + "=" * 50)
print("FINAL MODEL")
print("=" * 50)

print("Selected model:", best_model_name)
print(f"Test accuracy: {best_accuracy * 100:.2f}%")

print("\nSaved files:")
print(model_path)
print(encoder_path)
print(metadata_path)