#!/usr/bin/env python3
"""Cut every silence, leaving N ms of padding (default 30 ms), from a word transcript.

Stage 2 of every edit: remove the silences between words, keeping a small pad
(30 ms = very tight and punchy; 100-150 ms = natural talking pace). Produces the
edit-ready clip AND a remapped word transcript whose timings match the new clip, so
the plan document, captions and animations all line up with the cut (never with the
raw file). Every join gets a 15 ms audio fade so cuts never click.

Usage:
  python cut_silences.py <raw_video> --words words.json --out edit_ready.mp4
                         [--pad-ms 30] [--min-gap-ms 0] [--drop "um,uh"] [--dry-run]

Writes next to --out:
  <name>.cuts.json   kept ranges in raw time + removed gaps (an EDL a human can audit)
  <name>.words.json  the transcript remapped to the cut clip's timeline

Rules:
- A word is kept from (start - pad) to (end + pad); overlapping ranges merge, so a
  gap is removed only when it is longer than 2 x pad (+ --min-gap-ms).
- --drop removes listed filler words entirely (off by default: only silence is cut).
- Video and audio are cut with the same ranges in one ffmpeg graph and re-encoded
  (frame-accurate; stream copy would snap to keyframes).
"""
import argparse
import json
import os
import subprocess
import sys


def keep_ranges(words, pad, min_gap, dur, drop):
    spans = []
    for w in words:
        if drop and w["w"].strip(".,!?").lower() in drop:
            continue
        lo = max(0, w["start_ms"] - pad, w.get("lo", 0))
        hi = min(dur, w["end_ms"] + pad, w.get("hi", dur))
        spans.append([lo, hi])
    spans.sort()
    merged = []
    for s in spans:
        if merged and s[0] - merged[-1][1] <= min_gap:
            merged[-1][1] = max(merged[-1][1], s[1])
        else:
            merged.append(s)
    return merged


def frame_db(raw):
    """20 ms RMS levels (dB) of the raw audio."""
    import subprocess
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", raw, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    fr = x[: len(x) // 320 * 320].reshape(-1, 320)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)


