# My rules for Claude Code (all projects)

These apply in every repo. A project's own CLAUDE.md can add to them or override them.

## About me
- I am learning to code. Keep code simple and add short comments that explain *why*.
- When you introduce something new (a library, a pattern, a command), explain it in one or two plain sentences.
- I work on Windows with PowerShell and VS Code. Give commands that work there.

## Python
- Every Python project uses its own `.venv` made with `uv`:
  `uv venv --python 3.12 .venv`, then `.\.venv\Scripts\Activate.ps1`, then `uv pip install -r requirements.txt`.
- Never install packages into the global Python, `ai-env`, or with `pip install --user` without asking me first.
- Pin versions in `requirements.txt` (for example `pandas==2.3.1`) so results stay the same.
- Tests use `pytest` in a `tests/` folder.

## Working style
- Before saying something is done, run the tests (and the app or script if there is one) and tell me the real result.
- Add or update a test when behaviour changes.
- Make the smallest change that does the job. Don't rename or reorganise things I didn't ask about.
- If something is unclear or there are two very different ways to do it, ask me first.
- Keep numbers that appear in several places (app, slides, video script, README) in sync.

## Git
- Commit messages: one short, simple line in plain English (e.g. `Add PCA slider to the app`).
- No `Co-Authored-By` or any other trailer in commit messages.
- Never force-push, never rewrite history on shared branches, never commit `.env` files, API keys or other secrets.
- Only commit or push when I ask (or when a project rule says to).

## Secrets
- Never read, print or copy `.env` files, keys or tokens. If a task needs a secret, tell me which one and let me set it.

## My global skills
- `stickman-video`: turn a script into a hand-drawn stickman cartoon video with a Microsoft neural voice.
- `python-project-setup`: start or tidy a Python project the way I like it (uv, .venv, pytest, CI).
- `marp-slides`: make or edit Marp slide decks that stay in sync with the project.
- `explain-for-learner`: explain what was changed and the new ideas behind it, step by step.
