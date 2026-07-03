# Security & Threat Model — ROM Offline Library

This appliance is unusual: it's **offline by design**, so the classic "someone hacks it over
the internet" risk mostly doesn't apply. The real risks are **physical** (the box is lost or
stolen with your data on it), **local-network** (anyone in Wi-Fi range), and **trust in the
answers** (Rom is a reference, not an authority). This document is the threat model plus a
hardening checklist. It is not a formal audit.

## What this device is / isn't, security-wise

- **No inbound internet.** At runtime nothing listens on the internet; the only network is the
  box's own local Wi-Fi. That removes most remote-attacker scenarios.
- **It is a data cache, not a vault.** It holds a library and possibly your personal/legal
  documents. Treat the storage drive as sensitive.
- **Rom can be wrong.** Answers are grounded and cited so a human can verify — but a local LLM
  can still misread a source. Never treat safety-critical output as authoritative without
  checking the cited document.

---

## Threat model (what we defend against, and how)

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|------------|
| **Device lost/stolen** with data on it | Medium | High | Full-disk encryption (LUKS); keep `content/private/` encrypted; don't store passwords in plaintext |
| **Anyone in Wi-Fi range joins the AP** | High (shared use) | Medium | Strong WPA2 passphrase (change the default!); treat the AP as a shared read-only kiosk |
| **A joined client attacks the services** | Low–Medium | Medium | Services are read-mostly; keep images updated; don't expose admin panels with default creds |
| **Malicious content in a downloaded pack** | Low | Medium | Download `.zim`/models from official mirrors only; content is served, not executed |
| **Bad/hallucinated answer trusted blindly** | Medium | High (medical) | Citations + clinical-vs-holistic labels + "seek a professional" prompts; operator training |
| **Supply-chain (tampered image/model)** | Low | Medium | Pin/verify images where practical; pull from official registries; keep an offline golden backup |
| **Data loss (drive failure/corruption)** | Medium | High | Redundant copy of `content/`; clean shutdowns; UPS/power station |
| **Power interruption corrupts storage** | Medium | Medium | Battery/UPS; shut down cleanly; journaling filesystem |

Out of scope: nation-state adversaries, RF/side-channel attacks, and anything requiring
physical possession you've already lost (encryption is the backstop there).

---

## Hardening checklist

### Must do (before real off-grid use)
- [ ] **Change the Wi-Fi password** from the default:
      `sudo ROM_WIFI_PASS='your-strong-passphrase' ./scripts/01-setup-wifi-hotspot.sh`
      (12+ chars; this is the single most important step.)
- [ ] **Encrypt the disk.** Install the OS with full-disk encryption (LUKS), or at minimum keep
      an encrypted container for private data (below). A lost unencrypted box = your documents
      in a stranger's hands.
- [ ] **Encrypt `content/private/`** (IDs, records, contacts):
      ```bash
      # one-time: make a 1 GB encrypted vault
      sudo cryptsetup luksFormat content/private.img
      sudo cryptsetup open content/private.img romprivate
      sudo mkfs.ext4 /dev/mapper/romprivate
      # mount to content/private when you need it; keep it closed otherwise
      ```
      `content/private/**` is already git-ignored so it can never be committed.
- [ ] **Set a strong OS login** and disable auto-login on the box.
- [ ] **Make a golden backup** of `content/` on a separate drive, stored elsewhere.

### Should do
- [ ] Keep container images current *while online*: `docker compose pull && ./scripts/03-start.sh`.
- [ ] Don't expose optional admin UIs with default creds — set a real password on **Jellyfin**
      and **OpenWebRX** on first run; only start them when needed (`--profile media`/`radio`).
- [ ] Change the default AP subnet/SSID if you run more than one box near each other.
- [ ] Disable SSH password auth (use keys) if you enable remote admin at all.
- [ ] Verify downloads come from official sources (kiwix.org mirror, ollama.com, vendor sites).

### Operational (people, not tech)
- [ ] Train every operator on the **⚠️ safety rules**: check Rom's citations, heed the
      "get professional help if…" flags, and never guess medication doses (see the manual).
- [ ] Decide who gets the Wi-Fi password; rotate it if the group changes.
- [ ] Keep the printed operator manual **with** the device, but not the passwords.

---

## AI-specific safety notes

- **Grounding is a safety control, not a nicety.** Rom answers only from the provided sources
  and cites them so a human can verify. Changes that let Rom answer from "general knowledge"
  without sources weaken this — don't remove the citation path (`rom/app.py`, `rom/prompts.py`).
- **Medical labelling is load-bearing.** Clinical vs. traditional/holistic separation and the
  escalation prompts exist so a scared person at 3 a.m. doesn't act on folk remedy as if it
  were clinical fact. Preserve it.
- **Prompt-injection via content:** a malicious document *could* contain text trying to
  redirect Rom. Impact is low (Rom has no tools/network to abuse and can't act on the host),
  but prefer content from reputable sources, and don't wire Rom up to execute anything.

---

## Reporting a problem

This is a personal/community build with no formal security team. If you find a real issue,
open an issue or PR describing it and the fix. For anything involving personal data exposure,
prefer a private channel with the device owner over a public issue.

*Reminder: ROM is a reference tool, not a substitute for a trained professional. Verify
anything safety-critical against the cited source.*
