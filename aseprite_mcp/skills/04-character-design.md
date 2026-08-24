---
name: pixel-art-character-design
title: Character Design for Sprites
description: Proportions, silhouette, feature hierarchy at low resolution, the animation-ready layer rig, directional sets, and designing a cast that reads in gameplay.
when_to_use: Phase 0 and Phase 3, whenever the asset is a character, enemy, NPC or creature.
tools: create_canvas, add_layer, add_group, draw_ellipse_at, draw_polygon, draw_pixels_at, export_frame, duplicate_layer, flip_layer, create_slice, set_slice_pivot
see_also: pixel-art-pipeline, pixel-art-animation, pixel-art-shading, pixel-art-fundamentals
---

## Design constraint first

A character sprite is not an illustration that happens to be small. It is a
*symbol* that must be identified in under a second, at 1x, while moving, next to
other characters, on a busy background. Every design decision serves that.

## Proportions

Measured in heads. Lower head counts read as cuter and survive small canvases;
higher counts read as realistic and need pixels to work.

| Head ratio | Feel | Min canvas | Typical use |
|---|---|---|---|
| **2 heads** (chibi) | Cute, iconic, huge expressive face | 16x16 | Mobile, farming/life sim, cosy games |
| **3 heads** | The pixel art default. Cute but capable | 24x24 - 32x32 | Most action-RPGs, roguelikes |
| **4-5 heads** | Grounded, heroic | 32x48 - 48x64 | Action-platformers, metroidvanias |
| **6-8 heads** | Realistic, cinematic | 64x64+ | Fighting games, cutscene sprites, portraits |

At 3 heads on a 32px-tall sprite: head ~11px, torso ~10px, legs ~11px. Round
in favour of the head — an undersized head reads as an adult mannequin and loses
all personality.

**The head is the identity.** At small sizes, enlarge the head and the
silhouette-defining accessory (hat, hair, weapon) and shrink everything else.
Anatomical correctness is worth nothing if the character is unrecognisable.

## The silhouette test

Draw the character as a single flat color before anything else, then look at it.

Passing means: you can name the character class, see which way it faces, and
identify its weapon or defining prop — from the black shape alone.

Techniques for a strong silhouette:

- **One big shape idea.** A triangle (mage robes), a rectangle (knight), a
  circle (slime). If the silhouette has no dominant geometric read, redesign.
- **Silhouette-defining accessory.** Hat, cape, horns, backpack, an oversized
  weapon. This is what distinguishes two characters with the same body.
- **Negative space.** A gap between arm and torso, between legs, under a cloak.
  Solid blobs read as amorphous; holes read as anatomy.
- **Asymmetry.** One pauldron, one arm raised, hair sweeping one way. Symmetric
  characters look static and are hard to tell apart.
- **Test against the cast.** If two characters have the same silhouette, one is
  redundant. Vary height, width and top-shape between them.

Verify with `export_frame(filename, 1, "sil.png", scale=8)` while only the flat
silhouette layer is visible (`set_layer_visibility`).

## Faces at low resolution

| Height available | What fits |
|---|---|
| 4-6px | Two eye pixels. That is all. Expression comes from body pose |
| 7-10px | Eyes (1-2px each), a hint of mouth or a nose pixel, hair shape |
| 11-16px | Eyes with pupils, mouth, brow, nose, defined hairline |
| 17px+ | Full expression, cheeks, individual features shaded |

Rules:

- **Eyes are the anchor.** Place them first, at roughly the vertical midpoint of
  the head (higher for cuter, lower for more mature). Eye *spacing* does more
  character work than eye shape.
- **Do not draw a mouth if it does not fit.** A misplaced mouth pixel reads as
  dirt or a chin scar. Better to omit it.
- **Brows carry the expression** at 32x32, more than the mouth does. A 1px brow
  angled down and in = angry. Up and out = worried.
- **Skip the nose** below ~12px of head height, unless the character's identity
  is the nose (a witch, a dwarf).
- Do not outline eyes in black if the head is under 10px — they turn into
  black holes.

## Character layer rig

