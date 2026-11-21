"""The production API: other programs send patient data, we send back a prediction.

Run it with:  uvicorn serve:app --reload
Then open http://127.0.0.1:8000/docs  (FastAPI makes a test page for free).

Endpoints:
  GET  /health      -> is the service up and is a model loaded?
  GET  /model-info  -> which model is running and how well it scored
  POST /predict     -> {"features": {...30 numbers...}} -> benign / malignant
"""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.predict import BadInput, load_model, predict_one

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("serve")

app = FastAPI(title="Tumour second-opinion API", version="1.0")

# Load the model ONCE when the server starts (not on every request: that would be slow).
bundle = load_model()
log.info("Model loaded, trained at %s", bundle["info"]["trained_at"])


class Patient(BaseModel):
    """The JSON body of /predict. Pydantic rejects anything that isn't numbers."""

    features: dict[str, float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/model-info")
def model_info():
    info = bundle["info"]
    return {key: info[key] for key in ("trained_at", "sklearn_version", "threshold", "metrics", "feature_names")}


@app.post("/predict")
def predict(patient: Patient):
    try:
        result = predict_one(bundle, patient.features)
    except BadInput as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    # Log every prediction: in production you watch these to spot problems.
    log.info("prediction=%s p=%.3f", result["prediction"], result["probability_malignant"])
    return result
