# Craft rules (the way of thinking + the rules that survived real review rounds)

These rules hold for every style unless the style's own STYLE.md says otherwise. They come
from editing a batch of short vertical talking-head videos with this skill and going through
several review rounds with a demanding owner: every rule below is a note that came back more
than once. Numbers are for 1080x1920 at 30 fps; scale them for other formats.

## 1. The way of thinking (design every beat with these five questions)
1. **What is the point, not the noun?** The visual is a metaphor that makes the idea land.
   "The best new model" is a gift box that opens with the logo rising out of it, not a picture
   of a model. "More natural" is a winner's trophy. "A comparison" is two objects side by side.
2. **Can I show the real thing working?** Rebuild the real tool in HTML: real URL, real logo
   (the official file, never a drawn look-alike), a cursor that clicks the real button, text
   typed letter by letter, counters and waveforms that run. A comparison feeds the SAME input
   to both sides. Mock content is marked "for illustration" (in the video's language).
3. **Can I make the invisible visible?** Sound as arcs or a live waveform sized by the real
   loudness; progress as bars and counters; time as a clock that actually turns.
4. **What is my reference for this move?** Before building a move, find a real one (the
   style's library, a catalog of motion, a real UI) and copy its physics: anticipation,
   overshoot, contact shadow, weight. Generic, floaty or glossy-blob motion reads as "AI".
   When the owner says "boring / banal / static / looks AI", replace the beat, never polish it.
5. **Is this new?** One idea per beat, never repeated inside a video: a new object, a new
   entrance, a new move each time. Something always moves.

## 2. Composition
- At most 2-3 elements on screen at once. The hook (first 3-4 s) gets ONE strong beat, not a pile.
- Elements sit in the visual centre of the free area (e.g. above a speaker inset). Nothing hugs
  an edge or sits half cut off while it is meant to be read.
- No container is empty and no headline area is blank for more than ~0.25 s; no half of the
  frame stays empty. Cards arrive already filled.
- Decoration earns nothing. A 3D object, a big background letter or a texture is there only
  when it IS the point of the sentence. Emphasis = highlight / marker / scale on the real thing.
  Textures go on 3-5 chosen scenes per video, varied, never on every scene.
- A weak asset (cheap-looking 3D, a generic icon) is replaced with a paper animation, a real
  UI or nothing. Never polish a weak asset.
- When a delete leaves a gap, centre what remains; do not fill the gap with a new prop
  unless asked.

## 3. Motion
- **Every element enters from outside the frame and leaves past the frame edge.** No fade-in
  or pop-in in place, no fade-out in place. Pick the direction from the layout: side elements
  go to their nearest edge, top elements go up.
- **Slow and clean.** Entrances 0.6-0.9 s with an ease-out (expo / quart out); exits
  0.45-0.6 s with an ease-in; moves ease-in-out ("slow-fast-slow"); counters ease-out. Never
  linear. Groups: a lead plus uneven reactions (offsets around 0.08-0.12 s, not an even stagger).
- **One curve per move, duration from distance and weight.** A long or heavy move takes longer.
  Combine properties only when they say the same thing (rise + fade = arriving).
- **Every scene change is a real exit and a real entrance.** Nothing builds on leftovers;
  nothing appears "in the middle" from nothing; nothing is left behind (rings, stickers,
  cards) when the beat ends.
- **Transitions:** a hard cut, or clear the frame and bring the next beat in. Change the
  ground (light / dark) only on a hard cut or an empty frame, never during a move.
- Holds stay alive: a slow drift or push-in (+10-40 % over the hold) so no frame is frozen.
- Motion blur only on fast whips, and short. No rack focus, no depth-of-field blur, no
  blurred backgrounds unless the style itself is built on them.
- Typed text: letter by letter, clean, high contrast, typed once (never retyped).

## 4. The speaker
- A full-face move lasts at least ~1.5 s; anything shorter feels like a glitch. Shorter beats
  stay in the inset.
- When the speaker goes full screen, B-roll stays on screen until the face covers it. Nothing
  vanishes before the move.
- During a full-face move, chips and labels sit UNDER the speaker layer, not on top.
- Never stack two videos of the same person (a blurred copy behind a cut-out drifts out of
  sync). Use one source: a cut-out over a clean plate of the empty room.
- Full-face captions sit under the chin, measured from the face box (about 120 px below it),
  on a soft grey pill (~50 % opacity) for contrast.
- Highlight rings around a head are fitted to the measured face box, drawn on slowly
  (~0.8 s), start a little before the line, and are removed when the beat ends.
- The hook is one continuous take; never splice two takes of the opening line.

## 5. Captions
- 1-2 words per caption in short-form; no gaps between captions while someone speaks.
- No caption shorter than 0.3 s on screen: merge it with its neighbour.
- One ease for all captions. Never a caption over a sound effect peak on a sentence-final word.
- Ask the caption language (or none). Never assume.

## 6. Cuts
- Natural pace: pauses of about 0.15-0.3 s at joins (pad 100-150 ms). 30 ms pads are for
  deliberately punchy styles only.
- Re-listen to every cut without VAD and without context (`transcribe_words.py --no-vad
  --no-context --start --end`). A word that lasts over ~1 s usually hides a repeated take.
- Keep a 40-80 ms tail after a word's real end (`word_edges.py`). Owners notice clipped
  endings immediately.
- No cut in the middle of a word. Check every join and the last word. If the video ends
  mid-speech, hold the last frame ~1 s and let the audio finish.
- Cut off-topic openings, laughs and throat clears even if they were said twice.
- Verify the finished cut by transcribing the cut file itself (`verify_cut.py`).

## 7. Sound
- A sound effect only on a visible event (an entrance, a click, a landing, a full-face move).
- The same SFX file at most twice per video, never twice within 4 s. No repeated
  riser / "filling" / whoosh bed: fatigue is the first sound note owners give.
- SFX at about -15 to -20 dB under the voice, never over a voice sample the video plays.
- Music: instrumental with no vocals, mixed after the render with ducking under the voice,
  dipped almost to silence under samples, final loudness about -14 LUFS / -1 to -2 dBTP.
  Only music the user is allowed to use; if posting to a platform with a music library,
  attaching the track there is often the cleanest route.

## 8. Sources and honesty
- Prefer the real thing over generic stock: the tool maker's own showcase, a real screenshot,
  the real page. Short excerpts only, with the user's permission, logged in `SOURCES.md`
  (what, where from, licence or permission, where used). Check frames for burned-in titles.
- Never invent a number, a quote, a result or a logo. Mock screens are marked as such.
- No readable text inside a generated image; text stays live (HTML).

## 9. Build hygiene
- Build 2 beats first, snapshot them, compare side by side with the approved reference, adjust,
  then build the rest.
- Validate (0 errors), then snapshot every 0.5 s (0.2 s over dense beats and the CTA) and read
  every snapshot before rendering. Look for: empty frames, leftovers, cut-off text, elements on
  top of the face, captions over the chin.
- Copy shared components into the video; never edit the shared kit in place.
