# Bundle 21 check review (handoff 68, all four model_ids, latest month 2026-08-31)

**Verdict: passes. Step 8 and the cleanup can go ahead.**

| model_id | High | Moderate | Low | Unknown | old Unknown |
|---|---:|---:|---:|---:|---:|
| cc_60_180 | 1.6% | 14.8% | 25.6% | 58.0% | 56.6% |
| rl_60_180 | 1.2% | 8.7% | 49.2% | 41.0% | 46.1% |
| cc_180_plus | 0.3% | 6.2% | 8.4% | 85.2% | 87.4% |
| rl_180_plus | 0.1% | 3.5% | 11.0% | 85.4% | 89.5% |

- **Outcomes order in both 60_180 books** (Jan–May cohort). CC cure / pay / roll: High 31.3 / 58.5 /
  52.8, Moderate 15.9 / 41.3 / 73.2, Low 10.9 / 29.1 / 82.3, Unknown 7.8 / 19.9 / 87.5. Both
  standardised gaps exclude 0 on all three outcomes (High − Moderate cure +14.7pp, Moderate − Low
  +5.1pp). Close to round 3 R4 (High 33.1 / 61.9 / 49.1).
- **RL**: raw rates order on all three outcomes (High cure 27.6% > Moderate 15.4%). High − Moderate is
  not significant (n = 105, cure +10.9pp [−2.5, 24.3]); Moderate − Low is. Same caveat as round 3:
  no High-vs-Moderate claim for loans.
- **High rises** from 0.2% to 1.6% (CC 60_180), mostly Moderate → High (two strong families now).
- **Low → Unknown** (CC 5.0%, RL 6.0% at 60_180): rows whose only sign of life was a CASA leg that
  the inclusion list no longer counts (fees, own-loan payments, netted pairs, small amounts). By
  design (spec §3).
- **Unknown → Low** (RL 10.3%, 180+ 2.4–4.5%): mostly cross-product "some" (another product current
  or held), evidence by spec §2. RL cross-product some = 23.9%.
- **The CASA balance** moves few rows, as expected: CC 60_180 101 rows (0.5%), RL 20, 180+ ≤ 0.2%.
  Sweepable flag 0.2–1.2%.
- **Money out is rarely strong** (0.1–1.6%); money in / out are NULL (no CASA data) for 84–99% of
  rows, as before.
- **180+**: Unknown falls 2–4pp; still 85%. The bureau swap (`feat_bureau_salary_unified`) is the
  next lever there.

Open, not blocking: the reason column is NULL for Low / Unknown rows without a strong family or
distress (71–93% of rows), as the spec defines it.
