#!/usr/bin/env python3
"""Render a Markdown file to styled, standalone HTML (dependency-free).

Supports the Markdown subset used by the manual: headings, bold/inline-code,
lists, tables, code fences, blockquotes, hr, paragraphs. build_manual_pdf.sh then
prints the HTML to PDF with headless Chromium.
"""
import html
import re
import sys


def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def render(md: str) -> str:
    out, lines, i = [], md.split("\n"), 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip().startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]+$", lines[i + 1]):
            def cells(r):
                return [c.strip() for c in r.strip().strip("|").split("|")]
            header = cells(line)
            i += 2
            rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(cells(lines[i]))
                i += 1
            thead = "".join(f"<th>{inline(c)}</th>" for c in header)
            tbody = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                            for r in rows)
            out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if re.match(r"^---+\s*$", line):
            out.append("<hr>")
            i += 1
            continue
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(inline(lines[i].lstrip("> ").rstrip()))
                i += 1
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>")
            continue
        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            buf = []
            while i < n and (re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^\s*\d+\.\s+", lines[i])):
                item = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", lines[i])
                buf.append(f"<li>{inline(item)}</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(buf) + f"</{tag}>")
            continue
        if not line.strip():
            i += 1
            continue
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not re.match(
                r"^(#{1,6}\s|>|```|\s*[-*]\s|\s*\d+\.\s|---+\s*$)", lines[i]) and "|" not in lines[i]:
            buf.append(lines[i])
            i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font: 11pt/1.5 -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
       color: #1a1a1a; max-width: 720px; margin: 0 auto; }
h1 { font-size: 24pt; border-bottom: 3px solid #6b46c1; padding-bottom: 6px; margin-top: 0; }
h2 { font-size: 15pt; color: #44337a; border-bottom: 1px solid #cbd5e0; padding-bottom: 4px; margin-top: 22px; }
h3 { font-size: 12.5pt; color: #553c9a; }
p, li { font-size: 11pt; }
code { background: #edf2f7; padding: 1px 5px; border-radius: 4px; font-family: Consolas, monospace; font-size: 9.5pt; }
pre { background: #1a202c; color: #e2e8f0; padding: 11px 13px; border-radius: 7px; overflow-x: auto; }
pre code { background: none; color: inherit; padding: 0; font-size: 9pt; }
blockquote { border-left: 4px solid #6b46c1; background: #faf5ff; margin: 10px 0; padding: 8px 14px; color: #44337a; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 10pt; }
th, td { border: 1px solid #cbd5e0; padding: 6px 9px; text-align: left; vertical-align: top; }
th { background: #f3e8ff; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }
a { color: #6b46c1; }
"""


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "manual/operation-manual.md"
    dst = sys.argv[2] if len(sys.argv) > 2 else "manual/operation-manual.html"
    with open(src) as f:
        body = render(f.read())
    doc = (f"<!doctype html><html><head><meta charset='utf-8'>"
           f"<title>KDP Automation Manual</title><style>{CSS}</style></head>"
           f"<body>{body}</body></html>")
    with open(dst, "w") as f:
        f.write(doc)
    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()
