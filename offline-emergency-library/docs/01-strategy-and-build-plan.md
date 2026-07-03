# 01 — Strategy & Build Plan

The goal is a **portable, fully offline knowledge appliance** with a capable AI assistant
("Rom"). The safest way to get there is to build it in **phases**, so you have a working,
useful device early and add capability without ever having a broken system.

## Design principles

1. **Offline-first, always.** Nothing the appliance does at runtime may require the
   internet. Internet is used *only* during one-time content downloads and updates.
2. **Reproducible.** The whole software stack is Docker Compose, so a rebuild is one command.
3. **Layered value.** Even with the AI turned off, the device is a full offline library.
   The AI is additive, not a single point of failure.
4. **Cited answers.** Rom must ground every answer in your library and cite the source, so
   a human can verify it — critical for medical/safety content.
5. **Graceful degradation.** Low battery? Run the library only. No GPU? Run a smaller model.

## Phased plan

### Phase 0 — Prep (½ day)
- Choose a hardware tier (see [`02-hardware-bom-and-tiers.md`](02-hardware-bom-and-tiers.md);
  recommended: **Balanced mini-PC**).
- Install Ubuntu Server 24.04 LTS (or Debian 12).
- Run `scripts/00-install-host.sh` to install Docker + dependencies.
- **Confirm you have internet for Phase 1–2, then you can go dark permanently.**

### Phase 1 — MVP: the offline library (½ day + download time)
- Run `scripts/02-download-content.sh` to fetch a **core content pack** of `.zim` files
  (offline Wikipedia, WikiMed medical encyclopedia, *Where There Is No Doctor*, survival
  manuals, iFixit). Downloads are large — do this on a fast connection.
- `scripts/03-start.sh` brings up **kiwix-serve**.
- **Deliverable:** any browser on the LAN can read the whole library at `:8090`.
  You now have a device equivalent to a basic PrepperDisk/PrepperPi.

### Phase 2 — Rom, the AI assistant (½ day)
- The same `03-start.sh` also starts **Ollama** + **Qdrant** + the **Rom** service.
- Pull a local model (`ollama pull <model>` — chosen automatically per tier by the script).
- `docker compose exec rom python ingest.py` indexes the library into Qdrant.
- **Deliverable:** ask Rom a question at `:8080`; it retrieves from your library, answers,
  and cites sources — with medical-safety labelling built in.

### Phase 3 — Off-grid access & power (½ day)
- `scripts/01-setup-wifi-hotspot.sh` turns the box into a self-contained Wi-Fi access point
  (`ROM-LIBRARY`) using hostapd + dnsmasq, so no router or internet is needed.
- Add power resilience: a UPS or high-capacity power bank (see BOM), and optionally solar.
- **Deliverable:** power the box anywhere, join its Wi-Fi from a phone, use the library + Rom.

### Phase 4 — Expand & harden (ongoing)
- Add more content packs (maps, radio/comms, defense manuals, media) — see
  [`03-content-library-manifest.md`](03-content-library-manifest.md). Re-run `ingest.py`.
- Add offline maps (OpenStreetMap tiles / topo) and a media library (Jellyfin) for
  downloaded how-to videos — the realistic substitute for "YouTube/Pinterest offline."
- Optional: mesh comms integration (Meshtastic/LoRa) so multiple appliances or nodes can
  share status off-grid.
- Make a **golden backup** of the whole `content/` directory and the SD/SSD image.

## What "done" looks like

- [ ] Box boots with no internet and serves the library on its own Wi-Fi.
- [ ] Rom answers questions with citations and medical-safety labelling.
- [ ] Operator manual PDF printed and kept **with** the device.
- [ ] A second copy of the content drive stored separately (redundancy).
- [ ] Power plan tested (how long does it run on the battery you have?).

## Risks & realistic limits (read this)

| Expectation | Reality |
|-------------|---------|
| "Put all of YouTube/Pinterest on it" | Not possible. You curate **specific** downloaded videos into an offline media server (Jellyfin). |
| "Institution-level database on a Raspberry Pi with a great AI" | The library fits, but a *capable* Rom wants 32GB RAM and ideally a GPU. Pi runs small models slowly. |
| "Rom knows everything perfectly" | Rom is only as good as the content you load + the local model. It can be wrong; that's why answers are **cited** — verify anything safety-critical. |
| "Geologic/fault/flood data offline" | Available but piecemeal — you download specific datasets (USGS, FEMA flood, SoilGrids) as files/tiles; there's no single tidy `.zim`. See content manifest. |
