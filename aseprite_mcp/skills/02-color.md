---
name: pixel-art-color
title: Color and Palettes
description: How to build ramps that harmonise - hue shifting, saturation curves, value spacing, palette budgets, and the checks that catch palette drift.
when_to_use: In Phase 2, before any color is placed, and whenever a sprite looks muddy, washed out or noisy.
tools: generate_color_ramp, set_palette, get_palette, apply_palette_preset, quantize_to_palette, get_color_stats, adjust_hsl, replace_color, remap_colors_in_cel_range
see_also: pixel-art-shading, pixel-art-fundamentals, pixel-art-pipeline
---

## Why palettes come first

A palette built up ad hoc — "a brown for the leather, a green for the cloak" —
produces colors that have no relationship to each other. The result reads muddy
and the sprite looks unfinished no matter how good the drawing is. Building the
palette first turns color into a *constraint*, and constraints are what make
pixel art cohere.

Work in **HSB/HSL**: Hue (0-360, which color), Saturation (0-100, how pure),
Brightness/Lightness (0-100, how light). Every rule below is a rule about how
those three move together.

## The ramp

A **ramp** is a set of colors for one material, ordered dark to light. It is the
unit of a pixel art palette — you do not pick colors, you pick ramps.

| Sprite size | Ramp length | Total palette |
|---|---|---|
| 16x16 | 2-3 per material | 4-8 colors |
| 32x32 | 3-5 per material | 8-16 colors |
| 64x64 | 5-7 per material | 16-32 colors |
| Scene / tileset | 5-9 per material | 24-48 colors |

More colors is not better. A tight palette forces value contrast to do the work,
which is what makes sprites readable.

## The three laws of a ramp

### Law 1 — Hue shifts with value

Do not darken a color by only reducing brightness. **Rotate the hue as you go.**

- Shadows shift toward **cool** — blue, purple, or the neighbouring cooler hue.
- Highlights shift toward **warm** — yellow, orange.
- Roughly **15-25 degrees of hue rotation per step**, in a consistent direction
  along the ramp. ~20 deg is a good default and about the maximum before the
  ramp stops reading as one material.

A red ramp: dark end shifts toward purple/magenta, light end toward orange/yellow.
A green ramp: dark end toward blue-green/teal, light end toward yellow-green.

This is the single highest-impact technique in the whole medium. A hue-shifted
ramp looks like light and atmosphere; an unshifted one looks like a Photoshop
brightness slider.

```
generate_color_ramp(base_color="#B03A48", steps=5, hue_shift_degrees=20,
                    lightness_range=0.5)
```

### Law 2 — Saturation peaks in the middle

Saturation is **not** linear along a ramp. It rises from the dark end, peaks at
or just below the mid-tone, and falls off toward the light end.

```
Value:      dark  ->  mid  ->  light
Brightness:  25     50    70    85    95     (rising, larger steps at the ends)
Saturation:  45     70    80    60    30     (peaks mid, falls off both sides)
Hue:        330    345     0    15    35     (rotating cool -> warm)
```

Never hit the extremes: saturation rarely reaches 0 or 100, brightness rarely
starts at 0 or ends at 100. **The biggest single mistake is high saturation
combined with high brightness** — it burns the eye and nothing else in the
sprite can compete with it.

### Law 3 — No pure black, no pure white

`#000000` and `#FFFFFF` are dead colors. They belong to no ramp, they flatten
everything adjacent, and they make a sprite look like clip art.

- Darkest value: a very dark, saturated, hue-shifted color — `#1A1226`,
  `#241C3B`, `#2B1B2E` rather than black.
- Lightest value: a warm or cool off-white — `#F4E9D8`, `#E8F0F5`.

Exception: a deliberate 1-bit style, or true black as a UI/background clear color.

## Value spacing and the squint test

Value (perceived lightness) is what carries readability, not hue. Two colors
with different hues but the same value merge into one shape at game scale.

- Keep **at least ~15% brightness difference** between adjacent ramp steps or
  the shading will not read at 1x.
- Keep **large value separation between adjacent materials** — a green shirt and
  a red belt at the same brightness will visually fuse.

The squint test, done with tools you have: export at 1x, then
`get_color_stats(filename, 1)` and compare the perceptual luminance of the
dominant colors: `L = 0.299R + 0.587G + 0.114B`. Adjacent regions with a
luminance gap under ~25 will merge.

