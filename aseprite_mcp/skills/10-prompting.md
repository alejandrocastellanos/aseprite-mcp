---
name: pixel-art-prompting
title: Prompting for Characters and Objects
description: Example prompts that produce game-ready sprites - the six decisions a brief must pin down, worked weak-to-strong rewrites for people and for objects, the vocabulary that actually steers the result, and the revision phrases that fix a finished sprite.
when_to_use: Whenever the request is one vague line ("draw a wizard", "make a sword icon"). Read before Phase 0, to fill the missing decisions deliberately instead of inventing them mid-draw.
tools: pixel_art_character, pixel_art_object, pixel_art_task, get_pixelart_skill
see_also: pixel-art-pipeline, pixel-art-character-design, pixel-art-environments, pixel-art-review
---

## The prompt is the first failure point

`pixel-art-pipeline` opens with Phase 0: five decisions written down before a
single pixel is placed. A one-line request — *"draw a wizard"* — settles none of
them. What happens next is the actual failure mode: the decisions still get
made, but one at a time, mid-draw, each one to suit the pixel currently being
placed. The canvas turns out too small for the detail already committed, the
palette grows a color per body part, and the sprite ends up as a small
illustration rather than a game asset.

So there are only two correct responses to a thin prompt:

1. **Fill the slots yourself and state them back** in your reply before drawing.
   This is the default — it keeps the work moving and makes the assumptions
   reviewable.
2. **Ask**, but only for the slots where a wrong guess would waste the whole
   sprite: the canvas size when the asset ships into an existing game, and the
   view angle when a set already exists.

Everything below is the raw material for both: the slots, and prompts that fill
them.

## The six slots

| # | Slot | For a person | For an object | Default if unstated |
|---|---|---|---|---|
| 1 | **Subject + role** | class, age, temperament | what it is, what it does in game | — (must be given) |
| 2 | **Canvas size** | 16 / 32 / 48 / 64 | 8 / 16 / 32 | 32x32 person, 16x16 object |
| 3 | **View angle** | side, top-down 3-4, front | flat icon, 3-4, isometric | matches the rest of the set |
| 4 | **Silhouette hook** | hat, cape, horns, weapon | the one shape that names it | the model invents one — say it |
| 5 | **Materials + palette** | cloth / leather / steel, mood | wood / iron / glass, mood | 8-16 colors, one accent |
| 6 | **Delivery** | states + frame counts, or "static" | icon on transparent, or in-scene | static PNG, transparent |

**Rule of thumb: leave at most two slots to the default.** Three or more and you
are no longer briefing a sprite, you are asking for a surprise.

Slot 4 is the one people skip and the one that decides whether the sprite works.
A silhouette hook is the single element that makes the shape nameable at 1x —
see the silhouette test in `pixel-art-character-design`. "A wizard" has no hook.
"A wizard whose pointed hat is half his height" has one.

---

## Person — the template

```
Draw {who: role, age, temperament} as a {W}x{H} pixel-art sprite.

View: {side | top-down 3-4 | front}, light from the top-left.
Proportions: {2 | 3 | 4-5} heads.
Silhouette hook: {the one oversized element that names the character at 1x}.
Materials: {list, dominant first}.
Palette: {N} colors, {mood}, one {color} accent on {small area}.
Deliver: {static sprite | idle 4f + walk 8f}, transparent background,
         layer rig split for animation.
```

### Weak → strong

**1. Hero, side view**

> Weak: `draw a knight`

What goes wrong: 32x32 is assumed, the armour detail wants 48x48, the palette
grows to nine greys, and the silhouette is a rectangle indistinguishable from
every other armoured sprite.

> Strong: `Draw a young knight as a 48x48 side-view sprite, 4 heads tall,
> light from the top-left. Silhouette hook: an oversized kite shield that
> covers half the body. Materials: steel plate (long high-contrast ramp),
> leather straps, a wool tabard. Palette 16 colors, cold steel and desaturated
> blue, one warm gold accent on the crest only. Static pose, transparent
> background, layers split body / head / arm_back / arm_front / shield.`

