#!/usr/bin/env python3
"""
index.py — Interactive CLI hub for your competitive programming solutions.

Usage:
    python index.py [/path/to/solutions]   # defaults to ./solutions

Search syntax (all combinable, space-separated):
    free text          — matches title, source, tags, keywords
    tags:dp            — must include this tag
    tags:dp,graph      — must include ALL listed tags
    source:codeforces  — source contains this string (case-insensitive)
    diff:1800          — exact difficulty match
    diff:>1700         — difficulty greater than
    diff:<2000         — difficulty less than
    diff:1600-1900     — difficulty in range

Commands at the prompt:
    open <n>           — open the nth result's PDF
    typ <n>            — open the nth result's .typ file
    list               — show all problems (no filter)
    help               — show this help
    quit / exit / q    — exit

Example:
    > tags:dp diff:>1700 source:codeforces segment
    > open 2
"""

import os
import sys
import re
import subprocess
import platform
from pathlib import Path

try:
    import readline  # noqa: F401 — enables arrow-key history on Linux/Mac
except ImportError:
    pass

try:
    from parse import build_index
except ImportError:
    print("Error: parse.py not found. Make sure it's in the same directory.")
    sys.exit(1)


# ── Colours ────────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
GREEN  = "\033[32m"
RED    = "\033[31m"
BLUE   = "\033[34m"
MAGENTA= "\033[35m"
WHITE  = "\033[37m"

BCYAN   = "\033[96m"
BYELLOW = "\033[93m"
BGREEN  = "\033[92m"
BRED    = "\033[91m"
BBLUE   = "\033[94m"
BMAGENTA= "\033[95m"
BWHITE  = "\033[97m"


def c(color, text):
    return f"{color}{text}{RESET}"


# ── Difficulty colouring ───────────────────────────────────────────────────────

def diff_color(d):
    if d is None or d < 1200:
        return WHITE
    if d < 1400:
        return BGREEN
    if d < 1600:
        return BCYAN
    if d < 1900:
        return BBLUE
    if d < 2100:
        return BMAGENTA
    if d < 2400:
        return BYELLOW
    return BRED


# ── Filtering logic ────────────────────────────────────────────────────────────

FILTER_PATTERNS = {
    "tags":    re.compile(r"\btags:([\w,+-]+)", re.I),
    "source":  re.compile(r"\bsource:([\w-]+)", re.I),
    "diff_eq": re.compile(r"\bdiff:(\d+)$"),
    "diff_gt": re.compile(r"\bdiff:>(\d+)"),
    "diff_lt": re.compile(r"\bdiff:<(\d+)"),
    "diff_rng":re.compile(r"\bdiff:(\d+)-(\d+)"),
}


def parse_query(query: str):
    """Extract structured filters and remaining free-text from a query string."""
    filters = {}
    remaining = query

    m = FILTER_PATTERNS["tags"].search(remaining)
    if m:
        filters["tags"] = [t.strip().lower() for t in m.group(1).split(",")]
        remaining = remaining[:m.start()] + remaining[m.end():]

    m = FILTER_PATTERNS["source"].search(remaining)
    if m:
        filters["source"] = m.group(1).lower()
        remaining = remaining[:m.start()] + remaining[m.end():]

    m = FILTER_PATTERNS["diff_rng"].search(remaining)
    if m:
        filters["diff"] = ("range", int(m.group(1)), int(m.group(2)))
        remaining = remaining[:m.start()] + remaining[m.end():]
    else:
        m = FILTER_PATTERNS["diff_gt"].search(remaining)
        if m:
            filters["diff"] = ("gt", int(m.group(1)))
            remaining = remaining[:m.start()] + remaining[m.end():]
        else:
            m = FILTER_PATTERNS["diff_lt"].search(remaining)
            if m:
                filters["diff"] = ("lt", int(m.group(1)))
                remaining = remaining[:m.start()] + remaining[m.end():]
            else:
                m = FILTER_PATTERNS["diff_eq"].search(remaining)
                if m:
                    filters["diff"] = ("eq", int(m.group(1)))
                    remaining = remaining[:m.start()] + remaining[m.end():]

    keywords = [w.lower() for w in remaining.split() if w.strip()]
    return filters, keywords


def matches(problem: dict, filters: dict, keywords: list[str]) -> bool:
    # Tag filter (ALL required tags must be present)
    if "tags" in filters:
        for t in filters["tags"]:
            if t not in problem["tags"]:
                return False

    # Source filter
    if "source" in filters:
        if filters["source"] not in problem["source"].lower():
            return False

    # Difficulty filter
    if "diff" in filters:
        d = problem["difficulty"]
        rule = filters["diff"]
        if d is None:
            return False
        if rule[0] == "eq"    and d != rule[1]:              return False
        if rule[0] == "gt"    and not (d > rule[1]):         return False
        if rule[0] == "lt"    and not (d < rule[1]):         return False
        if rule[0] == "range" and not (rule[1] <= d <= rule[2]): return False

    # Free-text keywords — match against title, source, tags, keywords
    if keywords:
        haystack = " ".join([
            problem["title"],
            problem["source"],
            " ".join(problem["tags"]),
            " ".join(problem["keywords"]),
        ]).lower()
        for kw in keywords:
            if kw not in haystack:
                return False

    return True


