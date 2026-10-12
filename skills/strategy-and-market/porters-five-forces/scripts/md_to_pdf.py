#!/usr/bin/env python3
"""Render a five-forces Markdown write-up to a styled A4 PDF.

Usage:
  python3 -I md_to_pdf.py "Competitive Strategy/<company>-five-forces.md"
  python3 -I md_to_pdf.py <input.md> <output.pdf>

Needs the `markdown` Python package (pip install markdown) and Google Chrome, which prints the
page to PDF in headless mode. Set CHROME_PATH to use a different Chromium-based browser.
"""
import os
import re
import subprocess
import sys
import tempfile
import time

import markdown

CHROME = os.environ.get("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

CSS = """
@page {
  size: A4; margin: 18mm 16mm 20mm;
  @bottom-center { content: "{TITLE} · " counter(page) " / " counter(pages);
                   font: 8pt 'Helvetica Neue', Arial, sans-serif; color: #888; }
}
body { font: 10pt/1.5 'Helvetica Neue', 'Arial Unicode MS', Arial, sans-serif; color: #1f2328; }
h1 { font-size: 20pt; margin: 0 0 4pt; color: #fc8019; }
h2 { font-size: 13pt; margin: 18pt 0 6pt; padding-bottom: 3pt; border-bottom: 1.5pt solid #fc8019;
     break-after: avoid; }
h1 + p em, h1 + p + p em { color: #57606a; }
p { margin: 4pt 0 6pt; }
ul { margin: 2pt 0 6pt; padding-left: 16pt; }
li { margin: 2pt 0; }
li > ul { margin-top: 2pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9pt; break-inside: avoid; }
th { background: #fff1e6; text-align: left; }
th, td { border: 0.6pt solid #d0d7de; padding: 4pt 6pt; vertical-align: top; }
strong { color: #111; }
a { color: #0b5cad; text-decoration: none; word-break: break-all; }
h2:nth-last-of-type(2) + ul li { font-size: 8.5pt; }
"""


def to_html(text):
    # Python-Markdown needs a blank line before a list or table that follows a paragraph line.
    text = re.sub(r"(?m)^(?![ \t]|[-|*]|$)(.+)\n((?:- |\|))", r"\1\n\n\2", text)

    # Tables inside list items are skipped by the tables extension, so render them on their own.
    def inline_table(m):
        indent = m.group(1)
        rows = "\n".join(line.strip() for line in m.group(0).splitlines())
        html = markdown.markdown(rows, extensions=["tables"]).replace("\n", "")
        return f"{indent}{html}\n"

    text = re.sub(r"(?m)^( +)\|.*\n(?:\1\|.*\n)+", inline_table, text)
    # Python-Markdown nests on 4-space indents; the write-ups use 2.
    text = re.sub(r"(?m)^( +)", lambda m: m.group(1) * 2, text)
    # Make bare URLs clickable.
    text = re.sub(r"(?<![(<])(https?://\S+)", r"<\1>", text)
    # Keep consecutive italic header lines as separate paragraphs.
    text = re.sub(r"(?m)^(\*[^\n]+\*)\n(?=\*)", r"\1\n\n", text)

    body = markdown.markdown(text, extensions=["tables", "sane_lists"])
    title_m = re.search(r"(?m)^# (.+)$", text)
    title = title_m.group(1).replace("'", "’") if title_m else "Five Forces"
    css = CSS.replace("{TITLE}", title)
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".pdf"

    with open(src, encoding="utf-8") as f:
        html = to_html(f.read())

    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, "write-up.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        # Headless Chrome writes the PDF but often keeps running afterwards, so wait for the file
        # to appear and stop the process ourselves instead of waiting for it to exit.
        if os.path.exists(out):
            os.remove(out)
        proc = subprocess.Popen(
            [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
             f"--user-data-dir={os.path.join(tmp, 'profile')}",
             f"--print-to-pdf={os.path.abspath(out)}", "file://" + html_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for _ in range(120):
            if os.path.isfile(out) and os.path.getsize(out) > 0:
                break
            time.sleep(1)
        time.sleep(2)  # let Chrome finish flushing the file before it is stopped
        proc.kill()
        proc.wait()

    if not os.path.isfile(out) or os.path.getsize(out) == 0:
        print(f"PDF was not created at {out}. Check that Chrome is installed at: {CHROME}", file=sys.stderr)
        return 1
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
