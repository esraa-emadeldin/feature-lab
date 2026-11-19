"""All the machine-learning logic for Feature Lab.

Every function here is "data in -> numbers out", so it is easy to test
and easy to explain. app.py only draws the screen and calls these.
"""

import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE, SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 42  # same seed everywhere -> same numbers on every run (good for recording)
N_NOISE = 50  # how many junk columns we add
METHODS = ("Filter", "Wrapper", "Embedded")


# ---------------------------------------------------------------- helpers
def _split(X, y):
    """Same train/test split everywhere (30% test, class balance kept)."""
    return train_test_split(X, y, test_size=0.3, stratify=y, random_state=SEED)


def _knn():
    # KNN measures distances, so every column counts equally.
    # That's why useless (noise) columns hurt it so much.
    return make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))


# ------------------------------------------------------ feature SELECTION
N_STUDENTS = 600
N_REAL = 4  # the first 4 columns really decide pass/fail


def load_students(add_noise: bool):
    """Generated data: will a student pass the exam?

    We MAKE this data ourselves, so we know the truth: only the first 4
    features affect the result. The next 4 are silly features that have
    nothing to do with passing. A good feature-selection method should
    find the 4 real ones. Returns (X, y, feature_names); y: 1 = pass, 0 = fail.
    """
    rng = np.random.default_rng(SEED)
    n = N_STUDENTS

    # --- the 4 features that matter
    study_hours = rng.uniform(0, 10, n)  # hours per week
    attendance = rng.uniform(40, 100, n)  # % of lectures attended
    past_grade = rng.uniform(30, 100, n)  # last term's grade
    sleep_hours = rng.uniform(4, 9, n)  # hours per night

    # --- 4 silly features (random, unrelated to passing)
    shoe_size = rng.integers(36, 47, n)
    height_cm = rng.normal(168, 9, n)
    favourite_colour = rng.integers(0, 6, n)  # colour stored as a number 0-5
    phone_brand = rng.integers(0, 5, n)  # brand stored as a number 0-4

    # Pass/fail comes ONLY from the real features (plus a little luck).
    score = 0.5 * study_hours + 0.05 * attendance + 0.05 * past_grade + 0.5 * sleep_hours
    score += rng.normal(0, 0.8, n)
    y = (score > np.median(score)).astype(int)  # top half passes -> balanced classes

    X = np.column_stack(
        [study_hours, attendance, past_grade, sleep_hours, shoe_size, height_cm, favourite_colour, phone_brand]
    )
    names = ["study_hours", "attendance", "past_grade", "sleep_hours",
             "shoe_size", "height_cm", "favourite_colour", "phone_brand"]  # fmt: skip

    if add_noise:
        noise = rng.standard_normal((n, N_NOISE))
        X = np.hstack([X, noise])
        names += [f"noise_{i}" for i in range(1, N_NOISE + 1)]
    return X, y, names


def knn_accuracy(X, y) -> float:
    """Test accuracy of KNN using ALL columns."""
    X_tr, X_te, y_tr, y_te = _split(X, y)
    return _knn().fit(X_tr, y_tr).score(X_te, y_te)


def _choose_columns(X_tr, y_tr, method: str, k: int) -> list[int]:
    """Pick k column indices using ONLY the training data (no peeking at the test set)."""
    if method == "Filter":
        # Filter: score each column on its own (ANOVA F-test), keep the top k.
        selector = SelectKBest(f_classif, k=k).fit(X_tr, y_tr)
        return list(np.flatnonzero(selector.get_support()))
    if method == "Wrapper":
        # Wrapper: train a model, drop the weakest columns, repeat until k are left.
        # step=5 drops 5 columns per round so it stays fast on video.
        X_scaled = StandardScaler().fit_transform(X_tr)
        rfe = RFE(LogisticRegression(max_iter=5000), n_features_to_select=k, step=5)
        return list(np.flatnonzero(rfe.fit(X_scaled, y_tr).get_support()))
    if method == "Embedded":
        # Embedded: the model ranks the columns while it trains (tree importances).
        forest = RandomForestClassifier(n_estimators=200, random_state=SEED).fit(X_tr, y_tr)
        return list(np.argsort(forest.feature_importances_)[::-1][:k])
    raise ValueError(f"Unknown method: {method}")


def selection_accuracy(X, y, method: str, k: int):
    """Select k columns with `method`, then return (test accuracy, kept indices)."""
    if not 1 <= k <= X.shape[1]:
        raise ValueError(f"k must be between 1 and {X.shape[1]}")
    X_tr, X_te, y_tr, y_te = _split(X, y)
    kept = sorted(int(i) for i in _choose_columns(X_tr, y_tr, method, k))
    acc = _knn().fit(X_tr[:, kept], y_tr).score(X_te[:, kept], y_te)
    return acc, kept


# ----------------------------------------------------- feature EXTRACTION
def load_digits_data():
    """Handwritten digits: each image is 8x8 = 64 pixel features."""
    data = load_digits()
    return data.data, data.target


def _pca(n: int):
    return PCA(n_components=n, random_state=SEED)


def pca_reconstruct(X, n: int):
    """Squeeze X down to n PCA features, then rebuild the 64 pixels from them."""
    pca = _pca(n).fit(X)
    return pca.inverse_transform(pca.transform(X))


def explained_variance(X, n: int) -> float:
    """How much of the information (variance) n components keep, from 0 to 1."""
    return float(_pca(n).fit(X).explained_variance_ratio_.sum())


def pca_accuracy(X, y, n: int) -> float:
    """KNN test accuracy when it only sees n PCA features instead of 64 pixels."""
    # No scaler here: all pixels already share the same 0-16 scale.
    X_tr, X_te, y_tr, y_te = _split(X, y)
    model = make_pipeline(_pca(n), KNeighborsClassifier(n_neighbors=5))
    return model.fit(X_tr, y_tr).score(X_te, y_te)


def pca_2d(X):
    """Project every image onto the first 2 PCA features (for a scatter plot)."""
    return _pca(2).fit_transform(X)
