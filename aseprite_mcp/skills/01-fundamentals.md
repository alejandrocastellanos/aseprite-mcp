---
name: pixel-art-fundamentals
title: Fundamentals - Lines, Clusters, Anti-Aliasing, Outlines
description: The craft rules that separate pixel art from a small image. Cluster control, jaggies, banding, selective outlining, orphan pixels, dithering doctrine.
when_to_use: Before drawing any line or edge, and always during the Phase 6 cleanup pass.
tools: draw_pixels_at, draw_line_at, outline_cel, outline_native, get_composite_rect, export_frame
see_also: pixel-art-pipeline, pixel-art-shading, pixel-art-color
---

## The premise

In pixel art every pixel is placed deliberately. The medium's whole aesthetic
comes from *control at low resolution*: a viewer reads the shape from a handful
of pixels, so a single misplaced one is visible. Filters, soft brushes and
automatic smoothing destroy that control — which is why "make it look like pixel
art" by downscaling an image never works.

Everything below is about controlling **clusters**: contiguous groups of the
same color. Clusters, not individual pixels, are what the eye reads.

## 1. Clusters

- **Keep clusters clean.** A cluster should be a compact, deliberate shape. Long
  ragged clusters of width 1 that wander are noise.
- **No orphan pixels.** A single pixel of a color, isolated inside a field of
  another color, reads as dirt (unless it is a deliberate highlight or star).
  During cleanup, hunt them and either delete them or grow them into a cluster.
- **Avoid "doubles" on a diagonal.** In a run of steps, one step being 2px while
  its neighbours are 1px breaks the line. Consistency of step length *is* the
  line quality.

## 2. Lines and jaggies

A **jaggy** is a step in a line that breaks the pattern the rest of the line
establishes. Perfect lines follow a consistent step run.

Clean step sequences (pixels per step along the line):

| Angle | Pattern | Reads as |
|---|---|---|
| 45 deg | 1,1,1,1,1 | Perfect diagonal |
| ~26 deg | 2,2,2,2 | Clean shallow slope |
| ~18 deg | 3,3,3,3 | Clean shallow slope |
| Curve | 1,1,2,3,4 or 4,3,2,1,1 | Smooth arc — step length changes **monotonically** |

The rule for curves: step lengths must increase or decrease *in order*. A
sequence of `1,2,1,2` is a jaggy; `1,1,2,3` is a curve. When a curve reverses
direction mid-run (`3,2,1,2,3`) that is a corner, not a curve, and it must be
intentional.

**Aseprite's line tool does not obey this.** `draw_line_at` gives you Bresenham,
which is correct geometrically and often ugly at low resolution. For any edge
that matters — a face profile, a sword, a silhouette boundary — place the pixels
yourself with `draw_pixels_at`, then verify with `get_composite_rect`.

## 3. Anti-aliasing (AA)

AA means placing intermediate-value pixels to soften a hard step. Manual AA is
the most misapplied technique in pixel art.

**The rule: AA belongs only at the *corner* of a step, not along the edge.**

```
No AA          Correct AA            Wrong AA (blur)
####           ####                  ####
####.          ####o                 ###oo
..####         ..o###                .oo###
..####         ...####               .oo###
```

The intermediate pixel goes in the notch where the step turns. Wrapping every
edge pixel in 3-4 intermediate shades turns the sprite into a low-resolution
photograph with a Gaussian blur — the single most recognisable failure of
AI-generated "pixel art".

Further rules:

- **AA against the neighbour, not against nothing.** The intermediate color must
  sit between the two colors it joins. Adding AA on the outer boundary of a
  sprite against transparency creates a halo when the sprite is composited over
  a different background.
- **Never AA a sprite that will be scaled or rotated in-engine.** The
  intermediates smear.
- **Longer steps get more AA, short steps get none.** A 45 deg diagonal (all
  1px steps) usually needs no AA at all.
- **Under ~24px, use AA very sparingly.** There is not enough pixel space; you
  will lose more to blur than you gain in smoothness.

## 4. Banding

Banding is when a band of one color runs *parallel and adjacent* to a band of
another color for a long stretch, with both following the same stair pattern.
It draws the eye to the grid and flattens the form — the opposite of what
shading is for.

