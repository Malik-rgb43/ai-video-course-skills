# Brand defaults (the course brand)

These are the fonts and colours of the "וידאו עם AI" course by Gabriel Gelman, read from the
course landing page (https://www.gabriel-gelman.com/vibe-editing, CSS variables, 2026-11-03).
The site is dark only; the light theme below is derived from it with the same accent and roles.

By default every style trained with style-lab keeps the reference style's layout, motion,
placement and structure, and swaps in these fonts and colours. Two ways out:
- **Your own brand:** write your fonts and colour tokens (same tables as below) to
  `~/.claude/style-lab/brand.md`. When that file exists it replaces this one for every style.
- **The reference's look:** for one style, record `fonts=reference` / `colors=reference` in the
  registry and keep the reference's own fonts and palette.

## Fonts (same three in Hebrew and English)
| Role | Font | Use |
|---|---|---|
| Headline / key word | **Karantina 700** (400 for light lines) | the big emphasised word, titles, numbers |
| Body / captions | **Heebo** 300-800 (site uses 400 body, 600 labels, 700-800 strong) | running captions, small words, labels |
| Code-like labels | `ui-monospace, Consolas, "Courier New", monospace` | prompts, file names, terminal-like text |

Both Karantina and Heebo have Latin glyphs (the site ships `karantina-700-latin` next to the
Hebrew subset), so the English variant uses the same fonts.

Mapping a reference's type pair: its main sans → Heebo (keep the light/bold contrast); its
"special" font (serif italic, script, display) → Karantina 700. Keep the reference's size
ratios (e.g. bold word 2.5× the light line). Heebo reads best slightly tight
(`letter-spacing: -0.04em`); Karantina stays at 0. Text on an accent fill is all Karantina 700.

Load in HyperFrames / HTML:
`https://fonts.googleapis.com/css2?family=Karantina:wght@400;700&family=Heebo:wght@300;400;500;600;700;800&display=swap`

## Colours — dark (the site's own theme, default for video)
| Token | Hex | Use |
|---|---|---|
| bg | `#0b0910` | scene ground |
| bg-2 | `#110e18` | second ground, card backs |
| surface | `#17131f` | cards, panels |
| surface-2 | `#1e1929` | raised cards, inputs |
| line | `rgba(237,233,255,.09)` | hairlines, dot/grid pattern |
| line-2 | `rgba(237,233,255,.16)` | card borders |
| fg | `#f4f1fb` | main text, captions |
| muted | `#aba4bf` | secondary text |
| dim | `#7e7791` | meta, blurred/upcoming items |
| **accent** | `#7c5cff` | the one accent: bars, buttons, highlights, pulses |
| accent-hi | `#9a82ff` | accent borders, glow, hover |
| accent-text | `#b8a8ff` | accent-coloured words on dark |
| accent-ink | `#ffffff` | text on an accent fill |
| ok (green) | `#5cffb0` | right / saved / good number |
| danger | `#ff7a90` | wrong / bad / warning |
| star (gold) | `#ffc94d` | ratings, one-off highlight; stripes use `rgba(255,216,77,.75)` |
| info blue | `#4fb4ff` | only inside the blue→violet gradient |

Signature effects from the site:
- violet glow: `radial-gradient(80% 60% at 50% 30%, rgba(124,92,255,.28), transparent 70%)` over `linear-gradient(#1e1929, #110e18)`
- headline gradient text: `linear-gradient(#ffffff, #e4dcff 45%, #9a82ff)`
- progress / accent gradient: `linear-gradient(90deg, #4fb4ff, #7c5cff)`
- accent tint fills: `rgba(124,92,255,.10-.20)`; glass cards: `rgba(255,255,255,.03-.04)` with `line-2` border

## Colours — light theme (the white option: white, black and violet)
Only three colours: pure white grounds, black text, the site's violet as the one accent.
No tinted greys; neutrals are true greys. Contrast on white measured (WCAG): black 21,
muted 7.5, accent-text 6.5, accent 4.4 (large text and fills), dim 3.0 (blurred / upcoming only).
| Token | Hex | Use |
|---|---|---|
| bg | `#ffffff` | scene ground |
| bg-2 | `#f5f5f5` | second ground, card backs |
| surface | `#ffffff` | cards (separated by `line-2` border or shadow) |
| line | `rgba(0,0,0,.08)` | hairlines, dot/grid pattern |
| line-2 | `rgba(0,0,0,.14)` | card borders |
| fg | `#000000` | main text, captions |
| muted | `#555555` | secondary text |
| dim | `#959595` | meta, blurred/upcoming items |
| **accent** | `#7c5cff` | bars, buttons, highlight fills, pulses (same as dark) |
| accent-text | `#5b3fe0` | violet words on white |
| accent-ink | `#ffffff` | text on a violet fill |
| accent soft | `#ece8ff` | marker fill behind words |
| ok / danger | `#0b8a56` / `#d93a55` | only for right / wrong, never decoration |
Effects: cards get `0 10px 30px rgba(0,0,0,.08)` instead of a glow; a violet glow
`radial-gradient(80% 60% at 50% 30%, rgba(124,92,255,.14), transparent 70%)` is allowed behind
a hero element only. Headline emphasis = the key word in violet (accent-text) or on a violet bar
with white text.

## Which theme
`theme` is set per style in the registry (`dark` default, `light`, or `both`) and can be
overridden per video ("make this one white"). With `both`, the style keeps the reference's
own rhythm of light and dark scenes (e.g. a light hook, dark body) using the two token sets.

## Mapping a reference palette
- its single accent colour (e.g. red) → **accent `#7c5cff`**, same discipline (where it was
  allowed, how often), glow → accent-hi;
- its grounds → bg / bg-2 (dark) or the light-scene ground, by brightness; grids → `line`;
- its text colours → fg / muted / dim;
- colours that carry meaning (green = good, red = bad) → ok / danger only.

Textures, shapes, sizing and motion stay as the reference has them.
