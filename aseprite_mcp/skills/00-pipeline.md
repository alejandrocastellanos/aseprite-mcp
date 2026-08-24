---
name: pixel-art-pipeline
title: The Pixel Art Pipeline
description: The master workflow. Order of operations from blank canvas to exported game asset, with the verification gates that catch mistakes you cannot see.
when_to_use: Always. Read this first, before any other skill and before the first draw call.
tools: create_canvas, add_layer, add_group, set_palette, export_frame, get_color_stats, get_composite_rect, audit_animation
see_also: aseprite-mcp-playbook, pixel-art-fundamentals, pixel-art-color, pixel-art-character-design
---

## The one thing that breaks AI pixel art

You are drawing blind. You issue coordinates into a file you never see, and a
sprite that is 60% correct looks *completely wrong* to a human — pixel art has
no forgiving middle ground, because at 32x32 every pixel is 0.1% of the image.

So the pipeline below is not a style preference. It is a sequence of commitments
made in the order that makes each one cheap to fix, with a **look at it** gate
after each phase. Skipping a gate does not save time; it moves the failure to
the end, where the only fix is to start over.

## Non-negotiables

1. **Never draw on the active cel implicitly.** Always use the `*_at` variants
   with an explicit `layer_name` and `frame_index`. Implicit-target drawing
   drifts onto the wrong layer as soon as a sprite has more than one.
2. **Decide the palette before the first pixel.** Colors invented per-part are
   the number one cause of muddy sprites. See `pixel-art-color`.
3. **Silhouette before detail.** If the black shape is not readable, no amount
   of shading rescues it. See `pixel-art-character-design`.
4. **Look at your work at 8x after every phase.** `export_frame(scale=8)` then
   actually read the PNG.
5. **One light source for the whole sprite**, chosen in Phase 0 and never
   contradicted. See `pixel-art-shading`.

## Phase 0 — Spec (no drawing)

Write the spec down in your reply before touching Aseprite. Five decisions:

| Decision | How to choose |
|---|---|
| Canvas size | See table below. Pick the smallest size that fits the required detail. |
| View angle | side / top-down 3-4 / top-down straight / isometric 2:1. Locks foreshortening. |
| Light direction | Default **top-left**. Pick once, obey everywhere. |
| Palette budget | 3-6 colors per material, 8-16 total for a character, 16-32 for a scene. |
| Animation list | The states needed (idle, walk, attack...) and frame counts, *before* the base pose is drawn — it dictates the layer split. |

### Canvas size table

| Size | Detail available | Typical use |
|---|---|---|
| 8x8 | Silhouette only, 2-3 colors | Items, bullets, particles |
| 16x16 | Head + body + one readable prop | NES-scale characters, tiles, icons |
| 32x32 | Face features, armour pieces, 2-value shading | **The default for a game character.** Best detail-to-effort ratio |
| 48x48 | Distinct hands, layered clothing, 3-value shading | Action-platformer protagonist |
| 64x64+ | Facial expression, material texture, dithering | Bosses, portraits, key art |

Rule: a character sprite should read at 1x. If it only works at 4x you have
drawn a small illustration, not a sprite.

## Phase 1 — Canvas and layer architecture

Layers are not organisation, they are **the animation rig**. Any part that will
ever move independently must be its own layer from the start; splitting later
means redrawing.

```
create_canvas(width=32, height=32, filename="ranger.aseprite")
add_group(filename, group_name="character")
add_layer(filename, layer_name="body",    group="character")
add_layer(filename, layer_name="head",    group="character")
add_layer(filename, layer_name="arm_back",  group="character")
add_layer(filename, layer_name="arm_front", group="character")
add_layer(filename, layer_name="weapon",  group="character")
add_layer(filename, layer_name="fx")
```

Draw order is bottom-to-top: `arm_back` below `body`, `arm_front` and `weapon`
above it. `reorder_layer` fixes a wrong stack without redrawing.

**Gate 1:** `get_sprite_info(filename)` — confirm every layer exists and the
order is what you intended.

## Phase 2 — Palette

Build the full palette now and load it into the sprite, so that later phases
can only pick from colors that already harmonise.

```
generate_color_ramp(base_color="#8A5A3B", steps=5, hue_shift_degrees=20)   # leather
generate_color_ramp(base_color="#3F6B4A", steps=5, hue_shift_degrees=20)   # cloth
set_palette(filename, colors=[...every ramp, dark to light...])
```

**Gate 2:** `get_palette(filename)` — read it back and sanity-check the count.
If it is over ~24 colors for a single character, cut it now.

## Phase 3 — Silhouette

