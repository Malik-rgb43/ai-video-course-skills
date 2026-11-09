"""Registry of trained editing styles, so several styles can live side by side and the user
can pick one by name when editing.

The registry is one JSON file outside the skill folder (survives skill updates):
    ~/.claude/style-lab/styles.json   (override with --registry or STYLE_LAB_REGISTRY)

Commands:
    styles.py list [--all] [--json]
    styles.py add <slug> --name "<display name>" --pack <style pack folder> [--description ...]
                  [--skill <path to style SKILL.md>] [--creator ...] [--fonts brand|reference]
                  [--colors brand|reference] [--theme dark|light|both] [--status training|ready]
    styles.py show <slug or name>
    styles.py set <slug> key=value [key=value ...]
    styles.py remove <slug>          (removes the registry entry only, never files)
    styles.py check                  (every pack and skill path still exists)
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_REGISTRY = Path.home() / ".claude" / "style-lab" / "styles.json"
STATUSES = ("training", "ready", "archived")
EDITABLE = {"name", "description", "pack", "skill", "creator", "fonts", "colors", "status",
            "board_url", "aliases", "notes", "theme"}


def registry_path(arg):
    return Path(arg or os.environ.get("STYLE_LAB_REGISTRY") or DEFAULT_REGISTRY)


def load(path):
    if not path.exists():
        return {"version": 1, "styles": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def today():
    return dt.date.today().isoformat()


def find(data, key):
    """Match by slug, display name or alias, case-insensitive."""
    k = key.strip().lower()
    for s in data["styles"]:
        names = [s["slug"], s.get("name", "")] + s.get("aliases", [])
        if k in (n.lower() for n in names if n):
            return s
    return None


def cmd_list(data, args):
    rows = [s for s in data["styles"] if args.all or s.get("status") != "archived"]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print("no styles yet")
        return 0
    for s in rows:
        print(f"{s['slug']}\t{s.get('name','')}\t{s.get('status','')}\t{s.get('description','')}")
    return 0


def cmd_add(data, args):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.slug):
        print("slug must be lowercase latin letters, digits and dashes", file=sys.stderr)
        return 1
    if find(data, args.slug) or find(data, args.name):
        print(f"a style named {args.slug!r} or {args.name!r} already exists", file=sys.stderr)
        return 1
    skill = args.skill or str(Path.home() / ".claude" / "skills" / f"style-{args.slug}" / "SKILL.md")
    data["styles"].append({
        "slug": args.slug,
        "name": args.name,
        "description": args.description or "",
        "creator": args.creator or "",
        "pack": str(Path(args.pack).resolve()),
        "skill": skill,
        "fonts": args.fonts,
        "colors": args.colors,
        "theme": args.theme,
        "status": args.status,
        "aliases": [],
        "board_url": "",
        "created": today(),
        "updated": today(),
    })
    print(f"added {args.slug} ({args.name}), status {args.status}")
    return None


def cmd_show(data, args):
    s = find(data, args.key)
    if not s:
        print(f"no style {args.key!r}", file=sys.stderr)
        return 1
    print(json.dumps(s, ensure_ascii=False, indent=2))
    return 0


def cmd_set(data, args):
    s = find(data, args.slug)
    if not s:
        print(f"no style {args.slug!r}", file=sys.stderr)
        return 1
    for pair in args.pairs:
        if "=" not in pair:
            print(f"expected key=value, got {pair!r}", file=sys.stderr)
            return 1
        k, v = pair.split("=", 1)
        if k not in EDITABLE:
            print(f"{k!r} is not editable; use one of {sorted(EDITABLE)}", file=sys.stderr)
            return 1
        if k == "status" and v not in STATUSES:
            print(f"status must be one of {STATUSES}", file=sys.stderr)
            return 1
        if k in ("fonts", "colors") and v not in ("brand", "reference"):
            print(f"{k} must be brand or reference", file=sys.stderr)
            return 1
        if k == "theme" and v not in ("dark", "light", "both"):
            print("theme must be dark, light or both", file=sys.stderr)
            return 1
        if k == "name":
            other = find(data, v)
            if other and other is not s:
                print(f"another style is already called {v!r}", file=sys.stderr)
                return 1
        s[k] = [a.strip() for a in v.split(",") if a.strip()] if k == "aliases" else v
    s["updated"] = today()
    print(f"updated {s['slug']}")
    return None


def cmd_remove(data, args):
    s = find(data, args.slug)
    if not s:
        print(f"no style {args.slug!r}", file=sys.stderr)
        return 1
    data["styles"].remove(s)
    print(f"removed {s['slug']} from the registry (files untouched: {s['pack']})")
    return None


def cmd_check(data, args):
    bad = 0
    for s in data["styles"]:
        for key in ("pack", "skill"):
            if s.get(key) and not Path(s[key]).exists():
                level = "missing" if s.get("status") == "ready" else "not yet"
                print(f"{s['slug']}: {key} {level}: {s[key]}")
                bad += level == "missing"
    print("ok" if not bad else f"{bad} missing path(s) on ready styles")
    return 1 if bad else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--registry")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("list"); a.add_argument("--all", action="store_true"); a.add_argument("--json", action="store_true")
    a = sub.add_parser("add")
    a.add_argument("slug"); a.add_argument("--name", required=True); a.add_argument("--pack", required=True)
    a.add_argument("--description"); a.add_argument("--skill"); a.add_argument("--creator")
    a.add_argument("--fonts", choices=("brand", "reference"), default="brand")
    a.add_argument("--colors", choices=("brand", "reference"), default="brand")
    a.add_argument("--status", choices=STATUSES, default="training")
    a.add_argument("--theme", choices=("dark", "light", "both"), default="dark")
    a = sub.add_parser("show"); a.add_argument("key")
    a = sub.add_parser("set"); a.add_argument("slug"); a.add_argument("pairs", nargs="+")
    a = sub.add_parser("remove"); a.add_argument("slug")
    sub.add_parser("check")
    args = p.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = registry_path(args.registry)
    data = load(path)
    rc = {"list": cmd_list, "add": cmd_add, "show": cmd_show, "set": cmd_set,
          "remove": cmd_remove, "check": cmd_check}[args.cmd](data, args)
    if rc is None:  # a command that changed the registry
        save(path, data)
        rc = 0
    return rc


if __name__ == "__main__":
    sys.exit(main())
