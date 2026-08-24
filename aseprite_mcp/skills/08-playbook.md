---
name: aseprite-mcp-playbook
title: Tool Playbook - Technique to Tool Call
description: How to perform each pixel-art technique with this server's tools, plus the coordinate, cel and layer gotchas that cause silent failures.
when_to_use: Read alongside pixel-art-pipeline before the first tool call, and whenever a tool did something you did not expect.
tools: draw_pixels_at, get_composite_rect, validate_scene, run_lua_script, export_frame, get_sprite_info
see_also: pixel-art-pipeline, pixel-art-animation, pixel-art-fundamentals
---

## Conventions you must know before the first call

| Rule | Detail |
|---|---|
| **Coordinates are sprite-global** | Every `x`/`y` is measured from the sprite's top-left, never from the cel. The tools handle the cel offset for you. |
| **Origin is top-left, y grows downward** | `y=0` is the top row. |
| **Frames are 1-based** | `frame_index=1` is the first frame. Frame `0` does not exist. |
| **Layers are addressed by name** | `layer_name="body"`, or `"group/child"` for a layer inside a group. A typo does not raise — it returns a "Layer not found" string. **Read the return value of every call.** |
| **Rectangles are inclusive of their corners** | `draw_rectangle_at(x=0, y=0, width=8, height=8)` covers x 0-7, y 0-7. |
| **Colors are hex, alpha optional** | `#RRGGBB` or `#RRGGBBAA`. `#RGB`/`#RGBA` shorthand also parses. |
| **Every tool returns a status string** | Success and failure are both plain text. Nothing throws. If you do not read the string, you will not notice a failed call. |

## The `*_at` rule

Every drawing tool exists in two forms:

- `draw_rectangle(...)` — draws on whatever cel Aseprite considers active.
- `draw_rectangle_at(layer_name, frame_index, ...)` — draws on an explicit target.

**Always use `_at`.** The implicit form is only safe on a one-layer,
one-frame sprite, and it silently paints the wrong layer the moment that stops
being true. `create_if_missing=True` (the default) creates the cel for you, so
there is no setup cost.

## Technique to tool

### Building the sprite

| Technique | Call |
|---|---|
| New sprite | `create_canvas(width, height, filename)` |
| Layer rig | `add_group(filename, "character")` then `add_layer(filename, "body", group="character")` |
| Reorder the stack | `reorder_layer(filename, "arm_front", position)` |
| Confirm the rig | `get_sprite_info(filename)` / `validate_scene(filename, required_layers=[...])` |

### Drawing

| Technique | Call |
|---|---|
| Silhouette masses | `draw_ellipse_at`, `draw_rectangle_at(fill=True)`, `draw_polygon(fill=True)` |
| Precise edges, AA, single pixels | `draw_pixels_at(pixels=[{"x":5,"y":7,"color":"#B03A48"}, ...])` |
| Fill a closed region | `fill_area_at(x, y, color)` |
| Erase pixels | `erase_region(...)`, or `draw_pixels_at` with `"#00000000"` |
| Erase one color everywhere | `erase_color(filename, layer, frame, color, tolerance)` |
| Smooth gradient | `apply_gradient_rect(...)` |
| Dithered gradient | `apply_dither_gradient(color_start, color_end, horizontal)` |
| Uniform dither mix | `apply_dither_pattern(color_a, color_b, density=0.5)` |
| Text / UI labels | `measure_text(...)` first, then `draw_text(..., antialias=False)` |

**Batch your pixels.** One `draw_pixels_at` with 200 pixels launches Aseprite
once; 200 separate calls launch it 200 times. Each launch is ~0.3-1s, so
batching is the difference between a 1-second and a 3-minute sprite.

### Color

| Technique | Call |
|---|---|
| Build a hue-shifted ramp | `generate_color_ramp(base_color, steps=5, hue_shift_degrees=20)` |
| Load the palette | `set_palette(filename, colors=[...])` |
| Retro palette | `apply_palette_preset(filename, "dawnbringer16")` |
| Force art onto the palette | `quantize_to_palette(filename, layer_name, start_frame, end_frame)` |
| Palette-swap variant (exact) | `remap_colors_in_cel_range(filename, layer, 1, 8, mappings=[{"from":"#A","to":"#B"}])` |
| Quick tint | `adjust_hsl(filename, layer, frame, hue_shift, saturation_shift, lightness_shift)` |
| Palette from existing art | `extract_palette(filename, max_colors=16)` |
| Audit colors actually used | `get_color_stats(filename, frame_index, top=32)` |

