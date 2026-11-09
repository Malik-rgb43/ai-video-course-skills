"""Word-level Hebrew transcript through the ivrit.ai RunPod endpoint (cloud), same output as
transcribe_words.py, so cut_silences.py and the plan document work unchanged.

Uses the official `ivrit` package (engine="runpod"), which chunks the upload itself.
Needs RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID in the environment. This is a PAID call
(RunPod serverless GPU time): use it only when the user chose cloud transcription.

Usage: python transcribe_cloud_ivrit.py <video> --out words.json [--model ivrit-ai/whisper-large-v3-turbo-ct2]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="ivrit-ai/whisper-large-v3-turbo-ct2")
    ap.add_argument("--language", default="he")
    a = ap.parse_args()
    key, ep = os.environ.get("RUNPOD_API_KEY"), os.environ.get("RUNPOD_ENDPOINT_ID")
    if not key or not ep:
        print("blocked: RUNPOD_API_KEY / RUNPOD_ENDPOINT_ID not set", file=sys.stderr)
        return 2
    import ivrit
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="ivrit_") as tmp:
        audio = os.path.join(tmp, "a.mp3")  # 16 kHz mono mp3 keeps the upload small
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.source, "-vn", "-ac", "1", "-ar", "16000",
                        "-b:a", "48k", audio], check=True)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio],
                                   capture_output=True, text=True, check=True).stdout.strip())
        model = ivrit.load_model(engine="runpod", model=a.model, api_key=key, endpoint_id=ep)
        res = model.transcribe(path=audio, language=a.language)
    words, segs = [], []
    for s in res["segments"]:
        sd = s if isinstance(s, dict) else s.__dict__
        segs.append({"start_ms": int(sd["start"] * 1000), "end_ms": int(sd["end"] * 1000), "text": sd["text"].strip()})
        for w in sd.get("words") or []:
            wd = w if isinstance(w, dict) else w.__dict__
            words.append({"i": len(words), "w": wd["word"].strip(), "start_ms": int(wd["start"] * 1000),
                          "end_ms": int(wd["end"] * 1000), "p": round(float(wd.get("probability") or 0), 3)})
    low = [w for w in words if w["p"] and w["p"] < 0.5]
    out = {"source": str(Path(a.source).resolve()), "language": a.language, "language_forced": True,
           "model": f"runpod:{a.model}", "duration_ms": int(dur * 1000), "word_count": len(words),
           "low_confidence": low, "words": words, "segments": segs, "elapsed_s": round(time.time() - t0, 1)}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"done: {len(words)} words, {dur:.0f}s audio in {out['elapsed_s']}s, {len(low)} low-confidence -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
