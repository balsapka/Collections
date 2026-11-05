# B14 check — CC and RL 60_180 (handoff 43, 2026-11-05)

Source: `tmp_validation/a1_b14_check/summary.md` in the workplace, transcribed from 6 photos. Latest
month 2026-08-31; CC 19,292 rows (18,731 CIFs), RL 3,985 (3,608). All rows match old ↔ new.

## Results

| | CC old | CC new | RL old | RL new |
|---|---:|---:|---:|---:|
| High | 46 | 45 | 10 | 11 |
| Moderate | 2,798 | 2,769 | 364 | 354 |
| Low | 5,688 | 5,568 | 1,835 | 1,783 |
| Unknown | 10,760 (55.8%) | 10,910 (56.6%) | 1,778 (44.6%) | 1,837 (46.1%) |
| Rows moved | | ~397 (2.1%) | | ~119 (3.0%) |
| No CASA (Unknown reason) | 3,986 | 4,917 | 0 | 524 (413 Auto) |
| Distress flagged | 1,683 (8.7%) | 1,795 (9.3%) | ~18.1% | ~19.1% |

- **Accounts:**
  - 15- and 16-character accounts never carry a current / savings scheme (CC 16-char: 25,536 legs,
    2,818 CIFs; RL: 41,642 legs, 3,598 CIFs, all other scheme). **Loans are outside the 49 codes.**
  - Current + savings = 90.6% of CC legs, 88.9% of RL legs.
  - 13-character legs on other schemes: CC 168,385 (1,438 CIFs), RL 33,917 (272). Top: 012 (CC 65k),
    095 (CC 61k, RL 13.7k on 65 CIFs), 014, 099. Unmatched (`no_scheme`) 0.55–0.6%.
  - CIFs with a CASA leg: CC 58.0%, RL 81.3%.
- **Moves:**
  - Low → Unknown: CC 245 (164 `no_casa`, 37 `dormant_casa`, 44 distress), RL 82 (69 `no_casa`).
    Their Low rested on non-CASA legs.
  - Unknown → Low through new distress: CC 95, RL 23. Moderate → Low: CC 43, RL 10.
- **Bounces (S15):** events +35% CC (24,800 → 33,389), +25% RL. New-only CIF-months 32% / 29%,
  old-only 8%. Extract − return date p50 / p75 / p95 = 2 / 3 / 9 days.

## Claude's review

- **Passes.** Loans are out (the question asked before the run). RL "No CASA" goes 0 → 524 as
  intended (the old zero was the loan account's own legs), concentrated on Auto (65% of Auto
  Unknown). Personal and Personal Cash stay mostly dormant.
- **More bounce events is expected.** The pull rule missed a second bounce of the same amount and
  dated by the extract; new-only months (32%) are mostly those. Old-only (8%) are amount restatements
  the old rule counted as new, or a pull dated into the next month.
- **The "legs since 2026-11-02" header is only the check's coverage table.** It anchors on the latest
  `tran_date` in `prm_casa_transactions`, which runs to the run date. The feature and A1 windows
  anchor on `observation_date` (`window_agg`, `_in_window`). No effect on states.
- **Open before step 8: the heavy 13-character other schemes.** 012 and 095 carry 65k and 61k CC legs
  (about 45 per CIF), which is not term-deposit behaviour. If they are current-like accounts outside
  WM's two lists, the new rule drops real CASA activity: part of the 164 + 69 new `no_casa`. A
  code-and-scheme-table lookup settles it (`sonnet_a1_other_schemes_prompt.md`); if they are CASA,
  the fix is the parameter lists only.
