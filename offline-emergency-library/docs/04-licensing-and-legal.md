# 04 — Licensing & Legal Notes

You are assembling a redistributable bundle of third-party content. For **personal/family
offline use** this is almost always fine; if you plan to **give or sell** copies (as
PrepperDisk does commercially), you must respect each source's license. This is guidance,
not legal advice.

## Quick reference

| Content | License / status | Redistribute? |
|---------|------------------|---------------|
| **Wikipedia / Wiktionary** `.zim` | CC BY-SA 4.0 | ✅ Yes, with attribution + share-alike |
| **Kiwix** software & most `.zim` | GPL / content varies | ✅ Yes (check per-`.zim` "About") |
| **iFixit** guides `.zim` | CC BY-NC-SA | ✅ Non-commercial only |
| **Hesperian** (*Where There Is No Doctor*, etc.) | Free for nonprofit/education; some CC | ✅ Personal/education; check for commercial |
| **Project Gutenberg** | Public domain (US) | ✅ Yes (respect the PG trademark rules) |
| **OpenStreetMap** | ODbL | ✅ Yes, with attribution + share-alike |
| **USGS / FEMA / MedlinePlus** (US gov) | Public domain (US works) | ✅ Yes |
| **US military field manuals** | Public domain if publicly released; **some are restricted** | ⚠️ Use only publicly releasable/PD manuals |
| **YouTube videos** (`yt-dlp`) | Copyrighted by uploader | ⚠️ Personal use; **do not redistribute** without permission |
| **Pinterest images** | Copyrighted by owners | ⚠️ Personal reference only |
| **Ollama models** (Llama, Mistral, Qwen, Phi, Gemma) | Per-model (Llama Community, Apache-2.0, Gemma terms, MIT…) | ⚠️ Check each model's license before distributing |

## Rules of thumb

1. **Attribution + share-alike** (CC BY-SA, ODbL): keep the source's attribution; if you
   redistribute, license your additions compatibly. Kiwix `.zim` files carry their own
   attribution in the "About" page — don't strip it.
2. **Non-commercial** (CC BY-NC-SA, e.g. iFixit): fine to share, **not** to sell. If you sell
   a device, exclude NC content or get permission.
3. **Personal-use-only** (YouTube, Pinterest, most restricted manuals): keep them on *your*
   device for *your* use; don't hand out copies.
4. **Model licenses matter if you ship the box.** Llama has a community license with an
   acceptable-use policy and a large-user threshold; Apache-2.0 (Mistral, Qwen) and MIT (Phi)
   are permissive; Gemma has its own terms. Read the one you pick.
5. **Medical/holistic content is reference, not practice authority.** Redistributing it
   doesn't transfer any warranty. Keep the disclaimer (see the operation manual) attached.

## What this repo does

- The repo contains **no** third-party content — only code, scripts, and docs. Content is
  downloaded by you at build time from the official sources, so the licenses stay attached to
  the originals.
- `content/` is git-ignored (except `.gitkeep`) precisely so you don't accidentally commit or
  redistribute licensed material.

**If in doubt, keep it personal-use and don't sell copies.** That keeps you clear of nearly
every restriction above.
