---
name: pixel-art-animation
title: Sprite Animation - Cycles, Timing and Feel
description: Frame counts, key poses, timing tables and the animation principles that survive at 32x32. Walk, run, idle, attack, jump, hit and death, built by moving cels rather than redrawing.
when_to_use: Phase 8, and any time the request involves motion, a cycle, a sprite sheet or a GIF.
tools: add_frames, propagate_cels, copy_cel, tween_cel_positions_eased, oscillate_cel_positions, tween_cel_scale_eased, tween_cel_opacity_eased, set_frame_duration, set_tag, render_onion_skin, compare_frames, audit_animation, export_tag, export_spritesheet
see_also: pixel-art-pipeline, pixel-art-character-design, pixel-art-vfx, aseprite-mcp-playbook
---

## The rule that governs everything

**Animate by moving cels, not by redrawing frames.**

Redrawing a 32x32 character eight times produces eight subtly different
characters — the head grows a pixel, the belt shifts, the colors drift. That
jitter is the clearest signal of amateur or generated animation.

The correct loop: draw the parts **once**, propagate them across the frames,
then move, scale, fade and reorder those cels per frame. Redraw only the parts
that genuinely deform (a bending knee, a swinging blade), and redraw them by
editing a copied cel, never from scratch.

```
add_frames(filename, count=7, duration_ms=120)                  # 8 frames total
propagate_cels(filename, ["body","head","arm_back","arm_front"], 1, 2, 8)
oscillate_cel_positions(filename, "head", 1, 8, amplitude_y=1, cycles=2)
tween_cel_positions_eased(filename, "weapon", 1, 4, 20,10, 26,6, easing="ease_out")
set_tag(filename, "walk", 1, 8, direction="forward")
```

## Frame budgets

| State | Frames | Notes |
|---|---|---|
| Idle (breathing) | 2-4 | 2 is enough: neutral + 1px raise. 4 for a settle |
| Idle (character-full) | 6-8 | Hair, cape, weapon shift; use for the player character |
| Walk | 4, 6 or **8** | 4 = retro/economical, 8 = the sweet spot, 6 = compromise |
| Run | 6-8 | Needs an airborne frame |
| Attack (melee) | 4-8 | 3 essentials: anticipation, strike, recovery |
| Jump | 3-5 | anticipation / launch / apex / fall / land |
| Hit / hurt | 2-3 | Short, hard, high contrast |
| Death | 6-12 | The one place to spend frames |
| Turn | 2-3 | Optional; sells 4-directional movement enormously |
| Item / prop loop | 4-8 | Coins, torches, portals |

More frames is not smoother if the poses are weak. **Four strong poses beat
twelve mushy ones.** Start with the extremes; add in-betweens only where the
motion visibly stutters.

## Timing

Frame duration is half of animation. Aseprite stores it per frame
(`set_frame_duration`) or globally (`set_frame_duration_all`).

| Motion | ms per frame | ~fps |
|---|---|---|
| Idle breathing | 150-250 | 4-6 |
| Walk | 100-150 | 7-10 |
| Run | 60-100 | 10-16 |
| Attack windup (anticipation) | 60-100 | fast in |
| Attack strike frame | **30-60** | the fastest frame in the sprite |
| Attack impact hold | **150-300** | **hold it** |
| Recovery | 80-120 | |
| Hit flash | 40-80 | |
| Explosion / burst | 40-70 | |
| Death | 80-150, slowing to 300+ | decelerate into stillness |

**Uneven timing is what creates feel.** A cycle with all frames at the same
duration reads mechanical. The single most effective trick in game animation:
make the wind-up quick, the strike frame the shortest in the sequence, and then
**hold the impact frame 3-5x longer than anything else**. That hold is what the
player feels as weight.

## The animation principles that matter at low resolution

Only these survive; the rest are for feature animation.

1. **Anticipation** — every action moves *opposite* first. Crouch before jump,
   pull the sword back before the swing, lean back before running. Without it
   the action has no readable start, and in a game the player has no cue to
   react to. Anticipation is game design, not polish.

2. **Squash and stretch** — at low res this is 1-2 pixels.
   - Anticipation (crouch): 1-2px shorter, 1px wider.
   - Launch / fast travel: 1-2px taller, 1px narrower.
   - Impact: squash on the frame of contact, snap back next frame.
   `tween_cel_scale_eased(start_scale=1.0, end_scale=0.9, anchor="bottom")`
   handles it for a whole layer.
   **Conserve volume**: if it gets shorter it must get wider, or it just shrinks.

