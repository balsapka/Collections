# GRR persona deck — storyboard and integration brief

Draft deck (22 slides, content + design): https://claude.ai/artifact/2NjxvqhabYHBPEYsxhNPe8
(downloadable as .pptx / PDF). This file is the brief for re-skinning it into the internal
template and the map of every number to its source.

## Audience and goal

Head of GRR and senior management. Goal: adopt the persona framework as a monthly strategy
input, approve two treatment tests, and deliver the bureau salary feed. Main deck ~15 minutes
(slides 1–17), appendix for the detailed discussion.

Storyline (situation → complication → idea → evidence → so-what → ask):
1. The bucket says how late, not who (problem).
2. Four questions a collector asks = four axes (idea).
3. Each axis works where it has evidence (axis slides with PROD numbers).
4. Combined: ability × credibility = persona (what to offer), locatability = contact route
   (how to reach), deterioration = journey group (why they are here).
5. Proof: within one DPD band personas still separate outcomes (back-test).
6. What the book tells strategy now; what to expect; three decisions.

## Design (replace with the internal template's tokens)

| Role | Draft value | Use |
|---|---|---|
| Dark | `#14213D` navy | headings, divider / closing backgrounds |
| Light | `#F6F5F0` | content backgrounds |
| Accent 1 | `#1F6FB2` blue | customer situation axes (A1, A2), eyebrows, positive bars |
| Accent 2 | `#C46A12` orange (fill tint `#E8A85C`) | behaviour axes (A3, A4) |
| Muted | `#4A5568` body, `#5A6578` footers, `#8FA3BC` "unknown" bars | |
| Type | Space Grotesk (headings), Inter (text) | scale 112 / 64–56 / 40–34 / 30–26 / 24 px on 1920×1080 |

Layout rules: eyebrow (axis / section) + one-sentence headline that states the finding; one
idea per slide; a takeaway bar at the bottom of each axis slide; a source footer on every
data slide. Blue = situation, orange = behaviour is the only colour coding; keep it.

## Slides

Status: **PROD** = number from a production run (source given); **PENDING** = placeholder
`[__]` filled from `tmp_validation/persona_deck/results_<model_id>.md` (snippet in
`workplace_mirror/bundle_helpers/b21_persona/`), table named.

| # | Id | Headline | Numbers | Status / source |
|---|---|---|---|---|
| 1 | cover | Who are we collecting from? | — | presenter, date |
| 2 | exec | The bucket says how late. Personas say who, and what to do. | 2 in 3 gone dark, 44% abroad, 15% capacity (CC 61–180) | PROD A2/A1 workbooks, 31 Aug 2026 |
| 3 | problem | Late buckets run dry, and the score re-reads the bucket | 87% CC 180+ A1 Unknown (278,654 / 318,663) | PROD A1 workbook |
| 4 | questions | Four questions a good collector asks | — | |
| 5 | principles | Built to be trusted, explained and acted on | — | |
| 6 | div-axes | Part 1 | — | |
| 7 | a2 | Two in three card customers no longer answer, and 44% look abroad | location 24/44/32%, reach 21/68/11%; RL Skip 43%, NR 58%; Skip×NR 6,114; Reachable 4,447 → 4,043 Jan→Aug | PROD A2 workbook (Results, trend) |
| 8 | a1 | Where we can see capacity, it predicts cure four times over | cure_3 33.6/16.3/12.1/7.9%; mix 0.2/14.4/28.9/56.6% | cure: `a1_final/payment_cure_results.md` (earlier rule version, High = 161); mix: A1 workbook |
| 9 | a3 | Each point of credibility cuts the roll rate | roll by points 95.0/90.6/73.8/62.9/33.5%; High/Mod CC 2.3/15.6, RL 2.2/22.1; AUC 0.714; Thin 81.8% | `a3_final/v1g_summary_60_180.md` (G = GRR deadline = bundle 20; roll by points = bundle 17 baseline) |
| 10 | a4 | Half of delinquent loans rolled straight to 61+ DPD | RL 61–180 shares (3,985); **CC column PENDING** | RL: A4 workbook; CC: `S1_a4` (cc_60_180) |
| 11 | div-combined | From four axes to one persona | — | |
| 12 | grid | Ability × credibility: nine personas | **PENDING** share + exposure per cell | `S1_persona_segment` (accounts share, exposure_aed) |
| 13 | playbook | Treatment hypotheses for GRR to test | — | proposal, GRR decides |
| 14 | proof | Same bucket, different outcomes | **PENDING** paid_any by segment at 91–120; AUC band vs band+segment | `S3_segment_x_band` (dpd_band `091-120`, `paid_any_pct`); `S3_auc` (`cured_band_only`, `cured_band_plus_segment`) |
| 15 | book | Four things the August book is telling us | 68%, 16,564 (6+ call days), 44%, 57%, 82% | PROD A2/A1 workbooks; 82% V1g Q4 |
| 16 | expect | What the framework can and cannot do today | 87.4% / 89.5% 180+ Unknown | PROD A1 workbook |
| 17 | roadmap | Three decisions for GRR | dates `[__]` | agree with the user |
| 18–22 | appendix | signals, rules, A4 tree, governance | — | specs |

After the snippet runs, also consider: a headline cross-axis number on slide 2 (e.g. share of
exposure in "able, not paying"), segment × contact route on slide 12, and the 180+ story
(vintage split) as a backup slide.

## Open decisions (user)

1. Persona rules in `crx_persona/persona_master/constants.py`: bands (High+Moderate = able /
   credible), the nine segment names, contact route order (Skip before Non-Reachable), journey
   groups (EPD + early-life = never settled; seasoned straight roller = sudden stop; slow roller
   + stabilized = partial payer).
2. Exposure: CC `stmt_balance`, RL `outstanding_balance`, snapshot in the observation month.
3. Which treatment tests to propose (slide 17 names skip tracing for gone dark, plans for paying
   while stretched).
4. Whether the axis-level validation from earlier rule versions (A1 cure, A3 roll by points) can
   be shown, or waits for the persona back-test.
