---
name: pixel-art-shading
title: Shading, Light and Form
description: Turning flat shapes into volume - light direction, the shadow anatomy, pillow shading, occlusion, materials, and rim light.
when_to_use: Phase 5, after flat colors are down. Also whenever a sprite looks flat, plastic or like a sticker.
tools: draw_pixels_at, fill_area_at, adjust_hsl, apply_dither_gradient, apply_dither_pattern, set_layer_blend_mode, set_layer_opacity, outline_cel
see_also: pixel-art-color, pixel-art-fundamentals, pixel-art-character-design
---

## The question that catches every mistake

After shading, ask: **"where is the light coming from?"** If you cannot point at
a direction, the shading is wrong. Every rule below descends from that one.

Pick the direction in Phase 0 and never contradict it. Default: **top-left**,
slightly in front. It is the convention, it describes form well, and it keeps
every sprite in a set consistent.

## Shadow anatomy

Even at 32x32 a lit form has distinct parts. You will not fit all of them; know
which to drop.

| Part | What it is | Priority |
|---|---|---|
| **Highlight** | Small, brightest, where the surface faces the light directly | Medium — an accent, never a coating |
| **Light** | Base color, the lit face | Essential |
| **Core shadow** | The darker step where the surface turns away | Essential |
| **Occlusion shadow** | Darkest, 1px, where two forms meet or contact | **Essential — highest value per pixel** |
| **Bounce light** | Slight lift at the bottom edge of a shadow, from light reflecting off the ground | Optional, 48x48+ |
| **Cast shadow** | Shadow the form throws onto another surface | Situational |

At 16x16: base + one shadow. At 32x32: base + shadow + occlusion + a few
highlight pixels. At 64x64: the full set including bounce.

**Occlusion is the technique beginners skip and pros never do.** One pixel of the
darkest value under the chin, under the arm, where the boot meets the ground —
that is what makes parts sit *in front of* each other instead of being pasted
side by side.

## Pillow shading — the defining beginner failure

Pillow shading is shading each part independently, with the highlight in the
*centre* of the shape and the shadow radiating outward to the edges. It produces
a soft, puffy, direction-less blob.

```
Pillow shading (WRONG)      Directional (RIGHT, light from top-left)
  .2222.                      .1112.
  233332                      112223
  234432   <- highlight       122333
  233332      dead centre     123334   <- highlight offset toward the light
  .2222.                      .23334      shadow gathers bottom-right
```

Symptoms:
- The shadow follows the outline all the way around the shape.
- The highlight is centred in every part.
- Every part is shaded the same way regardless of where it sits.

Cure: pick the light direction, then shade **the whole sprite as one object**.
The arm on the shadow side of the body is darker overall than the arm on the lit
side — not because of its own form, but because of where it is.

## Rules

1. **Shade the form, not the outline.** The shadow edge should follow the
   surface turning away from the light. If it traces the silhouette, you have
   banding (see `pixel-art-fundamentals`).

2. **Value change should be abrupt at a terminator.** Pixel art has few colors;
   smearing a soft transition wastes them. Let the shadow edge be a decisive
   line that describes where the form turns.

3. **Highlights go on "sweet spots", not everywhere.** Pick the two or three
   surfaces most directly facing the light — the top of the shoulder, the brow,
   the top of the helmet. Over-highlighting bleaches out the base color and
   destroys the material's identity.

4. **Shade parts relative to the whole.** Build the value hierarchy first
   (which masses are in light, which in shadow) before shading any individual
   part's internal form.

5. **Two values well placed beat five values badly placed.** At small sizes,
   more shades usually means less clarity.

6. **Cast shadows are directional too.** If light comes from the top-left, the
   sword casts a shadow down-right onto the body. A cast shadow on the ground
   is what stops a character floating.

## Materials

Materials differ by **ramp length**, **highlight size** and **contrast**, not by
hue alone.

| Material | Ramp | Highlight | Notes |
|---|---|---|---|
| Skin | 4-5, warm, low contrast | Soft, small | Shadows shift red/purple, not grey. Add subtle warmth at the cheeks/knuckles |
| Cloth (matte) | 3-4, low contrast | Almost none | Value change is gradual; folds are the interest, not shine |
| Leather | 4, medium contrast | Small, dull, at edges | Slight sheen on worn edges only |
| Wood | 3-4 + grain texture | None | Grain lines in the shadow color, broken not continuous |
| Stone | 3-4, desaturated | None | Texture via scattered darker clusters, not dithering |
| **Metal (steel)** | **6-7, very high contrast** | **Hard, bright, small** | Long ramp, abrupt jumps, a near-white specular pixel next to a near-black. This contrast *is* what reads as metal |
| Gold / brass | 6, warm, high contrast | Hard, near-white warm | Same as steel plus a strong hue shift toward orange |
| Glass / gem | 3 base + bright specular + dark core | 1-2 pixels, brightest in the sprite | Reads via the specular dot and a dark interior |
| Water | 4-5, high sat, cool | Moving specular highlights | Highlights animate; that is what sells it |
| Fire / glow | 4-5, from white core outward | The whole thing | See `pixel-art-vfx` |

The practical takeaway: **the difference between plastic and steel is contrast,
not color.** A 3-step low-contrast ramp will always read as plastic.

## Rim light / back light

A 1px line of a bright, often cool color along the edge *opposite* the main
light. It separates the character from the background and adds enormous
production value for very few pixels.

Rules: use it on the shadow-side edge only, keep it 1px, keep it to the upper
edges of forms, and do not close it into a full outline — a full rim is
pillow shading in disguise.

## Doing it with the tools

Two workable approaches.

**A. Direct (preferred at small sizes).** Draw the shadow pixels straight onto
the material's layer with `draw_pixels_at` using the ramp's darker step. Full
control, no surprises.

**B. Shadow layer (good for big sprites and quick iteration).**

```
duplicate_layer(filename, "body", new_name="body_shadow")
adjust_hsl(filename, "body_shadow", 1, hue_shift=-15, saturation_shift=5,
           lightness_shift=-25)
# then erase the lit region from the shadow layer
erase_region(filename, "body_shadow", 1, x, y, w, h)
```

This gives a physically consistent shadow ramp for free — the hue shift is
applied uniformly — and you sculpt by *removing* rather than by placing. Merge
down with `merge_layer_down` once satisfied.

**Blend modes** (`set_layer_blend_mode`) are a trap in pixel art: `multiply`
and `overlay` generate colors that are not in your palette. If you use them,
follow with `quantize_to_palette` to snap back onto the palette, then verify
with `get_color_stats`.

## Ambient occlusion pass

A cheap, high-impact final pass: go around the sprite and put the darkest ramp
value at every point where two forms touch.

- Under the chin / helmet brim
- Where the arm overlaps the torso
- Inside the elbow and knee
- Where a strap crosses the body
- Where the character meets the ground

One pixel each. This single pass typically does more for perceived quality than
an extra shading value.

## Checklist

- [ ] One light direction, stated, and obeyed everywhere
- [ ] No highlight sits in the centre of a part
- [ ] Shadow edges follow the form, not the outline
- [ ] Occlusion shadows present at every form intersection
- [ ] Highlights limited to 2-3 sweet spots
- [ ] Parts on the shadow side of the body are darker overall
- [ ] Metal has a long high-contrast ramp; cloth has a short low-contrast one
- [ ] Contact shadow on the ground, so the character is not floating
- [ ] Every color used exists in the palette (`get_color_stats`)