3. **Follow-through and overlap** — parts do not stop together. Hair, cape,
   scabbard and ears keep moving 1-2 frames after the body stops. Implement by
   running the same tween on the secondary layer **offset by one frame**. This
   is the cheapest thing that makes an animation look alive.

4. **Arcs** — nothing moves in a straight line. A hand travels along a curve.
   Use `tween_cel_positions_eased` in two segments with different easing rather
   than one linear move, or hand-place the mid-frame off the straight line.

5. **Slow in / slow out** — extremes hold, middles move fast. `easing="ease_out"`
   for something arriving, `"ease_in"` for something departing, `"smoothstep"`
   for a settle. **Exception: impacts have no ease.** A punch is linear-fast then
   a dead stop.

6. **Secondary action** — a small extra motion that supports the main one: the
   head turning as the body leans, the tail flicking, dust at the feet.

## Walk cycle (8 frames, side view)

Key poses, in order. Frames 5-8 mirror 1-4 with the opposite leg.

| # | Pose | Body height | Description |
|---|---|---|---|
| 1 | **Contact** | lowest (-1) | Front heel lands, back toe leaves. Legs at maximum spread, arms at maximum swing |
| 2 | **Down / recoil** | lowest (-1) | Weight drops onto the front leg, knee bends. The lowest point of the cycle |
| 3 | **Pass** | **highest (+1)** | Legs cross under the body, the moving leg's knee lifts. Body pushed up by the straight support leg |
| 4 | **Up / swing** | mid | The moving leg swings forward, body starts to fall |
| 5-8 | Mirror of 1-4 | | Opposite leg leading |

Rules:

- **Arms oppose legs.** Left leg forward = right arm forward. Always.
- **Vertical bob is 1-2px** at 32x32 — no more. The head traces a
  **triangle-shaped wave, not a smooth sine**: it rises to the pass pose and
  falls sharply into the contact. Uniform sine bobbing feels floaty and wrong.
- **Same stride distance for both legs**, or the character appears to stretch
  and compress like an accordion.
- **Animate in order: legs, then arms, then head and body bob.** Do not try to
  solve all three at once.
- 4-frame version: contact, pass, contact (mirrored), pass (mirrored). It works,
  it just reads as retro.
- **A walk cycle is drawn in place.** Movement across the world is the engine's
  job. The feet must not slide: at the contact pose the planted foot should be
  visually locked, which means the *body* moves over it, not the reverse.

## Run cycle (6-8 frames)

Differences from a walk:

- **Forward lean**: 2-3px at 32x32.
- **Airborne frame**: at least one frame where neither foot touches ground —
  this is the difference between a run and a fast walk.
- **Longer stride, higher knee lift, arms bent ~90 degrees** and pumping hard.
- **Larger vertical bob** — 2-3px.
- More extreme contact pose: legs fully extended fore and aft.

## Idle (2-8 frames)

The most-seen animation in any game. Do not leave it static.

- 2-frame minimum: neutral, then the whole body 1px down (a breath out), held
  longer than the up frame.
- Better: `oscillate_cel_positions(amplitude_y=1, cycles=1)` on the body across
  6-8 frames, plus the same on `head` **offset by one frame** for overlap.
- Add a rare accent: a blink, a weapon adjustment, hair moving. Do not loop it
  every cycle — irregular is what reads as alive.
- Breathing is asymmetric: the inhale is faster than the exhale.

## Attack (4-8 frames)

The three-part structure, in this proportion of screen-time:

```
| ANTICIPATION      | STRIKE | IMPACT HOLD    | RECOVERY   |
| 2 frames, 80ms ea | 1 fr   | 1 fr, 200ms    | 2 fr, 100ms|
| pull back, lean   | 40ms   | the money shot | settle back|
```

- The anticipation should read as a **held pose** — the player must have time to
  see it coming.
- The strike frame is often barely a pose at all: it is a **smear** (below).
- The impact frame carries the hit: maximum extension, maximum contrast, the fx
  layer at its brightest, and it holds.
- Recovery returns to idle. Skipping it makes attacks feel like they teleport.

## Smear frames

A smear is a single deliberately distorted frame that represents the whole path
of a fast motion. It is what makes 4-frame attacks feel smooth.

Forms, cheapest first:

- **Elongation**: stretch the moving part along its path (a 4px fist becomes a
  10px streak).
- **Multiples**: draw the limb in 2-3 positions at once in the same frame.
- **Motion arc**: replace the object entirely with the arc it swept — a crescent
  in the blade's highlight color. Standard for sword swings.