```
Banding                 Fixed
11111                   11111
22222   <- 2 traces 1    22211   <- band broken, shadow turns with the form
33333   <- 3 traces 2    33221
```

Three fixes:

1. **Vary the band width** so the two edges do not track each other.
2. **Break the band at a terminator** — let the shadow edge follow the actual
   form, not the outline.
3. **Interrupt with a detail cluster** where the surface changes.

Banding and AA look similar and are opposites: AA is *one* transitional pixel at
a corner; banding is a *continuous run* of transitional pixels. If your
"anti-aliasing" is longer than two pixels in a row, it is banding.

## 5. Outlines

Three strategies. Pick one per asset and stay consistent.

| Style | What it is | Use for |
|---|---|---|
| **Black outline** | Full 1px black border all around | Busy backgrounds, cartoon style, tiny sprites that must pop |
| **Selective outline** | Outline only where the form needs separating; absent on lit edges | The default for character sprites — more depth, less flatness |
| **No outline** | Form defined by internal value contrast only | Large sprites, illustrations, realistic style |

Selective outlining rules:

- **Drop the outline on the lit side.** Light hitting a surface means the edge
  loses its dark border there.
- **Keep the outline darkest at the bottom / shadow side**, where the form is
  occluded.
- **Do not outline in pure black.** Use a very dark, hue-shifted version of the
  base color (dark blue-purple for warm subjects). Pure black flattens the
  sprite, drags every adjacent color darker, and looks cheap.
- **Break the outline where the sprite meets the ground** so it does not look
  like a sticker floating on the scene.

Tools: `outline_cel(color=..., include_diagonals=False)` gives a uniform
outline — a fine *starting point*. Then remove segments manually with
`draw_pixels_at` (transparent) or `erase_region` to make it selective.
`outline_native(place="outside")` uses Aseprite's own filter and keeps the
existing art untouched.

## 6. Noise, detail and "islands of detail"

Low resolution has a detail budget. Spend it unevenly.

- Put detail where the eye goes: the face, the weapon, the focal silhouette.
- Leave the rest as clean flat clusters. Uniform detail everywhere reads as
  noise and destroys hierarchy.
- Do not draw a texture pixel-by-pixel that will be invisible at 1x. If it does
  not survive `export_frame(scale=1)`, delete it — it is costing you clarity.

## 7. Dithering

Dithering interleaves two colors so the eye blends them into a third, faking a
gradient without spending a palette slot.

Patterns, from sparse to dense:

```
25%          50% checker      75%
#...#...     #.#.#.#.         ###.###.
....#...     .#.#.#.#         #.######
..#...#.     #.#.#.#.         ###.###.
```

`apply_dither_pattern(density=0.25 | 0.5 | 0.75)` for a uniform mix.
`apply_dither_gradient(color_start, color_end)` for a Bayer 4x4 ramp across a
rect — the workhorse for skies and large smooth surfaces.

**Doctrine — dither only when it does two jobs at once:** creating the gradient
*and* portraying a texture that belongs there (rough stone, rust, cloth,
airbrushed retro sky). Dithering a surface that should read as smooth is a
downgrade; add a palette color instead.

Other rules:

- Chain sparse -> checker -> sparse to build a *smooth* gradient. A single 50%
  checker between two colors is a hard band, not a gradient.
- Dither between **adjacent** ramp steps. Dithering between two distant values
  reads as static.
- **Check at 1x.** A dither that looks elegant at 8x can turn into a vibrating
  moire at game scale.
- Avoid dithering on small moving sprites — it flickers when the sprite moves
  sub-pixel.

## Cleanup checklist (run at Phase 6)

- [ ] No orphan pixels
- [ ] Every curve has monotonic step lengths; no jaggies
- [ ] AA only at step corners, never a run of 3+ transitional pixels
- [ ] No outer-edge AA against transparency
- [ ] No banding: shadow edges do not trace the outline
- [ ] Outline strategy consistent; not pure black; broken at the ground contact
- [ ] Detail concentrated at the focal point, flat clusters elsewhere
- [ ] Dithering (if any) survives the 1x test and is texturally justified
- [ ] `export_frame(scale=1)` is still readable