Split by what moves independently, not by what looks separate. Decide this
*before* drawing, from the animation list.

Side-view action character:

```
character/
  arm_back        <- below body
  leg_back
  body            <- torso, hips: the anchor, usually barely moves
  head            <- bobs, turns
  hair            <- follows head with a 1-frame delay (overlap)
  leg_front
  arm_front
  weapon          <- the biggest mover
fx                <- slashes, dust, flashes: above everything
```

Top-down character: `shadow / legs / body / head / hair / held_item / fx`.

Rules:

- **The body is the anchor.** Everything else is positioned relative to it.
  Animate the body's vertical bob first, then hang the other layers off it.
- **Overlapping parts need their own layer** even if they never move alone —
  otherwise you cannot re-order them for a turn.
- **Keep an `fx` layer at the top from the start**, so an attack flash never
  forces a restructure.
- Name layers exactly as you will call them; every drawing tool takes
  `layer_name` and a typo silently creates or misses a target.

Verify the rig with `validate_scene(filename, required_layers=[...])`.

## Directional sets

| Set | Directions | Cost | Use |
|---|---|---|---|
| 1-dir | side only | 1x | Platformers — mirror for the other side |
| 2-dir | left/right | 1x + flip | Side-scrollers with asymmetric characters |
| 4-dir | down/up/left/right | ~3x | Classic top-down RPG. **The standard.** |
| 8-dir | + diagonals | ~5x | Twin-stick shooters, action RPGs |

Rules:

- **Mirroring is free but lies.** `flip_layer(direction="horizontal")` gives you
  the opposite facing instantly, but any asymmetric element — a scabbard on the
  left hip, a scar, a single pauldron — jumps to the wrong side. Either design
  the character symmetric, or mirror and then hand-fix the asymmetric layer.
- **The back view is not the front view with a different head.** It needs its
  own hair mass, no face, and usually a different shoulder read.
- **Keep the same pixel height across all directions.** A character that grows
  1px when turning will bounce visibly in game.
- Front (down) view: shoulders wider than the side view. Side view: narrower
  body, one arm hidden or in front.

## Designing a cast

- **Vary the primitive.** Give each character a different dominant shape:
  triangle, square, circle, tall rectangle. This is the fastest way to make a
  roster readable.
- **Silhouette-first differentiation.** Two characters must differ before color
  is applied — colorblind players and dark scenes both depend on this.
- **Gameplay reads before flavour.** An enemy that can hurt you should be
  visually louder than scenery. A dangerous part (a spike, a blade) should be
  the highest-contrast area of the sprite.
- **Palette family per faction.** Same ramps, rotated hue, identical values —
  see the palette-swap section in `pixel-art-color`.
- **Size = threat.** Players read bigger as stronger before they read anything
  else. Use it deliberately.

## The pivot / anchor

Every character sprite has an origin the engine positions it by — usually the
**centre of the feet**. It must be identical across every frame and every
direction, or the character will jitter and slide.

Record it in the file so the engine and the artist agree:

```
create_slice(filename, name="origin", x=0, y=0, width=32, height=32)
set_slice_pivot(filename, name="origin", x=16, y=31)     # feet centre
```

For a weapon-hand attachment point, add a second slice. `list_slices` reads them
back, and `export_spritesheet(data_filename=...)` writes slice data into the
JSON for the engine.

Also keep the character in a consistent **canvas box** across states: idle,
walk and attack should all place the feet at the same y. Attack animations that
extend past the box need a bigger canvas for *all* states, not just that one.

## Checklist

- [ ] Head ratio chosen and consistent with the canvas size
- [ ] Silhouette test passed at 1x before any detail
- [ ] One dominant shape idea + one silhouette-defining accessory
- [ ] Asymmetry present; negative space present
- [ ] Face features limited to what the head height supports
- [ ] Layer rig derived from the animation list, `fx` layer at the top
- [ ] Same pixel height and same feet-y across all directions and states
- [ ] Pivot recorded as a slice
- [ ] Distinguishable from the rest of the cast in silhouette alone
