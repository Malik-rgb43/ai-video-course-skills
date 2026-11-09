# The two artifacts: style board and edit plan

Both pages (and the review room, see `review-loop.md`) are in the course design: RTL Hebrew UI,
Karantina 700 headlines, Heebo body at -0.04em, white / black / violet with light and dark
themes (a theme button on the page). Content fields can be in any language (`dir="auto"`).
Both are single HTML pages built from `assets/*-template.html` by replacing the JSON block
(`<script type="application/json" id="board-data">` / `id="plan-data"`) and publishing with
the Artifact tool. Load the `artifact-design` skill before the first publish in a session.
Images and the clip are published as supporting files with `files` (paths relative to the
page). Keep the page's `<title>` as the style or clip name ("Paper Explainer Style",
"Three Habits Edit Plan"). Both start private.

## Style board (`board.json`)
```json
{
  "example": false,
  "style": "Paper Explainer Style",
  "subtitle": "20 reference videos · 131 scenes · trained 2026-11-02",
  "tokens": {
    "fonts":   [{"name": "Heebo", "role": "main text, light + bold", "sample": "one idea", "css": "font-family:Heebo;font-weight:800"}],
    "colors":  [{"hex": "#7C5CFF", "name": "Accent violet"}],
    "textures": ["…"], "shapes": ["…"], "sizing": ["…"], "layout": ["…"]
  },
  "categories": [
    {"id": "captions", "name": "On-Screen Text (Captions)",
     "rule": "one sentence: the category's design rule",
     "tiles": [{"id": "V01-A01", "label": "common", "thumb": "thumbs/V01-A01.jpg",
                "clip": "", "strip": "thumbs/V01-A01.strip.jpg", "notes": "notes.md text"}],
     "annotations": [{"thumb": "thumbs/V01-A01.jpg",
                      "callouts": [{"x": 50, "y": 63, "label": "Multiple sans light small text"}]}],
     "why": {"design": "", "colors": "", "effects": "", "animations": ""}}
  ]
}
```
- `tiles` are the inspiration pieces (aim for 100-150). `thumb` is a 9:16 JPG ~360 px wide.
  `clip` stays empty by default (reference clips are not published); set it only if the user
  asks and the board stays private.
- `annotations[].callouts`: `x`,`y` are percent positions on the frame where the red dot sits;
  `label` is one measurable rule. 3–5 callouts per frame, at least one annotated frame per
  category. Measure on the frame (pixels, ratios), never eyeball a number you can measure.
- `why`: Claude's draft answers to the four questions; the user rewrites them on the board.
- Controls: page list (left) jumps to sections; a tile opens a detail view (still or clip,
  strip, notes); **העתקת ההערות לבורד** (copy board notes) copies every "why" answer as Markdown for the user to
  paste back. Edits are kept in the viewer's browser only, so the paste is how they reach
  Claude: apply them to `board.json` and republish to the same URL.

Thumbs: `ffmpeg -ss <t> -i refs/V01.mp4 -frames:v 1 -vf scale=360:-2 -q:v 3 board/thumbs/V01-A01.jpg`
(the library's `still.png` scaled down works too). A publish takes at most 255 files; publish
more in several calls to the same `url`.

## Edit plan (`plan.json`)
```json
{
  "example": false,
  "title": "Three habits",
  "clip": {"file": "clip.mp4", "name": "three-habits-edit-ready-9x16.mp4", "length_s": 57.4},
  "source": "My own talking-head take, 2026-11-08",
  "style": "Paper Explainer Style",
  "beats": [
    {"n": 1, "start": 0.0, "end": 1.9,
     "script": "There are three habits that decide your week",
     "seen": "A framework announced in the first line, like V04 … cut away at 1.7 s.",
     "camera": "Camera: Medium shot 0–31.8 s.",
     "pick": "A",
     "options": [
       {"key": "A", "title": "Opening zoom-out + justified number",
        "category": "On-Screen Text (Captions)", "scene_type": "a-roll",
        "desc": "Justified block … (rule 13) …", "ref": "V14-A01", "thumb": "thumbs/V14-A01.jpg"}]}
  ]
}
```
- Times are seconds on the **edit-ready** clip (after the silence cut), from
  `edit_ready.words.json`. Beats cover the clip end to end without gaps.
- `scene_type`: `a-roll` (A-roll + captions), `overlay` (Overlay on A-roll), `cutaway` (Cut-away
  scene). The beat timeline colours each beat by its chosen option's type.
- `pick` is Claude's recommendation; it starts as the chosen option and is shown as **ההמלצה שלי** (my pick).
- `seen`: why this fits, citing reference videos (V04, V08) and style rules (rule 13, §10).
- `clip.file`: publish a proxy, not the master: `ffmpeg -i edit_ready.mp4 -vf scale=540:-2 -c:v libx264 -crf 28 -preset fast -c:a aac -b:a 96k -movflags +faststart clip.mp4` (must stay under 15 MB; lower the bitrate for long clips). Each beat's player loops that beat's range.
- Controls: "לבחור בזה" (use this) chooses an option; the text box takes the user's own plan for the beat;
  **העתקת התוכנית** (copy plan) copies the whole plan as Markdown (`# תוכנית עריכה: <title>`, then per beat: time,
  script, chosen design with category, scene type and ref, the design text, and "My notes").
  The user pastes that back with the build prompt.

## Checks before publishing either page
- The JSON parses (`python -c "import json,re,sys; …"` or load it in the page once).
- Every `thumb` path exists in the `files` map.
- Hebrew text: elements already use `dir="auto"`; check one beat renders right-to-left.
