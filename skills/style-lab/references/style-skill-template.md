# Template: the generated style skill (step A5)

Write this to `~/.claude/skills/style-<slug>/SKILL.md`, filled from the board, the breakdown and
the library. Keep every rule numbered and measurable; a plan or a revision note must be able to
say "rule 7" and mean one thing. Replace every <…>.

```markdown
---
name: style-<slug>
description: The <Style Name> editing style (Hebrew name: <name as the user calls it>; registry slug <slug>) for <format, e.g. 9:16 talking-head reels>, trained on <N> reference videos of <creator/source>. <One sentence on the look: grounds, type, accent, motion.> Use whenever the user wants to edit, plan, caption or design a clip "in the <Style Name> style", "like <creator>", or names this style. Editing runs through the style-lab skill (phase B); this skill holds the style's rules, tokens and reference library.
---

# <Style Name>

Registry: `<slug>` in ~/.claude/style-lab/styles.json · fonts: <brand|reference> · colours: <brand|reference>

Trained <date> from <N> reference videos (<creator>, list in <pack>/refs/sources.md) and the style
board <board artifact URL>. Library: <absolute path>/library (<count> animations, index.json).
To edit a clip in this style, follow style-lab phase B (B1–B6) with this skill loaded.

## What makes it work
<3–5 sentences: the feeling, the discipline, what is never done.>

## Tokens
| Token | Value | Notes |
|---|---|---|
| Main font | <brand default: Heebo, weights> | <reference's original, e.g. Inter> |
| Special font | <brand default: Karantina 700> | <reference's original; when used> |
| Mono font | <brand default: Consolas / Courier New> | <when used> |
| Colours | <brand tokens from style-lab references/brand-defaults.md> | <reference's original hex; where each is allowed> |
| Grounds / textures | <…> | <strength, e.g. paper grain 12 % opacity> |
| Line work / shapes | <…> | <thickness px at 1080×1920> |
| Sizing | <ratios> | <e.g. bold word 2.5× light line> |
| Layout / safe zones | <…> | <caption band y-range, margins> |

## Rules (numbered)
1. <Caption rule …>
2. …
(Every rule: what, measured value, when it applies. Cite the board callout it came from.)

## Categories
### <n>. <Category name>  (<scene type: a-roll / overlay / cutaway>)
- Design: <ground, texture, type pair, colour, element style, position>
- Motion: <in/out durations in frames at <fps>, easing, camera moves>
- Placement: <which kinds of script lines get this scene; how long after the trigger word>
- Refs: <V##-A## — one-line description> (2–3)

## Planning patterns (from the references)
- <e.g. Announce a new idea on the face; describe it with a visual.>
- <Opening: …> <Ending: …> <Rhythm: a cut-away every ~N s; never two of the same category back to back …>

## Way of thinking (how a beat is designed in this style)
<3-6 short principles, e.g. "the visual is a metaphor for the point, not the noun";
"show the real tool working"; "one idea per beat, never repeated". See style-lab
references/craft-rules.md for the general ones; write only what is specific here.>

## Sound profile
- Music: <feel, level under voice in LUFS or dB>
- Effects: <text appear → click; line/graph draw → marker; transition → whoosh; …>, density ≈ <n per minute>

## Review-round rules (added after each round)
<Numbered, dated. A note the owner gave twice becomes a rule here and applies to every
video in this style. Example: "R3.1 Every B-roll element enters from outside the frame and
leaves past the edge (2026-11-06)".>

## Known gaps
<what the references did not show enough of; what to ask the user>
```

After writing it, list it to the user with its name and tell them a new session will pick it up
(skills load at session start).
