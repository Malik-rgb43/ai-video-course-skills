# The review loop (drafts, notes, rounds, final)

The owner's taste finishes every edit. This loop is how notes reach Claude exactly and how
each round makes every video better, not only the one that got the note.

## Show the work without being asked
- Phase A: the style board opens as soon as it exists (checkpoint 1).
- Phase B: the edit plan opens before any build code (checkpoint 2). If there are captions,
  show the caption look (font, size, height) at the start.
- After every draft render: open the review page in the same turn, unasked.

## Drafts
- Render drafts at low quality and with a rough music bed, so the owner judges the real feel
  (HyperFrames: `render --quality draft`; other engines: 540p, fast preset).
- One draft render per round per video. Never render the final before the owner says OK.
- Say plainly that a first draft is about 60-70 % of the way and the notes finish it.

## The review page (`assets/review-template.html`)
A ready page in the course design (RTL Hebrew, Karantina / Heebo, white-black-violet, light and
dark). Fill its `review-data` JSON block: `title`, `round`, `project`, `fps`, `lang` (speech
language, default `he-IL`) and `videos[]`, each with `id`, `title`, `subtitle`, optional `thumb`
and `versions[]` (`label`, `file`, `date`, newest last). Publish it as an artifact with the
drafts as supporting files (540p proxies, under ~15 MB each), or open it from a local folder.
What the owner gets:
- a frame-accurate player (frame / second steps, keyboard: space, arrows, Shift+arrows, N);
- note kinds (fix / liked / note) and three scopes: **one frame**, **a range** (mark start and
  end) and **the whole video**;
- **drawing on the frame** (four colours, undo, clear); strokes are saved with the note as 0-1
  coordinates of the frame, so Claude can redraw them on the extracted frame;
- **voice dictation** through the browser's speech recognition (Chrome / Edge), with a hint to
  use the keyboard's own dictation when it is not supported;
- a versions list per video, a notes count / approved mark on each video tab;
- **Send notes** copies all unsent notes as numbered text (and any unsent draft text in the
  box), and downloads a JSON file when there are drawings; **Approve** copies an approval line;
  **Download / Load JSON** moves notes between browsers.
Notes live in the viewer's browser (localStorage) until they are sent; drafts autosave. The
owner pastes the text (and attaches the JSON) back into the chat. If the artifact runtime
offers a shared database, you may wire the same note objects to it instead, so Claude reads
them directly; keep the same fields (`video`, `version`, `kind`, `mode`, `t`, `t2`, `frame`,
`text`, `strokes`, `sent`).
If no page can be shown, accept the same thing as text: one numbered note per line,
`0:12.40 - the caption is late`.

## Reading notes
- Read every note, including **drafts** the owner never sent (the page's "Send" includes
  unsent draft text; ask for the JSON or the text if the owner only says "I left notes").
- Look at every attached frame and drawing before fixing. Extract frames ±1 s around the time
  to see the motion the note is about.
- Restate each note as one concrete change ("move the chip under the speaker layer at 0:14.2")
  and keep the owner's words next to it.

## Fixing
- Batch: all notes of the round → fix → one draft render → next round. Never render per note.
- **Same note in two rounds = a global rule.** Write it into the style's STYLE.md / style
  skill under "Review-round rules" with the date, and fix every occurrence in every video,
  not only the noted time.
- "Delete this" means delete and centre what is left; do not swap in a new prop unless asked.
- "Boring / banal / static / looks AI" means replace the beat with a new idea (craft-rules §1),
  not add more motion to the old one.
- Keep everything the owner added himself and every note already fixed. Back up the build
  before a round (`build.pre-r2.py`).
- Log each round in `revisions.md`: note, change, status.

## Verify before handing back
- Validate (0 errors), snapshot every noted time ±0.5 s at 0.2 s steps and every entrance or
  exit you changed. Read the snapshots and confirm each note is fixed.
- Report one line per note: number, what changed. Then render the round's draft.

## Final
Only on the owner's explicit OK: final quality render, loudness pass, a last look at a 2.5 s
contact sheet of the whole video for empty frames and leftovers, then deliver with the
`SOURCES.md` list.
