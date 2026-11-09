# Pitfalls we hit, and the fix for each

Real bugs from editing a batch of Reels with this skill. Check this list before building and
again when something "jumps", "flashes" or "sounds cut".

## 1. A tween helper that resets every property makes elements snap
**Symptom:** the cursor jumps across the screen; cards pop in instead of flying in; an element
flickers to its start position halfway through a move.
**Cause:** a shared helper like `anim(el, {x, y, scale, opacity, rotate})` wrote ALL properties
of the element on every tween, so a second tween on the same element (or an overlapping one)
reset the properties the first one was animating.
**Fix:**
- A tween sets only the properties it animates. Never write defaults for the others.
- On one element, a move does not start before the previous move on that element ends
  (or chain them on one timeline with explicit start times).
- Set the start state once, at the element's creation (e.g. off-frame), not inside each tween.
```js
// wrong: every call rewrites x, y, scale, opacity
function anim(el, t, to) { tl.fromTo(el, {x:0, y:0, scale:1, opacity:1}, {...DEFAULTS, ...to}, t); }
// right: only what this move changes; start state set once
gsap.set(cursor, {x: 1300, y: 900});            // off-frame, once
tl.to(cursor, {x: 540, y: 820, duration: .7, ease: "expo.out"}, 2.0);
tl.to(cursor, {x: 610, y: 1010, duration: .5, ease: "expo.inOut"}, 2.7); // starts after the first ends
```

## 2. In-composition cuts break everything after them
**Symptom:** after removing a doubled word inside the composition, captions, B-roll and the CTA
drift; a word ending is clipped.
**Cause:** the speaker video, cut-out and audio were split into clips with media offsets
(`data-media-start` in HyperFrames), but later times were not remapped, or the cut point came
from transcript timings.
**Fix:**
- Prefer re-cutting the edit-ready file if nothing is built yet. Once beats exist, split the
  speaker's video, cut-out and audio into clips with matching media offsets, all with the same
  ranges.
- Find the real word boundaries: re-transcribe the window without VAD and without context
  (`transcribe_words.py --start --end --no-vad --no-context`) and read the energy chart
  (`word_edges.py --at <t>`). Keep a 40-80 ms tail after the word's end.
- Keep one table of removed spans and remap EVERY later time through it (captions, beats,
  SFX, CTA, music cues). Then re-check captions, B-roll and the CTA after the shift.
- Re-listen to the result. Owners notice clipped word endings.

## 3. Short full-face moves look like a glitch
Full-face moves shorter than ~1.5 s read as an error. Keep short beats in the inset.
B-roll must stay on screen until the face covers it; if it leaves first, the frame flashes empty.

## 4. Very short captions flash
A caption shorter than 0.3 s on screen reads as a flicker. Merge it with its neighbour.

## 5. SFX fatigue
The same whoosh / riser / "filling" sound repeated is the first sound note owners give.
Same file at most twice per video, never twice within 4 s, no repeated riser bed. Keep a SFX
log (time, file) and check it before the mix.

## 6. Pop-ins and fade-outs in place look cheap
Every element enters from outside the frame and leaves past the edge, slowly
(0.6-0.9 s in, 0.45-0.6 s out). Search the build for opacity-only entrances and replace them.

## 7. Decorative 3D gets cut
Owners delete 3D props that are not the point (pens, gems, magnets, magnifiers, background
letters, stopwatches, crowns). Use 3D only when the object IS the idea of the sentence, and
only if it looks premium (real materials, bevels, studio light, contact shadow).

## 8. A label above the speaker during a full-face move
A chip or label layered above the speaker while the face grows to full screen looks wrong.
Put it under the speaker layer (z-order), or move it out before the move.

## 9. Red circles that miss the head
A ring drawn at a guessed position floats beside the face. Fit it to the measured face box
(a face detector or the matte), draw it on slowly (~0.8 s), start a little early, remove it
when the beat ends.

## 10. Review notes that were never sent
Owners type notes on the review page and close it without pressing send. Read draft notes too.
Batch all notes → fix → one draft render per round; final render only on the owner's OK.

## 11. A note repeated in two rounds
If the owner repeats a note, it is not about one frame any more: make it a global rule in the
style, fix every video, and write it into the style's "Review-round rules".

## Smaller ones
- **Two copies of the speaker drift.** A blurred background copy of the same video under a
  cut-out drifts out of sync. Use a still clean plate of the room instead.
- **Transcripts drift on references.** Word timings can run 0.3-0.5 s late on downloaded
  reels; when measuring lags (word → animation), check against burned-in captions or the frame.
- **Non-ASCII paths.** Some decoders fail on Hebrew or other non-ASCII paths on Windows; the
  scripts decode to a temp WAV with an ASCII path first. Do the same in your own tools.
- **Huge contact strips.** JPEG cannot exceed 65,500 px per side; the library script samples
  long animations (max 240 frames per strip).
- **Artifact limits.** One publish takes at most 255 files; a published clip must stay under
  ~15 MB (publish a 540p proxy).
- **Empty headline mid-morph.** When a card morphs into the next one, the next headline must
  already be in place as the card lands.
- **Ground change during a move** to the full face reads as a flash. Change the ground only on
  a hard cut or an empty frame.
