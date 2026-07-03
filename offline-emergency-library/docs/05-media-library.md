# 05 — Offline Media Library (the realistic "YouTube / Pinterest offline")

You **cannot** mirror YouTube or Pinterest wholesale — there's no legal or practical way to
put "all of YouTube" on a box. What you *can* do, and what this project does, is **curate
specific videos and images while you're online** and serve them from an **offline media
server** ([Jellyfin](https://jellyfin.org)) plus a plain image gallery.

- **Videos** → downloaded with [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) into
  `content/media/<Category>/`, then browsed/streamed offline via Jellyfin at port **8096**.
- **Images / infographics** (the Pinterest use-case) → downloaded with
  [`gallery-dl`](https://github.com/mikf/gallery-dl) into `content/media/Infographics/`,
  viewable as files or through Jellyfin's photo library.

> **Personal use only.** These downloads are copyrighted by their creators. Keep them on
> *your* device for *your* household — do **not** redistribute or sell copies. See
> [`04-licensing-and-legal.md`](04-licensing-and-legal.md).

## How to build the media library (while online)

```bash
# 1. Start the media server (optional 'media' profile)
docker compose --profile media up -d jellyfin

# 2. Curate: copy the example list, edit it, then download
cp content/media/playlist.example.txt content/media/playlist.txt
#    edit content/media/playlist.txt — add/remove lines, paste exact playlist URLs
./scripts/05-download-media.sh            # downloads videos + infographics

# 3. Open Jellyfin, add 'content/media' as a library (Movies/Home Videos type)
#    http://10.42.0.1:8096   (first run walks you through a quick setup)
```

Downloads are organized into per-category folders so Jellyfin shows them as tidy
collections. Re-run the script any time to add more.

## Curated categories (from your request)

The starter list in `content/media/playlist.example.txt` seeds every category below with
robust `ytsearch` queries (so nothing breaks if a channel URL changes). For best quality,
replace a search line with the **exact playlist/channel URL** you want.

| Category | Folder | What it covers |
|----------|--------|----------------|
| Tactical | `Tactical/` | Field craft, situational awareness, movement, tactical first aid |
| Ancient history & civilizations | `AncientHistory/` | Ancient civilizations, lost cities, historical overviews |
| Ancient knowledge & technology | `AncientTech/` | Ancient engineering, tools, techniques, "how the ancients built it" |
| Religious teachings | `Religious/` | Scripture readings, teachings, comparative religion |
| Ancient mysteries & unexplained | `AncientMysteries/` | Ancient-astronaut theories, megaliths, unexplained sites ("alien"/lost-knowledge topics) |
| Minerals & natural elements | `Minerals/` | Identifying rocks/minerals, practical uses of natural elements |
| Security & protection | `Security/` | Personal security, home protection, situational safety |
| Technology builds (DIY) | `TechBuilds/` | Homemade generator, DIY water filter, off-grid power, electronics builds |
| Gardening & seeds | `Gardening/` | Seed saving, planting guides, food gardens |
| Survival DIY | `SurvivalDIY/` | Shelter, fire, traps, tools, off-grid skills |
| Survival infographics (images) | `Infographics/` | Printable survival/skill infographics (Pinterest-style) |
| Computer & online safety | `ComputerSafety/` | Digital hygiene, privacy, staying safe online/offline |
| Homestead cooking | `HomesteadCooking/` | From-scratch, preservation, root-cellar, off-grid cooking |
| Cooking for fun | `CookingForFun/` | Everyday/fun recipes and technique |
| Kids — learning & shows | `Kids/` | Blippi, Bluey, StoryBots, Numberblocks, Twirlywoos, Tayo, Pixar Cars |

> **On "alien info":** included as an *ancient mysteries / unexplained* category — historical
> theories and documentary-style content. Treat it as entertainment/speculation, not
> verified fact; Rom won't cite it as evidence for anything safety-critical.

## Storage planning

Video is big. Budget roughly:

- ~0.3–1 GB per hour at 480–720p (good enough for how-to on a phone/tablet).
- A kids library of a few hundred episodes can run 50–150 GB on its own.
- Set a per-item quality cap in the script (default **720p**) to keep it reasonable; drop to
  480p for the kids/entertainment folders if space is tight.

Keep the media library on the **same drive** as `content/` and include it in your backup.