- **Full replace**: for a single frame, the object *is* the smear.

Smears live on their own frame and last 30-60ms. They look absurd paused and
perfect in motion — do not judge them frame-by-frame.

## Jump

| Phase | Frames | Detail |
|---|---|---|
| Anticipation | 1-2 | Crouch, squash 2px, hold ~100ms |
| Launch | 1 | Stretch 2px tall, arms up, the fastest frame |
| Apex / fall | 1-2 | Neutral-ish, arms out, legs tucking |
| Land | 1-2 | Squash hard, then a 1-frame recovery back to idle |

The landing squash + recovery is what gives a jump weight. Skipping it is the
most common jump-animation mistake.

## Hit and death

- **Hit**: 2-3 frames. Recoil away from the impact direction, whole body shifted
  2-3px. Combine with a **full-white flash** on the sprite for 1-2 frames — use
  a duplicated layer filled with white on the `fx` layer, or
  `adjust_brightness_contrast(brightness=100)` on a copy.
- **Death**: the one place to be generous. Impact -> stagger -> fall -> settle,
  with frame durations *increasing* toward the end so the motion decelerates
  into stillness. Optionally end with a dissolve using
  `tween_cel_opacity_eased(start_opacity=255, end_opacity=0)`.

## Sub-pixel animation

For motion slower than one pixel per frame, you cannot move the cel. Instead,
shift the *shading* inside the sprite while the outline stays put: move a
highlight one pixel, darken an edge, redistribute one pixel of a cluster. The
eye integrates this as motion smaller than a pixel.

Use it for: slow idle breathing on a small sprite, a slowly turning head, a
gently drifting cloud, water surface movement.

## Anti-drift discipline

The failures that ruin otherwise good animation:

| Failure | Cause | Prevention |
|---|---|---|
| Sprite jitters when it should be still | Redrawn frames | `propagate_cels` from one source frame |
| Character grows/shrinks over the cycle | Redrawn frames | Same |
| Parts separate from the body | Independent tweens with mismatched ranges | Tween relative to the body's motion; verify each frame |
| Feet slide during a walk | Contact foot not locked | Check with `render_onion_skin`: the planted foot must not move |
| Frame 1 and the last frame are identical | Miscounted loop | A forward loop must not repeat frame 1 at the end — cut the last frame |
| A frame is accidentally empty | Missing cel | `audit_animation` / `ensure_layers_present` |
| Colors drift across frames | Hand-picked colors per frame | Palette + `get_color_stats` per frame |

**Loop rule:** for a `forward` cycle of N frames, frame N must be the frame
*before* returning to frame 1 — never a copy of frame 1. For `pingpong`, the
first and last frames each play once, so a 5-frame pingpong reads as 8.

## Verification (do not skip)

```
render_onion_skin(filename, frame_index=3, output_filename="onion3.png",
                  before=1, after=1, scale=4)      # motion continuity
compare_frames(filename, 2, 3)                     # changed pixels, bbox
audit_animation(filename, report_cels=True, report_bounds=True)
export_tag(filename, "walk", "walk.gif", scale=4)  # then look at it
```

Reading the results:

- `compare_frames` returning ~0% changed = a dead frame; delete it or make it do
  something.
- `compare_frames` returning a huge % between neighbours = a pop; you need an
  in-between.
- `render_onion_skin` where the ghosts do not form a smooth path = broken arc.
- A bounding box that grows over the cycle = drift.

## Export

```
export_tag(filename, "walk", "preview.gif", scale=4)
export_spritesheet(filename, "player_walk.png", sheet_type="horizontal",
                   data_filename="player_walk.json", tag_name="walk",
                   padding=1, list_tags=True)
```

Use `padding=1` when the engine samples with filtering, to prevent bleeding
between frames. Ship the sheet plus its JSON, never the GIF.

## Checklist

- [ ] Built by propagating and moving cels, not redrawing
- [ ] Frame count matched to the state, extremes drawn before in-betweens
- [ ] Frame durations are **uneven**; the impact frame is held 3-5x
- [ ] Anticipation exists before every significant action
- [ ] Arms oppose legs; stride distance equal both sides
- [ ] Vertical bob 1-2px, triangle wave, not a sine
- [ ] Secondary parts lag the primary by one frame
- [ ] Squash/stretch conserves volume
- [ ] Loop does not repeat frame 1 at the end
- [ ] Feet do not slide (verified on onion skin)
- [ ] `audit_animation` clean; no dead frames per `compare_frames`
- [ ] Tag set, sheet exported with JSON
