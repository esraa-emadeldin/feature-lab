"""Tests for the feature-SELECTION half of src/ml.py (student exam data)."""

import pytest

from src.ml import METHODS, N_REAL, knn_accuracy, load_students, selection_accuracy

REAL = ["study_hours", "attendance", "past_grade", "sleep_hours"]


def test_shapes():
    X, y, names = load_students(add_noise=False)
    Xn, _, names_n = load_students(add_noise=True)
    assert X.shape == (600, 8)  # 4 real + 4 silly features
    assert Xn.shape == (600, 58)  # + 50 noise columns
    assert names[:N_REAL] == REAL
    assert names_n[-1] == "noise_50"
    assert set(y) == {0, 1}  # 0 = fail, 1 = pass


def test_noise_hurts():
    clean = knn_accuracy(*load_students(add_noise=False)[:2])
    noisy = knn_accuracy(*load_students(add_noise=True)[:2])
    assert clean - noisy >= 0.03


def test_button_finds_the_real_features():
    # The app's button uses Wrapper (RFE) with k=4: it must keep exactly the 4 real ones.
    X, y, names = load_students(add_noise=True)
    acc, kept = selection_accuracy(X, y, "Wrapper", 4)
    assert [names[i] for i in kept] == REAL
    assert acc > knn_accuracy(X, y)


@pytest.mark.parametrize("method", METHODS)
def test_selection_recovers(method):
    X, y, _ = load_students(add_noise=True)
    acc, kept = selection_accuracy(X, y, method, k=4)
    assert acc > knn_accuracy(X, y)
    assert len(kept) == 4
    assert sum(i < N_REAL for i in kept) >= 3  # mostly real features


def test_deterministic():
    X, y, _ = load_students(add_noise=True)
    assert selection_accuracy(X, y, "Wrapper", 4) == selection_accuracy(X, y, "Wrapper", 4)


def test_bad_k():
    X, y, _ = load_students(add_noise=True)
    for bad in (0, 59):
        with pytest.raises(ValueError):
            selection_accuracy(X, y, "Filter", bad)
    _, kept = selection_accuracy(X, y, "Filter", 1)
    assert len(kept) == 1
