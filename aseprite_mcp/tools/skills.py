"""Expose the bundled pixel-art skills to any MCP client.

Three surfaces over one set of Markdown files:

* tools     -- `list_pixelart_skills` / `get_pixelart_skill`, which every MCP
               client supports, so any assistant can discover and read them.
* resources -- `skill://pixelart/index` and `skill://pixelart/{name}` for
               clients that let a user attach context explicitly.
* prompts   -- `pixel_art_task`, plus `pixel_art_character` and
               `pixel_art_object`, ready-made briefs that fill the six slots
               `pixel-art-prompting` says a request must pin down.
"""
from ..core.skills import get_skill, load_skills, skill_index
from .. import mcp

# Prompt arguments arrive as strings whatever the client sends, so booleans
# have to be recovered by hand.
_TRUTHY = ("yes", "true", "1", "y", "si", "sí")


def _is_yes(value: str) -> bool:
    return value.strip().lower() in _TRUTHY


@mcp.tool()
async def list_pixelart_skills() -> str:
    """List the pixel-art craft skills bundled with this server.

    Call this first, before drawing anything. Each skill is a compact set of
    rules -- proportions, palette construction, shading, cycle timing, tiling --
    that turns raw drawing tools into art that reads correctly at game scale.
    Read one with get_pixelart_skill(name).
    """
    return skill_index()


@mcp.tool()
async def get_pixelart_skill(name: str) -> str:
    """Read one pixel-art skill document in full.

    Args:
        name: Skill name from list_pixelart_skills, e.g. "pixel-art-pipeline".
            The bare topic ("color", "shading", "playbook") also resolves.
    """
    skill = get_skill(name)
    if skill is None:
        available = ", ".join(s.name for s in load_skills().values())
        return f"Unknown skill '{name}'. Available: {available}"
    return skill.render()


@mcp.resource("skill://pixelart/index", mime_type="text/markdown")
def pixelart_skill_index() -> str:
    """Index of the pixel-art skills bundled with this server."""
    return skill_index()


@mcp.resource("skill://pixelart/{name}", mime_type="text/markdown")
def pixelart_skill(name: str) -> str:
    """One pixel-art skill document, by name."""
    skill = get_skill(name)
    return skill.render() if skill else f"Unknown skill '{name}'."


@mcp.prompt()
def pixel_art_task(subject: str, size: str = "32x32", animated: str = "no") -> str:
    """Seed a pixel-art job with the craft rules already loaded.

    Args:
        subject: What to draw, e.g. "a hooded ranger with a shortbow".
        size: Canvas size in pixels, e.g. "32x32".
        animated: "yes" to include the animation skills in the brief.
    """
    wanted = ["pixel-art-pipeline", "aseprite-mcp-playbook", "pixel-art-prompting"]
    if _is_yes(animated):
        wanted.append("pixel-art-animation")
    return (
        f"Draw {subject} as a {size} pixel-art sprite with this Aseprite MCP server.\n\n"
        f"First read these skills with get_pixelart_skill: {', '.join(wanted)}. "
        "This brief is deliberately thin: use `pixel-art-prompting` to fill the "
        "decisions it leaves open, and state what you settled on before drawing. "
        "Follow the pipeline in order and do not skip its verification gates -- "
        "export at 8x and look at the result before you call the sprite done."
    )


