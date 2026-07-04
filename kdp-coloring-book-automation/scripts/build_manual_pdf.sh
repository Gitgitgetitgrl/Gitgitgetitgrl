#!/usr/bin/env bash
# Build the operator manual PDF from manual/operation-manual.md.
# Uses a bundled Markdown->HTML renderer + a headless browser to print the PDF.
#   bash scripts/build_manual_pdf.sh
set -euo pipefail
cd "$(dirname "$0")/.."

SRC="manual/operation-manual.md"
HTML="manual/operation-manual.html"
PDF="manual/KDP-Operation-Manual.pdf"

echo "==> Rendering Markdown -> HTML"
python3 scripts/build_manual.py "$SRC" "$HTML"

# Find a headless browser (also check the Playwright-bundled Chromium).
BROWSER=""
for c in chromium chromium-browser google-chrome google-chrome-stable chrome; do
    if command -v "$c" >/dev/null 2>&1; then BROWSER="$c"; break; fi
done
if [[ -z "$BROWSER" ]]; then
    PW=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1 || true)
    [[ -n "$PW" ]] && BROWSER="$PW"
fi

if [[ -n "$BROWSER" ]]; then
    echo "==> Printing PDF with $BROWSER"
    "$BROWSER" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
        --print-to-pdf="$PDF" "file://$(pwd)/$HTML" 2>/dev/null || \
    "$BROWSER" --headless --no-sandbox --disable-gpu \
        --print-to-pdf="$PDF" "file://$(pwd)/$HTML"
elif command -v pandoc >/dev/null 2>&1; then
    pandoc "$SRC" -o "$PDF"
else
    echo "!! No PDF engine found. Open $HTML in a browser and Print -> Save as PDF."
    exit 1
fi

echo "==> Built $PDF"
ls -lh "$PDF"
