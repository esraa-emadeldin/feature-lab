# Style experiments: the hook scene in 4 styles

**Decision: the stickman cartoon (`../scenes.js`) is our default style.** These are kept for reference only.

The same 16-second hook (Ava's voice, same words) made with four different tools, to choose a
style for the video and a future YouTube channel. Our own stickman version is `../scenes.js`.

All three need two files made by our pipeline first, in the same folder as the scene:
`hook.mp3` (Ava's voice) and `hook-words.json` (when each word is spoken). Make them with:

```powershell
python -c "import sys, json; sys.path.insert(0, 'video'); from make_video import make_voice; t = open('video/styles/hook.txt').read(); json.dump(make_voice(t, 'video/styles/hook.mp3'), open('video/styles/hook-words.json', 'w'))"
```

| File | Tool | Look | How to run |
|---|---|---|---|
| `khan-hook.js` | [khan-explainer](https://github.com/haiderfarooq3/khan-explainer) (MIT) | Chalk on a blackboard, drawn as it's said | Clone the repo, `cd scripts; npm install`, then `node <repo>/scripts/render.js khan-hook.js khan-hook.mp4`. It expects Mac handwriting fonts; we swapped in Patrick Hand. |
| `manim_hook.py` | [Manim](https://www.manim.community) | 3Blue1Brown-style maths animation | Separate venv: `uv pip install manim` (on Linux also `apt install libpango1.0-dev`), then `manim -qh manim_hook.py Hook` |
| `remotion-hook.tsx` | [Remotion](https://www.remotion.dev) + its official Claude skills | Clean YouTube motion graphics (React) | `npx create-video@latest --yes --blank --no-tailwind my-video`, put this file in `src/Composition.tsx`, `hook-words.json` as `src/words.json`, `hook.mp3` in `public/`, then `npx remotion render Hook out/hook.mp4`. Free for teams of up to 3. |
