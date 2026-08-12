#!/usr/bin/env python3
"""
Generate figures for newly written chapters in the existing hand-drawn style.

Matches the visual language of the extracted diagrams: dot-grid background,
turbulence 'roughen' filter, Segoe Print lettering, and the established
palette. Every defs id is namespaced per figure, the same convention
tools/extract.py enforces, so figures stay standalone-safe.

Usage:
    python3 tools/make_figures.py
"""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIAGRAMS = ROOT / "assets" / "diagrams"

HAND = "'Segoe Print', 'Comic Neue', cursive"
MONO = "'Fira Code', monospace"

BLUE, GREEN, RED, GREY, AMBER = "#0066cc", "#0ba360", "#c62828", "#86868b", "#d97706"
INK, PAPER, PANEL = "#3d3728", "#fefefe", "#f5f5f7"


def defs(fid: str) -> str:
    return f"""<defs>
<pattern id="{fid}-dotGrid" width="20" height="20" patternUnits="userSpaceOnUse">
<circle cx="10" cy="10" r="0.8" fill="#d0d0d0"/></pattern>
<filter id="{fid}-roughen" x="-2%" y="-2%" width="104%" height="104%">
<feTurbulence type="turbulence" baseFrequency="0.03" numOctaves="3" seed="7" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="1.5" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<marker id="{fid}-arw" viewBox="0 0 12 12" refX="10" refY="6"
 markerWidth="10" markerHeight="10" orient="auto">
<path d="M 1 1 L 10 6 L 1 11" fill="none" stroke="#333"
 stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>
<marker id="{fid}-arwRed" viewBox="0 0 12 12" refX="10" refY="6"
 markerWidth="10" markerHeight="10" orient="auto">
<path d="M 1 1 L 10 6 L 1 11" fill="none" stroke="{RED}"
 stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>
</defs>"""


def frame(fid: str, w: int, h: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'style="max-width: {w}px">\n{defs(fid)}\n'
        f'<rect width="{w}" height="{h}" rx="12" fill="{PAPER}"/>\n'
        f'<rect width="{w}" height="{h}" rx="12" fill="url(#{fid}-dotGrid)"/>\n'
        f"{body}\n</svg>\n"
    )


def t(x, y, s, size=13, fill=INK, anchor="middle", weight="400", font=HAND, style=""):
    st = f' font-style="{style}"' if style else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{st}>{s}</text>')


