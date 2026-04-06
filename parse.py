"""
parse.py — Crawls your solutions folder and parses YAML frontmatter from .typ files.

Expected frontmatter format at the top of each .typ file:
    // ---
    // title: Longest Increasing Subsequence
    // source: Codeforces 1234A
    // difficulty: 1800
    // tags: dp, binary-search
    // keywords: patience sorting, LIS, nlogn
    // ---

All fields are optional but recommended.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Optional


FRONTMATTER_RE = re.compile(
    r"^(?:// ---\s*\n)((?:// .*\n)*?)(?:// ---)",
    re.MULTILINE,
)


def parse_frontmatter(typ_path: Path) -> dict:
    """Parse YAML frontmatter from a .typ file. Returns a dict (empty if none found)."""
    try:
        text = typ_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}

    match = FRONTMATTER_RE.search(text)
    if not match:
        return {}

    # Strip the leading "// " from each line
    raw_yaml = "\n".join(
        line[3:] if line.startswith("// ") else line
        for line in match.group(1).splitlines()
    )

    try:
        data = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError:
        return {}

    return data


def normalise(data: dict, typ_path: Path) -> dict:
    """Normalise and enrich a parsed metadata dict."""

    def to_list(val) -> list[str]:
        if val is None:
            return []
        if isinstance(val, list):
            return [str(v).strip().lower() for v in val]
        return [s.strip().lower() for s in str(val).split(",") if s.strip()]

    folder = typ_path.parent
    pdf_candidates = list(folder.glob("*.pdf"))
    pdf_path = str(pdf_candidates[0]) if pdf_candidates else None

    difficulty = data.get("difficulty")
    if difficulty is not None:
        try:
            difficulty = int(difficulty)
        except (ValueError, TypeError):
            difficulty = None

    return {
        "title":      str(data.get("title", typ_path.parent.name)),
        "source":     str(data.get("source", "")).strip(),
        "difficulty": difficulty,
        "tags":       to_list(data.get("tags")),
        "keywords":   to_list(data.get("keywords")),
        "typ_path":   str(typ_path),
        "pdf_path":   pdf_path,
        "folder":     str(folder),
    }


def build_index(root: str | Path) -> list[dict]:
    """
    Walk *root* recursively, find all .typ files, parse their frontmatter,
    and return a list of normalised problem dicts.
    """
    root = Path(root).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Root directory not found: {root}")

    problems = []
    for typ_file in sorted(root.rglob("*.typ")):
        raw = parse_frontmatter(typ_file)
        problem = normalise(raw, typ_file)
        problems.append(problem)

    return problems
