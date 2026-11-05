# Decisions

Format: `D-<round>-<n> | what | why | who decided | proposal ids`

## Round 1

D-1-1 | Merge S7 in full: apply `S7.patch` and the 12-file delete list (tier D, 7,028 lines), move `build_rl_depart_spine` unchanged into `rl_a4_spine/nodes.py`, delete the dead tier-L symbols (`parse_yyyymmdd`, `priority_reason`, `SEGMENTS`) | tier D confirmed dead by import and dataset search; the move must precede deleting `cc_departure_signature` (PLAN §2) | Master | S7

D-1-2 | Merge S1-01, 03, 02, 04, 05, 06, 07, 08 from S1's combined diff in its order; S1-07 (`episode_start`) and S1-08 (`window_agg(start=)`) go in now although no tier-L pipeline calls them yet; S1-06's A4 log text change is recorded under "PROD log changes" | PLAN §2 asks this refactor to put A3's shared helpers in the shared layer; the reviewers judge them | Master | S1-01 … S1-08

D-1-3 | Merge S3-01, 02, 03, 05, 06, 07; hold S3-04 (tag normalisation) | tags are what the workplace runs with; waits for the user (Q-15 [Q-S3-1]) | Master | S3-01 … S3-07

D-1-4 | Merge S2-01 … S2-07; output column order stays exactly as at baseline: where a change reorders columns, end with a select in the original order | hard rule 1 (identical outputs, columns included) | Master | S2-02 (liquidity select), S2-03 (aggregate order)

D-1-5 | Merge all of S4 re-based onto the S1 helpers, except: drop S4-08 `label_column` (duplicate of S1-04, the earlier stage wins; S4-01/S4-03 use `scoring_engine.state_label`), drop the window-start part of S4-04 (S1-03 did it); S4-01's constant renames update spec cells S2, S4, S10, S12 of `specs/A1_ability_spec.md` in the same commit | merge-order rule; spec cells must name the code's constants | Master | S4-01, S4-04, S4-08

D-1-6 | Re-base S2-03 onto S1-05: `_dcore_days` aggregates the rows of `_common.dcore_account_events` instead of reading followup / agreements itself | both intents survive (one shared DCORE reader for A2/A3; account-day reduction before the observation join); golden and A2 spec unchanged | Master (merge) | S1-05, S2-03

D-1-7 | Skip the DCORE part of S4-04 (`_call_days`, `_last_call_days`); keep its location split and `_cif_rows` | S2-03 (earlier stage) rewrote `build_dcore_signals` as one aggregate; the split's shape no longer exists | Master (merge, overlap rule) | S4-04, S2-03

D-1-8 | Re-base S4-10: `SEG_60_180` / `SEG_180_PLUS` defined in `_common` beside `MODEL_ID_SEGMENT`, not in `_dpd_journey/constants.py` | S1-01 made the shared layer own the segment map; constants in `_dpd_journey` would make `_common` import the engine again (the cycle S1-01 removed) | Master (merge) | S4-10, S1-01

D-1-9 | Revert S4-03 (split of `build_dpd_sequences` / `build_deterioration`, type hints) | gate 2: `_dpd_journey/_dates.py` gains a ruff finding (E501, new 89-char docstring); the rule is revert, not patch; re-submit in round 2 with the line wrapped | Master (gate) | S4-03

D-1-10 | Revert S4-09 (A4 wrapper steps `_original_loan_months`, `_restructure_blind_spot`) | gate 2: `rl_a4_deterioration/nodes.py` gains a ruff finding (E501, new 90-char docstring line); re-submit in round 2 | Master (gate) | S4-09

D-1-11 | Revert S2-06 (CC A4 restructure flag as one aggregate) | gate 2: `cc_a4_deterioration/nodes.py` gains a ruff finding (E501, new 89-char comment); re-submit in round 2 | Master (gate) | S2-06

D-1-12 | S4-05 keeps S2-05's pruning: `_distress_events` takes `since`; S4-09's CC part had been re-based onto S2-06 before both were reverted | earlier stage wins; intent of both kept | Master (merge) | S4-05, S2-05
