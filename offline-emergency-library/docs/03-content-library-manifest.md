# 03 — Content Library Manifest

Everything Rom can serve and search. Organized by priority so you can build a **Core** pack
first (fits ~256–512GB) and expand toward a **Full** build (1–2TB). Sizes are approximate.

Legend: **[CORE]** build first · **[IMPORTANT]** add next · **[NICE]** if space allows.

Most text content is `.zim` (Kiwix format) and is fetched by `scripts/02-download-content.sh`
from the Kiwix library (`https://library.kiwix.org` / `download.kiwix.org`). Maps and
geo/media are files/tiles fetched separately (URLs in the script comments).

---

## 1. Medical & health

| Content | Source | Size | Priority |
|---------|--------|------|----------|
| **WikiMed** medical encyclopedia (`.zim`) | Kiwix | ~1–2 GB | **[CORE]** |
| MedlinePlus (`.zim`) | Kiwix | ~1 GB | **[CORE]** |
| *Where There Is No Doctor* | Hesperian (PDF, free) | ~50 MB | **[CORE]** |
| *Where There Is No Dentist* | Hesperian (PDF, free) | ~30 MB | **[IMPORTANT]** |
| First aid / CPR / wound care / trauma guides | Curated PDFs | ~200 MB | **[CORE]** |
| WikiProjectMed / Wikipedia Medicine subset | Kiwix | ~2 GB | **[IMPORTANT]** |
| **Holistic / herbal / traditional** (clearly labelled) | Public-domain herbals, curated PDFs | ~500 MB | **[IMPORTANT]** |

> **Safety labelling:** the holistic material is ingested into a separate collection tag so
> Rom can distinguish *clinical evidence* from *traditional practice* and say which is which.
> See `rom/prompts.py`.

## 2. General reference

| Content | Source | Size | Priority |
|---------|--------|------|----------|
| **Wikipedia (English), no images** (`.zim`) | Kiwix | ~50 GB | **[CORE]** |
| Wikipedia (English), **with images** (`.zim`) | Kiwix | ~100 GB | **[IMPORTANT]** |
| Simple English Wikipedia (`.zim`) — lightweight fallback | Kiwix | ~1 GB | **[CORE]** |
| Wiktionary (`.zim`) | Kiwix | ~5 GB | **[NICE]** |
| Project Gutenberg (`.zim`) | Kiwix | ~65 GB | **[NICE]** |
| Stack Exchange (relevant sites) (`.zim`) | Kiwix | varies | **[NICE]** |

## 3. Repair, tools & making

| Content | Source | Size | Priority |
|---------|--------|------|----------|
| **iFixit** repair guides (`.zim`) | Kiwix | ~2 GB | **[CORE]** |
| Appropriate-tech / homesteading manuals | Curated PDFs | ~1 GB | **[IMPORTANT]** |
| Electronics / solar / small-engine references | Curated PDFs | ~1 GB | **[NICE]** |

## 4. Maps & geospatial

| Content | Source | Size | Priority |
|---------|--------|------|----------|
| **OpenStreetMap** offline (region) — tiles/`.mbtiles` or `.zim` | Kiwix / OpenMapTiles | 1–20 GB | **[CORE]** |
| Topographic maps (USGS US Topo / OpenTopoMap tiles) | USGS / OpenTopoMap | region-dependent | **[IMPORTANT]** |
| **FEMA flood zones** (National Flood Hazard Layer) | FEMA (GIS export) | region-dependent | **[IMPORTANT]** |
| **USGS faults & geology** (Quaternary Faults, geologic maps) | USGS | region-dependent | **[IMPORTANT]** |
| Soil / land stability (SoilGrids, USGS landslide susceptibility) | ISRIC / USGS | region-dependent | **[NICE]** |

> Reality note: there is no single tidy "geology + fault + flood" `.zim`. You download the
> specific USGS/FEMA datasets for **your region** as GIS files/tiles and view them in an
> offline map viewer (the media/maps container). Keep it regional to keep it small.

## 5. Communications & radio

| Content | Source | Size | Priority |
|---------|--------|------|----------|
| Ham/GMRS/CB how-to, band plans, frequencies | Curated PDFs | ~300 MB | **[IMPORTANT]** |
| ARRL-style antenna & propagation basics (public/curated) | Curated PDFs | ~200 MB | **[NICE]** |
| **Meshtastic / LoRa** setup & off-grid mesh comms | Curated docs | ~50 MB | **[IMPORTANT]** |
| Winlink / APRS / emergency net procedures | Curated PDFs | ~100 MB | **[NICE]** |

## 6. Survival, skills & training

| Content | Source | Size | Priority |
|---------|--------|------|----------|
| Fire (start/extinguish), shelter, knots, navigation | Curated PDFs | ~500 MB | **[CORE]** |
| **Water** purification & storage; **food** preservation | Curated PDFs | ~500 MB | **[CORE]** |
| Foraging / edible & medicinal plants (region) | Curated PDFs | ~500 MB | **[IMPORTANT]** |
| Sanitation & hygiene (Hesperian *Sanitation & Cleanliness*) | Hesperian PDF | ~50 MB | **[IMPORTANT]** |
| Gardening / seed-saving / animal husbandry | Curated PDFs | ~1 GB | **[NICE]** |
| **Self-defense** for varied situations | Curated PDFs | ~300 MB | **[IMPORTANT]** |

## 7. Defense / tactical / field manuals

| Content | Source | Size | Priority |
|---------|--------|------|----------|
| Public-domain military field manuals (first aid, land nav, field craft) | Curated PDFs | ~2 GB | **[IMPORTANT]** |

> Use publicly releasable / public-domain manuals only; see
> [`04-licensing-and-legal.md`](04-licensing-and-legal.md).

## 8. Media library (the honest "YouTube/Pinterest" substitute)

You **cannot** mirror YouTube or Pinterest wholesale offline. The realistic approach:

- Curate **specific** downloaded how-to videos (knot-tying, CPR, fire-starting, first aid)
  into an **offline media server** (Jellyfin, optional container). Download with `yt-dlp`
  **while online**, organized into folders (`content/media/`).
- Save reference images/infographics as files in the same tree.

| Content | Source | Size | Priority |
|---------|--------|------|----------|
| Curated how-to videos | `yt-dlp` (while online) | you choose | **[NICE]** |
| Jellyfin media server (container) | Docker | app only | **[NICE]** |

See [`05-media-library.md`](05-media-library.md) for the full curation workflow and the
starter category list (tactical, ancient history/tech, minerals, DIY tech builds, gardening,
survival, homestead cooking, kids' shows, and more), and
[`06-radio-comms.md`](06-radio-comms.md) for Meshtastic + RTL-SDR comms hardware.

## 9. Personal & legal (do this, everyone forgets it)

| Content | Priority |
|---------|----------|
| Scans of IDs, passports, insurance, deeds, prescriptions, contacts | **[CORE]** |
| Family medical records, allergy/medication lists | **[CORE]** |
| Emergency plans, meeting points, ICE contacts | **[CORE]** |

> Keep these in an **encrypted** folder (`content/private/`, git-ignored). See the manual.

---

## Suggested Core pack (fits comfortably on 512GB, good on 256GB if you drop full Wikipedia)

WikiMed + MedlinePlus + *Where There Is No Doctor* + first-aid PDFs + Simple English
Wikipedia (and full no-images Wikipedia if space) + iFixit + fire/shelter/water/food
survival PDFs + OSM for your region + personal/legal docs. That single pack already beats a
basic commercial offline library, and Rom can search all of it.