def search(problems: list[dict], query: str) -> list[dict]:
    if not query.strip():
        return problems
    filters, keywords = parse_query(query)
    return [p for p in problems if matches(p, filters, keywords)]


# ── Display ────────────────────────────────────────────────────────────────────

def fmt_tags(tags):
    if not tags:
        return "no tags"
    return " ".join(f"#{t}" for t in tags)


def print_results(results: list[dict]):
    if not results:
        print(c(RED, "  No results found."))
        return
    print()
    for i, p in enumerate(results, 1):
        has_pdf = "📄" if p["pdf_path"] else c(DIM, "  ")
        color   = diff_color(p["difficulty"])
        title   = c(BOLD, c(color, p["title"]))
        source  = c(color, p["source"]) if p["source"] else c(DIM, "unknown source")
        diff    = c(color, p["difficulty"])
        tags    = c(DIM, c(color, fmt_tags(p["tags"])))
        print(f"  {c(YELLOW, f'[{i}]')} {has_pdf} {title}")
        print(f"       {source}  ·  {diff}  ·  {tags}")
        # if p["keywords"]:
        #     kws = c(DIM, ", ".join(p["keywords"]))
        #     print(f"       {kws}")
        print()


def print_help():
    print(f"""
{c(BOLD, "Search syntax")} (space-separated, all combinable):
  {c(CYAN, "free text")}         matches title, source, tags, keywords
  {c(CYAN, "tags:dp")}           must include tag 'dp'
  {c(CYAN, "tags:dp,graph")}     must include ALL listed tags
  {c(CYAN, "source:codeforces")} source contains string (case-insensitive)
  {c(CYAN, "diff:1800")}         exact difficulty
  {c(CYAN, "diff:>1700")}        difficulty greater than
  {c(CYAN, "diff:<2000")}        difficulty less than
  {c(CYAN, "diff:1600-1900")}    difficulty in range

{c(BOLD, "Commands")}:
  {c(CYAN, "open <n>")}          open nth result's PDF
  {c(CYAN, "typ <n>")}           open nth result's .typ file
  {c(CYAN, "list")}              show all problems
  {c(CYAN, "help")}              show this help
  {c(CYAN, "quit")} / {c(CYAN, "q")}          exit
""")


# ── File opener ────────────────────────────────────────────────────────────────

def open_file(path: str):
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", path])
        elif system == "Linux":
            subprocess.Popen(["xdg-open", path])
        else:
            os.startfile(path)
        print(c(GREEN, f"  Opened: {path}"))
    except Exception as e:
        print(c(RED, f"  Could not open file: {e}"))


# ── Main REPL ──────────────────────────────────────────────────────────────────

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "./content"

    print(c(BOLD, "\n📚 CP Solutions Hub"))
    print(c(DIM,  f"   Indexing {root} …"))

    try:
        problems = build_index(root)
    except FileNotFoundError as e:
        print(c(RED, f"\n  Error: {e}"))
        print(c(DIM,  f"  Usage: python index.py /path/to/solutions\n"))
        sys.exit(1)

    print(c(GREEN, f"   Found {len(problems)} problem(s). Type 'help' for usage.\n"))

    last_results: list[dict] = []

    while True:
        try:
            raw = input(c(CYAN, "> ")).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue

        # Commands
        lower = raw.lower()

        if lower in ("quit", "exit", "q"):
            break

        if lower == "help":
            print_help()
            continue

        if lower == "list":
            last_results = problems
            print_results(last_results)
            print(c(DIM, f"  {len(last_results)} problem(s) total."))
            continue

        if lower.startswith("open ") or lower.startswith("typ "):
            parts = raw.split()
            cmd   = parts[0].lower()
            if len(parts) < 2 or not parts[1].isdigit():
                print(c(RED, "  Usage: open <n>  or  typ <n>"))
                continue
            idx = int(parts[1]) - 1
            if not last_results:
                print(c(RED, "  No results yet — run a search first."))
                continue
            if idx < 0 or idx >= len(last_results):
                print(c(RED, f"  Index out of range (1–{len(last_results)})."))
                continue
            p = last_results[idx]
            if cmd == "open":
                if p["pdf_path"]:
                    open_file(p["pdf_path"])
                else:
                    print(c(RED, "  No PDF found for this problem."))
            else:
                open_file(p["typ_path"])
            continue

        # Search
        last_results = search(problems, raw)
        print_results(last_results)
        if last_results:
            print(c(DIM, f"  {len(last_results)} result(s) · open <n> to open PDF · typ <n> for source"))


if __name__ == "__main__":
    main()
