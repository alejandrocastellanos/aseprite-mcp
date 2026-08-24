---
name: pixel-art-vfx
title: Effects and Game Feel
description: Impacts, explosions, smoke, fire, magic, trails and hit flashes - the short, loud animations that make a game feel responsive.
when_to_use: Any effect, particle, projectile, impact or screen-feedback asset; and when an attack animation lacks punch.
tools: draw_circle_at, draw_pixels_at, tween_cel_scale_eased, tween_cel_opacity_eased, adjust_brightness_contrast, apply_dither_gradient, set_layer_blend_mode, set_frame_duration, invert_colors
see_also: pixel-art-animation, pixel-art-color, pixel-art-shading
---

## What effects are for

Effects are not decoration — they are **feedback**. They tell the player that an
input registered, that a hit landed, that damage was dealt. That is why they are
short, bright and loud, and why they break the rules the character sprites obey.

Three properties separate a good effect from a bad one:

1. **Contrast.** An effect must be the brightest or the most saturated thing on
   screen for the frames it exists. Effects that blend in do not read.
2. **Speed.** Most effects are 4-8 frames at 40-70ms. If the player can study
   it, it is too slow.
3. **Growth and decay.** Effects almost always *expand fast and fade slow*.

## The universal effect curve

Nearly every impact effect follows the same three-beat shape:

```
frame:      1        2         3        4        5        6
size:      small -> BIGGEST -> big  -> medium -> small -> gone
bright:    white -> white  -> color -> color  -> dark  -> transparent
duration:   40ms     40ms     50ms    60ms      80ms     100ms
```

Expand to maximum within the first two frames, then decay over the rest with
*increasing* frame durations. An effect that grows gradually feels weak.

Implement it with the tweens rather than by hand:

```
tween_cel_scale_eased(filename, "fx", 1, 3, start_scale=0.4, end_scale=1.6,
                      easing="ease_out", anchor="center")
tween_cel_opacity_eased(filename, "fx", 3, 6, start_opacity=255, end_opacity=0,
                        easing="ease_in")
```

## Color for effects

Effects use a **hot-core ramp**, which is different from a material ramp:

```
core (white) -> hot (pale yellow) -> body (saturated) -> edge (deep) -> smoke (desat)
   #FFFFFF        #FFE9A0             #FF8A2B            #B03A18        #4A3A3A
```

- **The core is near-white regardless of the effect's color.** A blue magic
  blast still has a white-hot centre. This is what makes it read as *energy*.
- The identity color sits in the middle of the ramp, not at the core.
- The outer edge is the deepest, most saturated version.
- Fire ramps run white -> yellow -> orange -> red -> dark red -> grey smoke.
- Ice/magic ramps run white -> pale cyan -> cyan -> blue -> deep violet.

Effects are the one place to use maximum saturation, because they cover few
pixels for few frames. See the accent rule in `pixel-art-color`.

## Impact / hit spark

The highest-value effect in any action game. 3-5 frames.

1. **Flash frame**: a mostly-white shape at the contact point, no detail. 1 frame,
   40ms. This alone conveys "hit".
2. **Burst**: radial spikes outward from the impact point — 4-8 lines of
   different lengths, asymmetric. Symmetric bursts look like clip art.
3. **Decay**: spikes shorten, color drops down the ramp, gaps open.
4. Optional **debris**: 2-4 single pixels flying outward, arcing down.

Rules: the burst should be **perpendicular to the impact surface**, and it must
be off-centre and irregular. Draw the spikes at unequal lengths (e.g. 5, 3, 6, 2
px) — regularity kills it.

Pair it with the **hit flash** on the victim: the entire target sprite rendered
in flat white for 1-2 frames.

```
duplicate_layer(filename, "body", new_name="hit_flash")
adjust_brightness_contrast(filename, "hit_flash", 1, brightness=100, contrast=100)
# or simply fill the silhouette with white and toggle visibility for 2 frames
```

## Explosion (8-12 frames)

