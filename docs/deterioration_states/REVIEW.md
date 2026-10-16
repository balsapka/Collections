# Independent review — findings and what was done

An independent reviewer (fresh context, no part in the design) reviewed the methodology and
code on 2026-10-16: read every file, probed the rules with crafted DPD strings, ran the
real-data path on Python 3.10 / pandas 1.5.3 as well as 3.13 / pandas 3.0, and reviewed the
Spark snippet by reading. **24 findings, none critical; 9 high or medium-high.** The
rules were confirmed MECE and the original edge cases passed. Business decisions were
taken by the owner (marked **owner**); everything else was fixed in code and documents.

Case strings are written oldest → newest (last digit = today's bucket).

| # | Sev. | Finding | Disposition |
|---|---|---|---|
| F01 | High | EPD depends on where the string starts; padded / fixed-length strings, numeric columns (lost digits), re-keyed cards and a `{"X": "9"}` example could all fake or hide EPD; E08's action invited circular tuning | **owner:** the oldest digit is the first billed month (0/1). Fixed: file reader refuses number-like values; Spark warns on non-string type; E27 flags fixed-length strings; `STRIP_CHARS` strips only the ends; `CHAR_MAP` example corrected; E08 action → compare and escalate |
| F02 | High | Strings that start inside the spell (`4567`, `444444`) became EPD; E04 (≤ 10%) too loose | **owner:** such histories are restructured re-opens or missing data. New Q0 data-quality state `history_starts_delinquent`; E04 tightened to ≤ 1%. Restructured accounts deferred |
| F03 | High | One-table backtest assumes all strings end in the same month; frozen / purged exits and letter exit codes bias it silently, with misleading diagnostics | Fixed: `COL_STRING_AS_OF` excludes stale strings; E02 covers backtest and whole table; E03 action lists frozen strings, letter codes, count vs balance; assumptions in METHODOLOGY §8. A T−k snapshot join remains an option if strings freeze |
| F04 | Med-high | +2 repair looked ahead and treated clean months as holds: `…0224` straight → `…02244` slow; `000034` became EPD | Fixed: causal repair (hold before the jump first), only holds at 2+, never moves a 4 below 4. Both cases are regression tests; E13 now 99.7% |
| F05 | Medium | Long-run clause documented as "6 months in 4+" but code counts months since first reaching 4; features used by rules missing from §3 and P6 | Fixed wording everywhere; §3 lists every input incl. `months_since_4`, `chg_6m`, `spell_pay_events`, `gap_prior_peak3`; P6 audit list updated |
| F06 | Medium | E16 passed when a state was empty | Fixed: shares reindexed to the option's full state list (empty = 0); E16 scoped to optional states |
| F07 | Medium | Crashes: a length-1 string (in `shape`), empty spine, < 8 residual rows, `"0000"`; an account at 0 silently labelled | Fixed: guards in `shape`, `build_features`, `run`, clustering; `journey_features` raises a clear error below bucket 2; P6 applies cleaning + spine filter first |
| F08 | Medium | Y/N flag columns silently became all-false | Fixed: `parse_flag` reads 1/0, Y/N, Yes/No, True/False; reports and skips when unparseable |
| F09 | Medium | E22 (residual-cluster ARI gain) cannot discriminate — a meaningless split passes | Demoted to INFO; METHODOLOGY no longer cites it as evidence for B |
| F10 | Medium | E25 already fired on synthetic (claim "cannot show" was false); 6-month exit saturates; E12 bucket-confounded | Fixed: bucket-standardised next-month roll and exit within 3 months; documentation corrected |
| F11 | Medium | Labels overclaim ("never paid"); an EPD paying monthly for 6–10 months stayed EPD → "early legal" | **owner:** an EPD never pays after crossing bucket 2 (new condition). Remarks now say "rolled straight to bucket 4 … some have paid since" |
| F12 | Medium | Slow roller overlaps credibility "money in" near bucket 4 (clock effect), undisclosed | Disclosed in §7; money-in by state × bucket reported every run |
| F13 | Medium | Straight vs slow rests on a single month for 41% of slow rollers; holds may be artefacts | Added E23 (outcome of one-hold slow rollers vs straight rollers) and E28 (calendar-month spike test of run-up holds). Business call deferred until real data |
| F14 | Medium | E07 spell definition ambiguous ("run at ≥4" also ≈ 85%) | E07 now INFO reporting four definitions; bank's exact definition is an open decision |
| F15 | Medium | Results contained raw 30-month DPD strings, against the stated governance | Fixed: only banded shapes shared by ≥ 10 accounts in results; check-only prints aggregates (newest/oldest digit counts, shapes) |
| F16 | Medium | Re-running in the same kernel used stale config | Fixed: snippet reloads the package each call and prints a config fingerprint |
| F17 | Medium | Expectation actions invited tuning agreed business definitions to hit shares | Fixed: `[business]` markers in `states.py`; all such actions say escalate; PROMPTS P3 forbids it |
| F18 | Low-med | Checks differed when re-run from the saved JSON (int vs str bucket keys) | Fixed: results are JSON-safe (str keys, no NaN) before checks run |
| F19 | Low-med | E02 blind to backtest / table; `STRIP_CHARS` removed mid-string characters | Fixed (see F01, F03) |
| F20 | Low-med | Repeat delinquent had no recency window; a one-month glitch created it | **owner:** earlier spell must end within 24 months of this one. Fixed: impossible one-month glitches (`4 0 4`, `0 3 0`) cleaned and counted; both are regression tests |
| F21 | Low | Ranges anchored on synthetic data not labelled; "never paid since 4" gap (59% vs ~90%) undiscussed | Every check now has an anchor (bank / design / synthetic / data); gap discussed in §9 |
| F22 | Low | `model_id` resolved before the config guard; E01 could never fail; hard-coded spine; NaN in JSON; Spark re-scans | Fixed all: guard first; E01 also checks unknown states; spine from config; JSON-safe; `cache()` |
| F23 | Low | Document inconsistencies (E01–E25 vs E26, stale names, quoted shares, "first three payments" vs "first or second bill") | Fixed in README, METHODOLOGY, PROMPTS, config |
| F24 | Low | Early-life straight roller acts for underwriting, small in synthetic; seasoned straight roller is in practice the residual | **owner:** keep early-life as a state; merge into straight roller if real share < 5% (E16). Seasoned straight roller's action is "read the other axes" by design |

## Verified independently before acting
F02 (`4567`, `444444` → EPD), F04 (`…0224` vs `…02244`; `000034` → EPD) and F11
(`00234444444444` → EPD) were reproduced before any change; all are now regression cases
in `dpd_states/selftest.py`.

## Still open
- The bank's exact spell definition (F14) and existing bust-out rule (F01 / E10).
- Restructured accounts re-opened at their old bucket (F02) — deferred by the owner.
- Whether a single paid month should separate slow from straight rollers (F13) — decide
  from E23 / E28 on real outcomes.
