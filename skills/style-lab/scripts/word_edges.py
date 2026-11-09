#!/usr/bin/env python3
"""Energy profile around a cut point, to find where a word really ends (or starts).

Transcripts place word edges +-50-150 ms off, and an edit that trusts them clips the
last consonant or leaves a breath. This prints the loudness of every 10 ms slice in a
window as a bar chart, marks the quietest slices, and suggests a cut point: after the
word's energy falls under the noise floor, plus a 40-80 ms tail so the ending breathes.

Usage:
  python word_edges.py <video_or_audio> --at 12.84 [--window 0.6] [--tail-ms 60]
  python word_edges.py <video_or_audio> --start 12.4 --end 13.4

Read the chart: speech is the tall run of bars; the word ends where the bars drop to the
floor and stay there. Cut at that point + tail. If the bars never reach the floor before
the next word, the words are joined: do not cut between them.
Needs ffmpeg only (no numpy).
"""
import argparse
import array
import math
import shutil
import subprocess
import sys

RATE = 16000
SLICE = RATE // 100  # 10 ms


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("--at", type=float, help="centre time in seconds")
    ap.add_argument("--window", type=float, default=0.6, help="seconds on each side of --at")
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    ap.add_argument("--tail-ms", type=int, default=60)
    ap.add_argument("--floor-db", type=float, default=None, help="noise floor; default = 20th percentile + 6 dB")
    a = ap.parse_args()
    if shutil.which("ffmpeg") is None:
        print("blocked: ffmpeg not on PATH", file=sys.stderr)
        return 2
    if a.at is not None:
        start, end = max(0.0, a.at - a.window), a.at + a.window
    elif a.start is not None and a.end is not None:
        start, end = a.start, a.end
    else:
        ap.error("give --at or --start and --end")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", a.source,
                          "-vn", "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    pcm = array.array("h")
    pcm.frombytes(raw[: len(raw) // 2 * 2])
    if sys.byteorder == "big":
        pcm.byteswap()
    dbs = []
    for i in range(0, len(pcm) - SLICE + 1, SLICE):
        chunk = pcm[i:i + SLICE]
        rms = math.sqrt(sum(x * x for x in chunk) / SLICE) / 32768
        dbs.append(20 * math.log10(rms) if rms > 0 else -96.0)
    if not dbs:
        print("no audio in that window", file=sys.stderr)
        return 1
    floor = a.floor_db if a.floor_db is not None else sorted(dbs)[len(dbs) // 5] + 6
    lo = min(dbs)
    for k, d in enumerate(dbs):
        t = start + k / 100
        n = int(max(0, d - lo) / 1.5)
        mark = "  <- floor" if d <= floor else ""
        print(f"{t:8.2f}s {d:6.1f} dB |{'#' * n}{mark}")
    # first sustained drop to the floor (3 slices = 30 ms) after the loudest slice
    peak = max(range(len(dbs)), key=lambda k: dbs[k])
    end_k = None
    for k in range(peak, len(dbs) - 2):
        if all(dbs[j] <= floor for j in range(k, k + 3)):
            end_k = k
            break
    print(f"\nnoise floor {floor:.1f} dB, loudest at {start + peak / 100:.2f}s")
    if end_k is None:
        print("no silence after the loudest point in this window: the words run together, do not cut here")
    else:
        t_end = start + end_k / 100
        print(f"speech falls to the floor at {t_end:.2f}s -> cut at {t_end + a.tail_ms / 1000:.2f}s "
              f"(+{a.tail_ms} ms tail)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
