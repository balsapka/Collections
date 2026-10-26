# A2 v01 — PROD summary (cc_60_180 + rl_60_180, 2026-10-26)

Part C of the v01 prompt (removed after it ran), written by the workplace Sonnet from
`tmp_validation/a2_v01/results_{cc,rl}_60_180.json`. Transcribed from photos by a chat session
(`pics/claude_code_handoff.md`, 2026-10-26), so single digits may be misread. The review and
the follow-ups are at the end.

## Summary (Sonnet, verbatim)

# A2 v01 — summary (cc_60_180 + rl_60_180)

Sources: `results_cc_60_180.json` (run 2026-10-26, `n_base=19,292`) and
`results_rl_60_180.json` (run 2026-10-26, `n_base=4,096`), both `crx_*_obs_base`,
latest month 2026-08-31. Two snippet bugs found and fixed while reading these runs
(not re-run after the second fix — neither blocks this summary): `crx_cc_transactions`
used the wrong join key (now `contract_id`, confirmed by a real PROD error); `t6`
coupled `prm_contract` and `feat_demographics_cif` into one try/except, so
`rl_60_180`'s real `prm_contract` PATH_NOT_FOUND (see t6) silently dropped RL's
demographics number too — now split into two independently-guarded sub-tables.
`feat_cc_txns_rfs` failed in both runs on a pinned-partition `PATH_NOT_FOUND` —
pre-existing catalog/environment issue (same class as `RESULTS.md` RL-A1-8), not fixed.

## t1 — DCORE keys
CC: join rate exact/same-month/account-only all 99.92%. RL: all 100%. Both: single-
agreement only (no 2/3+ bucket); 98.5% (CC) / 99.9% (RL) of agreements have ≥1 event/24m.
**Verdict:** month-truncated matching works for both; neither segment carries multiple
live agreements per account.

## t2 — DCORE events, list coverage
CC: 1,224,650 events/24m, ~48% on a list / ~52% none. RL: 258,027 events, ~42% on a
list / ~58% none. Both: top unmatched are administrative (Result Not Found, Follow
up, CALL CONNECTED, E mail Sent, LEFT_MSG); "Skip - Under Tracing/Traced" sits on no
list in either (~1.5% CC, ~0.3% RL). RL-only: a legal/repossession vocabulary (RPO
case *, Vehicle Repossesed/Under Auction, Legal notice Sent, ~1% combined) entirely
outside the 5 lists.
**Verdict:** the lists cover roughly half of volume in both; RL's repossession/legal
codes are a distinct, uncovered vocabulary worth their own list if A2 extends to auto.

## t3 — reach preview
Both: ~95% of accounts have 6+ outbound dates/3m and /6m — heavy attempt volume.
Inbound share: CC 12.5%/17.1% (3m/6m), RL higher at 16.3%/22.4%. Last-3-all-dead/
ringing-none-confirmed: **CC 38.9% vs RL 19.0%** — a real segment difference, not noise.
**Verdict:** expect a materially larger strict Non-Reachable baseline on CC than RL;
don't assume one number fits both domains.

## t4 — login
Both: `month_number` lands only on 28/30/31 (true month-end); lag p50 2d(CC)/1d(RL),
0% negative — `last_login_date` is the real day. Foreign-flag share 20.8%(CC)/21.6%
(RL). Coverage within 12m: CC 75%, RL 82% (better). RL's new raw/staging check (login
is CIF-based, not product-specific — generalizes to CC): `raw_digital_login_data` has
zero session duplication; `raw_digital_login_data_history` does (407,510 rows vs
300,487 distinct sessionid) — confirms `stg_digital_login`'s session dedup is
load-bearing, not redundant.
**Verdict:** both format questions confirmed; RL has better login coverage than CC
60-180; the staging dedup step is necessary, evidenced not assumed.

## t5 — location-source coverage
`feat_fx_leakage` foreign share: CC 36.2%, **RL 55.5%** (notably higher). `comp_
financial_tran_repos_dly` foreign share: CC 50.7%, **RL 70.4%** — both still look
inflated by the unconfirmed UAE-code heuristic; do not trust either until real
`merchant_country` codes are confirmed. `crx_cc_transactions` (CC only, fixed this
round): `is_international`=**96.35%** flagged — implausibly high next to its own MCC-
travel proxy (28.3%) on the same table; flagging as a likely existing-pipeline defect
in `is_international`'s derivation (R19), not fixed here.
**Verdict:** `feat_fx_leakage` is the cleanest, best-covered source in both segments;
RL's foreign shares run higher than CC's across every source — worth checking if real
or heuristic/defect-amplified; `is_international` needs a PROD look before any A2 use.

## t6 — deceased
CC: `prm_contract` joins 100% on all 3 definitions. RL: `prm_contract`'s catalog path
does not exist under the `rl_60_180` namespace at all — confirms it is genuinely
Way4/CC-only (architecture, not a bug). `feat_demographics_cif` (CC): 1 row/cif
(18,666), no date column, deceased 25/18,666 (0.13%). RL's demographics number is open
— lost to the now-fixed coupling bug, not yet re-run.
**Verdict:** `feat_demographics_cif` needs no point-in-time pick in either domain; RL
has categorically no Way4 deceased corroboration; RL's demographics-only count is a
cheap, non-blocking re-run away.

