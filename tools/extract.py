#!/usr/bin/env python3
"""
One-time extractor: hand-authored article HTML -> Markdown + standalone SVG.

Reads the 10 book articles, emits:
  content/<slug>.md          frontmatter + Markdown body
  assets/diagrams/<slug>-figNN.svg   standalone figures

Two things this does that a generic html2text cannot:

1. Preserves the semantic blocks the articles are built from (callouts, deep
   dives, entity grids, level cards, API endpoints, stat rows) instead of
   flattening them to paragraphs.
2. Namespaces every SVG <defs> id per figure and rewrites the matching
   url(#...) references. Several articles reuse ids like `dotGrid` and
   `exArrow` across many inline SVGs -- harmless in one combined document,
   silently broken the moment each figure becomes its own file.

Anything it does not recognise is reported to stderr and wrapped in an
<!-- UNMAPPED --> comment rather than dropped, so the automation rate is
measurable and nothing is lost silently.

Usage:
    python3 tools/extract.py            # write files
    python3 tools/extract.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import Counter

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DIAGRAMS = ROOT / "assets" / "diagrams"

# part, source path, output slug
ARTICLES = [
    ("design-patterns", "DesignPatterns/creational-pattern.html",   "p1-01-creational"),
    ("design-patterns", "DesignPatterns/structural-pattern.html",   "p1-02-structural"),
    ("design-patterns", "DesignPatterns/behavioural-pattern.html",  "p1-03-behavioural"),
    ("deep-dives",      "DeepDives/concurrency-system-design.html", "p2-01-concurrency"),
    ("deep-dives",      "DeepDives/caching-system-design.html",     "p2-02-caching"),
    ("deep-dives",      "DeepDives/api-rate-limiting-system-design.html", "p2-03-rate-limiting"),
    ("deep-dives",      "DeepDives/kafka-system-design.html",       "p2-04-event-streaming"),
    ("system-designs",  "SystemDesign/tinder-system-design.html",   "p3-01-proximity-matching"),
    ("system-designs",  "SystemDesign/bookmyshow-system-design.html", "p3-02-ticketing"),
    ("system-designs",  "SystemDesign/bookmyride-system-design.html", "p3-03-ride-hailing"),
]

# Syntax-highlighting spans. The DesignPatterns articles use short names, the
# others use long ones; both are presentational and must collapse to plain text.
CODE_SPANS = {
    "kw", "fn", "cl", "cm", "st", "dc", "ty", "nm", "op", "pn",
    "keyword", "comment", "string", "number", "type", "function", "class",
}

# Chrome that never belongs in the manuscript.
CHROME_SELECTORS = [
    ".progress-bar", ".global-nav", ".sub-nav-frosted", ".toc-wrapper",
    ".toc", ".author-bar", ".article-footer", ".series-footer",
    ".series-link-card", ".series-trail", ".series-band", ".series-banner",
    "footer", "nav",
]

unknown = Counter()


# ---------------------------------------------------------------- inline text


def inline(node) -> str:
    """Render inline content to Markdown."""
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", str(node))
    if not isinstance(node, Tag):
        return ""

    name = node.name
    kids = "".join(inline(c) for c in node.children)

    if name in ("strong", "b"):
        return f"**{kids.strip()}**" if kids.strip() else ""
    if name in ("em", "i"):
        return f"*{kids.strip()}*" if kids.strip() else ""
    if name == "code":
        return f"`{kids.strip()}`" if kids.strip() else ""
    if name == "a":
        href = node.get("href", "")
        if href.startswith("#") or not href:
            return kids
        return f"[{kids.strip()}]({href})"
    if name == "br":
        return "  \n"
    if name in ("span", "div", "sup", "sub", "small"):
        return kids
    return kids


def tidy(text: str) -> str:
    """
    Clean up spacing artifacts from inline extraction.

    The source wraps punctuation outside inline tags, so `get_text(" ")` and
    the inline() walker both leave a space before it: "the constructor is
    `private` ." Left alone this shows up in every chapter.
    """
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?%])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s+'s\b", "'s", text)
    return text.strip()


def text_of(node) -> str:
    return tidy(node.get_text(" ", strip=True))


# ------------------------------------------------------------------- diagrams


def namespace_svg(svg: Tag, prefix: str) -> str:
    """
    Rewrite every id defined inside this SVG to be unique to this figure, and
    update the references that point at them.

    Without this, figures extracted from the same source article collide:
    `url(#dotGrid)` in figure 12 would resolve against figure 1's definition,
    or against nothing at all once they live in separate files.
    """
    ids = {el["id"] for el in svg.find_all(attrs={"id": True})}
    if not ids:
        return str(svg)

    mapping = {old: f"{prefix}-{old}" for old in ids}

    for el in svg.find_all(attrs={"id": True}):
        el["id"] = mapping[el["id"]]

    # Attribute references: fill="url(#x)", filter="url(#x)", href="#x", etc.
    for el in svg.find_all(True):
        for attr, val in list(el.attrs.items()):
            if not isinstance(val, str):
                continue
            new = val
            for old, repl in mapping.items():
                new = re.sub(rf"url\(#{re.escape(old)}\)", f"url(#{repl})", new)
                if attr in ("href", "xlink:href") and val == f"#{old}":
                    new = f"#{repl}"
            if new != val:
                el[attr] = new

    out = str(svg)
    # Inline <style> blocks inside the SVG may also reference the ids.
    for old, repl in mapping.items():
        out = out.replace(f"url(#{old})", f"url(#{repl})")
    return out


def inject_shared_defs(svg: Tag, registry: dict) -> int:
    """
    Pull in <defs> this figure uses but does not own.

    In the source documents a filter or marker is often defined in the first
    diagram of a section and then referenced by every later diagram on the
    page -- legal, because they share one DOM. The moment each figure becomes
    its own file those references dangle and the arrowheads and textures
    silently disappear. Copy any missing definition in before namespacing.
    """
    text = str(svg)
    refs = set(re.findall(r"url\(#([^)]+)\)", text))
    refs |= set(re.findall(r'(?:xlink:)?href="#([^"]+)"', text))
    local = {el["id"] for el in svg.find_all(attrs={"id": True})}
    missing = [r for r in refs - local if r in registry]
    if not missing:
        return 0

    defs = svg.find("defs")
    if defs is None:
        defs = BeautifulSoup("<defs></defs>", "html.parser").defs
        svg.insert(0, defs)
    for r in missing:
        frag = BeautifulSoup(registry[r], "html.parser")
        for node in list(frag.children):
            defs.append(node)
    return len(missing)


def emit_svg(svg: Tag, slug: str, index: int, caption: str, write: bool,
             registry: dict | None = None) -> str:
    fig = f"{slug}-fig{index:02d}"
    if registry:
        inject_shared_defs(svg, registry)
    markup = namespace_svg(svg, fig)
    if write:
        DIAGRAMS.mkdir(parents=True, exist_ok=True)
        (DIAGRAMS / f"{fig}.svg").write_text(markup, encoding="utf-8")
    alt = caption or f"Figure {index}"
    rel = f"../assets/diagrams/{fig}.svg"
    return f"![{alt}]({rel})\n\n*Figure {index} — {alt}*" if caption else f"![{alt}]({rel})"


# ---------------------------------------------------------------------- table


def render_table(tbl: Tag) -> str:
    rows = []
    for tr in tbl.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        rows.append([tidy(" ".join(inline(c) for c in cell.children)).replace("|", "\\|")
                     for cell in cells])
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    head, body = rows[0], rows[1:]
    out = ["| " + " | ".join(head) + " |",
           "|" + "|".join([" --- "] * width) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in body]
    return "\n".join(out)


# ----------------------------------------------------------------- code block


def render_code(block: Tag) -> str:
    """
    Render a code listing.

    `block` is either a wrapper containing the <pre>, or the <pre> itself.
    The three articles families label code three different ways:
      .code-block > .code-block-label + pre     (deep dives)
      .code-header > .code-lang + .code-file    (structural/behavioural)
      .code-label followed by a sibling pre     (creational)
    The last one is why this must never search beyond its own block -- an
    earlier version called block.find("pre") on the document root and
    rendered the first listing five times over.
    """
    # The System Design articles use .code-block > <code> with no <pre> at all
    # (their API request/response bodies). Fall back to the <code> element so
    # those listings survive.
    pre = block if block.name == "pre" else block.find("pre")
    if pre is None and block.name != "pre":
        pre = block.find("code")
    if pre is None:
        return ""

    label = ""
    scope = block if block.name != "pre" else None
    if scope is not None:
        el = scope.select_one(".code-block-label, .code-lang, .code-label")
        if el:
            label = text_of(el)
            f = scope.select_one(".code-file")
            if f and text_of(f) not in label:
                label = f"{label} — {text_of(f)}"
    if not label:
        prev = pre.find_previous_sibling()
        if prev is not None and (set(prev.get("class") or []) &
                                 {"code-label", "code-header", "code-block-label"}):
            label = text_of(prev)

    # Strip presentational syntax spans, keep the text.
    clone = BeautifulSoup(str(pre), "html.parser")
    for span in clone.find_all("span"):
        cls = set(span.get("class") or [])
        if cls & CODE_SPANS or not cls:
            span.unwrap()

    code = clone.get_text()
    code = code.replace("\xa0", " ").strip("\n")

    lang = "text"
    low = label.lower()
    for needle, tag in (("java", "java"), ("typescript", "typescript"),
                        ("javascript", "javascript"), ("python", "python"),
                        ("go", "go"), ("sql", "sql"), ("yaml", "yaml"),
                        ("json", "json"), ("bash", "bash"), ("redis", "bash")):
        if needle in low:
            lang = tag
            break

    header = f"**{label}**\n\n" if label else ""
    return f"{header}```{lang}\n{code}\n```"


# ------------------------------------------------------------ semantic blocks


def render_callout(el: Tag) -> str:
    label_el = el.select_one(".callout-label, .callout-tag")
    label = text_of(label_el) if label_el else ""
    if label_el:
        label_el.extract()
    body = tidy(" ".join(inline(c) for c in el.children))
    head = f"> **{label}**\n>\n" if label else "> "
    return head + "\n".join(f"> {ln}" for ln in wrap_para(body))


def render_deep_dive(el: Tag, ctx) -> str:
    head = el.select_one(".deep-dive-header h4, .deep-dive-header")
    title = text_of(head) if head else "Deep Dive"
    inner = el.select_one(".deep-dive-content-inner") or el.select_one(".deep-dive-content")
    body = render_children(inner, ctx) if inner else ""
    quoted = "\n".join(f"> {ln}" if ln else ">" for ln in body.split("\n"))
    return f"> ### {title}\n>\n{quoted}"


def render_entity_grid(el: Tag) -> str:
    out = []
    for card in el.select(".entity-card"):
        icon = card.select_one(".entity-icon")
        if icon:
            icon.extract()
        strong = card.find(["h4", "h3", "strong"])
        name = text_of(strong) if strong else ""
        if strong:
            strong.extract()
        desc = text_of(card)
        out.append(f"- **{name}** — {desc}" if name else f"- {desc}")
    return "\n".join(out)


def render_stats(el: Tag) -> str:
    rows = []
    for s in el.select(".scale-stat"):
        v = s.select_one(".stat-value")
        d = s.select_one(".stat-desc")
        rows.append((text_of(v) if v else "", text_of(d) if d else ""))
    if not rows:
        return ""
    out = ["| | |", "| --- | --- |"]
    out += [f"| **{v}** | {d} |" for v, d in rows]
    return "\n".join(out)


def render_levels(el: Tag) -> str:
    out = []
    for card in el.select(".level-card"):
        lbl = card.select_one(".level-label")
        focus = card.select_one(".level-focus")
        name = text_of(lbl) if lbl else ""
        if lbl:
            lbl.extract()
        f = text_of(focus) if focus else ""
        if focus:
            focus.extract()
        rest = text_of(card)
        line = f"- **{name}**"
        if f:
            line += f" *({f})*"
        if rest:
            line += f" — {rest}"
        out.append(line)
    return "\n".join(out)


def render_api(el: Tag) -> str:
    m = el.select_one(".api-method")
    u = el.select_one(".api-url")
    d = el.select_one(".api-desc")
    sig = f"`{text_of(m)} {text_of(u)}`" if m and u else f"`{text_of(el)}`"
    return f"- {sig}" + (f" — {text_of(d)}" if d else "")


def render_verdict_box(el: Tag) -> str:
    """The 'Reach for X when… / Avoid X when…' pairs. Class names differ per
    article family: .v-box/.v-title/.v-list vs .verdict-box/.verdict-title."""
    title_el = el.select_one(".v-title, .verdict-title")
    title = text_of(title_el) if title_el else ""
    title = title.replace("✔", "").replace("✗", "").replace("✘", "").strip()
    good = any(m in text_of(title_el or el) for m in ("✔", "✓"))
    lst = el.select_one("ul")
    items = [text_of(li) for li in lst.find_all("li")] if lst else []
    mark = "**Use when**" if good else "**Avoid when**"
    head = f"> {mark} — {title}" if title else f"> {mark}"
    body = "\n".join(f"> - {i}" for i in items)
    return f"{head}\n>\n{body}" if items else head


def render_analogy(el: Tag) -> str:
    for ic in el.select(".analogy-icon"):
        ic.extract()
    body = text_of(el)
    return "\n".join(f"> {ln}" for ln in wrap_para(body))


def render_pull(el: Tag) -> str:
    return "\n".join(f"> {ln}" for ln in wrap_para(text_of(el)))


def render_gh_card(el: Tag) -> str:
    a = el.find("a", href=True)
    label_el = el.select_one(".gh-label")
    label = text_of(label_el) if label_el else "Source code"
    return f"> {label}: <{a['href']}>" if a else ""


def render_pattern_header(el: Tag) -> str:
    """Pattern section heading. Two markups: .pattern-header (h2 + em subtitle
    + .pat-tagline) and .pat-opener (.pat-name + .pat-tagline)."""
    for junk in el.select(".pat-series, .pat-cat, .pat-category, .pat-big-num, .pat-num"):
        junk.extract()
    h = el.find(["h2", "h3"])
    name_el = el.select_one(".pat-name")
    tag_el = el.select_one(".pat-tagline")
    tagline = text_of(tag_el) if tag_el else ""
    if tag_el:
        tag_el.extract()

    if h is not None:
        em = h.find("em")
        sub = text_of(em) if em else ""
        if em:
            em.extract()
        name = text_of(h)
    else:
        name = text_of(name_el) if name_el else text_of(el)
        sub = ""

    out = [f"## {name}".rstrip()]
    if sub:
        out.append(f"*{sub}*")
    if tagline:
        out.append(f"*{tagline}*")
    return "\n\n".join(out)


def render_list(el: Tag) -> str:
    out = []
    ordered = el.name == "ol"
    for i, li in enumerate(el.find_all("li", recursive=False), 1):
        for ic in li.select(".check-icon, .cross-icon"):
            mark = text_of(ic)
            ic.replace_with(NavigableString("[+] " if "✔" in mark or "✓" in mark else "[-] "))
        txt = tidy(" ".join(inline(c) for c in li.children))
        bullet = f"{i}." if ordered else "-"
        out.append(f"{bullet} {txt}")
    return "\n".join(out)


def wrap_para(text: str, width: int = 92):
    words, line, out = text.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > width and line:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        out.append(line)
    return out or [""]


# ------------------------------------------------------------------- dispatch


class Ctx:
    def __init__(self, slug, write, defs_registry=None):
        self.slug = slug
        self.write = write
        self.fig = 0
        self.captions = []
        self.defs = defs_registry or {}


def classes(el: Tag) -> set:
    return set(el.get("class") or [])


def render_el(el, ctx: Ctx) -> str:
    if isinstance(el, NavigableString):
        t = re.sub(r"\s+", " ", str(el)).strip()
        return ""
    if not isinstance(el, Tag):
        return ""

    cl = classes(el)
    name = el.name

    # Figures -------------------------------------------------------------
    if name == "svg":
        ctx.fig += 1
        return emit_svg(el, ctx.slug, ctx.fig, "", ctx.write, ctx.defs)

    if cl & {"diagram-container", "diagram-wrap"}:
        cap_el = el.select_one(".diagram-title, .diagram-bar, .diagram-label, .diagram-caption")
        caption = text_of(cap_el) if cap_el else ""
        # 'Excalidraw · Sequence Diagram' names the drawing tool, not the content.
        caption = re.sub(r"^Excalidraw\s*·\s*", "", caption).strip()
        svg = el.find("svg")
        parts = []
        if svg:
            ctx.fig += 1
            parts.append(emit_svg(svg, ctx.slug, ctx.fig, caption, ctx.write, ctx.defs))
            ctx.captions.append(caption)
        after = el.select_one("p.diagram-caption")
        if after and after is not cap_el:
            parts.append(text_of(after))
        return "\n\n".join(p for p in parts if p)

    # Structural ----------------------------------------------------------
    if name in ("h1", "h2", "h3", "h4", "h5"):
        for sn in el.select(".section-number"):
            sn.extract()
        t = tidy(" ".join(inline(c) for c in el.children))
        if not t:
            return ""
        level = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####"}[name]
        return f"{level} {t}"

    if name == "p":
        if "diagram-caption" in cl:
            return ""  # already emitted with its figure
        t = tidy(" ".join(inline(c) for c in el.children))
        return "\n".join(wrap_para(t)) if t else ""

    if name in ("ul", "ol"):
        return render_list(el)

    if name == "table":
        return render_table(el)

    if name == "pre":
        return render_code(el)

    if name == "blockquote":
        inner = render_children(el, ctx)
        return "\n".join(f"> {ln}" for ln in inner.split("\n"))

    if name == "hr":
        return "---"

    # Semantic blocks -----------------------------------------------------
    if "code-block" in cl:
        return render_code(el)
    # A label div immediately followed by its <pre>; the pre renders both.
    if cl & {"code-label", "code-header", "code-block-label"}:
        nxt = el.find_next_sibling()
        if nxt is not None and nxt.name == "pre":
            return ""
        return ""
    if cl & {"pattern-header", "pat-opener"}:
        return render_pattern_header(el)
    if cl & {"v-box", "verdict-box"}:
        return render_verdict_box(el)
    if "verdict" in cl:
        return render_children(el, ctx)
    if "analogy" in cl:
        return render_analogy(el)
    if "pull" in cl:
        return render_pull(el)
    if "gh-card" in cl:
        return render_gh_card(el)
    if "callout" in cl:
        return render_callout(el)
    if "deep-dive" in cl:
        return render_deep_dive(el, ctx)
    if "entity-grid" in cl:
        return render_entity_grid(el)
    if "scale-stats" in cl:
        return render_stats(el)
    if "level-grid" in cl:
        return render_levels(el)
    if "api-endpoint" in cl:
        return render_api(el)
    if "pat-block" in cl:
        return render_children(el, ctx)
    if cl & {"diagram-bar", "diagram-title", "diagram-label"}:
        return ""  # captions are emitted alongside their figure

    # Transparent containers ----------------------------------------------
    if name in ("div", "section", "article", "main", "span", "figure", "header"):
        if cl:
            known = {
                "article-body", "section", "content", "container", "inner",
                "deep-dive-content", "deep-dive-content-inner", "pat-sep",
                "entity-card", "scale-stat", "level-card", "code-header",
                "pat-tagline", "pat-title-block", "pat-name", "pat-number-row",
                "pat-label-stack", "pat-series", "analogy-body", "v-title", "st-item",
                "table-scroll", "analogy-text", "verdict-title", "gh-body",
                "gh-icon", "gh-label", "gh-link", "gh-url", "analogy-icon",
                "pat-sep-num", "pat-num", "pat-category", "pat-big-num", "pat-cat",
                "code-lang", "code-file", "verdict-list", "v-list", "use", "skip",
                "section-number", "check-icon", "cross-icon", "callout-label",
                "callout-tag", "stat-value", "stat-desc", "entity-icon",
                "level-label", "level-focus", "api-method", "api-url", "api-desc",
                "diagram-caption", "deep-dive-header", "deep-dive-toggle",
            }
            known = cl & known
            if not known:
                unknown[f"{name}.{sorted(cl)[0]}"] += 1
        return render_children(el, ctx)

    return render_children(el, ctx)


def render_children(parent, ctx: Ctx) -> str:
    if parent is None:
        return ""
    blocks = []
    for child in parent.children:
        out = render_el(child, ctx)
        if out and out.strip():
            blocks.append(out.strip())
    # Collapse duplicate blank lines between blocks
    return "\n\n".join(blocks)


# ---------------------------------------------------------------- frontmatter


def build_frontmatter(soup: BeautifulSoup, part: str, slug: str, src: str) -> dict:
    def sel(css):
        el = soup.select_one(css)
        return text_of(el) if el else ""

    h1 = soup.select_one(".article-hero h1") or soup.find("h1")
    title = text_of(h1) if h1 else ""
    doc_title = text_of(soup.title) if soup.title else ""
    if doc_title:
        doc_title = re.split(r"\s*\|\s*", doc_title)[0].strip()

    desc_el = soup.select_one(".article-hero p, .hero-sub, .article-subtitle")
    return {
        "title": title or doc_title,
        "source_title": doc_title,
        "part": part,
        "slug": slug,
        "category": sel(".article-category"),
        "date": sel(".article-date"),
        "read_time": sel(".article-read-time"),
        "description": text_of(desc_el) if desc_el else "",
        "source_html": src,
        "status": "draft",
    }


def yaml_dump(d: dict) -> str:
    out = ["---"]
    for k, v in d.items():
        v = (v or "").replace('"', '\\"') if isinstance(v, str) else v
        out.append(f'{k}: "{v}"' if isinstance(v, str) else f"{k}: {v}")
    out.append("---")
    return "\n".join(out)


# -------------------------------------------------------------------- driver


def extract(part, src, slug, write) -> dict:
    path = ROOT / src
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    for t in soup.find_all(["style", "script", "noscript"]):
        t.decompose()
    for css in CHROME_SELECTORS:
        for t in soup.select(css):
            t.decompose()

    fm = build_frontmatter(soup, part, slug, src)

    body = soup.select_one("article.article-body") or soup.select_one("main.article-body")
    if body is None:
        body = soup.find("article") or soup.find("main")
    if body is None:
        raise SystemExit(f"{src}: no content container found")

    # Map every id defined anywhere in the document to its element, so a
    # figure that borrows a sibling's filter or marker can take a copy.
    # Snapshot the markup, not the live element: namespace_svg renames ids in
    # place, so a figure extracted later would otherwise borrow a definition
    # that an earlier figure had already renamed out from under it.
    registry = {}
    for holder in soup.find_all("defs"):
        for child in holder.find_all(True, recursive=False):
            if child.get("id"):
                registry.setdefault(child["id"], str(child))

    ctx = Ctx(slug, write, registry)
    md = render_children(body, ctx)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"

    if write:
        CONTENT.mkdir(parents=True, exist_ok=True)
        (CONTENT / f"{slug}.md").write_text(yaml_dump(fm) + "\n\n" + md, encoding="utf-8")

    # Fidelity check.
    #
    # A naive word-count ratio is meaningless here: Markdown adds syntax
    # tokens (pipes, bullets, backticks) while chrome removal takes tokens
    # away, and the two roughly cancel. The number that actually matters is
    # whether any *source token* vanished for a reason we did not intend.
    #
    # So: take the multiset of source tokens minus the multiset of output
    # tokens, then subtract the tokens we deliberately drop (decorative
    # numbering, series labels, diagram-tool captions). The residual must be
    # zero. Anything else means content was silently lost.
    body_probe = BeautifulSoup(str(body), "html.parser")
    for s_ in body_probe.find_all("svg"):
        s_.decompose()

    def toks(s):
        return re.sub(r"[^a-zA-Z0-9 ]", " ", s.lower()).split()

    intentional = Counter()
    for sel in (".pat-series", ".pat-cat", ".pat-category", ".pat-big-num",
                ".pat-num", ".pat-sep-num", ".diagram-bar", ".diagram-title",
                ".diagram-label", ".analogy-icon", ".gh-icon", ".gh-link",
                ".gh-label", ".gh-url", ".pat-sep", ".section-number",
                ".deep-dive-toggle", ".entity-icon"):
        for el in body_probe.select(sel):
            intentional.update(toks(el.get_text(" ", strip=True)))

    src_c = Counter(toks(body_probe.get_text(" ", strip=True)))
    out_c = Counter(toks(md))
    deficit = src_c - out_c
    residual = deficit - intentional

    return {
        "slug": slug, "src": src, "figures": ctx.fig,
        "src_words": sum(src_c.values()), "out_words": sum(out_c.values()),
        "deficit": sum(deficit.values()),
        "residual": sum(residual.values()),
        "residual_top": residual.most_common(6),
        "title": fm["title"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="substring filter on slug")
    args = ap.parse_args()
    write = not args.dry_run

    rows = []
    for part, src, slug in ARTICLES:
        if args.only and args.only not in slug:
            continue
        rows.append(extract(part, src, slug, write))

    print(f"{'slug':<26}{'figs':>5}{'src_w':>8}{'md_w':>8}{'lost':>6}  {'':<4}title")
    print("-" * 96)
    tf = tsw = tow = tres = 0
    bad = []
    for r in rows:
        tf += r["figures"]; tsw += r["src_words"]; tow += r["out_words"]
        tres += r["residual"]
        flag = "OK  " if r["residual"] == 0 else "LOSS"
        if r["residual"]:
            bad.append(r)
        print(f'{r["slug"]:<26}{r["figures"]:>5}{r["src_words"]:>8}'
              f'{r["out_words"]:>8}{r["residual"]:>6}  {flag}  {r["title"][:32]}')
    print("-" * 96)
    print(f'{"TOTAL":<26}{tf:>5}{tsw:>8}{tow:>8}{tres:>6}')
    print(f"\nFidelity: unexplained token loss = {tres} "
          f"({'lossless' if tres == 0 else 'REVIEW NEEDED'})")
    for r in bad:
        print(f'  {r["slug"]}: {r["residual_top"]}', file=sys.stderr)

    if unknown:
        print("\nUnmapped constructs (kept as plain text, review these):", file=sys.stderr)
        for k, v in unknown.most_common(25):
            print(f"  {k:<34} {v}", file=sys.stderr)
    else:
        print("\nNo unmapped constructs.", file=sys.stderr)

    if args.dry_run:
        print("\n(dry run — nothing written)")


if __name__ == "__main__":
    main()