Draw the entire character as one flat mid-tone on the `body` layer. No features,
no shading. Use `draw_ellipse_at` / `draw_rectangle_at` / `draw_polygon` for the
masses, then `draw_pixels_at` to carve the edges.

**Gate 3:** `export_frame(filename, 1, "check.png", scale=8)` and look. Ask:
can I name the character from the black shape alone? Where is the head, the
weapon, the direction it faces? If no, fix here — it is 10x cheaper than later.

## Phase 4 — Flat colors

Fill each region with its **base** (mid) color from its ramp, on its own layer.
Still no shading. `fill_area_at` for enclosed regions, `draw_pixels_at` for
edges. Every material gets exactly one flat color at this stage.

**Gate 4:** export at 8x. Check region boundaries read clearly and no two
adjacent materials share a value (see the squint test in `pixel-art-color`).

## Phase 5 — Shading

Two passes, in this order:

1. **Core shadow** — the darker step of each ramp on every surface facing away
   from the light. One value is enough at 32x32.
2. **Highlight** — the lighter step, only on the few "sweet spot" faces pointing
   straight at the light. Highlights are an accent, not a coating.

Then the **occlusion shadow**: the darkest step, a 1px line where two forms
meet (under the chin, under the arm, where a sleeve meets a hand). This is what
separates parts without an outline, and it is the single highest-value pixel in
the sprite.

See `pixel-art-shading` for the rules and the pillow-shading trap.

**Gate 5:** export at 8x, and `get_color_stats(filename, 1)`. If a color you
never chose appears, or a ramp has 9 near-identical entries, you have drifted.

## Phase 6 — Outline and cleanup

Selective outlining, anti-aliasing at step corners only, orphan-pixel removal.
See `pixel-art-fundamentals`. This is the polish pass and it is what makes a
sprite look drawn rather than generated.

## Phase 7 — Verification gate (the one that is always skipped)

Before declaring the sprite done, run all four:

| Check | Call | Fail condition |
|---|---|---|
| Read at 1x | `export_frame(..., scale=1)` | Cannot identify the subject |
| Read at 8x | `export_frame(..., scale=8)` | Jaggies, banding, stray pixels |
| Palette discipline | `get_color_stats(filename, 1)` | Colors outside the palette; >24 colors |
| Pixel truth | `get_composite_rect(filename, x, y, w, h)` | Region is empty / wrong color / off by one |

`get_composite_rect` is how you *read* what you actually drew, flattened across
layers. Use it when a shape does not look right and you need to know whether the
problem is the drawing or the layer order.

## Phase 8 — Animation

Only after the base pose passes Phase 7. Read `pixel-art-animation`.

Core rule: **animate by moving cels, not by redrawing frames.** Redrawing is
where consistency dies.

```
add_frames(filename, count=7, duration_ms=120)
propagate_cels(filename, layer_names=["body"], source_frame=1, start_frame=2, end_frame=8)
tween_cel_positions_eased(filename, "head", 1, 8, 0, 0, 0, -1, easing="smoothstep")
set_tag(filename, "walk", 1, 8, direction="forward")
```

**Gate 8:** `render_onion_skin` for motion continuity, `compare_frames` to catch
frames that are accidentally identical (a dead frame) or wildly different (a
pop), and `audit_animation` for missing cels and layer overlaps.

## Phase 9 — Export

```
export_tag(filename, "walk", "walk.gif", scale=4)                  # to look at
export_spritesheet(filename, "walk.png", sheet_type="horizontal",
                   data_filename="walk.json", tag_name="walk")     # for the engine
```

Never ship the GIF as the game asset — engines want the sheet plus its JSON.

## Failure table

When the result is wrong, the cause is almost always one of these:

| Symptom | Cause | Fix |
|---|---|---|
| Looks blurry / washed out | Over-anti-aliasing, too many colors | Cut the palette, AA only at step corners |
| Looks flat, like a sticker | Pillow shading, no single light source | Re-shade from one direction, add occlusion shadow |
| Cannot tell what it is at 1x | Silhouette never checked | Back to Phase 3 |
| Colors look muddy | Ramps mixed toward grey/black, no hue shift | Rebuild ramps with `generate_color_ramp` |
| Animation jitters | Redrawn frames instead of moved cels | Rebuild with `propagate_cels` + tweens |
| Parts drift apart while animating | Independent layers, no anchor discipline | Fix the pivot; see the anchor rules in `pixel-art-animation` |
| Nothing appears at all | Drew on a cel that does not exist, or wrong layer | Use `*_at` with `create_if_missing=True`; check `validate_scene` |
