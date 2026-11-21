# Global Claude Code kit

My Claude Code setup for **every** project, kept in git so I can change it in one place and
install it on any computer. It goes into `C:\Users\<me>\.claude\`.

| File | What it does |
|---|---|
| `CLAUDE.md` | My rules for all projects: learner-friendly code, `.venv` + `uv`, run tests before "done", short commits with no trailers, no secrets |
| `settings.json` | **Fewer prompts:** safe read-only commands (git status/diff/log, ls, pytest, versions) run without asking. **Safety guards:** blocks reading/editing `.env` and keys, force-push, `git reset --hard`, `git clean -f`, `rm -rf`; asks before `git push` and global `pip install`. Turns off Claude's `Co-Authored-By` commit trailer. |
| `skills/stickman-video` | Make a hand-drawn stickman cartoon video with a Microsoft neural voice, in any project |
| `skills/python-project-setup` | Start or tidy a Python project my way (uv, .venv, pytest, CI, README, CLAUDE.md) |
| `skills/marp-slides` | Make or edit Marp slide decks that stay in sync with the project |
| `skills/explain-for-learner` | Explain code, changes and errors step by step, with something to try |
| `install.ps1` | Copies all of the above into `~\.claude` (with a backup first) |

## Install (Windows)

From the feature-lab folder, in PowerShell:

```powershell
git pull
powershell -ExecutionPolicy Bypass -File claude-global\install.ps1
```

Then restart Claude Code. Run the same command again any time you change the kit.

What the installer does:
- Backs up your current `CLAUDE.md`, `settings.json` and these skills to `~\.claude\backups\global-kit-<date>\`.
- `CLAUDE.md`: puts these rules between `<!-- global-kit:start -->` and `<!-- global-kit:end -->`
  and keeps anything else you wrote there.
- `settings.json`: **adds** these permission rules to yours (nothing is removed). Sets the commit
  attribution only if you have none.
- Copies the skills, plus this repo's `video/` engine into `stickman-video/template/`.

## Check it worked

In Claude Code: type `/` and look for the skill names, run `/permissions` to see the rules,
and `/memory` to see that the user CLAUDE.md is loaded.

## Notes

- The deny rules block `.env.example` too (it matches `.env.*`). Ask Claude to show it to you
  another way, or remove that rule if it gets in the way.
- `rm -rf` is blocked. Delete build folders yourself, or approve a narrower command.
- Project rules win: a project's own `CLAUDE.md` / `.claude/settings.json` can add or override.
- Claude cloud sessions don't read this folder. They only use what's in the repo.
