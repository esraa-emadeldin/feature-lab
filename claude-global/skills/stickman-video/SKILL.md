---
name: stickman-video
description: The user's DEFAULT video style (and the look of their YouTube channel). Turn a script or topic into a fun hand-drawn stickman cartoon video (wobbly drawn lines, stick figures with poses and faces, a robot character, sticky-note cards, captions) narrated by a free Microsoft neural voice (edge-tts), rendered to MP4. Use when the user wants an explainer video, a cartoon/animated/whiteboard-style video, a video for a presentation, or to add, edit or re-render scenes of such a video in any project.
---

# Stickman cartoon video (any project)

**This is the default style for all the user's videos and their YouTube channel.** Use it whenever
they ask for a video without naming a style, and keep the look consistent between videos: cream
paper, the same student and robot characters, yellow sticky-note cards, captions, Ava's voice.
Other styles (blackboard, Manim, Remotion) only when asked.

A small pipeline that draws every frame from code, so the video can be fixed and re-rendered any time.
The engine lives in `template/` next to this file (copied there by the global-kit installer).

## If the project already has `video/`

Use it as it is: read `video/scenes.js` and the project's CLAUDE.md, then follow "Workflow" below.

## Setting it up in a new project

1. Copy the engine into the project:
   - `template/draw.js`, `template/make_video.py`, `template/stage.html`, `template/requirements.txt` → `video/`
   - `template/assets/` → `video/assets/` (handwriting font + its OFL licence)
   - `template/scenes.example.js` → `video/scenes.js`, then replace the example scene with the project's scenes.
2. Add `video/build/` to `.gitignore`.
3. Install into the project's `.venv` (never global): `uv pip install -r video/requirements.txt`
4. On a laptop, once: `python -m playwright install chromium`. ffmpeg comes with `imageio-ffmpeg`.
5. Add a line to the project's CLAUDE.md: `Video: python video/make_video.py (stickman-video skill)`.

The voice needs internet access to `speech.platform.bing.com`. If edge-tts fails with a 403 or
"No server date", that host is blocked (in a Claude cloud session, ask to allow it in the environment).

## Commands

```
python video/make_video.py --still <scene> 6   # one PNG at 6 s: fast check of the drawing
python video/make_video.py --only <scene>      # one scene as MP4
python video/make_video.py                     # the whole video
```

Output goes to `video/build/`. Default voice: `en-US-AvaMultilingualNeural` (`VOICE` in make_video.py).
Other good ones: `en-US-EmmaMultilingualNeural`, `en-US-AndrewMultilingualNeural`, `en-US-BrianMultilingualNeural`.
Before a full video, offer the user 2–4 voice samples to pick from.

## Workflow

1. **Script first.** Find the project's video script (e.g. `docs/video-script.md`). If none exists,
   write one with the user: ~130 spoken words per minute, short sentences, one idea per scene.
   Copy the spoken lines into each scene's `say` word for word. Keep any numbers identical to the
   project's app, slides and README.
2. **Pilot one scene** (~15–20 s) and send it to the user before making the rest.
3. **Time drawings to words, not seconds:** `at("word")` / `at("word", 2)` = when that word is spoken;
   `prog(start, dur)` = smooth 0 → 1; `poseAt([[t, "stand"], [t2, "cheer"]])` blends poses;
   `stepAt([[t, "happy"], ...])` switches moods or labels. `at()` throws if the word is missing.
4. **Building blocks in draw.js:** `stickman({x, y, pose, mood, p, hair, head: "robot"})` returns
   `{svg, hand}`; `card(label, icon, x, y, {p, rot, s})`; `ICONS` (clock, moon, shoe, palette, book,
   grade, calendar; add new ones as small drawings); `text`, `line`, `circle`, `rect`, `arrow`,
   `check`, `cross`, `sparkle`, `sweat`, `group`. Moods: happy, neutral, confused, sad, surprised,
   dizzy, worried. Poses: stand, shrug, wave, point, hold, cheer, think, hips.
5. **Stage is 1280 × 720;** keep y > 640 free for captions. Keep the same characters all video long.
6. **Check stills, then render:** look at 3–5 `--still` frames at key words, fix overlaps or text off
   the stage, then render with `--only`. Send the MP4 to the user.

## Style

- Fun comes from the characters (confused robot, cards flying, junk crossed out and falling), never
  from bending facts or numbers.
- Simple, commented code. Explain any new helper in a comment.
- Credit: inspired by chrisaswain/stickman-animation-agent (MIT). Font: Patrick Hand (SIL OFL).
