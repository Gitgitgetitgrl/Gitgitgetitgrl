#!/usr/bin/env bash
# ONE-TIME content download (needs internet). Fetches .zim libraries into
# content/zim/. Pick a pack; you can re-run to add more later.
#
#   ./scripts/02-download-content.sh            # interactive menu
#   ./scripts/02-download-content.sh core       # non-interactive
#
# After downloading, index it:  docker compose exec rom python ingest.py
#
# NOTE: filenames on the Kiwix mirror are DATED (e.g. ..._2024-10.zim) and change
# over time. This script resolves the newest match from the mirror automatically.
set -euo pipefail
cd "$(dirname "$0")/.."
DEST="content/zim"; mkdir -p "$DEST"
MIRROR="https://download.kiwix.org/zim"
DL="aria2c -x8 -s8 -c --dir=$DEST"
command -v aria2c >/dev/null || DL="wget -c -P $DEST"

# Resolve the newest file matching a prefix in a mirror directory, then download.
fetch() {  # fetch <zim-subdir> <filename-prefix>
    local dir="$1" prefix="$2"
    echo "==> Resolving newest '$prefix*' in $dir"
    local file
    file=$(curl -s "$MIRROR/$dir/" \
        | grep -oE "href=\"${prefix}[^\"]*\.zim\"" \
        | sed -E 's/href="([^"]+)"/\1/' | sort -V | tail -1)
    if [[ -z "$file" ]]; then echo "  !! not found: $prefix (skipping)"; return; fi
    echo "==> Downloading $file"
    $DL "$MIRROR/$dir/$file"
}

pack_core() {
    echo "### CORE pack (~55-60 GB): the essentials"
    fetch wikipedia   "wikipedia_en_all_nopic"       # full English Wikipedia, no images
    fetch wikipedia   "wikipedia_en_simple_all_maxi" # lightweight fallback
    fetch other       "wikimed_en_all_maxi"          # WikiMed medical encyclopedia
    fetch ifixit      "ifixit_en_all"                # repair guides
    fetch gutenberg   "gutenberg_en_all"             # (large; comment out to skip)
    echo "### Add curated survival/first-aid/radio PDFs into content/ manually (see docs/03)."
}

pack_medical() {
    echo "### MEDICAL pack"
    fetch other       "wikimed_en_all_maxi"
    fetch other       "mdwiki_en_all_maxi" || true
    fetch zimit       "www.who.int" || true
}

pack_reference() {
    echo "### REFERENCE pack (large)"
    fetch wikipedia   "wikipedia_en_all_maxi"        # WITH images (~100 GB)
    fetch wiktionary  "wiktionary_en_all_maxi"
    fetch other       "wikivoyage_en_all_maxi"
}

menu() {
    cat <<EOF
Choose a content pack to download into $DEST:
  1) core       Wikipedia(no-pic)+Simple+WikiMed+iFixit+Gutenberg   (~55-60 GB)  [recommended first]
  2) medical    Medical/health libraries only
  3) reference  Wikipedia WITH images + Wiktionary + Wikivoyage     (large, ~110 GB+)
  4) all        core + medical + reference
  q) quit
EOF
    read -rp "Selection: " sel
    case "$sel" in
        1|core) pack_core ;;
        2|medical) pack_medical ;;
        3|reference) pack_reference ;;
        4|all) pack_core; pack_medical; pack_reference ;;
        q|Q) exit 0 ;;
        *) echo "Unknown selection"; exit 1 ;;
    esac
}

if [[ $# -gt 0 ]]; then
    case "$1" in core) pack_core;; medical) pack_medical;; reference) pack_reference;; all) pack_core;pack_medical;pack_reference;; *) echo "usage: $0 [core|medical|reference|all]"; exit 1;; esac
else
    menu
fi

echo
echo "==> Done. Files in $DEST:"; ls -lh "$DEST"/*.zim 2>/dev/null || true
echo "==> Next: ./scripts/03-start.sh  then  docker compose exec rom python ingest.py"
