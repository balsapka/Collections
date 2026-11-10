# A1 bundle 21: step 4 follow-up (user decisions on your two open questions)

Your apply summary (`data/input/a1_bundle21_apply_summary.md`) asked two questions. The user decided:

1. **Lane before the self label on the wash lane.** In `feat_cif_casa.flow_class`, a leg in the wash
   lane (direct-debit returns, DDS legs) keeps the dictionary's lane-first class (`own_transfer` /
   `reversal_return`) even when `self_transfer_flag = 1`. The self label decides `own_in_external` /
   `own_out_external` only outside that lane. Nothing else in the class order changes; the three user
   decisions (cash counts, own-account transfers with other banks count both ways, `MISCELLANEOUS` /
   cheque stems never count) stay.
2. **WM assets stay in F4.** `wm` rows keep counting in `xp_assets_aed`. No change.

Deliverables:
- the change for 1, with a test in `test_feat_cif_casa_flows.py` for a self-labelled wash-lane leg
  (both directions);
- rerun your comparison against both flow dictionaries and report the remaining differing
  combinations and their AED, CC and RL (the wash-lane rows should drop out of the table);
- black / pylint clean, tests pass; one-paragraph summary appended to
  `data/input/a1_bundle21_apply_summary.md` under a "Follow-up" heading.

Hard rules: no `kedro run`, no PROD data, no changes outside `feat_cif_casa.py` and its test.
