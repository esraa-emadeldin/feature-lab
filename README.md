# 🧪 Feature Lab

A small Streamlit app that shows **feature selection** vs. **feature extraction** live, made for a 5-minute presentation video.

- **Part 1, Selection: "Will a student pass the exam?"** 600 generated students with 4 features that really matter (`study_hours`, `attendance`, `past_grade`, `sleep_hours`) and 4 silly ones (`shoe_size`, `height_cm`, `favourite_colour`, `phone_brand`).
  - KNN with all 8 features: **79.4%**.
  - With 50 random noise columns added: **63.9%**.
  - One click on "Select the best 4 features" (RFE) keeps exactly the 4 real features: **86.7%**.
- **Part 2, Extraction: PCA on 8×8 handwritten digits.** 10 components give **97.0%** accuracy, vs. **98.7%** with all 64 pixels.

## Files
| Path | What |
|---|---|
| `src/ml.py` | All the ML, as small functions (data in → numbers out) |
| `app.py` | The screen only (widgets + charts) |
| `tests/` | pytest tests (ML + the app itself) |
| `slides/slides.md` | The presentation ([Marp](https://marp.app) Markdown) |
| `docs/video-script.md` | The 5-minute video script |
| `src/train.py` | **Production:** trains the model on real data, saves `models/model.joblib` |
| `src/predict.py` | **Production:** loads the saved model, checks the input, predicts |
| `serve.py` | **Production:** the web API (FastAPI) that other programs call |
| `examples/` | Two real patients from the test set, ready to send to the API |
| `Dockerfile` | Packages the API + a freshly trained model into one image |

## Run the app
```powershell
uv venv --python 3.12 .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
streamlit run app.py
```
> On the very first run Streamlit asks for your email. Just press **Enter**.

## Production version: real data, real API
The Streamlit page is a **demo** (a screen for people). In production, a model usually runs as an
**API**: another program (say, a hospital lab system) sends data and gets a prediction back.
scikit-learn does the ML in both; the difference is how the model is trained, saved and served.

**Use case:** a tumour "second opinion". The lab measures 30 things about a breast-tumour biopsy;
the API answers *benign* or *malignant*. Data: the real **Wisconsin Diagnostic Breast Cancer**
dataset (569 patients, 212 malignant). It is built into scikit-learn, so no download is needed.

**1. Train** (scale → feature selection → logistic regression, tuned with 5-fold cross-validation):
```powershell
python -m src.train
```
Result on the 114 held-out test patients: **98.2%** accuracy, **41 of 42** cancers caught,
1 false alarm. The model flags "malignant" from 30% probability (not 50%), because missing
a cancer is much worse than a false alarm.

**2. Serve:**
```powershell
uvicorn serve:app --reload
```
Open http://127.0.0.1:8000/docs to try it in the browser, or send a real patient:
```powershell
curl.exe -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "@examples/patient_malignant.json"
```
→ `{"prediction":"malignant","probability_malignant":1.0,"threshold":0.3}`

**3. Ship:** `docker build -t tumour-api .` then `docker run -p 8000:8000 tumour-api`.

> ⚠️ This is a learning project, not a medical device. Never use it for real diagnosis.

## Run the tests
```powershell
pytest
```

## Edit the slides
1. Install the **Marp for VS Code** extension (VS Code suggests it when you open this folder).
2. Open `slides/slides.md`, then click the preview icon (top right) to see the slides live.
3. To export, open the command palette (`Ctrl+Shift+P`), choose **Marp: Export slide deck…**, then pick PDF or PPTX.

Speaker notes are the `<!-- ... -->` comments under each slide.

## Working as a team
1. `git pull` to get the latest version.
2. `git checkout -b my-change` to work on a branch.
3. Run `pytest` before every commit.
4. Push the branch and open a Pull Request. Merge only when CI is green.

> ⚠️ Don't upgrade the libraries in `requirements.txt` before the video is recorded, or the numbers may no longer match the script and slides.
