---
name: python-project-setup
description: Start a new Python project or tidy an existing one the user's way - uv + .venv, pinned requirements.txt, src/ and tests/ with pytest, .gitignore, GitHub Actions CI, README and a project CLAUDE.md. Use when the user says "new project", "set up the repo", "add tests/CI", or a Python repo is missing these basics.
---

# Python project setup

The user is learning, works on Windows (PowerShell), and likes small, simple, commented projects.
Show each step and explain new things in one sentence.

## Layout

```
my-project/
  src/            code (small functions: data in -> result out)
  tests/          pytest tests, one test file per topic
  app.py          only if there is a UI (e.g. Streamlit); keep logic in src/
  requirements.txt
  pytest.ini
  .gitignore
  README.md
  CLAUDE.md
  .github/workflows/ci.yml
```

## Steps

1. **Virtual environment** (never install globally):
   ```powershell
   uv venv --python 3.12 .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. **requirements.txt** with pinned versions. Install, then pin what got installed:
   `uv pip install pandas pytest` → `uv pip freeze` → copy only the top-level packages with `==` versions.
   Start the file with a comment: `# Pinned so everyone gets the same results`.
3. **pytest.ini**:
   ```ini
   [pytest]
   testpaths = tests
   pythonpath = .
   ```
4. **.gitignore**: `__pycache__/`, `*.pyc`, `.venv/`, `.pytest_cache/`, `.ipynb_checkpoints/`, `.env`, `.env.*`,
   `.claude/settings.local.json`, plus any build/output folders.
5. **CI** `.github/workflows/ci.yml`: on push to main and on pull requests, ubuntu-latest,
   `actions/checkout@v4`, `actions/setup-python@v5` with `python-version: '3.12'` and `cache: pip`,
   `pip install -r requirements.txt`, `pytest -q`. Add a comment at the top saying what it does.
6. **A first test** that really checks behaviour (not just "imports work"), then run `pytest`.
7. **README.md**: one-paragraph "what it is", a Files table, "Run it" and "Run the tests" with
   PowerShell commands.
8. **CLAUDE.md** for the project, short: language/version, where code and tests live, the exact
   setup/run/test commands, and project-specific rules (e.g. numbers to keep in sync).

## Rules

- Keep it minimal: don't add linters, type checkers, Docker or packaging unless asked.
- If the project already exists, change only what's missing and list what you added.
- Finish by running `pytest` and reporting the real result.
