#!/usr/bin/env python3
"""Regenerate .claude/skills/ wrappers from aseprite_mcp/skills/*.md.

The Markdown documents under aseprite_mcp/skills/ are the single source of
truth. Claude Code discovers skills only from .claude/skills/<name>/SKILL.md,
so this script writes one thin wrapper per document that points back at the
original file. Content is never duplicated.

Run after adding or renaming a skill:

    python3 scripts/sync-claude-skills.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from aseprite_mcp.core.skills import load_skills  # noqa: E402

OUT = ROOT / ".claude" / "skills"

TEMPLATE = """---
name: {name}
description: {description}. Use when: {when_to_use}
---

# {title}

The full skill lives in `aseprite_mcp/skills/{filename}` — **read that file now**,
it is the authoritative version and this wrapper intentionally holds no content.

If you are talking to the `aseprite` MCP server rather than working inside this
repository, call `get_pixelart_skill("{name}")` instead.

Related skills: {see_also}
"""


def main() -> int:
    skills = load_skills()
    if not skills:
        print("No skills found — nothing to sync.", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    written = set()
    for skill in skills.values():
        target = OUT / skill.name
        target.mkdir(exist_ok=True)
        (target / "SKILL.md").write_text(
            TEMPLATE.format(
                name=skill.name,
                title=skill.title,
                description=skill.description.rstrip("."),
                when_to_use=skill.when_to_use[0].lower() + skill.when_to_use[1:],
                filename=skill.filename,
                see_also=", ".join(skill.see_also) or "none",
            ),
            encoding="utf-8",
        )
        written.add(skill.name)
        print(f"wrote {target.relative_to(ROOT)}/SKILL.md")

    # Drop wrappers whose source document no longer exists.
    for stale in OUT.iterdir():
        if stale.is_dir() and stale.name not in written:
            for f in stale.iterdir():
                f.unlink()
            stale.rmdir()
            print(f"removed stale wrapper {stale.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