### Shading and effects

| Technique | Call |
|---|---|
| Shadow layer from a copy | `duplicate_layer` + `adjust_hsl(lightness_shift=-25, hue_shift=-15)` + `erase_region` |
| Uniform outline | `outline_cel(color, include_diagonals=False)` or `outline_native(place="outside")` |
| Selective outline | `outline_cel` first, then remove segments with `erase_region` / transparent pixels |
| Hit flash | `duplicate_layer` + `adjust_brightness_contrast(brightness=100, contrast=100)` |
| Sharpen / blur / emboss | `list_convolution_matrices()` then `apply_convolution(matrix=...)` |
| Invert (glitch, negative) | `invert_colors(...)` |

### Animation

| Technique | Call |
|---|---|
| Add frames | `add_frames(filename, count, duration_ms)` |
| Copy a base pose everywhere | `propagate_cels(filename, ["body","head"], source_frame=1, start_frame=2, end_frame=8)` |
| Copy an entire frame | `copy_frame` / `propagate_frame_to_range` |
| Move a part over time | `tween_cel_positions_eased(..., easing="smoothstep"\|"ease_in"\|"ease_out")` |
| Bob / breathe / hover | `oscillate_cel_positions(amplitude_y=1, cycles=1, phase_deg=0)` |
| Squash and stretch | `tween_cel_scale_eased(start_scale=1.0, end_scale=0.9, anchor="bottom")` |
| Fade in / out | `tween_cel_opacity_eased(start_opacity=255, end_opacity=0)` |
| Shift a whole range | `offset_cel_positions(start_frame, end_frame, dx, dy)` |
| Per-frame timing | `set_frame_duration(filename, frame_index, duration_ms)` |
| Name the cycle | `set_tag(filename, "walk", 1, 8, direction="forward"\|"reverse"\|"pingpong")` |

`phase_deg` on `oscillate_cel_positions` is how you get overlap for free: run
the same oscillation on `hair` with `phase_deg=45` and it lags the head.

### Verification

| Question | Call |
|---|---|
| What does it look like? | `export_frame(filename, frame, "check.png", scale=8)` **then read the PNG** |
| Does it read at game size? | `export_frame(..., scale=1)` |
| What color is actually at (x,y)? | `get_composite_pixel(filename, x, y, frame)` |
| What is in this region, flattened? | `get_composite_rect(filename, x, y, w, h, frame)` |
| What is on this one layer? | `get_pixels_rect(filename, x, y, w, h, layer_name, frame)` |
| Is the palette clean? | `get_color_stats(filename, frame)` |
| Does the motion flow? | `render_onion_skin(filename, frame, "onion.png", before=1, after=1, scale=4)` |
| Is this frame doing anything? | `compare_frames(filename, a, b)` |
| Are cels missing / layers overlapping? | `audit_animation(filename, report_cels=True, report_bounds=True)` |
| Fix missing cels | `ensure_layers_present(filename, layer_names, start_frame, end_frame)` |

**`get_composite_rect` vs `get_pixels_rect`**: composite reads the flattened
result across all layers, which is what the player sees. Per-layer reads tell
you what a specific layer contains. When something looks wrong, compare the two
— if the layer has the art but the composite does not, it is a layer order or
opacity problem, not a drawing problem.

### Export

| Target | Call |
|---|---|
| Look at it | `export_frame(scale=8)` / `export_tag(..., "x.gif", scale=4)` |
| Engine sprite sheet | `export_spritesheet(sheet_type="horizontal", data_filename="x.json", tag_name="walk", padding=1)` |
| Per-layer PNGs | `export_layers(filename, output_directory)` |
| Final image | `export_sprite(filename, "out.png")` |
| Duplicate the source | `copy_sprite(filename, "variant.aseprite")` |

`sheet_type`: `horizontal` for a simple strip, `rows`/`columns` for a grid,
`packed` for atlas efficiency (only when the engine reads the JSON). Use
`data_format="json-hash"` plus `list_tags=True` when the engine needs tag
metadata.

## Gotchas that cause silent wrong results

1. **Nothing was drawn.** The cel did not exist and `create_if_missing` was
   `False`, or the layer name did not match. Check the return string; then
   `validate_scene`.

