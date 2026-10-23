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
| D3 | — | RL only: `ecl_gap_blind_spot_flag` (disbursed before the ECL/DPL seam with a product code outside the ECL extract) bypasses the whole tree → stabilized if Q2, else unknown | Confirmed source gap: the visible run-up may be an artefact, so no fall-in state is claimed |
| D4 | +2 billing-cycle jump repair described for CC | RL skips the repair (`BucketScheme.repair_jumps=False`); an RL +2 is a real move | RL only |
| D5 | One CC history floor (2024-01) | Separate overridable floor for CC 180+ (`cc_history_floor_date_180_plus`, same default) | None until overridden |

## Recommendation

Accept D1–D5 as the current spec and update `METHODOLOGY.md` §2/§4 (Q0 wording, the two
blind-spot flags, the RL scheme). No code change.
