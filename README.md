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

## Run the app
```powershell
uv venv --python 3.12 .venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
streamlit run app.py
```
> On the very first run Streamlit asks for your email. Just press **Enter**.

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
