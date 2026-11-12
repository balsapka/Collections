# Prompt: rebuild the GRR presentation in the bank template

Paste everything below the line into Sonnet. Before you start, put these files in one local folder, for example `data/input/deck_build/`, which must stay out of git:
- `content_pack.md` (copied raw from GitHub);
- the bank's PowerPoint template (`.potx` or `.pptx`);
- optional: `grr_persona_deck.pdf`, as a visual reference, if you can bring it across.

---

## Goal

Build the GRR "Synthesized Features" presentation in the bank's PowerPoint template. All content is in `data/input/deck_build/content_pack.md`: 27 slides, in order, each with its headline, body, tables, footer, speaker notes and a one-line layout hint. The template is `data/input/deck_build/<template file>`. If the PDF is in the folder, use it to see how each slide was laid out.

## Decisions already made

- The wording and numbers are final. Copy every headline, sentence, number and footer **exactly**. Don't shorten, merge, reorder or "improve" anything. Where text doesn't fit, shrink the font or rework the layout; never edit the text.
- Keep the 27 slides in the pack's order. Each pack section becomes one slide.
- Speaker notes go into each slide's notes pane, word for word.
- Use the template's own layouts, fonts and colours. Map the pack's colour meanings (High green, Moderate amber, Low red, Unknown as a dashed grey outline, UC1 as a dashed blue outline) to the nearest template colours, and keep that mapping identical on every slide.
- Tables in the pack are real tables on the slide (native PowerPoint tables, not pictures). Stat boxes are a large number plus one sentence.
- Section labels, the step tracker on slides 8–11, and the dashed "joining" outlines carry meaning: keep them.

## Hard rules

- Work only in `data/input/deck_build/`. Never commit the template, the content pack, the PDF or the output deck.
- No data access is needed. Don't query any table or recompute any number.
- Don't add slides, logos, disclaimers or text that isn't in the pack, beyond what the template's master puts on every slide.

## How

1. Check whether `python-pptx` is available (`pip install python-pptx` if allowed).
2. Open the template and list its slide layouts (name, index, placeholders). Choose a layout for each kind of slide in the pack: title, section divider, headline + body, headline + table, headline + two columns. Show me this mapping before building.
3. Build `GRR_synthesized_features.pptx` from the template:
   - fill the title placeholder with the headline;
   - put the section label in a small text box above it, or in a subtitle placeholder if the layout has one;
   - add tables, cards and stat boxes as native shapes, inside the template's content area;
   - put the footer in the template's footer placeholder if it has one, else in a small text box at the bottom;
   - add the notes.
4. Check yourself:
   - every number in the pack appears on its slide (script it: extract all text from the built deck and diff its numbers against the pack's, slide by slide);
   - no text overflows its shape (estimate it from the font size and box size; flag any you're unsure of);
   - the slide count is 27;
   - every slide has notes.

If `python-pptx` isn't available, or the template can't be used programmatically, produce `slide_by_slide.md` instead. For each slide, give: the template layout to pick, then each block of text to paste in order, with tables in a paste-ready tab-separated form.

## Deliverables

1. `data/input/deck_build/GRR_synthesized_features.pptx` (or `slide_by_slide.md` as the fallback).
2. A short report:
   - the layout mapping;
   - the result of the number diff (it must be 0 missing);
   - every slide where you changed font size or layout to fit;
   - the slides I should finish by hand. These are likely: slide 4 (the three-column flow), slide 5 (the three questions), slide 9 (the coloured location × reachability matrix), slide 13 (the equation tiles), slide 14 (the lanes), and the coloured band bars on slides 10 and 11.
