# Worked example: the "3D + paper" style (a finished style pack, condensed)

This is a real style trained and approved with style-lab, used as the worked example of what a
finished STYLE.md looks like after review rounds. It was made for the course's own organic
Reels (9:16 talking head, Hebrew, one speaker, an Instagram comment-keyword CTA at the end).
It is an example to learn from, not a default: train your own style, or start from this one
and change it.

How it was reached: a first style trained from reference reels (split stage, speaker inset,
1-2 word captions, a headline bar, working UI mockups) was built for a batch of videos; the
owner then loved one beat (a photoreal gold trophy rendered in 3D on a clean white card over a
light grid) and asked for a direction built from it. One video was rebuilt that way, approved
on its second draft with no notes, and became the style for every video. Three review rounds
across the batch then added the rules marked R2 / R3.

## Way of thinking (approved with the style)
1. **Ask what the point is, not what the noun is.** The visual is a metaphor. "The best new
   voice model" → a gift box opens and the logo rises out of it. "More natural" → a winner's
   trophy. "Comparison" → two gramophone horns.
2. **Show the real thing working.** Rebuild the real tool UI: real URL, real logo, cursor
   clicks, typing letter by letter, waveforms and counters that run. A comparison uses the same
   sentence in both tools, and the real output plays.
3. **Make the invisible visible.** Sound comes out of the horn as arcs sized by the real audio
   loudness; progress shows as bars and counters.
4. **Reference first.** Copy a real reference's physics (anticipation, overshoot, contact
   shadow, weight). Anything generic, floaty or glossy-blob reads as "AI" and gets replaced.
5. **One idea per beat, never repeated.** Something always moves; nothing is empty more than
   0.25 s; no half-frame is empty.

## The look
| Token | Value |
|---|---|
| Ground | light violet-grey grid on near-white; dark ground only for the CTA, entered on a hard cut |
| Cards | white and fibre-paper cards, soft contact shadows |
| Hero objects | own 3D renders: gold, violet `#7c5cff`, white, black; studio light, violet rim light; transparent PNG sequences |
| Paper | an ANIMATION, never a background: slips that drop, hinge folds, a copy peeling off with a corner curl, pop-ups |
| Fonts | Karantina 700 (key words, headlines), Heebo (captions, labels, -0.04em), Consolas (code-like) |
| Blur | none: no rack focus, no depth of field, no blurred backgrounds; short motion blur on fast whips only |
| Easing | expo out for entrances, expo in for exits, expo in-out for moves, ease-out for counters |

## Rules
1. Transitions: a hard cut, or clear the frame and bring the next beat in. The ground never
   changes during the move to the speaker's full face.
2. Captions: 1-2 words. In full-face shots, about 120 px under the chin (measured per shot),
   white text on a soft grey pill (~50 % opacity). (R2)
3. Every scene change has a real exit of the old scene and an entrance of the new one; no
   leftovers. (R2)
4. Slower and cleaner: entrances a little earlier and longer, overlapping slightly, fast at the
   start and settling slower. (R2)
5. A 3D object must earn its place; deleted props are not replaced unless asked; a 3D object
   that stays is re-rendered properly (materials, bevels, studio light, contact shadow). (R2)
6. Face highlights: red brush strokes fitted to the head, drawn on in sync, started a bit early,
   removed when the beat ends. (R2)
7. UI actions press the real UI button (the app's own send button), never an invented 3D key. (R2)
8. Every B-roll element flies in from outside the frame and out past the edge; 0.6-0.9 s in,
   0.45-0.6 s out; groups offset 0.08-0.12 s. (R3)
9. Elements centred in the area above the speaker inset; at most 2-3 on screen; the hook gets
   one strong B-roll beat. (R3)
10. No decorative 3D (pen, gem, magnet, magnifier, big background letters). Emphasis =
    highlight / marker / scale on the real thing. (R3)
11. SFX on visible events only; a file at most twice per video, never twice within 4 s; no
    repeated riser / "filling" sound. (R3)
12. Full-face moves last at least ~1.5 s, and B-roll stays until the face covers it. (R3)
13. No cut mid-word; ~1 s hold at the end if the video ends mid-speech. (R3)

## CTA (comment keyword)
- Hard cut to dark. Headline at the very top: only the keyword on a solid violet pill (white
  Karantina), the verb ("comment") tight beside it, the second line plain white, no bar.
- A paper envelope opens and the comment sheet slides out of it; the keyword types in letter by
  letter, the cursor presses send, a heart appears, then a DM card ("the link is in your DMs")
  arrives. Holds to the last frame.

## Sound
- An SFX for every visible action at -15 to -20 dB, never over a voice sample.
- Music: instrumental, no vocals, mixed after the render with ducking under the voice, dipped
  almost to silence under samples, final -14 LUFS / -2 dBTP.

## Workflow notes
- Each video is built in its own copy of the project (speaker, words and captions kept), so the
  approved earlier version stays untouched.
- Reusable beats (envelope CTA, paste-a-copy, idea bulb) live in a kit and are copied into a
  video, never edited in place.
- Drafts at draft quality; final render only after approval.
