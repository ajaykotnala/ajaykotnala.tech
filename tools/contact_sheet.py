#!/usr/bin/env python3
"""
Build a contact sheet of every extracted figure: assets/diagrams/index.html

Two jobs:
  1. Confirm each SVG still renders standalone -- arrowheads, filters and
     textures intact -- after being split out of its source article.
  2. Support the print audit. Pass --grayscale to preview how the figures
     will look in a black-and-white KDP interior, which is where colour-only
     encoding (red line vs green line, no other difference) falls apart.

Usage:
    python3 tools/contact_sheet.py
    python3 tools/contact_sheet.py --grayscale
    python3 tools/contact_sheet.py --width 4.5in   # print column width
"""

from __future__ import annotations

import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIAGRAMS = ROOT / "assets" / "diagrams"

PAGE = """<!doctype html>
<meta charset="utf-8">
<title>Figure contact sheet — {n} diagrams</title>
<style>
  body {{ font: 14px/1.5 -apple-system, system-ui, sans-serif;
         background: #fff; color: #111; margin: 24px; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; }}
  .sub {{ color: #666; margin-bottom: 22px; }}
  .grid {{ display: grid; gap: 20px; }}
  figure {{ margin: 0; border: 1px solid #e3e3e3; border-radius: 10px;
            padding: 14px; background: #fff; overflow: hidden; }}
  figcaption {{ font-weight: 600; font-size: 13px; margin-bottom: 10px;
                display: flex; justify-content: space-between; gap: 12px; }}
  figcaption .warn {{ color: #b00; font-weight: 500; }}
  .box {{ {width_rule} overflow-x: auto; }}
  svg {{ max-width: 100%; height: auto; display: block; }}
  {filter_rule}
</style>
<h1>Figure contact sheet</h1>
<div class="sub">{n} figures{mode}. Any blank panel, missing arrowhead or
lost texture means a definition failed to travel with its figure.</div>
<div class="grid">
{body}
</div>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grayscale", action="store_true",
                    help="preview as a black-and-white print interior")
    ap.add_argument("--width", default="",
                    help="constrain figures to a print column width, e.g. 4.5in")
    args = ap.parse_args()

    files = sorted(DIAGRAMS.glob("*.svg"))
    if not files:
        raise SystemExit("no diagrams found — run tools/extract.py first")

    blocks = []
    for f in files:
        svg = f.read_text(encoding="utf-8")
        ids = set(re.findall(r'id="([^"]+)"', svg))
        refs = set(re.findall(r"url\(#([^)]+)\)", svg))
        refs |= set(re.findall(r'(?:xlink:)?href="#([^"]+)"', svg))
        missing = sorted(refs - ids)
        warn = (f'<span class="warn">dangling: {", ".join(missing)}</span>'
                if missing else "")
        blocks.append(
            f'<figure><figcaption><span>{f.stem}</span>{warn}</figcaption>'
            f'<div class="box">{svg}</div></figure>'
        )

    out = PAGE.format(
        n=len(files),
        body="\n".join(blocks),
        mode=" — grayscale print preview" if args.grayscale else "",
        filter_rule=".box { filter: grayscale(1) contrast(1.08); }" if args.grayscale else "",
        width_rule=f"max-width: {args.width};" if args.width else "",
    )
    target = DIAGRAMS / "index.html"
    target.write_text(out, encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)} ({len(files)} figures)")


if __name__ == "__main__":
    main()
