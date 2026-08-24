"""Loader for the bundled pixel-art skill documents.

The skills live as plain Markdown in ``aseprite_mcp/skills/``. They are the
single source of truth: the MCP tools in ``tools/skills.py``, the MCP
resources, the server instructions, and the ``.claude/skills`` wrappers all
read these same files.

Each document opens with a small frontmatter block::

    ---
    name: pixel-art-color
    title: Color and Palettes
    description: one line, shown in the index
    when_to_use: one line, tells the model when to open it
    tools: generate_color_ramp, set_palette, quantize_to_palette
    see_also: pixel-art-shading, pixel-art-fundamentals
    ---

Frontmatter is parsed by hand rather than with PyYAML so the server keeps
its three-dependency footprint (httpx, mcp, pillow).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

# Keys whose value is a comma-separated list rather than a plain string.
_LIST_KEYS = ("tools", "see_also")


@dataclass(frozen=True)
class Skill:
    """One skill document: its metadata plus the Markdown body."""

    name: str
    title: str
    description: str
    when_to_use: str
    tools: tuple[str, ...]
    see_also: tuple[str, ...]
    body: str
    filename: str

    def render(self) -> str:
        """The full document as handed to a model, header restored."""
        header = [f"# {self.title}", "", self.description]
        if self.when_to_use:
            header += ["", f"**When to use:** {self.when_to_use}"]
        if self.see_also:
            header += ["", f"**See also:** {', '.join(self.see_also)}"]
        return "\n".join(header) + "\n\n---\n\n" + self.body.strip() + "\n"


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split a document into its frontmatter mapping and its body.

    A document without a leading ``---`` fence yields an empty mapping and
    the untouched text, so a skill file is still readable if the header is
    ever dropped.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    meta: dict[str, str] = {}
    key: str | None = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, "\n".join(lines[i + 1:])
        if line.startswith((" ", "\t")) and key:
            # Continuation of the previous value, folded onto one line.
            meta[key] = f"{meta[key]} {line.strip()}".strip()
            continue
        head, sep, value = line.partition(":")
        if not sep:
            continue
        key = head.strip()
        meta[key] = value.strip()
    # Unterminated fence: treat the whole file as body.
    return {}, text


def _slug(name: str) -> str:
    """Normalize a skill name so lookups tolerate spacing and separators."""
    return "".join(c if c.isalnum() else "-" for c in name.strip().lower()).strip("-")


def _load() -> dict[str, Skill]:
    skills: dict[str, Skill] = {}
    if not SKILLS_DIR.is_dir():
        return skills
    for path in sorted(SKILLS_DIR.glob("*.md")):
        meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
        name = meta.get("name") or path.stem
        lists = {
            k: tuple(p.strip() for p in meta.get(k, "").split(",") if p.strip())
            for k in _LIST_KEYS
        }
        skills[_slug(name)] = Skill(
            name=name,
            title=meta.get("title", name),
            description=meta.get("description", ""),
            when_to_use=meta.get("when_to_use", ""),
            body=body,
            filename=path.name,
            **lists,
        )
    return skills


_CACHE: dict[str, Skill] | None = None


def load_skills(refresh: bool = False) -> dict[str, Skill]:
    """All skills keyed by slug. Parsed once, then cached."""
    global _CACHE
    if _CACHE is None or refresh:
        _CACHE = _load()
    return _CACHE


def get_skill(name: str) -> Skill | None:
    """Look up one skill, tolerating case, spaces and a `.md` suffix."""
    skills = load_skills()
    key = _slug(name.removesuffix(".md"))
    if key in skills:
        return skills[key]
    # Accept a bare topic ("color") for a prefixed name ("pixel-art-color").
    matches = [s for k, s in skills.items() if k.endswith(f"-{key}") or k.startswith(f"{key}-")]
    return matches[0] if len(matches) == 1 else None


def skill_index() -> str:
    """A compact Markdown table of every skill, for listing tools."""
    skills = load_skills()
    if not skills:
        return "No skill documents are installed."
    lines = [
        "# Pixel Art Skills",
        "",
        "Read a skill with `get_pixelart_skill(name)` before doing the matching work.",
        "",
        "| Skill | Use it when |",
        "|-------|-------------|",
    ]
    for skill in skills.values():
        lines.append(f"| `{skill.name}` | {skill.when_to_use or skill.description} |")
    return "\n".join(lines)


SERVER_INSTRUCTIONS = """\
This server drives Aseprite to produce pixel art and animated sprites for games.

Pixel art has hard craft rules — cluster control, anti-aliasing placement, hue
shifting, silhouette readability, cycle timing — and ignoring them is what makes
generated sprites read as "AI slop" rather than as game art. The rules ship with
this server as skill documents.

Before you draw anything, call `list_pixelart_skills()` and then
`get_pixelart_skill(name)` for the ones that match the task. Start with
`pixel-art-pipeline`: it is the master workflow and tells you which other skills
to open and in what order. `aseprite-mcp-playbook` maps each technique onto the
exact tool call that performs it, and lists the coordinate and cel gotchas that
cause silent mistakes.

You cannot see the sprite you are drawing. Do not skip the visual feedback loop:
export with `export_frame(scale=8)` and actually look at the PNG, check the
palette with `get_color_stats`, and verify motion with `render_onion_skin` and
`compare_frames`.
"""
