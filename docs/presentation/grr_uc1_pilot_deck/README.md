# GRR deck: UC1 integration and pilot selection (27 Nov 2026)

Source of the artifact deck https://claude.ai/artifact/DY5FLA436G3EqPKUXFmVLE (12 slides). It continues from Part 2 of `../grr_persona_deck/` (slides 2–3 reuse its slides 14–15; slide 2's UC1 tile now reads "beside the persona").

- `project/deck.json`, `project/deck.css`, `project/slides/*.html`: the slides (speaker notes in `<aside>`).
- `grr_uc1_pilot_deck.pdf`: printed copy (no notes). `grr_uc1_pilot_deck.pptx`: editable copy with notes; needs Plus Jakarta Sans on the machine that opens it.
- Content sources: the collector card doc https://claude.ai/artifact/G7azKojwrzePgVCELYbue8 and `docs/context/results/uc1_latest_findings_brief.md` (UC1 figures on the August refresh; not the workshop doc's older figures). Headless Chrome may hang on the screenshot: add `--disable-gpu --user-data-dir=<scratch>/prof`. If later slides come out grey (the 21,600 px screenshot is too tall), take two 1920×6480 screenshots of copies of `page.html` that hide slides 7–12 / 1–6 (`body>section:nth-of-type(n+7){display:none !important}`, then `(-n+6)`), with `--run-all-compositor-stages-before-draw`, and wait for Chrome to exit.

Rebuild the PDF and pptx after editing a slide (headless Chrome):

```bash
cd <scratch dir> && python <deck>/tools/build_page.py <deck> <deck>/tools/extract.js
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars --force-device-scale-factor=2 --window-size=1920,10800 --virtual-time-budget=6000 --screenshot=all.png file://$PWD/page.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --window-size=1920,10800 --virtual-time-budget=8000 --dump-dom file://$PWD/page_extract.html > dom.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --virtual-time-budget=6000 --no-pdf-header-footer --print-to-pdf=<deck>/grr_uc1_pilot_deck.pdf file://$PWD/page.html
```

Then split `all.png` into `s01.png…` (3840×2160 each), take the JSON in `<pre id="out">` of `dom.html` as `layout.json`, and run `python <deck>/tools/build_pptx.py <deck>/grr_uc1_pilot_deck.pptx layout.json <deck>/project .`.
