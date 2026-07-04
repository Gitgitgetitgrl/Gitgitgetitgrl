# 02 — Hardware: Tiers, Bill of Materials & Recommendation

Three tiers, cheapest to most capable. **All three run the identical software stack** in
this repo — they differ in how large a library they hold and how fast/large a model Rom
can run. Prices are rough US street prices (2026) for guidance only.

---

## Tier 1 — Compact / Low-power (Raspberry Pi)

Pocketable, sips power, great as a pure library + light assistant. This is the
PrepperDisk/PrepperPi class.

| Part | Spec | ~Cost |
|------|------|-------|
| SBC | **Raspberry Pi 5, 16GB** | $120 |
| Storage | 1TB NVMe + M.2 HAT (or 512GB high-endurance SD) | $80 |
| Cooling | Active cooler (fan) or aluminium heatsink case | $15 |
| Power | 27W USB-C PD supply + 20,000mAh PD power bank | $50 |
| Case | Rugged enclosure | $25 |
| Wi-Fi | Onboard (AP-capable) | — |
| **Total** | | **~$310** |

- **Library:** comfortably 512GB–1TB of `.zim` content.
- **Rom:** small models only — **Phi-3-mini (3.8B)**, **Gemma 2 2B**, or a quantized
  **Mistral 7B / Llama 3.1 8B** (slow, a few tokens/sec, CPU-only).
- **Power draw:** ~5–10W. ~10–14h on a 72Wh (20,000mAh) bank.
- **Best when:** portability and battery life matter more than AI quality.

---

## Tier 2 — Balanced / Mini-PC ⭐ **RECOMMENDED**

The value sweet spot for prioritizing a genuinely useful Rom. Small, quiet, low-power, but
with real RAM and NVMe throughput.

| Part | Spec | ~Cost |
|------|------|-------|
| Mini-PC | **Intel N100/N305 or AMD Ryzen 7 mini-PC, 32GB RAM** | $350 |
| Storage | 2TB NVMe SSD (fast RAG indexing + big library) | $120 |
| Power | 20,000–27,000mAh USB-C PD bank **or** small DC UPS | $70 |
| Wi-Fi | Onboard AP-capable card (or a USB AP-mode dongle) | $20 |
| Case/cooling | As shipped (fanless N100 options exist) | — |
| **Total** | | **~$560** |

- **Library:** 1–2TB — room for full Wikipedia *with images* plus everything else.
- **Rom:** **Llama 3.1 8B** or **Mistral 7B** quantized run well; **Phi-3-medium (14B)** or
  a quantized **Qwen2.5 14B** are usable. Comfortable, responsive answers.
- **Power draw:** ~12–25W. Runs several hours on a large PD bank; indefinitely on wall/solar.
- **Why recommended:** best answer-quality-per-dollar-per-watt. 32GB RAM is the line above
  which Rom stops feeling cramped, and mini-PCs hit it cheaply while staying portable and
  quiet. This is the tier the repo's defaults target.

---

## Tier 3 — Max capability (Gaming laptop / GPU box)

When Rom is the priority and you want the largest models and fastest responses. A **used**
gaming laptop is the cost-effective way to get a discrete GPU + battery + screen in one unit.

| Part | Spec | ~Cost |
|------|------|-------|
| Laptop | Used gaming laptop, **RTX 4060/4070 (8–12GB VRAM), 32–64GB RAM** | $900–1,400 |
| Storage | 2TB+ NVMe (add a second drive if the bay exists) | $120 |
| Power | Built-in battery + large PD bank / inverter for recharge | $80 |
| **Total** | | **~$1,100–1,600** |

- **Library:** 2TB+ — everything, with images, plus a media library.
- **Rom:** GPU-accelerated. **Llama 3.1 8B/14B** fast; quantized **Qwen2.5 32B** or
  **Llama 3.3 70B** feasible on 12–16GB VRAM + system RAM offload. Near-instant, high-quality.
- **Power draw:** 30–90W under load — the trade-off for capability. Built-in battery + screen
  means it's self-contained even with no other hardware.
- **Best when:** you want the smartest possible offline assistant and can feed it power.

---

## Recommendation

