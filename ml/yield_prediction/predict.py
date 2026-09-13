import os
import joblib
import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH = os.path.join(MODEL_DIR, "yield_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "yield_preprocessor.pkl")
METADATA_PATH = os.path.join(MODEL_DIR, "yield_model_metadata.pkl")


# =========================================================
# LOAD MODEL, PREPROCESSOR, METADATA (once, at import time)
# =========================================================

MODEL = joblib.load(MODEL_PATH)
PREPROCESSOR = joblib.load(PREPROCESSOR_PATH)
METADATA = joblib.load(METADATA_PATH)

FEATURES = METADATA["features"]
# ["Crop", "Season", "State", "Area", "Annual_Rainfall",
#  "Fertilizer", "Pesticide", "Avg_Temperature", "Max_Temperature", "Min_Temperature"]


# =========================================================
# DROPDOWN OPTIONS (Crop / Season / State)
# For the frontend form's <select> options
# =========================================================

def get_dropdown_options():
    """
    Returns valid Crop, Season, State values that the
    trained OneHotEncoder recognizes -- use these to
    populate <select> dropdowns on the yield prediction page.
    """

    categorical_transformer = None

    for name, transformer, columns in PREPROCESSOR.transformers_:
        if name == "categorical":
            categorical_transformer = transformer
            break

    if categorical_transformer is None:
        return {"crops": [], "seasons": [], "states": []}

    crops, seasons, states = categorical_transformer.categories_

    return {
        "crops": sorted(crops.tolist()),
        "seasons": sorted(seasons.tolist()),
        "states": sorted(states.tolist())
    }


# =========================================================
# PREDICT
# =========================================================

def predict_yield(data: dict):
    """
    data must contain: Crop, Season, State, Area, Annual_Rainfall,
    Fertilizer, Pesticide, Avg_Temperature, Max_Temperature, Min_Temperature
    """

    input_df = pd.DataFrame([{
        "Crop": data.get("Crop"),
        "Season": data.get("Season"),
        "State": data.get("State"),
        "Area": float(data.get("Area")),
        "Annual_Rainfall": float(data.get("Annual_Rainfall")),
        "Fertilizer": float(data.get("Fertilizer")),
        "Pesticide": float(data.get("Pesticide")),
        "Avg_Temperature": float(data.get("Avg_Temperature")),
        "Max_Temperature": float(data.get("Max_Temperature")),
        "Min_Temperature": float(data.get("Min_Temperature")),
    }])

    input_processed = PREPROCESSOR.transform(input_df)

    prediction = MODEL.predict(input_processed)[0]

    return round(float(prediction), 2)


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print("\n======================================")
    print(" AgroWise - Yield Prediction")
    print("======================================")

    options = get_dropdown_options()
    print("\nAvailable crops:", options["crops"][:10], "...")
    print("Available seasons:", options["seasons"])
    print("Available states:", options["states"][:10], "...")

    sample_input = {
        "Crop": options["crops"][0],
        "Season": options["seasons"][0],
        "State": options["states"][0],
        "Area": 1000,
        "Annual_Rainfall": 1200,
        "Fertilizer": 5000,
        "Pesticide": 50,
        "Avg_Temperature": 27,
        "Max_Temperature": 35,
        "Min_Temperature": 20
    }

    result = predict_yield(sample_input)

    print("\nSample input:", sample_input)
    print("Predicted Yield:", result)