**2. Enemy, must read as a threat**

> Weak: `a goblin enemy`

> Strong: `Draw a goblin skirmisher as a 32x32 side-view sprite, 3 heads tall,
> light from the top-left. It must read as *lower* threat than the player
> knight: shorter, hunched, narrower silhouette. Silhouette hook: a jagged
> bone dagger held low and a single ragged ear. Materials: green-grey skin,
> filthy cloth. Palette 12 colors, sickly yellow-green; the dagger edge is
> the highest-contrast area on the sprite. Static, transparent background.`

Note what the strong version does: it briefs the character **against the rest of
the cast**, which is how enemy readability is actually decided.

**3. Top-down RPG NPC, a directional set**

> Weak: `make a shopkeeper for my rpg`

> Strong: `Draw a shopkeeper as a 24x24 top-down 3-4 view sprite for a 4-dir
> RPG, 3 heads tall, light from the top-left. Start with the "down" facing
> only. Silhouette hook: a wide apron and a tray held at chest height.
> Materials: linen apron, cotton shirt. Palette 12 colors, warm earthy,
> one red accent on the neckerchief. Feet centred at the bottom of the canvas,
> pivot recorded as a slice, identical pixel height across the other three
> facings I will ask for next.`

The last sentence is what stops the four facings from drifting a pixel apart.

**4. Portrait / key art**

> Weak: `a wizard portrait`

> Strong: `Draw an old wizard portrait as a 64x64 front-view bust, 6 heads
> proportions cropped at the shoulders, light from the top-left. Silhouette
> hook: a brow-heavy scowl under a broad hat brim. Materials: weathered skin
> (warm 5-step ramp), coarse beard, felt hat. Palette 24 colors, deep violet
> and cool grey, one cyan accent in the eyes. Facial expression must read at
> 1x: brows carry it, not the mouth. Static, transparent background.`

---

## Object — the template

```
Draw {what it is} as a {W}x{H} pixel-art {icon | prop | tile}.

View: {flat front | top-down 3-4 | isometric 2:1}, light from the top-left.
Silhouette hook: {the shape that names it at 1x, on transparency}.
Materials: {list} — {which one is metal/glass, so it gets the long ramp}.
Palette: {N} colors, {mood}, one {color} accent.
Deliver: {transparent icon | sits on a {surface} in a scene}.
Set: {matches <other asset> — same palette, same ramp, same outline style}.
```

### Weak → strong

**1. Weapon icon**

> Weak: `a sword icon`

What goes wrong: at 16x16 a sword drawn straight up is a 2px vertical line with
a crossbar — unreadable in an inventory grid. Nothing in the prompt prevented it.

> Strong: `Draw a longsword as a 16x16 inventory icon, flat front view rotated
> 45 degrees so the blade fills the diagonal, light from the top-left.
> Materials: steel blade — long high-contrast ramp with a hard 1px specular,
> which is what makes it read as metal, not plastic — leather grip, brass
> pommel. Palette 10 colors, one gold accent on the pommel only. Selective
> outline, transparent background. Must be identifiable at 1x in a grid of
> other icons.`

The 45-degree instruction is doing the real work: it is a *composition* fix for
a resolution problem.

**2. Consumable**

> Weak: `a health potion`

> Strong: `Draw a health potion as a 16x16 inventory icon, flat front view,
> light from the top-left. Silhouette hook: a round-bellied flask with a
> short cork neck, so it is not confusable with the tall thin mana vial I
> will ask for next. Materials: glass — 3 base values plus one bright
> specular pixel and a dark interior, which is how glass reads — cork, liquid.
> Palette 10 colors, red liquid, one near-white specular. Transparent
> background, selective outline.`

**3. Prop inside a scene**

> Weak: `draw a treasure chest`