## t7 — splits
Both: vintage 100% "unknown" (expected — `chargeoff_age_months` only populates at
180+). RL product split: Personal 1,478 (36.1%), Auto 1,394 (34.0%), Personal Cash
1,224 (29.9%) — a genuinely three-way balanced population.
**Verdict:** vintage behaves as documented for 60-180 in both; the inventory's RL-D4-
vs-S15 product-split ambiguity now has real weight behind it — Auto is a full third
of `rl_60_180`, not a rounding error.

---

## Review (2026-10-26)

**Settled**

- **t1 / D-A2-8.** One agreement per account in both segments, so the agreement does not
  change between collections episodes: map account → agreement and read all events up to the
  observation date.
- **t4 / O50.** `month_number` is the month end and `last_login_date` the real login day. 12-month
  login coverage: CC 75%, RL 82%, the best single location source.
- **t4 / O54.** `loginlog` (history) does carry `sessionid` (300,487 distinct over 407,510
  rows), so the whole history does not collapse into one row. The 107K-row gap is duplicates
  **or** NULL sessionids; the fix (dedup only non-NULL ids) is right either way.
- **t6.** RL has no `prm_contract` (Way4 is CC only), so RL deceased = DCORE + demographics,
  as spec §5 already says. `feat_demographics_cif` is one static row per CIF: max flag, no
  point-in-time pick. CC deceased by demographics: 25 / 18,666 CIFs (0.13%).
- **t7.** RL: Personal 1,478 (36.1%), Auto 1,394 (34.0%), Personal Cash 1,224 (29.9%).
  Vintage is `unknown` at 60–180 by construction. The product split for A2 results is already
  decided (D-A2-12); the RL-D4 vs S15 question the Sonnet raises is about the model unit, not
  A2.
- **t3.** Heavy call volume (~95% have 6+ outbound dates in 3 months), so the 3-attempt
  minimum rarely binds. The strict gone-dark baseline is ~39% on CC and ~19% on RL; Reachable
  is at least the inbound share (CC 12.5%, RL 16.3% in 3 months) plus answered outbound calls.

**Not usable / needs a decision**

- **t5 `feat_fx_leakage` is not location evidence.** Its "foreign" is a currency or
  cross-border outflow, i.e. transfers and remittances, which D-A2-13 excludes. Being the best
  covered does not make it a candidate.
- **t5 `is_international` = 96.35% on `crx_cc_transactions` (new O59).** It is the Way4
  `DOMESTIC=N` flag in `add_info` (`cc_raw_extract/nodes.py:104–112`, the same logic as
  `prm_cc.build_transaction`), so `prm_transaction` very likely carries it too. Today it feeds
  `cc_departure_signature.last_txn_foreign_flag` → the old A2's `departure_trail_flag`, so the
  current CC A2 probably marks most card users as having a departure trail. The new A2 must
  not read it until v02 shows what `DOMESTIC=` means (added to the v02 prompt).
- **t5 CASA foreign shares (CC 50.7%, RL 70.4%)** rest on an unconfirmed UAE-code heuristic:
  not usable as is. v02 t7b decides the debit-card route and the country field.
- **t2 list coverage (~48% CC / ~42% RL of event volume)** is low, and unmatched codes change
  states: an attempt date with only unlisted outcomes is neither failed nor a contact, so it
  breaks a gone-dark run. **Decided (user, 2026-10-26, D-A2-17):** LEFT_MSG = failed;
  CALL CONNECTED (not SUC) = neutral attempt; Skip - Under Tracing = diagnostic only;
  legal / repossession and admin codes dropped. The questions were:
  - `LEFT_MSG` (voicemail / message left): a failed attempt (no answer)?
  - `CALL CONNECTED`: a confirmed contact when its category is not `SUC`?
  - `Skip - Under Tracing/Traced` (~1.5% CC, ~0.3% RL): a collector skip-trace status, not
    a departure; keep it off the evidence lists (diagnostic only)?
  - RL legal / repossession codes (`RPO case *`, `Vehicle Repossesed/Under Auction`,
    `Legal notice Sent`, ~1%): routing, outside A2 (D-A2-10)?
  - `Result Not Found`, `Follow up`, `E mail Sent`: administrative, not attempts?

**Doubtful — check before relying on it**

- **t1 / t6 "exact date" joins of 99.92% / 100%.** The v01 inventory found
  `dcore_observation_spine` and `prm_contract` on billing dates, and the CC obs base is on
  month ends, so an exact-date join should mostly fail (O49). The user confirmed (2026-10-26)
  that `cc_spine` and the DCORE inputs are still on mid-month billing dates in PROD, so
  exact = same month = account-only means the snippet compared months, not days. Part 0
  confirms how it joined; the engine never joins these on the date anyway.
- **Missing from the summary although asked:** t4 `stg_digital_login` rows by
  `is_foreign_login` and by both-country-NULL (the O53 number: the 20.8% / 21.6% foreign share
  may be mostly missing countries), and NULL `sessionid` share per raw source; t5 coverage of
  `prm_transaction` and the WM CIF features; t6 block-code `D` count; RL demographics (lost to
  the snippet bug).

All of these are already in the JSONs except RL demographics (a t6-only re-run). The v02
prompt now opens with a Part 0 that appends them to `tmp_validation/a2_v01/summary.md`.
