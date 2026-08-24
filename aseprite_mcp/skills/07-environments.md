---
name: pixel-art-environments
title: Tilesets, Environments and UI
description: Seamless tiles, autotile sets, top-down and side-view level art, parallax backgrounds, props, and 9-slice UI panels.
when_to_use: Any level art, tileset, background, prop or interface asset - anything that is not a character.
tools: create_tilemap_layer, draw_on_tile, set_tiles, get_tilemap_info, get_tile_at, create_slice, set_slice_center, apply_dither_gradient, copy_region, export_spritesheet, draw_text
see_also: pixel-art-fundamentals, pixel-art-color, pixel-art-shading
---

## Tile sizes

| Tile | Character scale | Use |
|---|---|---|
| 8x8 | 8-16px | NES-style, dense detail, hard to make seamless |
| **16x16** | 16-32px | **The standard.** SNES/GBA-style top-down and platformers |
| 32x32 | 32-64px | Detailed modern pixel art, fewer tiles needed |
| 48/64 | 64px+ | Large-scale scenes; approaching hand-painted |

Keep tile size, character size and UI on the **same pixel grid**. Mixed
resolutions in one scene (a 16px tileset with a 40px character) is the fastest
way to make a game look unfinished.

## Making a tile seamless

A tile must connect to a copy of itself on every edge.

Rules:

1. **Design the edges first, the centre last.** The edges are the constraint;
   the middle is free.
2. **Opposite edges must be complementary.** Whatever leaves the right edge at
   row y must enter the left edge at row y.
3. **Never put a strong feature at the edge.** A high-contrast detail on an edge
   becomes a visible seam line repeated every N pixels.
4. **Break the grid inside the tile.** Diagonal or irregular internal detail
   fights the eye's tendency to find the repeat.
5. **Avoid a centred feature.** A prominent detail in the middle of a tile
   produces a polka-dot pattern when tiled.

Test the tile by placing it in a 4x4 block with `set_tiles` and exporting — the
repeat will be obvious immediately, and it is invisible while looking at a single
tile.

## Breaking repetition

Even a perfect tile becomes ugly at scale. Two techniques:

- **Variants**: 3-5 versions of the same tile, identical at the edges but
  different inside. Make one "quiet" (nearly flat) and use it for 70% of the
  field, with the busier ones sprinkled sparsely. A field of uniformly detailed
  tiles reads as noise.
- **Rhyming shapes**: variants that are visually distinct but structurally
  consistent — the same grass silhouette with a different tuft arrangement.

Detail tiles (a flower, a crack, a pebble) placed on a second layer over the
base field do more than more base variants.

## Autotile / blob sets

To let a terrain connect to itself in every configuration you need a set of
edge and corner tiles. Standard set sizes:

| Set | Tiles | Handles |
|---|---|---|
| Minimal | 9 (3x3) | Edges + outer corners only. Blocky but cheap |
| **Blob / 47-tile** | 47 | Every edge, outer corner and inner corner combination. The industry standard for smooth terrain |
| Wang 2-corner | 16 | Corner-matched tiles; good for paths and water |

Practical approach: build the 3x3 core (top-left, top, top-right, left, centre,
right, bottom-left, bottom, bottom-right), then add the four **inner corners**
(the concave joints) — that covers the vast majority of real layouts. Expand to
the full 47 only if the terrain is used at scale.

Build tiles from smaller components: four 8x8 quadrants can be recombined into
many 16x16 tiles, which cuts the drawing work dramatically.

```
create_tilemap_layer(filename, "terrain", tile_width=16, tile_height=16)
draw_on_tile(filename, "terrain", tile_index=1, pixels=[...])     # appends new tiles
set_tiles(filename, "terrain", frame_index=1,
          tiles=[{"col":0,"row":0,"tile_index":1},{"col":1,"row":0,"tile_index":2}])
get_tilemap_info(filename, "terrain")
```

## Top-down environments

- **Pick a view angle and hold it.** Straight top-down (pure overhead) or the
  much more common **3/4 top-down**, where walls show their front face. Mixing
  them is the classic top-down mistake.
- In 3/4 view, a wall's *height* is a design constant — every wall in the game
  shows the same number of face pixels.
- **Floors are quiet, objects are loud.** Floor tiles should be low-contrast and
  low-saturation, or the character disappears into them.