def quietest_ms(db, a_ms, b_ms):
    """Start time (ms) of the quietest 20 ms frame in [a_ms, b_ms]: where a take boundary cuts cleanly."""
    a, b = max(0, int(a_ms // 20)), min(len(db) - 1, int(b_ms // 20))
    if b <= a:
        return int(a_ms)
    k = a + int(db[a:b + 1].argmin())
    return k * 20


def audio_silences(raw, noise_db, min_s):
    """Silences measured on the sound itself, in ms. Catches pauses the transcript hid inside a
    stretched word (a 2 s "stall" that is really silence). The threshold adapts to the room:
    the recording's own noise floor (10th percentile of 20 ms frames) + 8 dB, never above noise_db + 12."""
    import subprocess
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", raw, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    fr = x[: len(x) // 320 * 320].reshape(-1, 320)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    thr = min(np.percentile(db, 10) + 8, noise_db + 12)
    quiet = db < thr
    out, start = [], None
    for k, q in enumerate(list(quiet) + [False]):
        if q and start is None:
            start = k
        elif not q and start is not None:
            if (k - start) * 20 >= min_s * 1000:
                out.append([start * 20, k * 20])
            start = None
    return out


def subtract_silences(ranges, silences, pad):
    """Shorten every silence inside the kept ranges to 2 x pad (0.3 s at pad 150)."""
    out = []
    for a, b in ranges:
        cur = [[a, b]]
        for s, e in silences:
            if e - s <= 2 * pad:
                continue
            cs, ce = s + pad, e - pad
            nxt = []
            for x, y in cur:
                if ce <= x or cs >= y:
                    nxt.append([x, y])
                    continue
                if cs > x:
                    nxt.append([x, cs])
                if ce < y:
                    nxt.append([ce, y])
            cur = nxt
        out.extend(r for r in cur if r[1] - r[0] > 40)
    return out


def remap(words, ranges, drop):
    out, offset_list = [], []
    acc = 0
    for a, b in ranges:
        offset_list.append((a, b, acc))
        acc += b - a
    for w in words:
        if drop and w["w"].strip(".,!?").lower() in drop:
            continue
        for a, b, base in offset_list:
            if w["start_ms"] < b and w["end_ms"] > a:
                nw = dict(w)
                nw["start_ms"] = base + (max(w["start_ms"], a) - a)
                nw["end_ms"] = base + (min(w["end_ms"], b) - a)
                nw["raw_start_ms"], nw["raw_end_ms"] = w["start_ms"], w["end_ms"]
                nw["i"] = len(out)
                out.append(nw)
                break
    return out, acc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raw")
    ap.add_argument("--words", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pad-ms", type=int, default=30)
    ap.add_argument("--min-gap-ms", type=int, default=0)
    ap.add_argument("--drop", default="", help="comma list of filler words to remove")
    ap.add_argument("--keep", default="", help='JSON file {"keep": [[first_word_i, last_word_i], ...]}: only these '
                    "word ranges survive (retakes and false starts are left out); padding never reaches into a "
                    "word that was left out")
    ap.add_argument("--audio-gaps", action="store_true",
                    help="also shorten silences found in the audio itself (inside stretched words) to 2 x pad")
    ap.add_argument("--noise-db", type=float, default=-40)
    ap.add_argument("--crf", type=int, default=16)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.load(open(args.words, encoding="utf-8"))
    words, dur = data["words"], data["duration_ms"]
    if args.keep:
        spans_i = json.load(open(args.keep, encoding="utf-8"))["keep"]
        keep_i = {i for a, b in spans_i for i in range(a, b + 1)}
        by_i = {w["i"]: w for w in words}
        db = frame_db(args.raw)
        kept = []
        for w in words:
            if w["i"] not in keep_i:
                continue
            w = dict(w)
            p, n = by_i.get(w["i"] - 1), by_i.get(w["i"] + 1)
            if p is not None and p["i"] not in keep_i:
                # next to a dropped word: cut at the quietest frame between the two (ASR word edges blur)
                w["lo"] = quietest_ms(db, min(p["end_ms"], w["start_ms"]), w["start_ms"] + 60)
            if n is not None and n["i"] not in keep_i:
                w["hi"] = quietest_ms(db, w["end_ms"] - 60, max(n["start_ms"], w["end_ms"])) + 20
            kept.append(w)
        words = kept
    drop = {d.strip().lower() for d in args.drop.split(",") if d.strip()}
    ranges = keep_ranges(words, args.pad_ms, args.min_gap_ms, dur, drop)
    if args.audio_gaps:
        sil = audio_silences(args.raw, args.noise_db, (2 * args.pad_ms + 50) / 1000)
        before = sum(b - a for a, b in ranges)
        ranges = subtract_silences(ranges, sil, args.pad_ms)
        print(f"audio gaps: {len(sil)} silences measured, {(before - sum(b - a for a, b in ranges))/1000:.2f}s more removed")
    new_words, new_dur = remap(words, ranges, drop)

    gaps, prev = [], 0
    for a, b in ranges:
        if a > prev:
            gaps.append([prev, a])
        prev = b
    if prev < dur:
        gaps.append([prev, dur])

    stem = os.path.splitext(args.out)[0]
    cuts = {"raw": os.path.abspath(args.raw), "pad_ms": args.pad_ms, "raw_duration_ms": dur,
            "cut_duration_ms": new_dur, "removed_ms": dur - new_dur,
            "kept": ranges, "removed": gaps}
    json.dump(cuts, open(stem + ".cuts.json", "w", encoding="utf-8"), indent=1)
    nd = dict(data, words=new_words, duration_ms=new_dur, word_count=len(new_words),
              cut_from=os.path.abspath(args.raw), pad_ms=args.pad_ms)
    nd.pop("segments", None)
    json.dump(nd, open(stem + ".words.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(ranges)} kept ranges, {len(gaps)} silences removed, "
          f"{dur/1000:.2f}s -> {new_dur/1000:.2f}s")
    if args.dry_run:
        return 0

    parts, labels = [], []
    fd = 0.015  # 15 ms fade at every join so no cut clicks
    for k, (a, b) in enumerate(ranges):
        s, e = a / 1000, b / 1000
        fades = (f",afade=t=in:d={fd}" if k else "") + \
                (f",afade=t=out:st={max(0, e - s - fd):.3f}:d={fd}" if k < len(ranges) - 1 else "")
        parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{k}];"
                     f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS{fades}[a{k}];")
        labels.append(f"[v{k}][a{k}]")
    graph = "".join(parts) + "".join(labels) + f"concat=n={len(ranges)}:v=1:a=1[v][a]"
    graph_file = stem + ".filter.txt"
    open(graph_file, "w", encoding="utf-8").write(graph)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", args.raw, "-filter_complex_script", graph_file,
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", str(args.crf),
           "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", args.out]
    subprocess.run(cmd, check=True)
    os.remove(graph_file)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
