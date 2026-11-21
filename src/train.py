"""Train the production model on REAL data and save it to disk.

Run it with:  python -m src.train

The use case: a hospital lab measures 30 things about a breast-tumour biopsy
(radius, texture, smoothness, ...). Our model gives a "second opinion":
how likely is this tumour to be malignant (cancer) vs benign (harmless)?

The data is the real Wisconsin Diagnostic Breast Cancer dataset
(569 patients, collected at the University of Wisconsin hospitals).
It ships inside scikit-learn, so no download is needed.

Steps (the normal ML workflow):
  1. load the data
  2. lock away a TEST set the model never sees while training
  3. try a few settings with cross-validation on the TRAINING set only
  4. check the best model ONCE on the test set (honest score)
  5. save the model + its scores so the API (serve.py) can use them
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
import sklearn
from sklearn.datasets import load_breast_cancer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED = 42
# Where the trained model is saved. Can be changed with the MODEL_DIR environment variable.
MODEL_DIR = Path(os.environ.get("MODEL_DIR", Path(__file__).parent.parent / "models"))
MALIGNANT = 1  # in OUR labels 1 = malignant (cancer), 0 = benign

# Decision threshold: flag a tumour as "malignant" when the model says >= 30%.
# The default would be 50%, but missing a cancer is far worse than a false alarm
# (a false alarm just means a doctor looks again). On the TRAINING folds, 30%
# halved the missed cancers (8 -> 4) for only 4 extra false alarms out of 285.
THRESHOLD = 0.3


def load_data():
    """Return (X, y, feature_names) with y: 1 = malignant, 0 = benign.

    scikit-learn stores it the other way round (0 = malignant), so we flip it:
    "1 = the thing we are looking for" is easier to read in the metrics.
    Names like "mean radius" become "mean_radius" so they are easy to type in JSON.
    """
    data = load_breast_cancer()
    y = 1 - data.target
    names = [name.replace(" ", "_") for name in data.feature_names]
    return data.data, y, names


def build_pipeline():
    """Scale -> keep the k best features (feature SELECTION!) -> logistic regression.

    Putting all steps in ONE Pipeline matters in production: the exact same
    scaling and column choice learned in training is applied to every new patient.
    """
    return Pipeline(
        [
            ("scale", StandardScaler()),
            ("select", SelectKBest(f_classif)),
            ("model", LogisticRegression(max_iter=5000)),
        ]
    )


def train(X, y):
    """Split, tune with cross-validation, score on the test set. Returns (model, metrics)."""
    # 1) Lock away 20% as the test set. stratify keeps the same cancer/no-cancer ratio.
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)

    # 2) Try every combination below with 5-fold cross-validation (training data only).
    #    k = how many of the 30 features to keep, C = how strongly to regularise.
    grid = {"select__k": [5, 10, 15, 20, 30], "model__C": [0.01, 0.1, 1, 10]}
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    # We score on recall: missing a cancer is much worse than a false alarm.
    search = GridSearchCV(build_pipeline(), grid, cv=folds, scoring="recall")
    search.fit(X_tr, y_tr)
    model = search.best_estimator_  # already refit on the whole training set

    # 3) Honest check on data the model has never seen.
    prob = model.predict_proba(X_te)[:, MALIGNANT]
    pred = (prob >= THRESHOLD).astype(int)  # our threshold, not the default 50%
    tn, fp, fn, tp = confusion_matrix(y_te, pred).ravel()
    metrics = {
        "test_accuracy": round(accuracy_score(y_te, pred), 4),
        "test_recall_malignant": round(recall_score(y_te, pred), 4),  # cancers we caught
        "test_roc_auc": round(roc_auc_score(y_te, prob), 4),
        "confusion_matrix": {"true_benign": int(tn), "false_alarm": int(fp),
                             "missed_cancer": int(fn), "caught_cancer": int(tp)},  # fmt: skip
        "threshold": THRESHOLD,
        "best_params": search.best_params_,
        "cv_recall": round(search.best_score_, 4),
        "n_train": len(y_tr),
        "n_test": len(y_te),
    }
    return model, metrics


def save(model, metrics, feature_names, model_dir=MODEL_DIR):
    """Save the model (binary) and a readable metrics.json next to it."""
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    selected = [n for n, keep in zip(feature_names, model.named_steps["select"].get_support()) if keep]
    info = {
        "threshold": THRESHOLD,  # the API uses the same threshold
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sklearn_version": sklearn.__version__,  # load with the SAME version
        "feature_names": feature_names,  # the API checks requests against this list
        "selected_features": selected,
        "metrics": metrics,
    }
    joblib.dump({"model": model, "info": info}, model_dir / "model.joblib")
    (model_dir / "metrics.json").write_text(json.dumps(info, indent=2))
    return info


def main():
    X, y, names = load_data()
    print(f"Loaded {len(y)} real patients, {X.shape[1]} features, {y.sum()} malignant.")
    model, metrics = train(X, y)
    info = save(model, metrics, names)
    m = info["metrics"]
    print(f"Best settings: {m['best_params']}")
    print(f"Kept {len(info['selected_features'])} of 30 features: {', '.join(info['selected_features'])}")
    print(f"Test accuracy: {m['test_accuracy']:.1%}   cancers caught: {m['test_recall_malignant']:.1%}")
    print(f"Confusion matrix: {m['confusion_matrix']}")
    print(f"Saved to {MODEL_DIR / 'model.joblib'}")


if __name__ == "__main__":
    main()