def box(fid, x, y, w, h, fill=PANEL, stroke=GREY, sw=1.6, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" filter="url(#{fid}-roughen)"/>')


def arrow(fid, x1, y1, x2, y2, colour="#333", dash="", marker="arw"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {x1} {y1} L {x2} {y2}" fill="none" stroke="{colour}" '
            f'stroke-width="1.6"{d} marker-end="url(#{fid}-{marker})"/>')


# --------------------------------------------------------------- fig 1: engines
def fig_engines(fid):
    b = [t(390, 28, "TWO WAYS TO PUT A ROW ON DISK", 14, INK, weight="700")]
    b += [box(fid, 40, 50, 330, 250, "#eef6ff", BLUE),
          t(205, 74, "B-TREE — update in place", 13, BLUE, weight="700")]
    for i, (lbl, y) in enumerate([("find page", 108), ("read page", 143),
                                  ("modify", 178), ("write page back", 213)]):
        b += [box(fid, 90, y, 230, 26, PAPER, BLUE, 1.2, 6),
              t(205, y + 18, lbl, 12, INK)]
        if i < 3:
            b += [arrow(fid, 205, y + 26, 205, y + 33, BLUE)]
    b += [t(205, 268, "random I/O · one location per key", 11, GREY, style="italic"),
          t(205, 286, "reads: predictable", 11, BLUE, weight="700")]

    b += [box(fid, 410, 50, 330, 250, "#e8f5e9", GREEN),
          t(575, 74, "LSM TREE — append only", 13, "#2e7d32", weight="700")]
    for i, (lbl, y) in enumerate([("append to memtable", 108),
                                  ("flush sorted file", 143),
                                  ("compact in background", 178)]):
        b += [box(fid, 460, y, 230, 26, PAPER, GREEN, 1.2, 6),
              t(575, y + 18, lbl, 12, INK)]
        if i < 2:
            b += [arrow(fid, 575, y + 26, 575, y + 33, GREEN)]
    b += [box(fid, 460, 213, 230, 26, "#fff8e1", AMBER, 1.2, 6),
          t(575, 231, "key may live in several files", 11, INK),
          t(575, 268, "sequential I/O · superseded values linger", 11, GREY, style="italic"),
          t(575, 286, "writes: fast   reads: variable", 11, "#2e7d32", weight="700")]
    return frame(fid, 780, 320, "\n".join(b))


# ------------------------------------------------------- fig 2: replication lag
def fig_replication(fid):
    b = [t(390, 26, "READ-YOUR-WRITES — NOTHING FAILED", 14, INK, weight="700")]
    b += [box(fid, 40, 60, 150, 60, "#eef6ff", BLUE), t(115, 88, "user", 13, INK),
          t(115, 106, "saves profile", 11, GREY, style="italic")]
    b += [box(fid, 315, 60, 150, 60, PANEL, INK), t(390, 85, "LEADER", 13, INK, weight="700"),
          t(390, 105, 'name = "Ajay"', 11, "#2e7d32", font=MONO)]
    b += [box(fid, 590, 60, 150, 60, PANEL, GREY), t(665, 85, "FOLLOWER", 13, GREY, weight="700"),
          t(665, 105, 'name = "A."', 11, RED, font=MONO)]
    b += [arrow(fid, 190, 90, 310, 90, BLUE), t(250, 82, "1. write", 11, BLUE),
          arrow(fid, 465, 90, 585, 90, GREY, "5 4"), t(525, 82, "2. replicate", 11, GREY),
          t(525, 118, "~ms … occasionally seconds", 10, AMBER, style="italic")]
    b += [arrow(fid, 660, 130, 200, 190, RED, "", "arwRed"),
          box(fid, 40, 170, 150, 60, "#ffebee", RED), t(115, 196, "user", 13, INK),
          t(115, 214, "reads old name", 11, RED, style="italic"),
          t(430, 172, "3. read routed to follower", 11, RED)]
    b += [box(fid, 250, 258, 420, 46, "#fff8e1", AMBER, 1.4),
          t(460, 278, "Every component did exactly what it was designed to do.", 12, INK),
          t(460, 295, "The bug is the routing decision, not the database.", 11, GREY, style="italic")]
    return frame(fid, 780, 320, "\n".join(b))


# ---------------------------------------------------------- fig 3: lost update
def fig_lost_update(fid):
    b = [t(390, 26, "THE LOST UPDATE — BOTH TRANSACTIONS WERE CORRECT", 14, INK, weight="700")]
    b += [t(150, 56, "TXN A", 13, BLUE, weight="700"),
          t(630, 56, "TXN B", 13, "#00796b", weight="700"),
          t(390, 56, "seats_left", 12, GREY, weight="700")]
    b += [f'<path d="M 390 66 L 390 268" stroke="{GREY}" stroke-width="1.4" stroke-dasharray="4 4"/>']
    steps = [(96, "read → 1", "read → 1", "1", BLUE, "#00796b"),
             (142, "compute 1-1=0", "compute 1-1=0", "1", BLUE, "#00796b"),
             (188, "write 0  ✓", "", "0", BLUE, None),
             (234, "", "write 0  ✓", "0", None, "#00796b")]
    for y, la, lb, mid, ca, cb in steps:
        if la:
            b += [box(fid, 60, y - 16, 180, 28, "#eef6ff", ca, 1.2, 6), t(150, y + 3, la, 11, INK)]
            b += [arrow(fid, 244, y, 370, y, ca, "4 3")]
        if lb:
            b += [box(fid, 540, y - 16, 180, 28, "#e0f2f1", cb, 1.2, 6), t(630, y + 3, lb, 11, INK)]
            b += [arrow(fid, 536, y, 412, y, cb, "4 3")]
        b += [t(390, y + 4, mid, 12, INK, font=MONO, weight="700")]
    b += [box(fid, 210, 268, 360, 40, "#ffebee", RED, 1.4),
          t(390, 285, "Two seats sold. One decrement recorded.", 12, RED, weight="700"),
          t(390, 301, "Neither transaction did anything wrong on its own.", 10, INK, style="italic")]
    return frame(fid, 780, 330, "\n".join(b))


# --------------------------------------------------------- fig 4: partitioning
def fig_partitioning(fid):
    b = [t(390, 26, "PARTITION KEY DECIDES WHETHER SCALING WORKS", 14, INK, weight="700")]
    b += [box(fid, 40, 50, 330, 250, "#ffebee", RED),
          t(205, 74, "RANGE by timestamp", 13, RED, weight="700")]
    for i, (lbl, load, col) in enumerate([("node 1", 6, GREY), ("node 2", 10, GREY),
                                          ("node 3", 96, RED)]):
        x = 75 + i * 100
        h = max(8, load)
        b += [box(fid, x, 240 - h, 60, h, col if col == RED else "#e0e0e0", col, 1.2, 4),
              t(x + 30, 258, lbl, 11, GREY),
              t(x + 30, 232 - h, f"{load}%", 10, col, weight="700")]
    b += [t(205, 282, "all of today's writes land on one node", 11, RED, style="italic")]

    b += [box(fid, 410, 50, 330, 250, "#e8f5e9", GREEN),
          t(575, 74, "HASH of user_id", 13, "#2e7d32", weight="700")]
    for i, lbl in enumerate(["node 1", "node 2", "node 3"]):
        x = 445 + i * 100
        b += [box(fid, x, 202, 60, 38, "#c8e6c9", GREEN, 1.2, 4),
              t(x + 30, 258, lbl, 11, GREY), t(x + 30, 194, "33%", 10, "#2e7d32", weight="700")]
    b += [t(575, 282, "even writes — but range scans now hit every node", 11, "#2e7d32",
            style="italic")]
    return frame(fid, 780, 320, "\n".join(b))


# ------------------------------------------------------------- fig 5: quorums
def fig_quorum(fid):
    b = [t(390, 26, "R + W > N — WHY THE SETS MUST OVERLAP", 14, INK, weight="700")]

    def cluster(cx, cy, title, wset, rset, verdict, ok):
        out = [t(cx, cy - 74, title, 13, INK, weight="700")]
        for i in range(3):
            x = cx - 92 + i * 92
            inW, inR = i in wset, i in rset
            if inW and inR:
                fill, stroke = "#fff8e1", AMBER
            elif inW:
                fill, stroke = "#eef6ff", BLUE
            elif inR:
                fill, stroke = "#e8f5e9", GREEN
            else:
                fill, stroke = PANEL, GREY
            out += [box(fid, x - 27, cy - 46, 54, 54, fill, stroke, 1.6, 27),
                    t(x, cy - 14, f"R{i+1}", 12, INK, weight="700")]
            tags = []
            if inW:
                tags.append(("W", BLUE))
            if inR:
                tags.append(("R", GREEN))
            for j, (lab, col) in enumerate(tags):
                out += [t(x - 10 + j * 20, cy + 26, lab, 12, col, weight="700")]
        col = GREEN if ok else RED
        out += [box(fid, cx - 138, cy + 40, 276, 34, "#e8f5e9" if ok else "#ffebee", col, 1.4),
                t(cx, cy + 62, verdict, 11, col if not ok else "#2e7d32", weight="700")]
        return out

    b += cluster(210, 118, "N=3  W=2  R=2", {0, 1}, {1, 2},
                 "2 + 2 > 3  →  R2 overlaps. Guaranteed.", True)
    b += cluster(570, 118, "N=3  W=1  R=1", {0}, {2},
                 "1 + 1 < 3  →  no overlap. Stale read is legal.", False)
    b += [t(390, 268, "The overlap is the entire guarantee — there is no consensus "
                      "protocol here,", 11, GREY, style="italic"),
          t(390, 285, "only a pigeonhole argument.", 11, GREY, style="italic")]
    return frame(fid, 780, 305, "\n".join(b))


FIGURES = {
    "p2-06-data-storage-fig01": fig_engines,
    "p2-06-data-storage-fig02": fig_replication,
    "p2-06-data-storage-fig03": fig_lost_update,
    "p2-06-data-storage-fig04": fig_partitioning,
    "p2-06-data-storage-fig05": fig_quorum,
}


def main():
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    for fid, fn in FIGURES.items():
        (DIAGRAMS / f"{fid}.svg").write_text(fn(fid), encoding="utf-8")
        print(f"wrote assets/diagrams/{fid}.svg")


if __name__ == "__main__":
    main()
