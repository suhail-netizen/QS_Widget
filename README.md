# Athan Countdown Widget

A small on-screen overlay for **Quran TV** (Masjid al-Haram, Makkah) and **Sunnah TV**
(Masjid an-Nabawi, Madinah) that shows the time remaining to the next prayer, and
the prayer's clock time, right next to each channel's own on-screen clock.

Two self-contained files, no build step, no server required:

| File | Channel | Mosque |
|---|---|---|
| `Quran_TV.html` | القرآن الكريم | Masjid al-Haram, Makkah |
| `Sunnah_TV.html` | السنة النبوية | Masjid an-Nabawi, Madinah |

## What it looks like

A small badge sits just to the left of the channel's own clock, shaped and sized
to match it (traced directly from a recorded broadcast frame), so it reads as
part of the same on-screen graphic rather than a separate overlay.

It alternates every **10 seconds** between two scenes:

1. **متبقي من الوقت لأذان** — prayer name + countdown remaining (e.g. `العصر 00:34`)
2. **وقت أذان** — prayer name + the prayer's actual clock time (e.g. `العصر 15:41`)

From each athan until **30 minutes after it**, the badge stops alternating and
shows only **وقت صلاة** with the prayer name below it (e.g. `وقت صلاة / الظهر`),
with no time. After 30 minutes it returns to the two scenes above, counting down
to the following prayer. The window length is `PRAYER_WINDOW_MS` in each file.

On Fridays, the Dhuhr slot automatically relabels itself **الجمعة** (Jumu'ah),
since Jumu'ah replaces Dhuhr at the same calculated time rather than having its
own separate time.

### Alternative layout: horizontal strip

`Quran_TV_bar.html` and `Sunnah_TV_bar.html` are the same widget with a
different layout: a single horizontal line placed directly below the channel's
lower-middle box (same width as that box, ~26px tall at 1080p) instead of the
badge beside the clock. Same logic, same data files, same scenes — only the
CSS layout differs. Read right to left: label, prayer name, time
(e.g. `متبقي من الوقت لأذان  العصر  00:34`). The main badge versions are
unchanged; use whichever layout suits the channel.

## How it works

- **No live internet calls at broadcast time.** Prayer times are pre-fetched and
  bundled as local JSON files (`makkah_1448.json`, `makkah_1449.json`,
  `madinah_1448.json`, `madinah_1449.json`) covering Hijri 1448–1449
  (2026-06-16 → 2028-05-24). Each widget loads only its own city's two JSON
  files, via a normal same-origin `fetch()` — nothing reaches an external
  domain. This matters for broadcast environments that won't run a script
  phoning out to a public API.
- **Calculation method:** Umm Al-Qura University, Makkah (method 4 in the
  [Aladhan API](https://aladhan.com/prayer-times-api)) — the standard Saudi
  calculation, same one used to derive the times baked into the JSON files.
- **Timezone:** Saudi Arabia is a fixed UTC+3 with no daylight saving, so the
  script computes "Riyadh wall-clock" directly from UTC rather than relying on
  the browser's local timezone (safe to run anywhere, including outside Saudi
  Arabia).
- **Rollover:** at local midnight the widget automatically switches to the next
  day's data; after Isha it counts down to tomorrow's Fajr.
- Everything (styling, logic, data lookup) is inline in each `.html` file —
  just open it in a browser or point an OBS/vMix Browser Source at it.

## Using it in OBS / vMix / any browser-source-capable software

1. Add a **Browser Source**.
2. Point it at the local file path, or host the two `.html` + `.json` files
   together (same folder) on any web server / GitHub Pages, and use that URL.
3. Set the source size to your canvas resolution — the layout is calibrated
   for **1920×1080**.
4. Leave the background transparent — the page has no background of its own,
   so it composites directly over your video feed.
5. Make sure "Shutdown source when not visible" is **unchecked**, so the clock
   keeps ticking accurately even when the scene isn't live on preview.

The **4 JSON files must sit in the same folder** as the `.html` files they
belong to (`Quran_TV.html` needs `makkah_1448.json` + `makkah_1449.json`;
`Sunnah_TV.html` needs `madinah_1448.json` + `madinah_1449.json`) — the widget
fetches them by relative filename.

## Updating the prayer-time data (once Hijri 1449 runs out, ~May 2028)

Re-run the included Python script with internet access (this is the only
part of the whole project that needs internet — do it once, offline from the
broadcast machine, then copy the resulting files over):

```bash
pip install requests
python fetch_prayer_times.py 1450 1451
```

This regenerates `makkah_1450.json`, `makkah_1451.json`, `madinah_1450.json`,
`madinah_1451.json`. Then, in both `.html` files, update the `DATA_FILES`
list near the top of the `<script>` block to point at the new filenames, e.g.:

```js
const DATA_FILES = ['makkah_1450.json', 'makkah_1451.json'];
```

## Customizing

Everything is plain HTML/CSS/JS, no dependencies beyond a Google Fonts import
(Tajawal) — search each file for these if you want to adjust them:

- **Position / size / shape** — `.clock-widget` (CSS `clip-path` defines the
  badge's cut-corner shape; `right` / `bottom` / `width` / `height` position it).
- **Text** — the two scene strings ("متبقي من الوقت لأذان" / "وقت أذان") and the
  `PRAYER_NAMES` map, inside the `<script>` block.
- **Timing** — the `10000` (ms) interval near the bottom of the script controls
  how often the two scenes alternate.

## License

Free to use, modify, or integrate into your own systems, with no restriction
and no cost.
