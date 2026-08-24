# Agent instructions — aseprite-mcp

This repository is an MCP server that drives Aseprite to produce pixel art and
animated sprites for games. If you are an AI agent about to create pixel art
with it, read this first.

## The rule

**Do not draw before reading the skills.**

Pixel art has hard craft rules — cluster control, anti-aliasing placement, hue
shifting, silhouette readability, cycle timing. A sprite that ignores them looks
generated, no matter how correct the tool calls were. Those rules ship with this
server as skill documents.

## How to load them

| Situation | How |
|---|---|
| You are connected to the `aseprite` MCP server | `list_pixelart_skills()` then `get_pixelart_skill(name)` |
| Your client supports MCP resources | `skill://pixelart/index`, `skill://pixelart/{name}` |
| You are working inside this repository | Read `aseprite_mcp/skills/*.md` directly |
| You are Claude Code | The skills are also registered in `.claude/skills/` |

Start with **`pixel-art-pipeline`** — it is the master workflow and tells you
which other skills to open, in what order.

## The skills

| Skill | Covers |
|---|---|
| `pixel-art-pipeline` | The master workflow, phase by phase, with verification gates |
| `pixel-art-fundamentals` | Clusters, jaggies, anti-aliasing, banding, outlines, dithering |
| `pixel-art-color` | Ramps, hue shifting, saturation curves, palette budgets |
| `pixel-art-shading` | Light direction, shadow anatomy, pillow shading, materials |
| `pixel-art-character-design` | Proportions, silhouette, faces at low res, the layer rig |
| `pixel-art-animation` | Frame counts, timing tables, walk/run/idle/attack/jump/hit |
| `pixel-art-vfx` | Impacts, explosions, fire, smoke, trails, game feel |
| `pixel-art-environments` | Tilesets, autotiles, parallax, props, 9-slice UI |
| `aseprite-mcp-playbook` | Technique → exact tool call, plus the silent-failure gotchas |
| `pixel-art-review` | How to critique work you cannot see, with a scoring rubric |
| `pixel-art-prompting` | Example prompts for people and objects: the six slots a brief must fill, weak→strong rewrites, revision phrases |

## Non-negotiables

1. **You are drawing blind.** Export with `export_frame(scale=8)` and actually
   read the PNG after every phase. A sprite you have not looked at is a draft.
2. **Always use the `*_at` drawing tools** with an explicit `layer_name` and
   `frame_index`. The implicit form silently paints the wrong layer.
3. **Build the palette before the first pixel.** See `pixel-art-color`.
4. **Silhouette before detail.** See `pixel-art-character-design`.
5. **Animate by moving cels, not by redrawing frames.** See `pixel-art-animation`.
6. **Read the return string of every tool call.** Nothing throws; failures come
   back as plain text and are easy to miss.

## Working on the repository itself

- Skill documents live in `aseprite_mcp/skills/` and are the single source of
  truth. After adding or renaming one, run
  `python3 scripts/sync-claude-skills.py` to regenerate the `.claude/skills/`
  wrappers.
- Tools are registered with `@mcp.tool()` in `aseprite_mcp/tools/*.py` and
  auto-registered by importing the module in `aseprite_mcp/tools/__init__.py`.
- Mutating tools generate Lua, run it through
  `AsepriteCommand.execute_lua_script_checked`, and signal failure by printing
  `ERROR:<message>` — batch-mode Lua cannot set the process exit code.
- Tests are end-to-end against a real Aseprite binary (`ASEPRITE_PATH`), not
  unit tests: `uv run pytest tests/`.