@mcp.prompt()
def pixel_art_character(
    subject: str,
    size: str = "32x32",
    view: str = "side",
    heads: str = "3",
    silhouette_hook: str = "",
    materials: str = "",
    palette: str = "12 colors, one accent",
    animated: str = "no",
) -> str:
    """Brief a character sprite with every Phase 0 decision already pinned down.

    Fills the six slots from `pixel-art-prompting` so the model never has to
    invent a canvas size or a palette mid-draw.

    Args:
        subject: Role, age and temperament, e.g. "a young knight, earnest".
        size: Canvas size in pixels, e.g. "32x32", "48x48".
        view: "side", "top-down 3-4", "front".
        heads: Proportion in heads: "2" chibi, "3" default, "4-5" heroic.
        silhouette_hook: The one oversized element that names the character
            at 1x, e.g. "a kite shield covering half the body". Left blank,
            the model must choose one and say so.
        materials: Materials, dominant first, e.g. "steel plate, leather, wool".
        palette: Palette budget and accent, e.g. "16 colors, cold steel, one
            gold accent on the crest".
        animated: "yes" to also brief the animation states.
    """
    hook = silhouette_hook or (
        "choose one and state it before drawing -- the sprite has no silhouette "
        "hook yet, and that is the decision that most often sinks a character"
    )
    lines = [
        f"Draw {subject} as a {size} pixel-art character sprite with this "
        "Aseprite MCP server.",
        "",
        f"- View: {view}, light from the top-left.",
        f"- Proportions: {heads} heads.",
        f"- Silhouette hook: {hook}.",
    ]
    if materials:
        lines.append(f"- Materials: {materials}.")
    lines.append(f"- Palette: {palette}.")

    wanted = [
        "pixel-art-pipeline",
        "pixel-art-character-design",
        "pixel-art-color",
        "pixel-art-shading",
        "aseprite-mcp-playbook",
    ]
    if _is_yes(animated):
        lines.append(
            "- Deliver: the base pose first, then the animation states; split "
            "the layer rig accordingly before drawing anything."
        )
        wanted.append("pixel-art-animation")
    else:
        lines.append(
            "- Deliver: a static sprite on a transparent background, with the "
            "layer rig already split so it can be animated later."
        )

    return "\n".join(lines) + (
        "\n\nFirst read these skills with get_pixelart_skill: "
        f"{', '.join(wanted)}. Follow the pipeline in order and do not skip its "
        "verification gates -- the silhouette must be readable at 1x before any "
        "detail, and you must export at 8x and look at the PNG before you call "
        "the sprite done."
    )


@mcp.prompt()
def pixel_art_object(
    subject: str,
    size: str = "16x16",
    kind: str = "inventory icon",
    view: str = "flat front",
    silhouette_hook: str = "",
    materials: str = "",
    palette: str = "10 colors, one accent",
    matches: str = "",
) -> str:
    """Brief a prop, item or icon with every Phase 0 decision pinned down.

    The object counterpart of `pixel_art_character`. Use `matches` when the
    asset joins an existing set -- that is what keeps a set from becoming a
    pile of unrelated sprites.

    Args:
        subject: What it is and what it does in game, e.g. "a health potion".
        size: Canvas size in pixels, e.g. "16x16", "32x24".
        kind: "inventory icon", "prop", "tile", "UI element".
        view: "flat front", "top-down 3-4", "isometric 2:1".
        silhouette_hook: The shape that names it at 1x, e.g. "a round-bellied
            flask with a short cork neck".
        materials: Materials; flag metal or glass so they get the long,
            high-contrast ramp that makes them read as such.
        palette: Palette budget and accent.
        matches: An existing asset this must match, e.g. "sword.aseprite".
            Its palette is then reused exactly rather than reinvented.
    """
    hook = silhouette_hook or (
        "choose one and state it before drawing -- at this size the object is "
        "its silhouette, and a shape that is not nameable at 1x is a failure"
    )
    lines = [
        f"Draw {subject} as a {size} pixel-art {kind} with this Aseprite MCP "
        "server.",
        "",
        f"- View: {view}, light from the top-left.",
        f"- Silhouette hook: {hook}.",
    ]
    if materials:
        lines.append(
            f"- Materials: {materials}. Any metal or glass needs a long "
            "high-contrast ramp with a hard specular -- that contrast, not the "
            "hue, is what separates steel from plastic."
        )
    lines.append(f"- Palette: {palette}.")
    lines.append("- Deliver: transparent background, selective outline.")

    wanted = [
        "pixel-art-pipeline",
        "pixel-art-fundamentals",
        "pixel-art-color",
        "pixel-art-shading",
        "aseprite-mcp-playbook",
    ]
    if matches:
        lines.append(
            f"- Set: this must sit beside {matches}. Read that file's palette "
            "with get_color_stats first and reuse it exactly -- same ramps, "
            "same outline style, same light angle, same visual weight in the "
            "frame. Do not invent new colors."
        )
        wanted.append("pixel-art-environments")

    return "\n".join(lines) + (
        "\n\nFirst read these skills with get_pixelart_skill: "
        f"{', '.join(wanted)}. Follow the pipeline in order. The asset must be "
        "identifiable at 1x next to other icons -- export at 1x and at 8x and "
        "look at both before you call it done."
    )
