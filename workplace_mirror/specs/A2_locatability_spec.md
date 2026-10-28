# A2 — Locatability: methodology

Signed off with the user (decisions in §8, latest 2026-10-27), for presentation to GRR; details may
still change after that review. Same architecture as A1: month-end observation dates,
calendar-month windows that include the observation month, no spell / T0.

**Status:** the logic is final (debit-card rule set after v03, D-A2-19). Built as mirror bundle 06
(§11); next its PROD check, then the final report.

---

## 1. What A2 answers

**"Can we find this customer, and can we reach them?"** — before ability (A1) or
willingness (A3).

```
can we reach them?
├─ yes → negotiate → settle / restructure / pressure          (ability + willingness)
└─ no  → why not?  → chase / field visit / agency / write off   (locatability)
```

| Dimension | Question | Evidence |
|---|---|---|
| **Location** | Where is the customer? | what they *do*: logins, in-person card use, a collector's departure note |
| **Reachability** | Do our calls get through? | DCORE call outcomes |
| **Deceased** | — overrides both | DCORE, Way4, demographics |

On both dimensions **the latest evidence wins**. Location never reads a call outcome (except
the departure note); reachability never reads location.

---

## 2. Population and conventions

- **Grain:** one row per `(account_id, observation_date)` of the obs base (`crx_cc_obs_base`,
  `crx_rl_obs_base`): month-end dates, persona months only. Every row gets a state.
- **Window `W`:** the observation month and the months before it — 3 months at 60–180, 6 at
  180+ (`_common.window_months`).
- **Customer level:** location evidence covers all accounts of the `cif_id` (every card, every
  CASA account), not only the scored account.
- **Dates:** evidence counts when dated on or before the observation date, compared by day (no
  timestamps). `cc_spine`, `dcore_observation_spine` and `prm_contract` are still on mid-month
  billing dates in PROD, so A2 never joins them to the base on the date: DCORE events and Way4
  snapshots are taken on or before the observation date, and the account → agreement map
  ignores dates.
- **DCORE** holds an account only while it is in collections; all its history counts (no T0).
  Call codes: outbound `OC`, `CB`; inbound `IC`; administrative notes (`IA`) never count.

---

## 3. Location

### Evidence

| Evidence | UAE | Foreign |
|---|---|---|
| Login (digital banking) | from the UAE | from abroad |
| In-person card use (shop payment, ATM) — credit and debit cards | in the UAE, not a travel purchase | abroad |
| Collector's note: left the country / out of country / final exit visa | — | on the note's date |
| Travel purchase (airline, cruise, travel agency), any channel | — | not dated evidence: feeds L2 |

**Not evidence:** online purchases, transfers and remittances, incoming money, salary, logins
with no country. No age limit on any evidence.

### States (checked in order)

| | State | Rule |
|---|---|---|
| L1 | **Skip** | the latest foreign evidence is on or after the latest UAE evidence (same day: foreign wins) |
| L2 | **Skip** | travel rule: a travel purchase, the latest UAE evidence at most **3 months** after the last one (or none), and no UAE evidence for at least **1 month** before the observation date |
| L3 | **In Country** | the latest UAE evidence is in `W` |
| L4 | **Unknown** | otherwise — `location_unknown_reason`: `no_evidence` · `domestic_before_window` |

**Why the travel rule.** A ticket is bought weeks before the flight and the customer lives
normally until then, so UAE activity after the purchase must not cancel it. A leaver who keeps
banking from abroad is caught by L1; the ticket matters for the one who goes silent: UAE
activity stops within three months of the purchase and has not resumed for a month. L2 is
checked before L3, so a recent leaver is Skip even with UAE activity earlier in `W`; a traveller
who comes back is In Country again on the next run. A ticket shows intent, not location, so any
channel counts.

**Why in person only.** A foreign shop can be paid online from the UAE, and most expats send
money home every month; neither places the customer.

---

## 4. Reachability

