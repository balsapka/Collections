# GRR persona deck (UC2)

Source of the artifact deck https://claude.ai/artifact/2NjxvqhabYHBPEYsxhNPe8 (v88, 2026-11-13); `grr_persona_deck.pdf` is the printed copy (speaker notes left out).

- `project/deck.json` — slide order and metadata; `project/slides/*.html` — one file per slide (speaker notes in `<aside>`).
- `tools/` — the one-off scripts that generated or edited slides; kept for reference, the slide HTML is the source of truth.
- Numbers come from the UAT Sonnet handoffs in `workplace_mirror/bundle_helpers/persona_deck/`.

`grr_persona_deck.pptx` is an editable PowerPoint copy (native text boxes and shapes, speaker notes), built from the rendered slides with `tools/extract.js` + `tools/build_pptx.py`; it uses Plus Jakarta Sans (Regular / Medium / SemiBold / Bold) installed on the machine that opens it.
