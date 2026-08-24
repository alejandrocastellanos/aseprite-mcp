---
name: pixel-art-review
title: Self-Review - Judging Work You Cannot See
description: The critique procedure. How to inspect your own sprite with the read-back tools, a scoring rubric, and a symptom-to-fix diagnosis table.
when_to_use: Before declaring any sprite finished, and whenever the user says the result looks wrong but cannot say why.
tools: export_frame, get_composite_rect, get_composite_pixel, get_color_stats, compare_frames, render_onion_skin, audit_animation, validate_scene, export_tag
see_also: pixel-art-pipeline, pixel-art-fundamentals, pixel-art-shading
---

## The blind-artist problem

A human pixel artist glances at the canvas a hundred times an hour. You do not.
Unless you deliberately export and read the image, you are working from an
internal model of what you *intended* to draw, and that model diverges from the
file almost immediately.

Treat inspection as a required step, not as debugging. **A sprite you have not
looked at is not finished, it is untested.**

## The inspection toolkit

Four different questions, four different tools.

| Question | Tool | What it gives you |
|---|---|---|
| "What does this look like?" | `export_frame(scale=8)` | A PNG you can actually read. Read it. |
| "Does it work at game size?" | `export_frame(scale=1)` | The only test that matters for readability |
| "What is actually at these coordinates?" | `get_composite_rect(x, y, w, h)` | The flattened truth, as data |
| "Which colors did I really use?" | `get_color_stats(frame, top=32)` | Palette drift, near-duplicate colors |

Plus, for animation: `render_onion_skin`, `compare_frames`, `audit_animation`.

**`get_composite_rect` is your most precise instrument.** When a shape looks
wrong, do not guess — read the region back and compare against what you meant to
draw. It resolves ambiguity that an image cannot: exact coordinates, exact
colors, exact emptiness.

## The review procedure

Run in this order. Each step is cheap and catches a different class of error.

### 1. Structure

```
get_sprite_info(filename)
validate_scene(filename, required_layers=["body","head","arm_front"])
```

Every intended layer exists, in the intended order, with cels where expected.
A missing cel is invisible in an export — it just looks like the part was never
drawn.

### 2. The 1x read

```
export_frame(filename, 1, "review_1x.png", scale=1)
```

Read it. Ask, in this order:

- Can I identify the subject?
- Can I tell which way it faces?
- Can I see the defining prop / weapon / feature?
- Would I be able to tell it apart from another character in the same set?

**If a sprite fails at 1x, nothing else matters.** Go back to the silhouette.

### 3. The 8x read

```
export_frame(filename, 1, "review_8x.png", scale=8)
```

Now look for craft errors — this is where they are visible:

- Orphan pixels, ragged clusters
- Jaggies: steps that break the line's pattern
- Banding: parallel runs of two colors tracing each other
- Over-anti-aliasing: 3+ transitional pixels in a row, halos on the outer edge
- Pillow shading: highlight centred in a part, shadow following the outline
- Pure black outlines flattening the form
- Missing occlusion shadows where forms meet
- A floating sprite: no contact shadow at the ground

### 4. Palette audit

```
get_color_stats(filename, 1, top=32)
```

- Count the colors. Over ~24 on a single character is a failure.
- Look for near-duplicates — two colors within a few RGB points mean an
  accidental color, usually from a blend mode or a typo.
- Compute luminance (`0.299R + 0.587G + 0.114B`) for the dominant colors. Two
  adjacent materials within ~25 luminance of each other will visually fuse.
- Any color not in the palette you set is drift. Fix with
  `quantize_to_palette` or `replace_color`.

### 5. Pixel truth (when something looks off)

```
get_composite_rect(filename, x=12, y=8, width=8, height=8, frame_index=1)
```

Use it to answer specifically: is this region empty, the wrong color, or one
pixel off? This distinguishes "I drew it wrong" from "it is drawn correctly but
hidden by layer order".

### 6. Animation review (if animated)

```
audit_animation(filename, report_cels=True, report_bounds=True)
compare_frames(filename, 1, 2)   # ... for every neighbouring pair
render_onion_skin(filename, 3, "onion3.png", before=1, after=1, scale=4)
export_tag(filename, "walk", "review.gif", scale=4)
```

