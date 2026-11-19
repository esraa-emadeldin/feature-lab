# Video script: Feature Selection vs. Feature Extraction (5:00)

Narration pace is about 130 words per minute. Split the parts between teammates however you like.
Read aloud, the narration takes about 4 minutes. Use the rest for pauses: let each number sit on screen for 2–3 seconds during the demo.
The slide numbers below match `slides/slides.md`.

---

## 1 · Hook (0:00–0:20) · slide 1
> "Is more data always better?
> Imagine predicting whether a student will pass an exam. You could give the model everything: study hours, sleep…
> and also shoe size and favourite colour.
> Today we'll see why fewer, better features can beat more data."

## 2 · The problem and the two fixes (0:20–1:10) · slides 2–3
> "Real datasets often have hundreds of features. Many are useless or repeat each other.
> They make models slower, harder to explain, and can even make them less accurate,
> because in many dimensions the data becomes sparse. This is called the curse of dimensionality.
> There are two ways to fix it.
> **Feature selection** keeps a subset of the original features. We drop columns, but the ones we keep still mean something, like 'study hours'.
> **Feature extraction** builds new features by combining the old ones. We get fewer features, but each one is a mix, so it's harder to explain."

## 3 · Methods (1:10–2:10) · slides 4–5
> "Selection has three families.
> **Filter** methods score each feature on its own with a statistical test, like ANOVA or correlation, and keep the best. They're very fast.
> **Wrapper** methods train a model again and again. Recursive Feature Elimination, or RFE, removes the weakest features each round. They're more accurate but slower.
> **Embedded** methods choose features while the model trains, like Lasso or random-forest importance.
> For extraction, the classic method is **PCA**. It finds new axes that keep the most information.
> **LDA** does something similar using the class labels, and **t-SNE** is mainly for drawing data in 2D.
> Let's see it live."

## 4 · Demo (2:10–4:10) · slide 6, then the app
### Part 1: Selection (2:10–3:10)
| Click | Say |
|---|---|
| Point at the first number | "600 students, 8 features: 4 that matter, and 4 silly ones like shoe size. With all 8, KNN is **79.4%** accurate." |
| Turn on **Add 50 random noise columns** | "Now we add 50 columns of pure random noise, and accuracy falls to **63.9%**. The model is drowning in junk." |
| Click **Select the best 4 features** | "RFE keeps 4 features, and accuracy jumps to **86.7%**. That's higher than all 8 features together." |
| Point at **Kept / Dropped** | "And look at what it kept: study hours, attendance, past grade and sleep, exactly the 4 that really matter. Shoe size and colour are gone." |

### Part 2: Extraction (3:10–4:10)
| Click | Say |
|---|---|
| Scroll down, slider at **2** | "Handwritten digits: 64 pixels each. With only 2 PCA components the images are blurry and accuracy is **62.4%**." |
| Slider to **10** | "At 10 components we keep 74% of the information, the digits are readable, and accuracy is **97.0%**…" |
| Slider to **64** | "…almost the same as all 64 pixels, **98.7%**. That's 6 times fewer features for a 1.7-point drop." |

## 5 · When to use which + recap (4:10–5:00) · slides 7–9
> "So which one should you use?
> If you need to explain your model, as in education, medicine or finance, use **selection**: the features keep their meaning.
> If you need compression or speed, as with images or signals, use **extraction**.
> Both fight the same enemy: too many useless features.
> We saw it: dropping the junk took us from 64% to 87%, and 10 PCA features did the work of 64 pixels.
> More data isn't always better. *Better* features are. Thank you."

---

## Recording checklist
- [ ] Run `streamlit run app.py` and click through everything once before recording, so every result is cached and appears instantly.
- [ ] Browser window at 1280×720 or larger, zoom 125% so the numbers are readable.
- [ ] Starting state: noise switch **off**, PCA slider at **2**.
- [ ] Record the demo with OBS or the Windows Snipping Tool (Win+Shift+R), then place it after slide 6 in your video editor.
- [ ] Time one full read-through. If it runs long, shorten part 3 first.