## Palette structure for a whole sprite

Build ramps in this order:

1. **The dominant material** (skin, hull, body) — the largest area. This anchors
   everything.
2. **Secondary materials** — clothing, metal, wood. Hue-rotate each ramp 45 deg
   or more from the previous so they stay distinguishable. Eight ramps at 45 deg
   apart cover the full wheel.
3. **The accent** — one small, high-saturation ramp used on <5% of the pixels:
   the gem, the eyes, the glowing rune. Saturation is a resource; spending it on
   a small area is what makes it read as an accent.
4. **A neutral ramp** — desaturated versions for shadows, outlines, and anything
   that should recede.

Rule of thumb for area vs saturation: **the more area a color covers, the less
saturated it should be.** Big saturated fields are exhausting.

## Color harmony shortcuts

| Scheme | How | Feels |
|---|---|---|
| Analogous | Ramps within 60 deg of each other | Calm, cohesive, natural |
| Complementary | Two ramps ~180 deg apart | High contrast, focal punch |
| Split-complementary | Base + two ramps flanking its complement | Contrast without harshness |
| Triadic | Three ramps 120 deg apart | Vivid, playful, arcade |

Practical version: pick one dominant hue family, one supporting family nearby,
and one complementary accent. That covers 90% of character work.

## Global light color

Ambient light tints everything. Instead of shading each material in isolation,
push every ramp's shadows toward the **ambient** color and every ramp's
highlights toward the **light source** color.

| Setting | Light (highlights) | Ambient (shadows) |
|---|---|---|
| Daylight | Warm yellow-white | Cool blue sky bounce |
| Sunset | Strong orange | Deep purple-blue |
| Night / moonlight | Pale cyan-blue | Very dark blue-violet |
| Torch / fire | Saturated orange | Cool desaturated blue-grey |
| Sci-fi interior | Cyan or magenta | Near-black with the complement |

This is what makes a set of sprites look like they belong in the same scene.
Apply it to an existing sprite with
`adjust_hsl(hue_shift=..., saturation_shift=..., lightness_shift=...)` on the
shadow layer, or `remap_colors_in_cel_range` for an exact palette swap.

## Retro presets

`list_palette_presets()` / `apply_palette_preset(filename, preset)` give you
`gameboy`, `pico8`, `c64`, `cga`, `dawnbringer16`, `dawnbringer32`,
`grayscale_4`, `monochrome`.

Use one when the brief asks for an era look, or as **training wheels**: a fixed
16-color palette forces value discipline because you cannot invent a color to
escape a problem. `dawnbringer16` is the best general-purpose choice.

To convert existing art onto a palette: `set_palette` then
`quantize_to_palette(filename, layer_name, start_frame, end_frame)`.

## Palette-swap variants (free content)

A recolour is the cheapest asset in game development. Two routes:

```
# Exact, per-color control - the right way for a shipped variant
remap_colors_in_cel_range(filename, "body", 1, 8,
    mappings=[{"from": "#B03A48", "to": "#3A6BB0"}, ...])

# Fast global shift - good for prototyping an enemy tint
adjust_hsl(filename, "body", 1, hue_shift=120, saturation_shift=-10)
```

For an enemy palette family, keep value identical and rotate only hue. Identical
values mean identical readability, so gameplay clarity is preserved.

## Checks

| Check | Call | Fail condition |
|---|---|---|
| Palette actually loaded | `get_palette(filename)` | Wrong count, missing ramps |
| No drift | `get_color_stats(filename, frame)` | Colors present that are not in the palette |
| Not over-budget | `get_color_stats(filename, frame, top=64)` | >24 colors on one character |
| Values separate | luminance of top colors | Adjacent materials within ~25 luminance |
| Extract from reference | `extract_palette(filename, max_colors=16)` | — |

## Checklist

- [ ] Palette built and loaded *before* drawing
- [ ] Every ramp hue-shifts 15-25 deg per step, cool shadows / warm highlights
- [ ] Saturation peaks mid-ramp, never combined with max brightness
- [ ] No pure black, no pure white
- [ ] >=15% brightness step between ramp neighbours
- [ ] Adjacent materials separated in value, not only in hue
- [ ] Exactly one high-saturation accent, on a small area
- [ ] Total color count inside the budget for the sprite size
- [ ] Ambient/light color applied consistently across every ramp
