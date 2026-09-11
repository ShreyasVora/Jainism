#!/usr/bin/env python3
"""Build prayer pages from Markdown.

Converts every src/*.md file into a standalone, print-friendly HTML page
plus a plain-text download in build/, and generates build/index.html
listing them all.

Only a small subset of Markdown is understood, on purpose:
  # Title      -> page title
  ## Section   -> section heading
  *word*       -> emphasis
  blank line   -> separates stanzas

Everything else is treated as plain text, and line breaks *inside* a
stanza are preserved rather than rewrapped -- prayers are chanted line
by line, not read as flowing prose.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR / "src"
BUILD_DIR = SCRIPT_DIR / "build"

EMPHASIS_RE = re.compile(r"\*(.+?)\*")

CSS = """
:root { color-scheme: light dark; }
html { background: #fdfdfd; color: #1a1a1a; }
body {
  max-width: 38em;
  margin: 0 auto;
  padding: 2rem 1.25rem 4rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.15rem;
  line-height: 1.8;
}
nav.top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 0.9rem;
}
nav.top a { color: #555; text-decoration: none; }
nav.top a:hover { text-decoration: underline; }
h1 { text-align: center; font-size: 1.6rem; margin-bottom: 2rem; }
h2 {
  font-size: 1.15rem;
  margin-top: 2.5rem;
  border-top: 1px solid #ddd;
  padding-top: 1rem;
}
p { margin: 1.4rem 0; }
ul.toc { list-style: none; padding: 0; }
ul.toc li {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid #eee;
}
ul.toc a.title { font-size: 1.1rem; text-decoration: none; color: inherit; }
ul.toc a.title:hover { text-decoration: underline; }
ul.toc a.dl {
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 0.85rem;
  color: #777;
  text-decoration: none;
  white-space: nowrap;
}
ul.toc a.dl:hover { text-decoration: underline; }
p.intro { color: #555; }
@media (max-width: 480px) {
  body { font-size: 1.05rem; padding: 1.25rem 1rem 3rem; }
  h1 { font-size: 1.35rem; }
}
@media (prefers-color-scheme: dark) {
  html { background: #1a1a1a; color: #eaeaea; }
  nav.top a { color: #aaa; }
  h2 { border-top-color: #333; }
  ul.toc li { border-bottom-color: #333; }
  ul.toc a.dl { color: #999; }
  p.intro { color: #aaa; }
}
@media print {
  nav.top, .no-print { display: none; }
  body { max-width: none; padding: 0 0.4in; font-size: 12pt; }
  a { color: inherit; text-decoration: none; }
}
""".strip()

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<nav class="top no-print">
  <a href="index.html">&larr; All prayers</a>
  <a href="{slug}.txt" download>Download .txt</a>
</nav>
<h1>{title}</h1>
{body}
</body>
</html>
"""

INDEX_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prayers</title>
<style>
{css}
</style>
</head>
<body>
<h1>Prayers</h1>
<p class="intro">A collection of Jain prayers, written out in English.</p>
<ul class="toc">
{items}
</ul>
</body>
</html>
"""


def render_inline(text: str) -> str:
    escaped = html.escape(text)
    return EMPHASIS_RE.sub(r"<em>\1</em>", escaped)


def parse(md_text: str) -> tuple[str, str, str]:
    """Return (title, body_html, plain_text)."""
    title = ""
    html_parts: list[str] = []
    text_parts: list[str] = []
    stanza_lines: list[str] = []

    def flush_stanza() -> None:
        if not stanza_lines:
            return
        html_parts.append(
            "<p>" + "<br>\n".join(render_inline(l) for l in stanza_lines) + "</p>"
        )
        text_parts.append("\n".join(stanza_lines))
        stanza_lines.clear()

    for raw_line in md_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            flush_stanza()
            continue
        if line.startswith("# "):
            flush_stanza()
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush_stanza()
            heading = line[3:].strip()
            html_parts.append(f"<h2>{render_inline(heading)}</h2>")
            text_parts.append(heading.upper())
            continue
        stanza_lines.append(line.strip())
    flush_stanza()

    return title, "\n".join(html_parts), "\n\n".join(text_parts)


def build() -> None:
    if not SRC_DIR.is_dir():
        raise SystemExit(f"Error: source directory '{SRC_DIR}' does not exist.")

    BUILD_DIR.mkdir(exist_ok=True)

    md_files = sorted(SRC_DIR.glob("*.md"))
    if not md_files:
        print(f"No markdown files found in {SRC_DIR}.")
        return

    toc_items = []
    for md_file in md_files:
        slug = md_file.stem
        title, body_html, plain_text = parse(md_file.read_text(encoding="utf-8"))
        title = title or slug

        (BUILD_DIR / f"{slug}.html").write_text(
            PAGE_TEMPLATE.format(title=html.escape(title), slug=slug, css=CSS, body=body_html),
            encoding="utf-8",
        )
        (BUILD_DIR / f"{slug}.txt").write_text(
            f"{title}\n{'=' * len(title)}\n\n{plain_text}\n", encoding="utf-8"
        )
        toc_items.append(
            f'  <li><a class="title" href="{slug}.html">{html.escape(title)}</a>'
            f' <a class="dl" href="{slug}.txt" download>download .txt</a></li>'
        )
        print(f"Built: src/{md_file.name} -> build/{slug}.html, build/{slug}.txt")

    (BUILD_DIR / "index.html").write_text(
        INDEX_TEMPLATE.format(css=CSS, items="\n".join(toc_items)), encoding="utf-8"
    )
    print(f"Built: build/index.html ({len(md_files)} prayer(s) listed)")


if __name__ == "__main__":
    build()