> Strong: `Draw a closed treasure chest as a 32x24 prop for a top-down 3-4
> view level, light from the top-left. Silhouette hook: a domed lid with two
> iron bands. Materials: dark oak (grain in the shadow color, broken not
> continuous), iron bands, brass lock. Palette 14 colors matching the dungeon
> tileset's earthy ramps, one brass accent on the lock. Include a contact
> shadow on the ground so it does not float. It is interactive, so it must be
> visually louder than the surrounding scenery.`

**4. A consistent set**

> Weak: `now make a shield icon too`

> Strong: `Draw a round wooden shield as a 16x16 inventory icon matching the
> longsword icon already in this file: same palette, same ramp steps, same
> selective outline, same 45-degree light from the top-left, same visual
> weight in the frame. Silhouette hook: a central iron boss. Read the existing
> icon's palette with get_color_stats first and reuse it exactly — do not
> invent new colors.`

That last sentence is the whole difference between a set and a pile.

---

## Vocabulary that steers the result

| Say this | And it changes |
|---|---|
| "reads at 1x" | Forces the silhouette gate; kills sub-pixel detail |
| "silhouette hook: X" | Fixes the single most-skipped design decision |
| "N heads tall" | Locks proportion; stops adult-mannequin drift |
| "light from the top-left" | Prevents contradictory per-part shading |
| "hue-shifted ramps" | Cool shadows, warm highlights — not a brightness slider |
| "one X accent on Y only" | Confines saturation to a small area |
| "long high-contrast ramp" | The difference between steel and plastic |
| "selective outline" | Depth, instead of a flat sticker border |
| "no dithering" | Stops texture noise on small moving sprites |
| "dawnbringer16" | Hard palette discipline via a fixed preset |
| "matches <asset>, reuse its palette" | Turns two assets into a set |
| "layers split for animation" | Produces a rig, not a flattened image |

## Anti-patterns

| Phrase | Why it hurts |
|---|---|
| "make it look like pixel art" | Invites downscaling a picture — the one thing that never works |
| "highly detailed", "8k", "ultra HD" | Detail is the constraint being fought; this fights the medium |
| "realistic" | Pushes toward anti-aliased mush at 32px |
| "photorealistic lighting" | Produces soft gradients where abrupt terminators belong |
| "cute AND gritty AND epic" | Stacked adjectives that resolve to no palette |
| "16x16, very detailed face" | A contradiction: 16px allows two eye pixels, nothing more |
| "use lots of colors" | Guarantees the muddy look; tight palettes are what cohere |
| "any size is fine" | The size *is* the design; it decides everything downstream |

## Revision prompts

When the sprite comes back wrong, name the symptom — the fix is then
deterministic. See the diagnosis table in `pixel-art-review`.

| What you see | Say this |
|---|---|
| Can't tell what it is at game size | "The silhouette fails at 1x — go back to Phase 3 and rebuild the flat shape before any detail" |
| Flat, like a sticker | "Pillow shading — re-shade from one top-left light and add occlusion shadows where forms meet" |
| Blurry, washed out | "Too many colors and over-anti-aliased — cut the palette and keep AA to step corners only" |
| Muddy colors | "Rebuild the ramps with hue shifting, cool shadows and warm highlights" |
| Metal looks like plastic | "Give the metal a 6-7 step high-contrast ramp with a hard near-white specular" |
| Two parts fuse together | "Those materials are the same value — separate them in brightness, not just hue" |
| Doesn't match the other asset | "Reuse the existing palette exactly; read it with get_color_stats first" |
| Animation jitters | "Frames were redrawn — rebuild with propagate_cels plus tweens" |

## Checklist for a brief

- [ ] Subject names a role, not just a noun
- [ ] Canvas size stated, and it fits the detail asked for
- [ ] View angle stated, or explicitly "match the existing set"
- [ ] One silhouette hook named
- [ ] Materials listed, with the metal/glass ones flagged for long ramps
- [ ] Palette budget and exactly one accent
- [ ] Static vs animated stated, with frame counts if animated
- [ ] For a second asset: "matches X, reuse its palette"
- [ ] No contradiction between the size and the level of detail requested
