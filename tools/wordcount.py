#!/usr/bin/env python3
"""
Report actual vs target words per chapter, so the remaining gap stays visible.

Reads content/book.yml for structure and targets, recounts the actual prose in
each content/<slug>.md (excluding frontmatter, code fences and figure lines,
which are not prose and would inflate the count), and prints a per-part
breakdown plus what is left to write.

Usage:
    python3 tools/wordcount.py
    python3 tools/wordcount.py --todo     # list outstanding per-chapter work
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

try:
    import yaml
except ImportError:
    sys.exit("needs pyyaml:  pip3 install pyyaml")


def prose_words(md: str) -> int:
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)   # frontmatter
    md = re.sub(r"```.*?```", " ", md, flags=re.S)          # code fences
    md = re.sub(r"^!\[.*$", " ", md, flags=re.M)            # figure lines
    md = re.sub(r"^\s*\|.*$", " ", md, flags=re.M)          # tables
    md = re.sub(r"[#>*`_\[\]()]", " ", md)
    return len(md.split())


def bar(frac: float, width: int = 22) -> str:
    frac = max(0.0, min(1.0, frac))
    fill = round(frac * width)
    return "#" * fill + "." * (width - fill)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--todo", action="store_true", help="list outstanding work")
    args = ap.parse_args()

    book = yaml.safe_load((CONTENT / "book.yml").read_text())
    gt = ga = 0
    todos = []

    for part in book["parts"]:
        pa = pt = 0
        print(f'\n{part["title"].upper()}   target {part.get("target_words", 0):,}')
        print("-" * 86)
        for ch in part["chapters"]:
            path = CONTENT / f'{ch["slug"]}.md'
            actual = prose_words(path.read_text()) if path.exists() else 0
            target = ch.get("target_words", 0)
            pa += actual
            pt += target
            frac = actual / target if target else 0
            state = ch.get("status", "?")
            print(f'  {ch["slug"]:<26}{actual:>7,}{target:>8,}  {bar(frac)} '
                  f'{frac*100:>4.0f}%  {state}')
            for t in ch.get("todo", []) or []:
                todos.append((ch["slug"], t))
        print(f'  {"":<26}{pa:>7,}{pt:>8,}   part total')
        ga += pa
        gt += pt

    print("\n" + "=" * 86)
    print(f'  TOTAL{"":<21}{ga:>7,}{gt:>8,}  {bar(ga/gt if gt else 0)} '
          f'{(ga/gt*100 if gt else 0):>4.0f}%')
    print(f"  remaining to write: {max(0, gt - ga):,} words")

    if args.todo:
        print("\nOUTSTANDING WORK")
        print("-" * 86)
        for slug, t in todos:
            print(f"  {slug:<26} {t}")
        for t in book.get("global_todo", []) or []:
            print(f'  {"(global)":<26} {t}')


if __name__ == "__main__":
    main()
