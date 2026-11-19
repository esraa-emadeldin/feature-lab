---
marp: true
title: Feature Selection vs Feature Extraction
paginate: true
size: 16:9
style: |
  /* Colours: blue = selection, orange = extraction */
  section {
    font-family: 'Segoe UI', 'Inter', sans-serif;
    background: #F4F1EA;
    color: #16181D;
    font-size: 30px;
    padding: 60px 80px;
  }
  h1, h2 { color: #16181D; font-weight: 800; }
  h2 { font-size: 52px; margin-bottom: 24px; }
  strong { color: #2F5FC4; }
  em { color: #B5530F; font-style: normal; font-weight: 700; }
  table { font-size: 26px; width: 100%; }
  th { background: #E6E1D6; }
  section.dark { background: #16181D; color: #F4F1EA; }
  section.dark h1, section.dark h2 { color: #F4F1EA; }
  section.dark strong { color: #8FB0F2; }
  section.dark em { color: #F09A52; }
  section.accent { background: #2F5FC4; color: #F4F1EA; }
  section.accent h1 { color: #F4F1EA; }
  section.lead { justify-content: center; }
  section.lead h1 { font-size: 80px; line-height: 1.1; }
  .big { font-size: 64px; font-weight: 800; }
---

<!-- _class: lead dark -->
<!-- _paginate: false -->

FEATURE SELECTION VS FEATURE EXTRACTION

# More data isn't always better.

[Team names] · [Course name] · FCAI, Cairo University

<!--
Hook (0:00–0:20): "Is more data always better? Imagine predicting whether a student will pass an exam. You could give the model everything: study hours, sleep… and also shoe size and favourite colour. Today we'll see why fewer, better features can beat more data."
-->

---

## The problem: too many features

Real datasets have **hundreds of features**, and many of them are useless.

| 🐢 Slower | 🤯 Harder to explain | 📉 Less accurate |
|---|---|---|
| More columns means more computation to train and predict | Nobody can reason about a model with 500 inputs | In many dimensions data gets sparse: the *curse of dimensionality* |

<!--
(0:20–0:45) "Real datasets often have hundreds of features. Many are useless or repeat each other. They make models slower, harder to explain, and can even make them less accurate, because in many dimensions the data becomes sparse. This is called the curse of dimensionality."
-->

---

## Two ways to fix it

| | **Feature Selection** | *Feature Extraction* |
|---|---|---|
| Idea | **Keep** a subset of the original columns | *Build* fewer, new columns from the old ones |
| Picture | ▮ ▯ ▮ ▯ ▯ ▮ → ▮ ▮ ▮ | ▮ ▮ ▮ ▮ ▮ ▮ → ◆ ◆ |
| Meaning | Kept: "study hours" still means study hours | Each new column is a mix, so harder to explain |

<!--
(0:45–1:10) "There are two ways to fix it. Feature selection keeps a subset of the original features: the ones we keep still mean something, like 'study hours'. Feature extraction builds new features by combining the old ones. We get fewer features, but each one is a mix, so it's harder to explain."
-->

---

## Feature selection: 3 families

| Family | How it works | Example | Trade-off |
|---|---|---|---|
| **Filter** | Score each feature on its own | ANOVA, correlation, chi-square | Very fast, ignores the model |
| **Wrapper** | Train, drop the weakest, repeat | RFE *(in our demo)* | More accurate, slower |
| **Embedded** | Model picks features while training | Lasso, random-forest importance | Good middle ground |

<!--
(1:10–1:45) "Selection has three families. Filter methods score each feature on its own with a statistical test, like ANOVA or correlation, and keep the best. They're very fast. Wrapper methods train a model again and again. Recursive Feature Elimination, or RFE, removes the weakest features each round. More accurate but slower. Embedded methods choose features while the model trains, like Lasso or random-forest importance."
-->

---

## Feature extraction: main methods

| Method | What it does | Use it for |
|---|---|---|
| *PCA* | New axes that keep the most information (variance) | Compression *(in our demo)* |
| *LDA* | Like PCA, but uses the class labels to separate classes | Supervised problems |
| *t-SNE* | Squeezes data into 2D so we can see clusters | Visualisation |

<!--
(1:45–2:10) "For extraction, the classic method is PCA. It finds new axes that keep the most information. LDA does something similar using the class labels, and t-SNE is mainly for drawing data in 2D. Let's see it live."
-->

---

<!-- _class: lead accent -->
<!-- _paginate: false -->

LIVE DEMO

# 🧪 Feature Lab

A Streamlit app built with scikit-learn

<!--
Demo (2:10–4:10): cut to the screen recording of the app here.
Part 1: all 8 features 79.4% → noise on 63.9% → click "Select the best 4 features" 86.7%, kept = study_hours, attendance, past_grade, sleep_hours.
Part 2: PCA slider 2 (62.4%) → 10 (97.0%, 74% variance) → 64 (98.7%).
Full narration: docs/video-script.md.
-->

---

<!-- _class: dark -->

## What the demo showed

**Selection: will a student pass?**
<span class="big">**63.9% → 86.7%**</span>
50 junk columns dragged accuracy down. RFE kept exactly the 4 real features and beat all 8 together (79.4%).

*Extraction: handwritten digits*
<span class="big">*64 → 10 features*</span>
10 PCA components: 97.0% vs 98.7% with all pixels. 6× fewer features for a 1.7-point drop.

<!--
Optional summary right after the demo if you have spare seconds. Point at each big number once.
-->

---

## When to use which?

| | **Selection** | *Extraction* |
|---|---|---|
| Keeps original meaning? | ✅ Yes | ❌ No, new mixed features |
| Best when | You must **explain** the model (education, medicine, finance) | You need *compression* or speed (images, signals) |
| Examples | Filter, RFE, Lasso, tree importance | PCA, LDA, t-SNE, autoencoders |

<!--
(4:10–4:40) "So which one should you use? If you need to explain your model, as in education, medicine or finance, use selection: the features keep their meaning. If you need compression or speed, as with images or signals, use extraction. Both fight the same enemy: too many useless features."
-->

---

<!-- _class: lead dark -->
<!-- _paginate: false -->

RECAP

# More data isn't always better. *Better features are.*

Thank you · Questions?

<!--
(4:40–5:00) "We saw it: dropping the junk took us from 64% to 87%, and 10 PCA features did the work of 64 pixels. More data isn't always better. Better features are. Thank you."
-->