```
1-2  White-hot core, small, expanding fast
3-4  Maximum size, body color, ragged irregular edge
5-6  Ring breaks apart, dark gaps appear in the middle, debris flies out
7-9  Smoke: desaturated, rising, expanding slowly
10-12 Smoke thins and fades
```

Rules:

- **Break the ring.** A clean expanding circle reads as a bubble. Chunks must
  detach and gaps must open on the inside.
- **Asymmetry always.** Never mirror an explosion.
- **Smoke rises and slows** while the fire phase expands and accelerates. Two
  different motion characters in one effect.
- Debris pixels follow arcs (fast out, then falling), not straight lines.

## Fire (4-6 frame loop)

- Shape is a **teardrop**: wide unstable base, narrow flickering tip.
- Animate by **moving the internal color boundaries upward** while the outer
  silhouette barely changes. The hot core rises and pinches off.
- Flicker asymmetrically — never mirror frame to frame, or it reads as a
  wagging tongue.
- Occasional detached embers: 1-2 single pixels rising and fading.
- Fire *lights its surroundings*: add a warm tint on nearby surfaces (a separate
  low-opacity layer) or the fire looks pasted on.

## Smoke and dust (5-8 frames)

- Expands **slowly**, drifts in one direction, fades from the edges inward.
- Built from overlapping circles of slightly different sizes, not one blob.
- Desaturated; smoke should never compete with the fire that made it.
- Dust puffs at the feet on a landing or a run start sell weight for 3 frames
  and almost no pixels — one of the best effort-to-impact ratios available.

## Projectiles and trails

- **The projectile itself is tiny**; the trail is what reads. A 3px bullet with
  a 10px tapering trail looks fast; a 6px bullet with no trail looks slow.
- The trail tapers and drops down the color ramp behind the head.
- For a curved path, the trail must follow the arc — use several
  `tween_cel_positions_eased` segments.
- A **ghost trail** for a dashing character: copy the body cel to the fx layer
  at 2-3 previous positions with decreasing opacity
  (`tween_cel_opacity_eased`, or `set_cel_opacity` per cel).

## Magic and energy

- Charge-up: small pulsing core that **grows in irregular steps**, with particles
  converging inward. Converging particles are the visual language of "charging".
- Release: the universal curve, expanded along the attack direction.
- Sustained aura: 4-6 frame loop, slow, low contrast, `oscillate_cel_positions`
  with a small amplitude on an outer glow layer.
- Runes and arcane shapes must **rotate or pulse**, otherwise they read as a
  static decal.

## Screen-level feedback

Not sprites, but part of the same job, and worth noting in the asset spec you
hand to the engineer:

- **Hitstop**: freeze both sprites for 2-4 game frames on impact. The single
  strongest game-feel technique in existence, and it is free.
- **Screen shake**: 2-4px, 3-5 frames, decaying.
- **Flash**: full-white or full-color screen overlay for 1-2 frames.

If an attack lacks punch, the fix is almost never more animation frames — it is
hitstop, the impact hold, and a brighter impact frame.

## Effect design rules

- **Effects are read in peripheral vision.** Detail is wasted; shape and
  brightness are everything.
- **Silhouette applies to effects too.** An explosion should read as an
  explosion in one flat color.
- **Loop only what should loop.** Fire and auras loop; impacts and explosions
  must not — they play once and end on transparency.
- **Keep effects on the `fx` layer**, above everything, so they can be reused
  across characters and toggled independently.
- **Test on the actual background.** An effect that reads on transparency can
  vanish on a bright tileset. Composite it and check with
  `get_composite_rect`.

## Checklist

- [ ] Peaks within the first 2 frames, decays with increasing durations
- [ ] Near-white core regardless of the effect's identity color
- [ ] Asymmetric and irregular; nothing mirrored
- [ ] Reads as a silhouette in one flat color
- [ ] Brighter / more saturated than anything else on screen while it plays
- [ ] Non-looping effects end fully transparent
- [ ] Impact paired with a hit flash on the target
- [ ] Verified against a real background, not against transparency
