---
name: stickman-video
description: Make or change the Feature Lab stickman cartoon video (the chosen default video style) (hand-drawn stick figures, a robot "model", feature cards, Ava's Microsoft neural voice, captions) from docs/video-script.md. Use when the user asks to make, render, preview or edit the video, add or change a scene, change the voice, or keep the video in sync with the script, slides or app numbers.
---

# Stickman cartoon video

The video is made by our own small pipeline in `video/` (inspired by the community skill
chrisaswain/stickman-animation-agent, MIT). Every frame is drawn from code, so the video can be
re-rendered at any time.

| File | What it does |
|---|---|
| `video/scenes.js` | The scenes in order: `id`, `say` (narration), `draw()` (the picture at time `T`) |
| `video/draw.js` | Drawing kit: `stickman`, `card`, `ICONS`, `text`, `arrow`, `check`, `cross`, `sparkle`, `sweat`, captions |
| `video/make_video.py` | edge-tts voice + word timings → frames in a hidden browser → MP4 with ffmpeg |
| `video/stage.html` | The page frames are drawn on. Open with `?preview=<id>` to watch with rough timings |
| `video/build/` | Output (git-ignored): `<id>.mp4`, `feature-lab-video.mp4`, test PNGs |

## Setup (once)

Use the project `.venv` (never global Python):

```
uv pip install -r requirements.txt -r video/requirements.txt
```

Playwright needs a Chromium: in a cloud container it is pre-installed; on a laptop run
`python -m playwright install chromium` once. ffmpeg comes with `imageio-ffmpeg`, nothing to install.

The voice needs `speech.platform.bing.com`. In a Claude cloud session use the `feature-lab`
environment, which allows it. If edge-tts fails with a 403 or "No server date", that host is blocked.

## Commands

```
python video/make_video.py --still hook 6   # one PNG of scene "hook" at 6 s (fast check)
python video/make_video.py --only hook      # one scene as MP4
python video/make_video.py                  # the whole video → video/build/feature-lab-video.mp4
```

## Workflow for adding or changing a scene

1. **Narration comes from `docs/video-script.md`.** Copy the spoken lines into `say` word for word.
   Numbers (79.4%, 63.9%, 86.7%, 62.4%, 97.0%, 98.7%, 74%) must match the script, the slides
   and the app. If one changes, change all of them (see CLAUDE.md).
2. **Time drawings to words, never to fixed seconds.** `at("shoe")` is when the voice says "shoe";
   `at("better", 2)` is the 2nd "better". `prog(start, dur)` gives a smooth 0 → 1;
   `poseAt([[t, "stand"], [t2, "cheer"]])` blends poses; `stepAt([[t, "happy"], ...])` switches moods.
   `at()` throws if the word is not in `say`, which catches typos early.
3. **Keep the cast consistent:** the student (`hair: true`, left) and the robot model
   (`head: "robot"`, right, labelled "the model"). Yellow sticky-note cards are features. Junk
   features get a red `cross` and fall off; good ones get a green `check`. Moods: happy, neutral,
   confused, sad, surprised, dizzy, worried. Poses: stand, shrug, wave, point, hold, cheer, think, hips.
4. **Leave the bottom strip (y > 640) free** for captions. Stage is 1280 × 720.
5. **Check stills before rendering video:** render 3–5 `--still` frames at key words, look at
   them, fix overlaps or text running off the stage, then render with `--only <id>`.
6. Send the user the MP4 from `video/build/` and say which scene changed.

## Style rules

- Simple, commented code: the owner is learning. Explain new helpers in a comment.
- Voice: `en-US-AvaMultilingualNeural` (`VOICE` in make_video.py), chosen by the owner.
- Fun but correct: jokes come from the characters, never from changing the numbers or claims.
- Run `pytest` before saying it's done; commit with a short one-line message, no trailers.