- **Every object needs a contact shadow**, a dark ellipse or a 1px dark line at
  its base. Without it, objects float.
- Depth comes from **value, not perspective**: things further "back" (higher on
  the screen) get slightly darker and cooler; things nearer get lighter and
  warmer.

## Side-view / platformer environments

- **Playable surfaces must be visually distinct from decoration.** The player
  must know what they can stand on within one glance. Give platforms a
  brighter top edge and higher contrast than the background.
- **Background layers must be desaturated and value-compressed** — push them
  toward the ambient color, reduce their contrast, and never let them exceed the
  foreground's contrast range.
- **Parallax layers**, back to front: sky gradient (`apply_gradient_rect` or
  `apply_dither_gradient`), far silhouettes (a single flat dark color), mid
  scenery (2-3 values), foreground gameplay layer (full palette), optional
  overlay layer (fully dark, scrolls fastest).
- The far silhouette layer costs almost nothing and creates most of the depth.

## Props and set dressing

- Props inherit the scene's light direction — decide it once for the whole
  tileset, and do not let a prop contradict it.
- Prop shapes should **contrast with the terrain grid**: rounded props against
  square tiles, and vice versa.
- Repeated props need mirrored or shifted variants; use `flip_layer` plus a
  small hand edit so the mirror is not obvious.
- Anything interactive must be **brighter or more saturated** than anything
  decorative. Gameplay reads before flavour.

## Skies and gradients

```
apply_dither_gradient(filename, "sky", 1, x=0, y=0, width=320, height=90,
                      color_start="#2B3A6B", color_end="#E8A87C",
                      horizontal=False)
```

Bayer dithering between 3-4 sky colors gives a retro sky that costs almost no
palette. Dither between *adjacent* ramp steps only; dithering across a big value
jump produces visible static.

## 9-slice UI panels

A 9-slice lets one small panel graphic stretch to any size: the four corners
stay fixed, the four edges tile along one axis, and the centre fills.

```
create_slice(filename, name="panel", x=0, y=0, width=24, height=24)
set_slice_center(filename, name="panel", x=8, y=8, width=8, height=8)
```

The centre rectangle is the stretchable region. Rules:

- **Corners must contain the whole corner decoration** and nothing that should
  repeat.
- **Edges must be seamless along their tiling axis** — the top edge slice must
  tile horizontally without a seam.
- **The centre should be flat or a simple repeating texture.** A gradient in the
  centre will band when stretched.
- Keep the border a consistent thickness (2-3px at 16px scale) across every
  panel in the UI.

## UI and text

- Use bitmap fonts for pixel-perfect UI: `list_text_fonts`, then `measure_text`
  before `draw_text` so labels can be centred or panels sized in one pass.
- **Never anti-alias UI text** — leave `antialias=False`. Blurry text is the
  clearest sign of a broken pixel-art pipeline.
- Text needs contrast against a possibly-variable background: use
  `shadow_color` (1px offset) or `outline_color` on any text drawn over gameplay.
- Keep the UI on the same pixel grid as the game. If the game renders at 320x180
  scaled 4x, the UI must be authored at 320x180, not at 1280x720.

## Composition

- **Value hierarchy**: foreground gameplay layer has the widest value range;
  background is compressed toward the middle. Squint and the playable area
  should be the first thing you see.
- **Focal point**: the highest contrast and the most saturated accent in the
  frame go where you want the player to look.
- **Leave quiet space.** Uniform detail everywhere destroys hierarchy. Detail
  should cluster into islands, with calm areas between them.

## Checklist

- [ ] One tile size, one pixel grid, across tiles, characters and UI
- [ ] Tiles tested in a 4x4 block, not judged individually
- [ ] No strong feature on a tile edge or dead-centre
- [ ] Variants exist, including a quiet one used for most of the field
- [ ] Inner-corner tiles present, not just edges and outer corners
- [ ] One view angle throughout (3/4 or straight top-down)
- [ ] Contact shadow under every object
- [ ] Background desaturated and value-compressed relative to the foreground
- [ ] Playable surfaces clearly distinct from decoration
- [ ] 9-slice corners fixed, edges seamless, centre flat
- [ ] UI text not anti-aliased, with shadow or outline for contrast