Interpretation:

| Reading | Means | Fix |
|---|---|---|
| `compare_frames` ~0% changed | Dead frame | Delete it or give it motion |
| `compare_frames` very high % between neighbours | A pop / missing in-between | Add an in-between, or check for a wrong cel |
| Bounding box grows across the cycle | Drift | Rebuild from propagated cels |
| Onion ghosts do not form a smooth path | Broken arc | Re-tween with easing, or hand-fix the mid frame |
| Planted foot moves between contact frames | Foot sliding | Lock the contact foot; move the body instead |
| `audit_animation` reports missing cels | Empty frames on a layer | `ensure_layers_present` |

## Scoring rubric

Score each 0-2 (0 = fails, 1 = passable, 2 = good). Anything under 12/20 is not
shippable; any single 0 must be fixed regardless of the total.

| # | Criterion | 2 points means |
|---|---|---|
| 1 | **Readability at 1x** | Subject, facing and key prop are all clear |
| 2 | **Silhouette** | Distinct shape idea; identifiable as a flat shape |
| 3 | **Palette discipline** | Inside budget, all ramps hue-shifted, no stray colors |
| 4 | **Value structure** | Adjacent materials clearly separated in value |
| 5 | **Light consistency** | One direction, obeyed by every part |
| 6 | **Form** | Occlusion shadows present; no pillow shading |
| 7 | **Cluster quality** | No orphan pixels, no jaggies, no banding |
| 8 | **AA / outline discipline** | AA at corners only; outline strategy consistent, not pure black |
| 9 | **Detail hierarchy** | Detail concentrated at the focal point, calm elsewhere |
| 10 | **Animation integrity** (or structure, if static) | No drift, no dead frames, uneven timing, correct loop |

## Symptom to cause

The user rarely says "the ramp lacks hue shifting". They say it looks bad. Map
the complaint:

| Complaint | Most likely cause | Fix |
|---|---|---|
| "Looks blurry / AI-generated" | Over-anti-aliasing, too many colors | Cut the palette; AA only at step corners; `quantize_to_palette` |
| "Looks flat" | Pillow shading, no occlusion | Re-shade from one light direction; add the occlusion pass |
| "Colors look muddy" | Ramps built by darkening only | Rebuild with `generate_color_ramp(hue_shift_degrees=20)` |
| "Too busy / noisy" | Uniform detail, over-dithering | Flatten clusters outside the focal area; remove dithering |
| "Can't tell what it is" | Weak silhouette | Back to Phase 3; strengthen the shape idea and the accessory |
| "Looks like a sticker" | No contact shadow, full black outline | Add ground shadow; make the outline selective and hue-shifted |
| "Cheap / plastic" | Short low-contrast ramps everywhere | Lengthen the ramps on metal/gem; raise contrast; add a specular |
| "Animation feels floaty" | Even frame durations, no anticipation | Uneven timing; add anticipation and an impact hold |
| "Animation feels stiff" | No overlap or follow-through | Offset secondary layers by one frame |
| "Attacks have no punch" | No impact hold, no flash | Hold the impact frame 3-5x; add a hit flash and hitstop |
| "Doesn't match the rest of the set" | Different ambient/light color, different palette | Apply one global light/ambient tint across all ramps |
| "Character jitters" | Redrawn frames | Rebuild with `propagate_cels` + tweens |

## Reporting to the user

When you present a sprite, state plainly:

- What you verified and how (which exports you read, what `get_color_stats`
  returned).
- The spec you worked to: canvas, palette size, light direction, frame counts.
- What you know is weak, and why you left it — never claim a check you skipped.

If you did not export and look at the result, say so. A sprite delivered without
inspection is a draft, and calling it finished is a false report.

## Final gate

- [ ] Exported at 1x and read it
- [ ] Exported at 8x and read it
- [ ] `get_color_stats` clean and inside budget
- [ ] `validate_scene` / `get_sprite_info` matches the intended rig
- [ ] Animation: `audit_animation` clean, no dead frames, onion skin smooth
- [ ] Rubric scored, no criterion at 0
- [ ] Sheet + JSON exported for the engine, pivot recorded as a slice
