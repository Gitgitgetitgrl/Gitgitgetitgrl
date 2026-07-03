#!/usr/bin/env bash
# Build the operator manual PDF from docs/operation-manual.md.
# Dependency-light: uses a bundled Markdown->HTML renderer + a headless browser
# (Chromium/Chrome) to print the PDF. Falls back to pandoc/wkhtmltopdf if present.
#   ./scripts/04-build-manual-pdf.sh
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="docs/operation-manual.md"
HTML="docs/operation-manual.html"
PDF="docs/ROM-Operation-Manual.pdf"

echo "==> Rendering Markdown -> HTML"
python3 scripts/build_manual.py "$SRC" "$HTML"

# Find a headless browser
BROWSER=""
for c in chromium chromium-browser google-chrome google-chrome-stable chrome; do
    if command -v "$c" >/dev/null 2>&1; then BROWSER="$c"; break; fi
done

if [[ -n "$BROWSER" ]]; then
    echo "==> Printing PDF with $BROWSER"
    "$BROWSER" --headless --no-sandbox --disable-gpu \
        --no-pdf-header-footer \
        --print-to-pdf="$PDF" "file://$(pwd)/$HTML" 2>/dev/null || \
    "$BROWSER" --headless --no-sandbox --disable-gpu \
        --print-to-pdf="$PDF" "file://$(pwd)/$HTML"
elif command -v pandoc >/dev/null 2>&1; then
    echo "==> Printing PDF with pandoc"
    pandoc "$SRC" -o "$PDF"
elif command -v wkhtmltopdf >/dev/null 2>&1; then
    echo "==> Printing PDF with wkhtmltopdf"
    wkhtmltopdf "$HTML" "$PDF"
else
    echo "!! No PDF engine found. Install chromium OR pandoc, or just print"
    echo "   $HTML from a browser (Print -> Save as PDF)."
    exit 1
fi

echo "==> Built $PDF"
ls -lh "$PDF"
