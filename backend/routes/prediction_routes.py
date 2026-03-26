from flask import Blueprint, request, jsonify
import os
import joblib
import pandas as pd

prediction_bp = Blueprint("prediction", __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MODEL_PATH = os.path.join(BASE_DIR, "model", "best_pcod_model.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "model", "model_features.pkl")

# Load model and features
model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURES_PATH)


def risk_from_probability(probability):
    if probability >= 70:
        return "High Risk of PCOD"
    elif probability >= 40:
        return "Moderate Risk of PCOD"
    return "Low Risk of PCOD"


@prediction_bp.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json() or request.form

        form_data = {
            "age": float(data.get("age", 0)),
            "bmi": float(data.get("bmi", 0)),
            "cycle_regular": int(data.get("cycle_regular", 0)),
            "cycle_length_days": float(data.get("cycle_length_days", 0)),
            "weight_gain": int(data.get("weight_gain", 0)),
            "hair_growth": int(data.get("hair_growth", 0)),
            "skin_darkening": int(data.get("skin_darkening", 0)),
            "hair_loss": int(data.get("hair_loss", 0)),
            "acne": int(data.get("acne", 0)),
            "fast_food": int(data.get("fast_food", 0)),
            "exercise": int(data.get("exercise", 0)),
        }

        input_df = pd.DataFrame([
            {feature: form_data.get(feature, 0) for feature in model_features}
        ])

        prediction = int(model.predict(input_df)[0])
        probability = float(model.predict_proba(input_df)[0][1]) * 100

        return jsonify({
            "success": True,
            "prediction": prediction,
            "probability": round(probability, 2),
            "risk": risk_from_probability(probability)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500