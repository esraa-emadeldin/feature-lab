"""Tests for the production pipeline: src/train.py, src/predict.py and serve.py."""

import importlib
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src import train
from src.predict import BadInput, load_model, predict_one

EXAMPLES = Path(__file__).parent.parent / "examples"


@pytest.fixture(scope="module")
def model_dir(tmp_path_factory):
    """Train once into a temporary folder (so tests never touch models/)."""
    folder = tmp_path_factory.mktemp("models")
    X, y, names = train.load_data()
    model, metrics = train.train(X, y)
    train.save(model, metrics, names, folder)
    return folder


@pytest.fixture(scope="module")
def client(model_dir):
    """Start the API (without a real server) using the model from model_dir."""
    mp = pytest.MonkeyPatch()
    mp.setattr(train, "MODEL_DIR", model_dir)
    import serve

    importlib.reload(serve)  # serve.py loads the model at import time
    yield TestClient(serve.app)
    mp.undo()


def example(name):
    return json.loads((EXAMPLES / f"patient_{name}.json").read_text())


def test_real_data():
    X, y, names = train.load_data()
    assert X.shape == (569, 30)
    assert y.sum() == 212  # 212 malignant tumours in the real dataset
    assert "mean_radius" in names


def test_model_is_good_enough(model_dir):
    # A "quality gate": refuse a model that misses too many cancers.
    m = json.loads((model_dir / "metrics.json").read_text())["metrics"]
    assert m["test_accuracy"] >= 0.95
    assert m["test_recall_malignant"] >= 0.95
    assert m["confusion_matrix"]["missed_cancer"] <= 2


def test_predict_examples(model_dir):
    bundle = load_model(model_dir)
    assert predict_one(bundle, example("malignant")["features"])["prediction"] == "malignant"
    assert predict_one(bundle, example("benign")["features"])["prediction"] == "benign"


def test_predict_rejects_bad_input(model_dir):
    bundle = load_model(model_dir)
    features = example("benign")["features"]
    del features["mean_radius"]
    with pytest.raises(BadInput, match="mean_radius"):
        predict_one(bundle, features)


def test_missing_model(tmp_path):
    with pytest.raises(FileNotFoundError, match="python -m src.train"):
        load_model(tmp_path)


def test_api_health_and_info(client):
    assert client.get("/health").json() == {"status": "ok"}
    info = client.get("/model-info").json()
    assert len(info["feature_names"]) == 30
    assert info["threshold"] == train.THRESHOLD


def test_api_predict(client):
    response = client.post("/predict", json=example("malignant"))
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] == "malignant"
    assert 0 <= body["probability_malignant"] <= 1


def test_api_rejects_bad_input(client):
    assert client.post("/predict", json={"features": {"mean_radius": 10}}).status_code == 422
    assert client.post("/predict", json={"features": {"mean_radius": "big"}}).status_code == 422