| Term | Meaning |
|---|---|
| confirmed contact | an inbound call, an outbound call with category `SUC`, or a right-party result name |
| attempt date | a date with at least one outbound call |
| failed attempt date | every outbound call that day rang out / no answer (`LEFT_MSG` included) or hit a dead line, and no contact was confirmed |
| neutral attempt | `CALL CONNECTED` without `SUC`: an attempt, neither failed nor a contact |
| ignored | RL legal / repossession codes (`RPO case *`, `Vehicle Repossesed/Under Auction`, `Legal notice Sent`), admin codes (`Result Not Found`, `Follow up`, `E mail Sent`); `Skip - Under Tracing/Traced` is a diagnostic column only |

| State | Rule (checked in order) |
|---|---|
| **Non-Reachable** | the last 3 attempt dates all failed, the oldest of them in `W`, no contact since ("gone dark") |
| **Reachable** | a contact confirmed in `W` |
| **Unknown** | otherwise — `reachability_unknown_reason`: `no_dcore_record` · `no_contact_in_window` |

A fresh run of failed calls outweighs an earlier answered call. A customer who only calls in is
Reachable; the 3-attempt minimum guards Non-Reachable only.

---

## 5. Deceased

`deceased_flag` = any of, at any age up to the observation date (`deceased_source` names which):

- a DCORE deceased result (DECEASED, DECEASED CLAIMED, DECEASED OR EXPIRED, …) — a relative's
  claim counts until disproved;
- Way4 `block_code_2 = 'D'` on the latest `prm_contract` snapshot on or before the observation
  date, any of the customer's cards (RL: optional input until Way4 runs for RL in PROD; few RL
  customers hold a card, so near zero is expected);
- `ft_deceased_flag` on `feat_demographics_cif` (max per CIF; a death is permanent).

---

## 6. Output

| Column | Values |
|---|---|
| `location_state` | `skip` · `in_country` · `unknown` |
| `reachability_state` | `reachable` · `non_reachable` · `unknown` |
| `deceased_flag` | 0 / 1 |
| `a2_state` | `deceased`, else `<location>__<reachability>` (10 values) |
| `a2_state_label` | Deceased · Skip – Non-Reachable · … |
| diagnostics | latest UAE / foreign evidence date and source, last travel purchase, rule fired (L1–L4), last confirmed contact, last attempt, attempt dates in `W`, unknown reasons, `deceased_source` |

Both dimensions are computed on every row, deceased included, so each can be used alone.

| Location \ Reachability | Reachable | Non-Reachable | Unknown |
|---|---|---|---|
| **In Country** | negotiate | dodging or wrong number: skip-trace, field visit | keep calling |
| **Skip** | abroad but answering: remote settlement | left and unreachable: agency, international recovery, legal | verify departure |
| **Unknown** | negotiate, ask where they are | skip-trace both | data gap — use other axes |
| **Deceased** | estate / insurance process | | |

---

## 7. Thresholds

| Threshold | Value | Basis (v02, cc / rl 60–180, Aug 2026) |
|---|---|---|
| Window `W` | 3 months (60–180), 6 (180+) | as every axis |
| Travel: last UAE evidence after the last ticket, at most | 3 months | covers 82% / 84% of known leavers' lags, ~5% of stayers' |
| Travel: silence before the observation date, at least | 1 month | catches recent leavers; L2 ≈ 3.8% / 2.9% of rows, ~130 / 17 of them from In Country |
| Gone dark | last 3 attempt dates failed | ~95% have 6+ outbound dates in 3 months, so the minimum rarely binds |

---

## 8. Decisions

