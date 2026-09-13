import os
import joblib
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH = os.path.join(MODEL_DIR, "crop_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.pkl")


# =========================================================
# LOAD MODEL, ENCODER, METADATA (once, at import time)
# =========================================================

MODEL = joblib.load(MODEL_PATH)
LABEL_ENCODER = joblib.load(ENCODER_PATH)
METADATA = joblib.load(METADATA_PATH)

FEATURES = METADATA["features"]  # ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


# =========================================================
# PREDICT
# =========================================================

def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    """
    Takes soil/climate values and returns the recommended crop name,
    plus the top 3 most likely crops with confidence scores.
    """

    input_df = pd.DataFrame(
        [[N, P, K, temperature, humidity, ph, rainfall]],
        columns=FEATURES
    )

    encoded_prediction = MODEL.predict(input_df)[0]

    crop_name = LABEL_ENCODER.inverse_transform([encoded_prediction])[0]

    top_crops = []

    if hasattr(MODEL, "predict_proba"):

        probabilities = MODEL.predict_proba(input_df)[0]

        top_indices = probabilities.argsort()[::-1][:3]

        for index in top_indices:
            top_crops.append({
                "crop": LABEL_ENCODER.inverse_transform([index])[0],
                "confidence": round(float(probabilities[index]) * 100, 2)
            })

    return {
        "recommended_crop": crop_name,
        "top_predictions": top_crops
    }


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print("\n======================================")
    print(" AgroWise - Crop Recommendation")
    print("======================================")

    N = float(input("Nitrogen (N): "))
    P = float(input("Phosphorus (P): "))
    K = float(input("Potassium (K): "))
    temperature = float(input("Temperature (°C): "))
    humidity = float(input("Humidity (%): "))
    ph = float(input("Soil pH: "))
    rainfall = float(input("Rainfall (mm): "))

    result = predict_crop(N, P, K, temperature, humidity, ph, rainfall)

    print("\n--------------------------------------")
    print("Recommended Crop:", result["recommended_crop"])
    print("\nTop 3 Predictions:")

    for item in result["top_predictions"]:
        print(f"{item['crop']} : {item['confidence']}%")
