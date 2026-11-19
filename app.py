"""Feature Lab: one simple page showing feature SELECTION, then feature EXTRACTION.

Run it with:  streamlit run app.py
All the ML lives in src/ml.py; this file only draws the screen.
"""

import matplotlib.pyplot as plt
import streamlit as st

from src import ml

st.set_page_config(page_title="Feature Lab", page_icon="🧪", layout="centered")


# --- cached helpers: each result is computed once, then every click is instant
@st.cache_data
def students(add_noise):
    return ml.load_students(add_noise)


@st.cache_data
def accuracy_all(add_noise):
    X, y, _ = students(add_noise)
    return ml.knn_accuracy(X, y)


@st.cache_data
def best_4(add_noise):
    # The button always uses the Wrapper method (RFE) and keeps 4 features.
    X, y, _ = students(add_noise)
    return ml.selection_accuracy(X, y, "Wrapper", 4)


@st.cache_data
def digits():
    return ml.load_digits_data()


@st.cache_data
def pca_results(n):
    X, y = digits()
    return ml.pca_reconstruct(X, n), ml.explained_variance(X, n), ml.pca_accuracy(X, y, n)


@st.cache_data
def accuracy_64():
    X, y = digits()
    return ml.pca_accuracy(X, y, 64)


# st.button is only "True" for ONE rerun, so we remember the click in
# session_state. Changing the noise switch clears it (the data changed).
if "selected" not in st.session_state:
    st.session_state.selected = False


def forget_selection():
    st.session_state.selected = False


st.title("🧪 Feature Lab")
st.caption("Fewer, better features: keep the useful columns (selection) or build new ones (extraction).")

# ============================================================ 1) SELECTION
st.header("1) Feature Selection")
st.write(
    "**Will a student pass the exam?** 600 students (generated data, so we know the truth): "
    "4 features really matter, 4 are silly (shoe size, height, favourite colour, phone brand)."
)

add_noise = st.toggle("Add 50 random noise columns", on_change=forget_selection)
X, y, names = students(add_noise)
st.metric(f"Accuracy using all {X.shape[1]} features", f"{accuracy_all(add_noise):.1%}")

if st.button("Select the best 4 features", type="primary"):
    st.session_state.selected = True

if st.session_state.selected:
    acc, kept = best_4(add_noise)
    gain = (acc - accuracy_all(add_noise)) * 100
    st.metric("Accuracy with only the 4 selected features", f"{acc:.1%}", delta=f"{gain:+.1f} pts")
    dropped = [name for i, name in enumerate(names) if i not in kept]
    st.write("✅ **Kept:** " + " · ".join(names[i] for i in kept))
    # Show only the first few dropped names, the 50 noise columns would fill the screen.
    shown = dropped[:6] + ([f"… +{len(dropped) - 6} more"] if len(dropped) > 6 else [])
    st.write("❌ **Dropped:** " + " · ".join(shown))

st.divider()

# ============================================================ 2) EXTRACTION
st.header("2) Feature Extraction (PCA)")
st.write("Handwritten digits: each image is 8×8 = 64 pixel features. PCA squeezes them into fewer, new features.")

n = st.slider("Number of PCA components (new features)", 1, 64, 10)
rebuilt, variance, acc_n = pca_results(n)

col1, col2 = st.columns(2)
col1.metric("Information kept (variance)", f"{variance:.1%}")
col2.metric(f"Accuracy with {n} components", f"{acc_n:.1%}", delta=f"{(acc_n - accuracy_64()) * 100:+.1f} pts vs 64 pixels")

st.write("**Top row: original images · Bottom row: rebuilt from only the PCA components**")
X_digits, _ = digits()
fig, axes = plt.subplots(2, 8, figsize=(8, 2.2))
for i in range(8):
    axes[0, i].imshow(X_digits[i].reshape(8, 8), cmap="gray_r")
    axes[1, i].imshow(rebuilt[i].reshape(8, 8), cmap="gray_r")
    axes[0, i].axis("off")
    axes[1, i].axis("off")
st.pyplot(fig)
plt.close(fig)
