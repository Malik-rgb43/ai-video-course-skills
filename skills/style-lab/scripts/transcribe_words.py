#!/usr/bin/env python3
"""Word-by-word transcript at the millisecond level (local, free).

Stage 1 of every edit: a word-by-word transcript with millisecond timings. Also used
in style training, where every reference video gets one so animations can be tied to
the exact words they sit on, and for re-listening around a cut (see --start/--end).

Usage:
  python transcribe_words.py <video_or_audio> --out words.json [--language auto|he|en|...]
                             [--model small|medium|large-v3|<path>] [--device cpu|cuda]
                             [--start S --end S] [--no-vad] [--no-context]

Re-listen mode (finding hidden repeats and clipped word endings around a cut):
  python transcribe_words.py clip.mp4 --out win.json --start 12.0 --end 16.5 --no-vad --no-context
  Whisper merges a repeated take into one long word when VAD and context are on; a word
  that lasts over ~1 s usually hides a first take. Times in the output stay in the
  clip's own timeline (the window offset is added back).

Output (words.json):
  {"source": ..., "language": "en", "model": ..., "duration_ms": 57400,
   "words":    [{"i": 0, "w": "There's", "start_ms": 120, "end_ms": 410, "p": 0.98}, ...],
   "segments": [{"start_ms": 120, "end_ms": 2310, "text": "There's four career patterns,"}, ...]}

Notes:
- Audio is first decoded by ffmpeg to a 16 kHz mono WAV in a temp folder with an
  ASCII path, because some decoders choke on non-ASCII (e.g. Hebrew) paths on Windows.
- Hebrew: pass --language he. If an ivrit-ai CT2 model is installed, pass its folder
  with --model; otherwise the multilingual model is used. Never trust one pass for
  names, brands and numbers: the plan document shows the script for a human to check.
- Models are loaded from the local cache only (no silent downloads). If the model is
  missing the script stops and prints what to download, so the user can say yes first.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time


def to_wav(src: str, tmpdir: str, start=None, end=None) -> str:
    dst = os.path.join(tmpdir, "audio16k.wav")
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if start is not None:
        cmd += ["-ss", f"{start:.3f}"]
    if end is not None:
        cmd += ["-to", f"{end:.3f}"]
    cmd += ["-i", src, "-vn", "-ac", "1", "-ar", "16000", dst]
    subprocess.run(cmd, check=True)
    return dst


def probe_duration_ms(path: str) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True).stdout.strip()
    return int(round(float(out) * 1000))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("--out", required=True)
    ap.add_argument("--language", default="auto", help="speech language code, or auto (detect)")
    ap.add_argument("--model", default="small", help="faster-whisper size or local CT2 folder")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--compute-type", default="int8")
    ap.add_argument("--no-vad", action="store_true", help="keep sung or very quiet speech; use when re-listening to cuts")
    ap.add_argument("--no-context", action="store_true",
                    help="condition_on_previous_text=False: stops whisper from merging repeated takes")
    ap.add_argument("--start", type=float, default=None, help="window start in seconds (re-listen mode)")
    ap.add_argument("--end", type=float, default=None, help="window end in seconds (re-listen mode)")
    args = ap.parse_args()

    if shutil.which("ffmpeg") is None:
        print("blocked: ffmpeg not on PATH", file=sys.stderr)
        return 2
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("blocked: pip install faster-whisper", file=sys.stderr)
        return 2

    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="stylelab_") as tmp:
        wav = to_wav(args.source, tmp, args.start, args.end)
        off = int(round((args.start or 0) * 1000))
        try:
            model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type,
                                 local_files_only=True)
        except Exception as e:  # missing weights: never download silently
            print(f"blocked: model '{args.model}' is not in the local cache ({e}).\n"
                  f"Ask the user before downloading it (faster-whisper fetches it on first use "
                  f"without --local-files-only).", file=sys.stderr)
            return 2
        lang = None if args.language == "auto" else args.language
        segs, info = model.transcribe(wav, language=lang, word_timestamps=True,
                                      vad_filter=not args.no_vad, beam_size=5,
                                      condition_on_previous_text=not args.no_context)
        words, segments = [], []
        for s in segs:
            segments.append({"start_ms": int(s.start * 1000) + off, "end_ms": int(s.end * 1000) + off,
                             "text": s.text.strip()})
            for w in (s.words or []):
                words.append({"i": len(words), "w": w.word.strip(),
                              "start_ms": int(round(w.start * 1000)) + off,
                              "end_ms": int(round(w.end * 1000)) + off,
                              "p": round(float(w.probability), 3)})
            print(f"[{s.start + off / 1000:7.2f}] {s.text.strip()}", flush=True)
        dur = probe_duration_ms(wav)

    out = {"source": os.path.abspath(args.source), "language": info.language,
           "language_forced": lang is not None, "model": args.model,
           "duration_ms": dur, "word_count": len(words),
           "low_confidence": [w["i"] for w in words if w["p"] < 0.5],
           "window_s": [args.start, args.end] if (args.start is not None or args.end is not None) else None,
           "words": words, "segments": segments,
           "elapsed_s": round(time.time() - t0, 1)}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"done: {len(words)} words, language={info.language}, "
          f"{len(out['low_confidence'])} low-confidence -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