**Build Tier 2 (Balanced mini-PC).** It clears the 32GB-RAM bar that makes Rom genuinely
useful, holds the full library with images, stays low-power and quiet enough to run off a
battery/solar, and costs a fraction of the GPU tier. Start here; if you later decide Rom's
intelligence is the whole point, Tier 3 is a drop-in (same software).

The repo defaults (`.env.example`) are set for Tier 2. To change model per tier, edit
`ROM_MODEL` in `.env`:

| Tier | Suggested `ROM_MODEL` |
|------|-----------------------|
| 1 (Pi) | `phi3:mini` or `gemma2:2b` |
| 2 (mini-PC) ⭐ | `llama3.1:8b` (default) |
| 3 (GPU) | `qwen2.5:14b` or `llama3.1:70b` |

## Accessories worth adding (any tier)

- **Redundant content drive** — a second copy of `content/` on a separate SSD. Data loss is
  the real failure mode.
- **Solar + charge controller** (e.g. 100W panel + PD-capable power station) for indefinite runtime.
- **Fault-tolerant power:** a DC UPS / power station so an unexpected cut doesn't corrupt the SSD.
- **Meshtastic/LoRa node** (~$30) if you want off-grid text comms between locations.
- **RTL-SDR dongle** (~$30) to *receive* radio (NOAA weather, aircraft, ham) — pairs with the
  radio content pack.

---

## Recommended purchases (≤ $1,200 budget, 2026 street prices)

Prices fluctuate — **verify current specs (especially RAM) and price before buying.** Avoid
listings with made-up CPU model numbers (e.g. "Ryzen R2544"), fake resolutions ("1920P"), or
Greek-letter titles ("Windοws") — those are low-quality/misleading listings.

### ⭐ Option A — Best value: mini-PC + big SSD (recommended for off-grid)

A mini-PC is the value sweet spot here: 32GB RAM, **very low power (9–25W)** which is ideal
for running off a battery/solar station, silent, and cheap enough to leave budget for storage
and power.

| Item | Example | ~Cost |
|------|---------|-------|
| Mini-PC, Ryzen 7 8845HS, 32GB DDR5, 1TB SSD | Beelink SER8 / GMKtec K12 / Minisforum UM870 | $640–690 |
| External 2TB USB SSD (full library + media) | any reputable brand | ~$120 |
| Power station / DC UPS (off-grid runtime) | ~$150–250 | |
| **Total** | | **~$900–1,050** |

- Rom: `llama3.1:8b` at ~18–25 tokens/sec on the iGPU; quantized 13B usable. No discrete GPU.
- Upgradeable to 64GB RAM later for bigger models.

**`.env` settings for Option A** (CPU/iGPU, no GPU block):

```ini
ROM_MODEL=llama3.1:8b        # or phi3:mini for snappier, gemma2:2b for lightest
EMBED_MODEL=nomic-embed-text
TOP_K=6
```

Leave the `deploy:` GPU block in `docker-compose.yml` **commented out**.

### Option B — GPU speed: RTX 4060 laptop (Tier 3)

Fastest Rom in budget, plus a built-in screen and battery (self-contained). Costs more and
draws more power; hunt for a **32GB** configuration — many at this price ship only 16GB.

| Item | Example | ~Cost |
|------|---------|-------|
| Laptop, RTX 4060 (8GB VRAM), **32GB RAM**, 1TB | ASUS TUF / Acer Nitro / Lenovo LOQ class | $1,050–1,200 |

- Rom: `qwen2.5:14b` GPU-accelerated; ~40–50 tokens/sec on 7–8B models.

**`.env` settings for Option B** (GPU):

```ini
ROM_MODEL=qwen2.5:14b        # 8GB VRAM sweet spot; llama3.1:8b for more speed
EMBED_MODEL=nomic-embed-text
TOP_K=6
```

And **enable the GPU** in `docker-compose.yml`: uncomment the `deploy: resources: reservations:
devices:` block under the `ollama` service, and run `scripts/00-install-host.sh` so the
NVIDIA Container Toolkit is installed.

> If you buy a 16GB (not 32GB) machine of either type, drop to a smaller model
> (`ROM_MODEL=phi3:mini` or `gemma2:2b`) — see the Tier table above.