2. **Drawing landed on the wrong layer.** You used a non-`_at` tool. Always
   pass `layer_name` and `frame_index`.

3. **The shape is one pixel off.** Rectangles are corner-inclusive:
   `width=8` spans 8 pixels, x through x+7. `draw_circle_at` uses a centre and
   radius, so an even-diameter circle has no exact centre pixel — decide
   whether you want radius 3 (7px) or 4 (9px).

4. **Lines look ugly.** `draw_line_at` is Bresenham; it does not produce
   pixel-art step patterns. For edges that matter, place pixels manually.

5. **A tween did nothing.** The cels did not exist in the target frames. Pass
   `create_missing_cels=True`, or `propagate_cels` first — that is the normal
   order: propagate, then tween.

6. **A blend mode produced off-palette colors.** `multiply`/`overlay` compute new
   RGB values. Follow with `quantize_to_palette` and verify with
   `get_color_stats`.

7. **The animation loop stutters.** The last frame duplicates frame 1. A
   `forward` loop of N frames must not repeat the first pose at the end.

8. **The sprite jitters when it should be still.** Frames were redrawn rather
   than propagated.

9. **Text is blurry.** `draw_text(antialias=True)`. For pixel-art UI, always
   `antialias=False` and prefer a bitmap font from `list_text_fonts`.

10. **A `_native` filter hit the wrong target.** The `native_fx` tools drive
    Aseprite's own `app.command.*`, which act on the *active* layer/frame.
    They activate the target for you, but always pass `layer_name` and
    `frame_index` explicitly rather than relying on whatever was last active.

11. **`draw_on_tile` tile indices.** Tile `0` is the reserved empty tile and
    cannot be drawn on; the first real tile is `1`. Passing the current tile
    count appends a new tile.

12. **Traversal is rejected.** Paths containing `..` are refused. Use paths
    inside the working directory.

## Performance

Every tool call launches Aseprite in batch mode. Cost is per *call*, not per
pixel, so:

- Batch pixels into one `draw_pixels_at` call.
- Prefer a range tool (`propagate_cels`, `tween_*`, `offset_cel_positions`) over
  a loop of per-frame calls.
- When a technique needs many heterogeneous operations at once, drop to
  `run_lua_script` and do them all in a single launch.

## The Lua escape hatch

`run_lua_script(script, filename)` runs arbitrary Aseprite Lua
(https://www.aseprite.org/api/). Use it when no tool fits, or to collapse a
long sequence into one launch.

Contract:

- Get the sprite with `app.activeSprite`.
- Wrap mutations in `app.transaction(function() ... end)`.
- **Save explicitly**: `spr:saveAs(spr.filename)` — nothing is written otherwise.
- **`print()` your results**; stdout is the only channel back to you.
- Signal failure by printing a line beginning with `ERROR:`.

```lua
local spr = app.activeSprite
if not spr then print("ERROR:No active sprite") return end
app.transaction(function()
  -- ... work ...
end)
spr:saveAs(spr.filename)
print("OK")
```

It runs unrestricted code on the host. Do not build scripts from untrusted
input.

## A complete minimal session

```
create_canvas(32, 32, "hero.aseprite")
add_layer("hero.aseprite", "body")
generate_color_ramp(base_color="#8A5A3B", steps=5)          # read the ramp back
set_palette("hero.aseprite", colors=[...])
draw_ellipse_at("hero.aseprite", "body", 1, 16, 12, 5, 6, "#8A5A3B", fill=True)
export_frame("hero.aseprite", 1, "check.png", scale=8)      # LOOK AT IT
draw_pixels_at("hero.aseprite", "body", 1, pixels=[...])    # shade, batched
get_color_stats("hero.aseprite", 1)                         # palette clean?
export_frame("hero.aseprite", 1, "check.png", scale=8)      # LOOK AGAIN
add_frames("hero.aseprite", 3, duration_ms=150)
propagate_cels("hero.aseprite", ["body"], 1, 2, 4)
oscillate_cel_positions("hero.aseprite", "body", 1, 4, amplitude_y=1, cycles=1)
set_tag("hero.aseprite", "idle", 1, 4, direction="forward")
audit_animation("hero.aseprite")
export_spritesheet("hero.aseprite", "hero.png", data_filename="hero.json",
                   list_tags=True)
```
