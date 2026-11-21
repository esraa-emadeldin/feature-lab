"""Use the saved model to predict for ONE new patient.

This is the part that runs "in production": it never trains anything,
it only loads model.joblib (made by `python -m src.train`) and predicts.
"""

from pathlib import Path

import joblib

from src import train
from src.train import MALIGNANT


class BadInput(ValueError):
    """The request is missing features or has unknown ones."""


def load_model(model_dir=None):
    """Load the saved {"model": pipeline, "info": {...}} bundle (from models/ by default)."""
    path = Path(model_dir or train.MODEL_DIR) / "model.joblib"
    if not path.exists():
        raise FileNotFoundError(f"No model at {path}. Train one first:  python -m src.train")
    return joblib.load(path)


def predict_one(bundle, features: dict) -> dict:
    """features: {"mean_radius": 17.99, ...} with all 30 names. Returns the prediction."""
    names = bundle["info"]["feature_names"]

    # Check the input BEFORE predicting: in production, bad data is the #1 problem.
    missing = [n for n in names if n not in features]
    unknown = [n for n in features if n not in names]
    if missing or unknown:
        raise BadInput(f"missing features: {missing}; unknown features: {unknown}")

    row = [[float(features[n]) for n in names]]  # same column order as in training
    prob = float(bundle["model"].predict_proba(row)[0, MALIGNANT])
    threshold = bundle["info"]["threshold"]
    return {
        "prediction": "malignant" if prob >= threshold else "benign",
        "probability_malignant": round(prob, 4),
        "threshold": threshold,
    }
