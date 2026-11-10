# Bundle 20 check, 60_180: Claude's review (2026-11-10)

Source: `b20_check_results_60_180.md` (handoff 56). CC n = 19,292, RL n = 3,985, month 2026-08,
every row matched to bundle 17's output. 180+ not run (user, 2026-11-10).

## Verdict

The check passes: every step does what it was built to do, and nothing points to a bug. Without
the threshold step, the bundle moves states **up**. The new promise logic and the 12-month window
each change about 7% of states. The window's effect is material but has no outcome evidence yet.

## Impact by step (share of states changed)

| Step | CC | RL | Direction |
|---|---:|---:|---|
| Whole bundle (old → grr) | 52.2% | 43.1% | mostly Moderate → Low (the thresholds) |
| Thresholds, Moderate from 2 (old → old_m2) | 51.6% | 42.4% | Moderate → Low only, as the what-if showed |
| Promise events, episode window (old_m2 → grr_ep) | 8.5% | 7.2% | CC 1,012 up / 515 down; RL 217 up / 63 down |
| 12-month window (grr_ep → grr) | 6.4% | 7.1% | CC 1,002 up / 185 down; RL 270 up / 5 down |
| 30 days instead of GRR (grr → d30) | 6.3% | 0.0% | CC 1,173 up / 21 down; RL identical |

States, old → as shipped (grr): CC High 1.4 → 2.5%, Moderate 66.3 → 19.4%, Low 20.1 → 66.5%,
Unknown 12.2 → 11.5%; RL High 1.6 → 4.9%, Moderate 66.4 → 27.9%, Low 25.2 → 60.6%, Unknown 6.9 → 6.6%.
Against bundle 17 at Moderate from 2 (old_m2), the new Dimension A adds High +219 CC / +134 RL and
Moderate +902 / +157.

## Promise events

- **Coverage.** Accounts with at least one concluded promise: CC 4,626 (bundle 17) → 5,627 (events,
  episode window) → 7,905 (12 months); RL 556 → 939 → 1,310. Dimension A Thin falls from 84.0 to 70.2%
  (CC) and from 90.1 to 72.8% (RL).
- **Mix.** Follow-up-only events are 42.7% (CC) / 58.4% (RL) of events in the window. Settlement
  plans rarely have a follow-up note around them (CC 2,719 table-only vs 304 matched).
- **Outcomes (GRR).** Paid: CC 36.8%, RL 70.5% of concluded events. On CC, follow-up-only events are
  paid most (40%; table-only 36%, matched 33%), as in V1f: they look like real promises.
- **The 30-day deadline on CC** raises paid or partial events from 8,991 to 12,503. It cuts Broken from
  13.6 to 8.9% and lifts Kept from 2.3 to 5.5%: the bias V1g found in GRR's next statement for
  promises made close to it. On RL the two deadlines are the same in practice (1 row differs).

## The 12-month window (D-A3-26)

- **Size.** 8,133 CC events on 4,147 accounts (21.5%) and 1,048 RL events on 593 accounts (14.9%)
  concluded before the episode start: 38% (CC) / 34% (RL) of all concluded events.
- **They are paid more often than events in the episode.** CC 49% paid before vs 29% in the episode;
  RL 88% vs 62%. This is partly selection: an earlier episode ended because the customer paid back to
  current, so the promises around that cure were mostly kept. That is genuine evidence of keeping
  promises, but it favours repeat delinquents who cured once over first-time ones, who have no earlier
  promises.
- **Net effect.** Mostly Thin → Partly kept (CC 1,395, RL 267) and Thin → Kept (184 / 124), so states
  move up (CC Low → Moderate 936). Thin → Broken also happens on CC (682): earlier episodes with
  broken promises.
- **Not known yet:** whether the window ranks customers better. The check has no outcome. V1g's
  roll test (rebuild as of persona_end_date − 3 months, roll / cure over 3 months, AUC) would answer
  it with the episode window vs 12 months.

## Small things, all explained

- 20 CC rows go from Low / Moderate to Unknown: bundle 17 counted instalments due in the window from
  plans started before it; an event is dated at the plan start, so those plans now fall outside.
- 137 CC Unknown → Low: the follow-up events give these accounts evidence for the first time.
- Contacts: the refusal flag is identical (844 CC / 185 RL; handoff 51's 857 came from an earlier run).
  Payment reports moved from ptp to paid on 686 CC / 233 RL rows, as designed.
- The per-node log lines differ from the compare block by 1 row in two cells (the file's own note).
  That is ties in the latest-row pick, not worth fixing in a temporary check.

## Open before the logic is final

- 180+ is not checked (user, 2026-11-10: not run); the 60_180 check stands for the bundle.
- Outcome evidence for the window: a V1h prompt, if wanted.
- GRR: next statement vs 30 days.