| # | Decision |
|---|---|
| D-A2-1 | Two independent dimensions + deceased; the latest evidence wins on both. |
| D-A2-2 | Location evidence is customer level (all the customer's cards and CASA accounts), built as a dedicated location data layer. |
| D-A2-3 | Latest evidence foreign → Skip at any age; latest UAE → In Country only within `W`. |
| D-A2-4 | Foreign spend counts only as the latest evidence (no share rule). |
| D-A2-5 | A collector's departure note is foreign evidence on its date; later UAE activity overrides it. |
| D-A2-6 | Salary stop is not location evidence (it stays an A1 signal). |
| D-A2-7 | Non-Reachable = last 3 attempt dates failed, oldest in `W`, no contact since; Reachable = confirmed contact in `W`; the 3-attempt minimum guards Non-Reachable only. |
| D-A2-8 | DCORE: all history up to the observation date, no T0; one agreement per account (v01). |
| D-A2-9 | Deceased: DCORE note (claims included), Way4 `block_code_2 = 'D'`, demographics — any age; RL reads Way4 as an optional input until it runs for RL. |
| D-A2-10 | Routing flags (promise to pay, hardship, refusing, field visit) leave A2. |
| D-A2-11 | Output: both dimension columns, `deceased_flag`, the combined `a2_state` with labels. |
| D-A2-12 | Results per model variant; RL by product (Personal, Personal Cash, Auto); 180+ by charge-off vintage (< 2 years / 2+ years). |
| D-A2-13 | Spending is evidence only in person (shop payment, ATM); online purchases and transfers / remittances are not. |
| D-A2-14 | Same-day UAE and foreign evidence: foreign wins; dates only, no timestamps. |
| D-A2-15 | Travel rule L2, checked before In Country, any channel, no lookback limit (thresholds: D-A2-18). |
| D-A2-16 | Credit cards: the model's scoped cards in `prm_transaction` as they are (CC: spine cards; RL: all cards of the scoped CIFs). |
| D-A2-17 | DCORE off-list outcomes: `LEFT_MSG` failed; `CALL CONNECTED` (not `SUC`) neutral; `Skip - Under Tracing/Traced` diagnostic only; RL legal / repossession and admin codes ignored. |
| D-A2-18 | After v02: travel GAP 3 months, SILENCE 1 month. Credit-card in-person = option C2 (§10). |
| D-A2-19 | Debit cards / CASA are evidence, from the raw CASA table via a new primary, with the v03 rule as recommended (user, 2026-10-28): POS Machine / Offline debits, ATM withdrawals placed by the narration country; no re-run. |

---

## 9. What changes against the workplace code

| Today | New |
|---|---|
| spine + spell table + departure signature (T0, 12 passes) | obs base + location feature + DCORE |
| departure trail = any of travel / last card txn foreign / foreign login / salary stop / DCORE note; a UAE login in 90/180 days beats it | latest evidence wins (§3) |
| card "foreign" = Way4 `DOMESTIC=N` on any transaction, online included (O59) — inflates CC Skip | in-person rows only (C2) |
| no debit-card location evidence | debit in-person use (D-A2-19) |
| travel: 3 months before the card block, scored account (CC) / raw CASA debits (RL) | L2 travel rule, all the customer's accounts |
| login months `< trunc(obs)` (CC) / `<=` (RL); no-country logins count as foreign (O53) | logins dated on or before the observation date; no country = no evidence |
| DCORE window `[t0, observation_date)` | all events up to the observation date |
| Reachable: any contact since T0, overridden only by 3 ringing events (O17, O46); dead line = any failed event in the last 2 dates (O45) | §4: contact in `W`; gone dark = every call failed on each of the last 3 dates, checked first |
| 3 outbound attempts needed for any reachability state | only for Non-Reachable |
| Way4 exact-date join (O15), demographics without PIT (O16), `cif_id` re-attach (O13) | latest snapshot on or before the observation date; obs base |
| routing flags, `rpc_rate`, `uns_rate`, `spell_id` (O52) | dropped |

Expect a large old-vs-new move on CC Skip: a correction of O59, not a regression.

---

## 10. Data sources

| Evidence | Source | Rule |
|---|---|---|
| Logins | `prm_digital_login_monthly` (fixed in §11) | `last_uae_login_date`, `last_foreign_login_date`; no country = ignored |
| Credit cards | `prm_transaction` | **C2:** cash advances (`txn_category` cash) or MCC grocery 5411/5422/5441/5451/5462/5499, fuel 5541/5542, restaurants 5812/5813/5814, pharmacy 5912, transport 4111/4121/4131, department / convenience 5311/5331. Abroad = `is_international = 1` (Way4 `DOMESTIC=N`: a foreign merchant, online included — hence the MCC filter). No card-present field exists in Way4 |
| Debit cards / CASA | `comp_financial_tran_repos_dly` → `prm_casa_card_transactions` | POS: `channel_desc` = Point of Sale, `merchant_type_desc` ∈ {Machine, Offline}; ATM: ATM Transactions with `tran_particular_code_desc` ∈ {DR ATM TRANSACTION, UAE SWITCH WDL}. Debits only; reason not in CHARGES / FEES / REVERSAL / CANCELLED / RETURNS / CHEQUE RETURNS / DDS Rejects/Reversal / Status Deleted in Finacle (NULL / '' / NA = none); remote MCCs 5815–5818, 4814, 4816, 4899, 5964–5969, 5734, 7372 excluded. Place: POS `merchant_country`; ATM the narration's country code (`:XX#` or trailing ` XX`), else `counter_party_bank_cntry`; UAE spellings normalised. Date `value_date` (else `tran_date`); dedup on the key; CIF 13339117 dropped. Online / NULL-type POS rows count only as travel purchases |
| Travel purchases | both card sources, any channel | MCC 3000–3299, 4411, 4511, 4722 or the travel keywords |
| Departure note, calls | `dcore_prm_followup_outcomes` via `prm_dcore_account_agreements` (distinct account × agreement of each model's `dcore_observation_spine`) | events on or before the observation date |
| Deceased | DCORE, `prm_contract`, `feat_demographics_cif` | §5 |
| Result splits | `rl_spine.loan_type`, `chargeoff_age_months` (both spines) | carried onto the obs base |

**Rejected sources:** `feat_fx_leakage` (foreign = currency / transfers), the WM CASA datasets
(Private / Priority / Premium Banking only, channel NULL on half the rows), `crx_cc_transactions`
(T0-scoped extract), Way4 `TRANS_LOCATION` (empty on most rows).

**A2 v03** (2026-10-28, `bundle_helpers/b04_a2/a2_v03_results.md`): settled the debit rule above; Way4 rows without a
`DOMESTIC=` key are fees / IPP (negligible); credit-card evidence uses purchase / cash debits only (payment credits carry
`is_international`). FTR row-handling reference: `bundle_helpers/ftr_transaction_handling.md`.

Evidence trail: `bundle_helpers/b04_a2/a2_v01_inventory_results.md`, `a2_v01_results.md`,
`a2_v02_results.md`; findings O45–O56, O59, O61 in `REVIEW_OBSERVATIONS.md`.

---

## 11. Refactor plan (the A2 bundle — next free number)

1. **Login fixes** (`digital_login`, shared): `stg_digital_login` — no country → NULL, not
   foreign (O53); dedup on non-NULL `sessionid` only (O54). `prm_digital_login_monthly` adds
   `last_uae_login_date`, `last_foreign_login_date` (O56) and `unknown_country_login_cnt`;
   a same-day tie takes the foreign login (O55). Same grain and columns, so current consumers
   keep working.
2. **Primaries:** `prm_casa_card_transactions` (beside `prm_casa_return_events`, pipeline
   `casa_primary`, the v03 filter) and `prm_dcore_account_agreements`.
3. **Location feature:** CIF × month end — latest UAE / foreign date and source, last travel
   purchase — from primary datasets only.
4. **Engine** `a2_locatability/` (location, reachability, deceased, classification) with thin
   CC / RL wrappers on the obs base. Result splits are read in the check from the spines (the obs base is
   left unchanged, so A1 is not touched).
5. **Retire** the old A2 nodes; the departure signatures go once the RL A1 waterfall that reads
   `crx_rl_departure_signature` is deleted (A1 finish bundle).
6. **Check pipeline:** old vs new crosstab, the state distribution by rule and source, and the
   v03 follow-ups, on temporary catalog entries removed by the cleanup prompt. Lint (black 88,
   ruff, pylint).
