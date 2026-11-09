#!/usr/bin/env python3
"""Build the reference library: one folder per animation found in the reference videos.

This is the "brain" the style skill picks designs from. A training pass over ~20
reference videos typically yields a few hundred animations, each saved as a folder
named like "V01-A06 Box wipe, line leads to icon" holding four files:

  still.png   the keyframe (the frame that best shows the finished design)
  strip.jpg   every frame of the animation tiled in order, each labelled with frame + ms
  clip.mp4    the animation itself, cut from the reference video
  notes.md    category, source frames, duration, the words it sits on, and a
              precise description of the design and the motion (what moves, how far,
              how fast, the easing) so it can be recreated

Claude writes animations.json during the frame-by-frame breakdown; this script turns
it into the folders and an index.json the board and the plan document read.

Usage:
  python build_reference_library.py animations.json --out <style>/library [--strip-width 150] [--force]

animations.json:
  {"style": "minimal-premium",
   "videos": {"V01": "refs/01.mp4", "V02": "refs/02.mp4"},
   "animations": [
     {"id": "V01-A06", "video": "V01", "start_s": 22.2, "end_s": 24.0,
      "title": "Box wipe, line leads to brain", "category": "Line + Illustrations",
      "words": "neurobiological benefits to that.", "keyframe_s": 23.83,
      "scene_type": "cut-away", "notes": "white sans word gets an azure box wiping L->R ..."}]}
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile


def probe_fps(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=r_frame_rate", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    n, d = out.split("/")
    return float(n) / float(d)


def safe_name(s):
    # Windows drops trailing spaces/dots from folder names, so trim after cutting to length
    return re.sub(r'[<>:"/\\|?*]', "", s)[:80].strip().rstrip(".")


MAX_STRIP_FRAMES = 240


def make_strip(frames_dir, out_path, fps, start_frame, width):
    from PIL import Image, ImageDraw, ImageFont
    files = sorted(f for f in os.listdir(frames_dir) if f.endswith(".jpg"))
    if not files:
        return 0
    with Image.open(os.path.join(frames_dir, files[0])) as first:
        h = int(first.height * width / first.width)
    # long entries (a whole-reel layout system) would exceed JPEG's 65500 px limit:
    # keep every frame up to MAX_STRIP_FRAMES, otherwise sample evenly and label the real frame
    step = max(1, math.ceil(len(files) / MAX_STRIP_FRAMES))
    picked = list(enumerate(files))[::step]
    cols = 8
    rows = math.ceil(len(picked) / cols)
    label_h = 16
    sheet = Image.new("RGB", (cols * width, rows * (h + label_h)), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 11)
    except OSError:
        font = ImageFont.load_default()
    for k, (idx, f) in enumerate(picked):
        with Image.open(os.path.join(frames_dir, f)) as src_im:
            im = src_im.resize((width, h))
        x, y = (k % cols) * width, (k // cols) * (h + label_h)
        sheet.paste(im, (x, y))
        fr = start_frame + idx
        draw.text((x + 3, y + h + 2), f"f{fr}  {int(round(fr / fps * 1000))}ms", fill=(200, 200, 200), font=font)
    sheet.save(out_path, quality=88)
    return len(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--strip-width", type=int, default=150)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    spec = json.load(open(args.spec, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(args.spec))
    videos = {k: (v if os.path.isabs(v) else os.path.join(base, v)) for k, v in spec["videos"].items()}
    os.makedirs(args.out, exist_ok=True)
    index = {"style": spec.get("style", ""), "animations": []}
    fps_cache = {}

    for a in spec["animations"]:
        src = videos[a["video"]]
        fps = fps_cache.setdefault(src, probe_fps(src))
        folder = os.path.join(args.out, safe_name(f'{a["id"]} {a["title"]}'))
        rel = os.path.relpath(folder, args.out)
        entry = dict(a, folder=rel, still=f"{rel}/still.png", strip=f"{rel}/strip.jpg",
                     clip=f"{rel}/clip.mp4")
        index["animations"].append(entry)
        if os.path.isdir(folder) and not args.force:
            continue
        os.makedirs(folder, exist_ok=True)
        s, e = float(a["start_s"]), float(a["end_s"])
        f0, f1 = int(round(s * fps)), int(round(e * fps))
        key = float(a.get("keyframe_s", (s + e) / 2))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{key:.3f}", "-i", src,
                        "-frames:v", "1", os.path.join(folder, "still.png")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-i", src, "-t", f"{e - s:.3f}",
                        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac",
                        os.path.join(folder, "clip.mp4")], check=True)
        with tempfile.TemporaryDirectory(prefix="strip_", ignore_cleanup_errors=True) as tmp:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-i", src, "-t", f"{e - s:.3f}",
                            "-vf", f"scale={args.strip_width * 2}:-2", "-q:v", "3",
                            os.path.join(tmp, "%05d.jpg")], check=True)
            n = make_strip(tmp, os.path.join(folder, "strip.jpg"), fps, f0, args.strip_width)
        notes = [f'# {a["id"]} — {a["title"]}', "",
                 f'- Category: {a.get("category", "")}',
                 f'- Scene type: {a.get("scene_type", "")}',
                 f'- Source: {a["video"]} frames {f0}–{f1} ({s:.1f}–{e:.1f} s, {n} frames ≈ {int(round((e - s) * 1000))} ms)',
                 f'- Words: "{a.get("words", "")}"',
                 f'- Keyframe: f{int(round(key * fps))}', "", a.get("notes", "")]
        open(os.path.join(folder, "notes.md"), "w", encoding="utf-8").write("\n".join(notes) + "\n")
        print(f"built {rel} ({n} frames)")

    cats = {}
    for a in index["animations"]:
        cats[a.get("category", "")] = cats.get(a.get("category", ""), 0) + 1
    index["counts"] = cats
    json.dump(index, open(os.path.join(args.out, "index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f'{len(index["animations"])} animations indexed -> {os.path.join(args.out, "index.json")}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
