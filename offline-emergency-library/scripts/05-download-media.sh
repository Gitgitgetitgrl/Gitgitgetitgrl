#!/usr/bin/env bash
# Curate an offline media library (needs internet, one time). Reads a playlist of
# categories + sources and downloads them into content/media/<Category>/ for Jellyfin.
#
#   cp content/media/playlist.example.txt content/media/playlist.txt   # then edit it
#   ./scripts/05-download-media.sh
#
# ⚠️ PERSONAL USE ONLY -- downloaded content is copyrighted by its creators. Keep it on
#    your own device for your household; do not redistribute. See docs/04-licensing-and-legal.md.
set -euo pipefail
cd "$(dirname "$0")/.."

LIST="${1:-content/media/playlist.txt}"
MEDIA_DIR="content/media"
MAX_HEIGHT="${MAX_HEIGHT:-720}"     # cap quality to keep sizes sane (set 480 for kids/space)

if [[ ! -f "$LIST" ]]; then
    echo "!! No playlist found at $LIST"
    echo "   Create one:  cp content/media/playlist.example.txt content/media/playlist.txt"
    exit 1
fi

# ---- tool checks (install hints, no auto-install of network tools) ----
if ! command -v yt-dlp >/dev/null 2>&1; then
    echo "!! yt-dlp not found. Install it (while online):"
    echo "     python3 -m pip install -U yt-dlp     # or: sudo apt install yt-dlp"
    MISSING=1
fi
HAVE_GALLERY=1
command -v gallery-dl >/dev/null 2>&1 || { HAVE_GALLERY=0; }
[[ "${MISSING:-0}" == 1 ]] && exit 1

echo "==> Downloading media from $LIST (max ${MAX_HEIGHT}p) into $MEDIA_DIR/"
vid_count=0; img_count=0; skipped_img=0

while IFS= read -r line; do
    # strip comments / blank lines
    line="${line%%#*}"; line="$(echo "$line" | sed 's/[[:space:]]*$//')"
    [[ -z "$line" ]] && continue
    [[ "$line" != *"|"* ]] && continue

    category="$(echo "${line%%|*}" | xargs)"
    source="$(echo "${line#*|}" | xargs)"
    [[ -z "$category" || -z "$source" ]] && continue

    # ---- image / infographic lines: 'IMG | <gallery url>' ----
    if [[ "$category" == "IMG" ]]; then
        if [[ "$HAVE_GALLERY" == 0 ]]; then
            echo "  (skip image set; gallery-dl not installed) $source"
            skipped_img=$((skipped_img+1)); continue
        fi
        echo "  [img] $source"
        gallery-dl -d "$MEDIA_DIR/Infographics" "$source" || echo "    ! failed: $source"
        img_count=$((img_count+1))
        continue
    fi

    # ---- video lines ----
    out="$MEDIA_DIR/$category"
    mkdir -p "$out"
    echo "  [vid] $category <- $source"
    # Embed metadata + thumbnail so Jellyfin shows titles/posters. Skip already-downloaded.
    yt-dlp \
        --no-warnings --ignore-errors --download-archive "$MEDIA_DIR/.downloaded.txt" \
        -f "bestvideo[height<=$MAX_HEIGHT]+bestaudio/best[height<=$MAX_HEIGHT]/best" \
        --merge-output-format mp4 \
        --embed-metadata --embed-thumbnail --restrict-filenames \
        -o "$out/%(title).150s [%(id)s].%(ext)s" \
        "$source" || echo "    ! some items failed for: $source"
    vid_count=$((vid_count+1))
done < "$LIST"

echo
echo "==> Media pass complete: $vid_count video source(s), $img_count image set(s) processed."
[[ "$skipped_img" -gt 0 ]] && echo "    ($skipped_img image set(s) skipped -- install gallery-dl: pip install gallery-dl)"
echo "==> Start/refresh the media server:"
echo "    docker compose --profile media up -d jellyfin   ->   http://10.42.0.1:8096"
echo "    In Jellyfin, add '$MEDIA_DIR' as a library so Rom's box can stream it offline."
du -sh "$MEDIA_DIR" 2>/dev/null | awk '{print "==> Media library size: "$1}'
