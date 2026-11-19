"""Tests for the feature-EXTRACTION (PCA) half of src/ml.py."""

import numpy as np

from src.ml import explained_variance, load_digits_data, pca_2d, pca_accuracy, pca_reconstruct

X, y = load_digits_data()


def test_reconstruct_shape():
    for n in (1, 10):
        assert pca_reconstruct(X, n).shape == (1797, 64)


def test_full_reconstruction():
    # Keeping all 64 components loses nothing.
    assert np.allclose(pca_reconstruct(X, 64), X, atol=1e-6)


def test_variance_grows():
    assert explained_variance(X, 2) < explained_variance(X, 10) < explained_variance(X, 64)
    assert abs(explained_variance(X, 64) - 1.0) < 1e-9


def test_few_components_enough():
    # 10 new features do almost as well as all 64 pixels.
    assert pca_accuracy(X, y, 10) >= pca_accuracy(X, y, 64) - 0.05


def test_2d():
    assert pca_2d(X).shape == (1797, 2)
