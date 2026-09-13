import json
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "model" / "mobilenetv2_plant.pth"
DISEASE_INFO_PATH = BASE_DIR / "disease_info.json"


# =========================================================
# SETTINGS
# =========================================================

NUM_CLASSES = 38
CONFIDENCE_THRESHOLD = 70.0


# =========================================================
# CLASS NAMES
# =========================================================

CLASS_NAMES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",

    "Blueberry___healthy",

    "Cherry___Powdery_mildew",
    "Cherry___healthy",

    "Corn___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn___Common_rust",
    "Corn___Northern_Leaf_Blight",
    "Corn___healthy",

    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",

    "Orange___Haunglongbing_(Citrus_greening)",

    "Peach___Bacterial_spot",
    "Peach___healthy",

    "Pepper___Bacterial_spot",
    "Pepper___healthy",

    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",

    "Raspberry___healthy",

    "Soybean___healthy",

    "Squash___Powdery_mildew",

    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",

    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]


# =========================================================
# DEVICE
# =========================================================

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")

elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
    DEVICE = torch.device("mps")

else:
    DEVICE = torch.device("cpu")


# =========================================================
# LOAD MODEL
# =========================================================

def load_model():

    model = models.mobilenet_v2(weights=None)

    model.classifier[1] = nn.Sequential(
        nn.Dropout(0.2),
        nn.Linear(
            model.classifier[1].in_features,
            NUM_CLASSES
        )
    )

    state_dict = torch.load(
        MODEL_PATH,
        map_location=DEVICE
    )

    model.load_state_dict(state_dict)

    model.to(DEVICE)
    model.eval()

    return model


MODEL = load_model()


# =========================================================
# IMAGE TRANSFORM
# =========================================================

TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# =========================================================
# DISEASE INFORMATION
# =========================================================

def get_disease_info(disease_name):

    try:

        with open(
            DISEASE_INFO_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            disease_info = json.load(file)

        return disease_info.get(
            disease_name,
            {
                "cause": "Information not available.",
                "symptoms": "Information not available.",
                "treatment": [],
                "prevention": []
            }
        )

    except Exception as e:

        print("Disease info error:", repr(e))

        return {
            "cause": "Information not available.",
            "symptoms": "Information not available.",
            "treatment": [],
            "prevention": []
        }


# =========================================================
# FORMAT CLASS NAME
# =========================================================

def format_prediction(class_name):

    parts = class_name.split("___", 1)

    if len(parts) == 2:

        crop = parts[0]
        disease = parts[1]

    else:

        crop = "Unknown"
        disease = class_name

    disease = disease.replace("_", " ")

    return crop, disease


# =========================================================
# PREDICT
# =========================================================

def predict(image_path):

    image = Image.open(image_path).convert("RGB")

    image_tensor = TRANSFORM(image)

    image_tensor = image_tensor.unsqueeze(0)

    image_tensor = image_tensor.to(DEVICE)

    with torch.no_grad():

        output = MODEL(image_tensor)

        probabilities = torch.softmax(
            output,
            dim=1
        )

    # Top 3
    top_probabilities, top_indices = torch.topk(
        probabilities,
        3,
        dim=1
    )

    top_probabilities = top_probabilities[0].cpu().tolist()
    top_indices = top_indices[0].cpu().tolist()

    predictions = []

    for probability, index in zip(
        top_probabilities,
        top_indices
    ):

        class_name = CLASS_NAMES[index]

        crop, disease = format_prediction(
            class_name
        )

        confidence = probability * 100

        predictions.append({
            "class_name": class_name,
            "crop": crop,
            "disease": disease,
            "confidence": round(confidence, 2)
        })

    # Best prediction
    best = predictions[0]

    crop = best["crop"]
    disease = best["disease"]
    confidence = best["confidence"]

    # Low confidence
    if confidence < CONFIDENCE_THRESHOLD:

        return {
            "success": True,
            "reliable": False,
            "healthy": False,
            "crop": crop,
            "disease": disease,
            "confidence": confidence,
            "message": (
                "Unable to identify the disease reliably. "
                "Please upload a clear leaf image."
            ),
            "cause": "",
            "symptoms": "",
            "treatment": [],
            "prevention": [],
            "top_predictions": predictions
        }

    # Healthy
    if best["class_name"].endswith("___healthy"):

        return {
            "success": True,
            "reliable": True,
            "healthy": True,
            "crop": crop,
            "disease": "Healthy",
            "confidence": confidence,
            "message": "No major disease detected.",
            "cause": "No disease detected.",
            "symptoms": "No major disease symptoms detected.",
            "treatment": [],
            "prevention": [],
            "top_predictions": predictions
        }

    # Disease
    info = get_disease_info(
        best["class_name"]
    )

    return {
        "success": True,
        "reliable": True,
        "healthy": False,
        "crop": crop,
        "disease": disease,
        "confidence": confidence,
        "message": "Possible disease detected.",
        "cause": info.get(
            "cause",
            "Information not available."
        ),
        "symptoms": info.get(
            "symptoms",
            "Information not available."
        ),
        "treatment": info.get(
            "treatment",
            []
        ),
        "prevention": info.get(
            "prevention",
            []
        ),
        "top_predictions": predictions
    }


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print("\n======================================")
    print(" AgroWise - Plant Disease Detection")
    print("======================================")

    print("Device:", DEVICE)

    image_path = input(
        "\nEnter image path: "
    ).strip()

    try:

        result = predict(image_path)

        print("\n--------------------------------------")
        print("RESULT")
        print("--------------------------------------")

        print("Crop       :", result["crop"])
        print("Disease    :", result["disease"])
        print("Confidence :", result["confidence"], "%")
        print("Message    :", result["message"])

        print("\nTop 3 Predictions:")

        for item in result["top_predictions"]:

            print(
                f"{item['crop']} - "
                f"{item['disease']} : "
                f"{item['confidence']}%"
            )

    except Exception as e:

        print("\nPrediction Error:")
        print(repr(e))