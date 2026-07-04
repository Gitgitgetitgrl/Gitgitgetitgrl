# ROM — Offline Emergency Resource Library

A fully **offline**, portable knowledge appliance for off-grid and emergency situations.
It serves a large curated library (Wikipedia, medical references, maps, radio/comms
guides, survival manuals, repair guides, and more) over its **own Wi-Fi network** — no
internet required — and answers questions through **Rom**, a local AI assistant that
searches the library and cites its sources.

> Build target in this repo: the **Balanced (mini-PC)** tier. The Compact (Raspberry Pi)
> and Max (gaming laptop / GPU) tiers are documented in [`docs/02-hardware-bom-and-tiers.md`](docs/02-hardware-bom-and-tiers.md)
> and the same software stack runs on all three.

## What this is (architecture at a glance)

```
                      ┌─────────────────────────────────────────────┐
   Phones / laptops   │   The Appliance (mini-PC, no internet)       │
   join its Wi-Fi ───►│                                             │
                      │   hostapd + dnsmasq   → offline Wi-Fi AP     │
                      │   kiwix-serve         → .zim content library │
                      │   ollama              → local LLM ("Rom")    │
                      │   qdrant              → vector DB (RAG)      │
                      │   rom (FastAPI + UI)  → ask questions, cited │
                      └─────────────────────────────────────────────┘
```

- **Content layer:** [Kiwix](https://kiwix.org) serving `.zim` files (the same open format
  used by Internet-in-a-Box and PrepperDisk).
- **AI layer ("Rom"):** [Ollama](https://ollama.com) (local LLM) + [Qdrant](https://qdrant.tech)
  (vector search) in a retrieval-augmented-generation (RAG) pipeline, modelled on the
  open-source *Project NOMAD* approach. Rom **only** answers from your library and
  **cites the source article** for every claim.
- **Access layer:** the box broadcasts its own Wi-Fi; any device with a browser can use it.

## Quick start

```bash
# 1. On the appliance (Ubuntu/Debian), install host dependencies + Docker
sudo ./scripts/00-install-host.sh

# 2. ONE TIME, WHILE YOU STILL HAVE INTERNET: download the content library
./scripts/02-download-content.sh            # interactive; pick a content pack

# 3. Bring the whole stack up (Kiwix + Ollama + Qdrant + Rom)
cp .env.example .env                        # edit if you want different models/ports
./scripts/03-start.sh

# 4. Index the library so Rom can search it (one time, and after adding content)
docker compose exec rom python ingest.py

# 5. Turn the box into an offline Wi-Fi access point (optional but recommended)
sudo ./scripts/01-setup-wifi-hotspot.sh

# 6. (Optional) Curate an offline media library of videos/infographics, then serve it
cp content/media/playlist.example.txt content/media/playlist.txt   # edit categories
./scripts/05-download-media.sh                                     # while online
docker compose --profile media up -d jellyfin
```

Then from any device, join the `ROM-LIBRARY` Wi-Fi and open:

| Service            | URL                              |
|--------------------|----------------------------------|
| **Rom assistant**  | `http://10.42.0.1:8080/`         |
| Kiwix library      | `http://10.42.0.1:8090/`         |
| Media (Jellyfin)   | `http://10.42.0.1:8096/` *(optional `--profile media`)* |
| SDR radio (OpenWebRX) | `http://10.42.0.1:8073/` *(optional `--profile radio`)* |
| (via Ethernet/dev) | `http://<box-ip>:8080` / `:8090` |

## Documentation

| Doc | Contents |
|-----|----------|
| [`docs/01-strategy-and-build-plan.md`](docs/01-strategy-and-build-plan.md) | Phased strategy: MVP → AI → expanded content |
| [`docs/02-hardware-bom-and-tiers.md`](docs/02-hardware-bom-and-tiers.md)   | 3 hardware tiers, full bill of materials, recommendation |
| [`docs/03-content-library-manifest.md`](docs/03-content-library-manifest.md) | Prioritized content, sources, sizes |
| [`docs/04-licensing-and-legal.md`](docs/04-licensing-and-legal.md)         | Redistribution / licensing notes |
| [`docs/05-media-library.md`](docs/05-media-library.md)                     | Offline video/image library (Jellyfin + yt-dlp/gallery-dl) |
| [`docs/06-radio-comms.md`](docs/06-radio-comms.md)                         | Off-grid comms: Meshtastic (send) + RTL-SDR (receive) |
| [`docs/operation-manual.md`](docs/operation-manual.md)                     | Non-technical operator manual (also built to PDF) |
| [`CONTRIBUTING.md`](CONTRIBUTING.md)                                       | Contributor setup + change checklist |
| [`SECURITY.md`](SECURITY.md)                                               | Threat model + offline-device hardening checklist |

Build the PDF manual:

```bash
./scripts/04-build-manual-pdf.sh    # -> docs/ROM-Operation-Manual.pdf
```

## ⚠️ Safety

Rom labels medical information as **clinical evidence** vs. **traditional/holistic
practice**, and is instructed to tell you when a situation is beyond self-care and needs
a professional or emergency responder. It is a reference aid, **not** a substitute for a
trained clinician. See the disclaimer in [`docs/operation-manual.md`](docs/operation-manual.md).

## License

The **code, scripts, and documentation in this repository** are licensed under the
[Apache License 2.0](LICENSE) (see also [`NOTICE`](NOTICE)). Apache-2.0 is permissive like
MIT but adds an explicit patent grant and patent-retaliation protection.

This does **not** cover the third-party **content you download** at build time (Wikipedia,
`.zim` libraries, PDFs, models, media, etc.) — each of those keeps its own license, and you
must respect it, especially if you redistribute a built device. See
[`docs/04-licensing-and-legal.md`](docs/04-licensing-and-legal.md).
