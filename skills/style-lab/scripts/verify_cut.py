"""Check a finished silence/retake cut against a fresh transcript of the cut file itself.

Compares the words the cut was supposed to keep (<stem>.words.json, remapped from the raw
transcript) with a new transcript of the rendered cut (verify.words.json). Reports:
  - extra words heard in the cut (a leftover syllable, half word or retake fragment at a cut point)
  - missing words (a word chopped by a cut)
  - pauses still longer than --max-gap-ms between spoken words
Small spelling differences between two ASR passes are ignored (normalised comparison).

Usage: python verify_cut.py <edit_ready.words.json> <verify.words.json> [--max-gap-ms 450]
Exit 0 = clean, 1 = something to look at.
"""
import argparse
import difflib
import json
import re
import sys


def norm(w):
    w = re.sub(r"[^\w]", "", w.lower())
    return w.replace("'", "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("expected")
    ap.add_argument("heard")
    ap.add_argument("--max-gap-ms", type=int, default=450)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    exp = json.load(open(a.expected, encoding="utf-8"))["words"]
    got = json.load(open(a.heard, encoding="utf-8"))["words"]
    e = [norm(w["w"]) for w in exp]
    g = [norm(w["w"]) for w in got]
    issues = []
    sm = difflib.SequenceMatcher(None, e, g, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        ew = " ".join(w["w"] for w in exp[i1:i2])
        gw = " ".join(w["w"] for w in got[j1:j2])
        t = (got[j1]["start_ms"] if j1 < len(got) else got[-1]["end_ms"]) / 1000
        if op == "replace" and difflib.SequenceMatcher(None, "".join(e[i1:i2]), "".join(g[j1:j2])).ratio() > 0.6:
            continue  # the same words, spelled differently by the second ASR pass
        kind = {"insert": "EXTRA", "delete": "MISSING", "replace": "DIFF"}[op]
        issues.append(f"  {t:7.2f}s {kind}: expected [{ew}] heard [{gw}]")
    for p, n in zip(got, got[1:]):
        if n["start_ms"] - p["end_ms"] > a.max_gap_ms:
            issues.append(f"  {p['end_ms']/1000:7.2f}s GAP {(n['start_ms'] - p['end_ms'])/1000:.2f}s between [{p['w']}] and [{n['w']}]")
    ratio = sm.ratio()
    print(f"match {ratio:.3f}, {len(exp)} expected / {len(got)} heard words, {len(issues)} item(s)")
    print("\n".join(issues))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
