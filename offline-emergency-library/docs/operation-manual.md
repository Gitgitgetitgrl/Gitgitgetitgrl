# ROM — Operation Manual

**Your offline emergency knowledge appliance**

This manual is written for anyone — no technical background needed. Keep a **printed copy
with the device**. If the screen and network work but you forget everything else, the two
things to remember are: **(1) power it on, (2) join its Wi-Fi and open the page.**

---

## 1. What this device is

ROM is a small computer that holds a huge offline library — medical guides, survival and
repair manuals, maps, radio instructions, and an encyclopedia — and an assistant named
**Rom** that answers your questions and shows you which document the answer came from.

**It needs no internet.** It makes its own Wi-Fi network. Any phone, tablet, or laptop can
connect and use it.

---

## 2. Turn it on

1. Connect power (wall outlet, power bank, or solar station).
2. Press the power button. Wait about **1–2 minutes** for it to start.
3. A steady light means it's ready. (On the mini-PC/laptop, the screen will show a login or
   a ready message — you do **not** need to log in to use the library from another device.)

---

## 3. Connect a phone or laptop to it

1. On your phone, open **Wi-Fi settings**.
2. Join the network named **`ROM-LIBRARY`**.
   - Password: the one you set (default `emergency-library` — **change it**, see §8).
3. Open any web browser and go to:

   > **http://10.42.0.1:8080**

   (You can also try **http://rom.library:8080**.)

4. You'll see the **Rom** chat screen. That's it — you're in.

To browse the raw library instead of asking Rom, go to **http://10.42.0.1:8090**.

---

## 4. Ask Rom a question

- Type a normal question, like *"How do I treat a burn?"* or *"How do I make water safe to
  drink?"*, and press **Ask**.
- Rom answers **from your library** and lists its **sources** underneath. Tap a source to
  open the full original document.
- Green-tagged sources are **clinical / evidence-based**; orange-tagged sources are
  **traditional / holistic** (not clinically proven). Rom keeps them separate on purpose.

**If Rom doesn't know**, it will say so rather than make something up. That's by design.

---

## 5. ⚠️ Health & safety — read this

- Rom is a **reference tool, not a doctor**. In a serious situation it will tell you to seek
  a professional or emergency responder — **do that whenever possible.**
- Watch for the **"⚠️ Get professional help if…"** notes Rom adds to medical answers. Those
  list the danger signs that mean *stop self-treating and get real help.*
- Never take a medication dose from memory or guesswork. If Rom cites a dose, **open the
  cited source and confirm it.**
- Traditional/holistic remedies are included for completeness. They are **not** a substitute
  for evidence-based care when care is available.

---

## 6. Power & battery

- The device uses roughly **5–90 watts** depending on your model (a Raspberry Pi sips power;
  a gaming-laptop build with the GPU busy uses the most, especially while Rom is "thinking").
- On a large USB-C power bank or power station it will run for **hours**; on wall power or
  solar, indefinitely.
- To save power: use the **library** (§3, port 8090) instead of asking Rom — browsing uses
  far less energy than the AI.
- **Shut down cleanly** when you can (don't just yank power): on the mini-PC/laptop choose
  Shut Down; on a Pi, hold the power button or run `sudo shutdown now`. This protects the
  storage.

---

## 7. Updating or adding content (needs internet, one time)

Do this **while you still have internet**, before you need the device off-grid.

1. Add more libraries: `./scripts/02-download-content.sh` and pick a pack.
2. Add your own PDFs (guides, manuals, **your personal/legal documents**): copy them into the
   `content/` folder.
3. Re-index so Rom can find the new material:
   `docker compose exec rom python ingest.py`

Keep a **second copy** of the `content/` folder on another drive. Losing the storage is the
most likely way to lose everything — a backup fixes that.

---

## 8. Change the Wi-Fi password (do this once)

The default password is weak on purpose so you can get started. To set your own:

```
sudo ROM_WIFI_PASS='your-strong-password' ./scripts/01-setup-wifi-hotspot.sh
```

---

## 9. Quick troubleshooting

| Problem | Try this |
|---------|----------|
| Can't find the `ROM-LIBRARY` Wi-Fi | Wait 2 min after power-on; make sure the device is on; re-run the hotspot script. |
| Joined Wi-Fi but the page won't load | Confirm the address **http://10.42.0.1:8080** (http, not https). Turn phone mobile-data off. |
| Rom says the library isn't indexed | Run `docker compose exec rom python ingest.py`. |
| Rom is very slow | Normal on small devices. Use a smaller model (`ROM_MODEL` in `.env`) or just browse the library at :8090. |
| Rom gives a weird/blank answer | Make sure the model was pulled: `docker compose exec ollama ollama list`. Re-run `./scripts/03-start.sh`. |
| Check overall health | Open **http://10.42.0.1:8080/health** — it lists what's working. |

---

## 10. One-page emergency cheat sheet

1. **Power on.** Wait ~2 minutes.
2. Phone → **Wi-Fi** → join **`ROM-LIBRARY`**.
3. Browser → **http://10.42.0.1:8080**
4. **Ask Rom** your question. Check the **sources**. Heed the **⚠️ warnings**.
5. For less battery use, browse the library at **http://10.42.0.1:8090**.
6. Serious injury/illness and help is reachable? **Get professional help.**

---

*Rom is a reference tool, not a substitute for a trained professional. Verify anything
safety-critical against the cited source.*
