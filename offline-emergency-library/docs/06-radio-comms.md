# 06 — Radio & Off-Grid Comms (Meshtastic + RTL-SDR)

The library tells you *how* to communicate off-grid; this doc adds the **hardware** that lets
the appliance actually **send** (Meshtastic mesh text) and **receive** (RTL-SDR radio) when
there's no internet and no cell service. Both are optional add-ons — the library and Rom work
without them.

> Know your local rules: transmitting on ham bands generally needs a license; GMRS needs a
> (no-exam) license in the US; Meshtastic uses license-free ISM bands. Receiving (RTL-SDR)
> is unlicensed. See the radio content pack in [`03-content-library-manifest.md`](03-content-library-manifest.md).

---

## A. Meshtastic — send/receive text off-grid (transmit)

[Meshtastic](https://meshtastic.org) turns cheap LoRa radios into a long-range, low-power
**mesh text network** — no internet, no cell, no license (ISM band). Messages hop node to
node, so two appliances (or you and a family member) can exchange short messages across
town or between camps.

**Hardware (~$25–40/node):** a LoRa board for your region's frequency — e.g. Heltec V3,
LILYGO T-Beam (has GPS), or a RAK WisBlock. Buy the variant matching your country's band
(US 915 MHz, EU 868 MHz).

**Two ways to use it with the appliance:**

1. **Phone app (simplest):** flash the node with Meshtastic firmware, pair it to a phone over
   Bluetooth, send/receive from the app. The appliance isn't required for this.
2. **Wired to the box (integrated):** plug a node into the appliance over USB so scripts/Rom
   can read and send mesh messages. Use the community
   [`meshtastic`](https://meshtastic.org/docs/software/python/cli/) Python/CLI:

   ```bash
   pip install meshtastic
   meshtastic --port /dev/ttyUSB0 --info                 # confirm the node
   meshtastic --port /dev/ttyUSB0 --sendtext "Camp OK"   # send a message
   ```

   To let the containers reach the USB node, pass the device through in
   `docker-compose.yml` (see the commented `meshtastic`/`devices:` note there).

**Good for:** short check-ins, coordinates, "I'm OK", small-group coordination over miles.
**Not for:** voice, big files, or web.

---

## B. RTL-SDR — receive radio (listen)

An [RTL-SDR](https://www.rtl-sdr.com/about-rtl-sdr/) USB dongle (~$30) turns the appliance
into a wideband **receiver**: NOAA weather radio, ham/GMRS traffic, aircraft (ADS-B), and
more. Receiving is unlicensed. This is your ears when the internet is down.

**Two ways to use it:**

1. **Command-line utilities** (lightweight):
   ```bash
   sudo apt install rtl-sdr
   rtl_test                       # confirm the dongle
   # NOAA weather / FM voice with an SDR app (e.g. gqrx, or rtl_fm piped to audio):
   rtl_fm -f 162.550M -M fm -s 22050 - | aplay -r 22050 -f S16_LE
   ```
2. **OpenWebRX web receiver (nice UI, optional `radio` compose profile):**
   a browser-based SDR you tune from any device on the `ROM-LIBRARY` Wi-Fi:
   ```bash
   docker compose --profile radio up -d openwebrx   # http://10.42.0.1:8073
   ```
   OpenWebRX needs the dongle passed through to the container (device mapping is included,
   commented, in `docker-compose.yml`). First run: set a receiver password when prompted.

**Good for:** weather alerts, listening to emergency/ham nets, ADS-B aircraft, spectrum awareness.
**Note:** RTL-SDR **receives only** — to *transmit* voice you need a licensed transceiver (ham/GMRS radio).

---

## C. Suggested comms kit (any tier)

| Item | Purpose | ~Cost |
|------|---------|-------|
| Meshtastic LoRa node (×2) | Off-grid text between locations | $60 |
| RTL-SDR v4 dongle + antenna | Receive weather/ham/air | $35 |
| Handheld GMRS/ham radio | Two-way voice (licensed) | $30–120 |
| NOAA weather radio (standalone) | Battery-backup weather alerts | $25 |

Pair this with the **radio content pack** so Rom can answer "what frequency is NOAA weather?"
or "how do I program my radio?" from the library while you operate the hardware.
