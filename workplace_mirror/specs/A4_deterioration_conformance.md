# A4 — Deterioration: workplace code vs `METHODOLOGY.md`

Spec: `docs/deterioration_states/METHODOLOGY.md` (and the reference engine
`docs/deterioration_states/spark/crx_persona/_dpd_journey.py`).
Code: `workplace_mirror/src/enbd_collections/pipelines/crx_persona/_dpd_journey/`.
Checked 2026-10-23.

## How it was checked

Both engines were run on ~103,000 random DPD histories (CC scale, with and without the
cropped flag). **Every feature is identical** (`journey_features`: glitch fix, +2 jump
repair, spells, blips, run-up, pay events, last-6 band, …). State differences: 12,007, all
of one kind (D1 below). Thresholds in `STATE_RULES` are identical.

## Differences (all deliberate in the code comments; the methodology was not updated)

| # | Methodology | Workplace code | Effect |
|---|---|---|---|
| D1 | **Q0:** any history whose oldest observed month is at bucket 2+ → stabilized if Q2, else unknown | Q0 fires only when the start is also **not observed** (`history_blind` = cropped by the window / floor / an unresolvable gap, or a restructured account). A history that starts delinquent but is fully observed falls through to the normal tree | RL loans that miss their very first EMI (native 1 → canonical 2) get a real state instead of unknown — typically **EPD**. For CC the comment argues a fully observed history cannot start at 2+, so it should be rare there (check E04) |
| D2 | Restructured re-opens are one of the reasons a history can start delinquent (caught by Q0) | `restructure_blind_spot_flag` (account ever restructured) is treated like `cropped` everywhere: Q0 applies, never EPD, a straight roller is always seasoned | Restructured accounts never become EPD or early-life straight rollers |
| D3 | — | Removed by bundle 11 (2026-11-02): the RL ECL-gap rule. RL history is now complete, so a rule on disbursement date and product code alone no longer marks a real gap | RL accounts it held in unknown go through the normal tree |
| D6 | — | Bundle 11: a matched restructured RL loan carries its original loans' months in front of its own (`crx_rl_full_history_linked`), from the later of its restructure flag and the original's closure; before that it reads its own history. Chains are walked transitively; closed months are dropped; a restructure that resets to 0 DPD stays in the history as an ended spell; ambiguous links are stitched and flagged. Unmatched ones stay blind for life, as does a chain ending in an unmatched restructure | Matched accounts get the real journey; `chain_*` audit columns |
| D4 | +2 billing-cycle jump repair described for CC | RL skips the repair (`BucketScheme.repair_jumps=False`); an RL +2 is a real move | RL only |
| D5 | One CC history floor (2024-01) | Separate overridable floor for CC 180+ (`cc_history_floor_date_180_plus`, same default) | None until overridden |

## Decision (2026-10-23)

The code is the spec. `METHODOLOGY.md` §2 and §4 now describe D1–D5 (Q0 for unobserved
starts only, the restructure blind spot, the RL scale, the CC 180+ floor).
No code change.
