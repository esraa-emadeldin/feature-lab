"""Make the cartoon video.

How it works, step by step:
  1. Open stage.html in a hidden browser and read the list of scenes from scenes.js
     (each scene has the sentence to say and a function that draws it).
  2. For each scene, ask Microsoft's free neural voice (edge-tts) to read the sentence.
     We also get the exact time every word is spoken, so drawings can appear "on the word".
  3. Draw the scene frame by frame in the browser and take a screenshot of each frame.
  4. Glue the frames and the voice together into one MP4 with ffmpeg.

Usage (from the project folder, with the .venv active):
  python video/make_video.py                 # the whole video
  python video/make_video.py --only hook     # just one scene (fast, for testing)
  python video/make_video.py --still hook 6  # save one PNG of scene "hook" at 6 seconds
"""

import argparse
import os
import subprocess
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

VOICE = "en-US-AvaMultilingualNeural"  # the voice you picked
FPS = 24  # frames per second; 24 is the classic cartoon frame rate
WIDTH, HEIGHT = 1280, 720  # page size; screenshots are 1.5x bigger, so the video is 1920x1080
PAUSE_AFTER = 0.6  # seconds of quiet at the end of each scene, so it doesn't feel rushed

HERE = Path(__file__).parent
BUILD = HERE / "build"  # everything we generate goes here (it's in .gitignore)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()  # a copy of ffmpeg that comes with pip, no install needed


def make_voice(text, mp3_path):
    """Read `text` aloud with edge-tts. Save the audio and return each word's timing."""
    # The proxy is only needed in some cloud setups; on a normal computer it's None.
    tts = edge_tts.Communicate(text, VOICE, boundary="WordBoundary", proxy=os.environ.get("HTTPS_PROXY"))
    words = []
    with open(mp3_path, "wb") as f:
        for chunk in tts.stream_sync():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # edge-tts counts time in units of 100 nanoseconds; divide by 10 million for seconds.
                words.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10_000_000,
                    "end": (chunk["offset"] + chunk["duration"]) / 10_000_000,
                })
    return words


def to_wav(mp3_path, wav_path, seconds):
    """Convert the mp3 to a wav that is exactly `seconds` long (padded with silence)."""
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", str(mp3_path),
         "-af", "apad", "-t", f"{seconds:.3f}", "-ar", "48000", "-ac", "1", str(wav_path)],
        check=True,
    )


def wav_length(wav_path):
    """How many seconds of sound are in a wav file."""
    with wave.open(str(wav_path)) as w:
        return w.getnframes() / w.getframerate()


def render_frames(page, scene_index, words, seconds, mp4_path):
    """Draw every frame of one scene and pipe the screenshots straight into ffmpeg."""
    page.evaluate("([i, words]) => loadScene(i, words)", [scene_index, words])
    ffmpeg = subprocess.Popen(
        [FFMPEG, "-y", "-loglevel", "error",
         "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",  # frames come in through a pipe
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(mp4_path)],
        stdin=subprocess.PIPE,
    )
    total = int(seconds * FPS)
    for frame in range(total):
        page.evaluate("t => drawAt(t)", frame / FPS)  # t = time in seconds
        ffmpeg.stdin.write(page.screenshot(type="jpeg", quality=92))
    ffmpeg.stdin.close()
    ffmpeg.wait()


def join_scenes(parts, out_path):
    """Put the scenes one after another and add each scene's voice."""
    # ffmpeg's "concat" reads a small text file listing the pieces in order.
    video_list = BUILD / "video_list.txt"
    audio_list = BUILD / "audio_list.txt"
    video_list.write_text("".join(f"file '{p['mp4'].name}'\n" for p in parts))
    audio_list.write_text("".join(f"file '{p['wav'].name}'\n" for p in parts))
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(video_list),
         "-f", "concat", "-safe", "0", "-i", str(audio_list),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_path)],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Make the stickman video.")
    parser.add_argument("--only", help="make just this one scene (use its id from scenes.js)")
    parser.add_argument("--still", nargs=2, metavar=("SCENE", "SECONDS"), help="save one PNG frame")
    args = parser.parse_args()
    BUILD.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1.5)
        page.goto((HERE / "stage.html").resolve().as_uri())
        page.evaluate("document.fonts.ready")  # wait for the handwriting font to load
        scenes = page.evaluate("SCENES.map(s => ({id: s.id, say: s.say}))")

        wanted = args.still[0] if args.still else args.only
        if wanted and wanted not in [s["id"] for s in scenes]:
            raise SystemExit(f"No scene called {wanted!r}. Scenes: {[s['id'] for s in scenes]}")

        parts = []
        for i, scene in enumerate(scenes):
            if wanted and scene["id"] != wanted:
                continue
            name = f"{i:02d}-{scene['id']}"
            print(f"[{name}] voice...", flush=True)
            mp3 = BUILD / f"{name}.mp3"
            words = make_voice(scene["say"], mp3)
            seconds = words[-1]["end"] + PAUSE_AFTER  # scene lasts until the last word, plus a pause

            if args.still:  # just one picture, for checking the drawing quickly
                page.evaluate("([i, words]) => loadScene(i, words)", [i, words])
                page.evaluate("t => drawAt(t)", float(args.still[1]))
                png = BUILD / f"{name}-{args.still[1]}s.png"
                page.screenshot(path=str(png))
                print(f"Saved {png}")
                return

            wav = BUILD / f"{name}.wav"
            to_wav(mp3, wav, seconds)
            seconds = wav_length(wav)
            print(f"[{name}] drawing {int(seconds * FPS)} frames ({seconds:.1f}s)...", flush=True)
            mp4 = BUILD / f"{name}.mp4"
            render_frames(page, i, words, seconds, mp4)
            parts.append({"mp4": mp4, "wav": wav})
        browser.close()

    out = BUILD / (f"{args.only}.mp4" if args.only else "feature-lab-video.mp4")
    join_scenes(parts, out)
    print(f"Done: {out}")


if __name__ == "__main__":
    main()
