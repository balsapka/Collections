# A2 — Locatability: methodology

Signed off with the user 2026-10-24 (decisions in §8), for presentation to GRR; details may
still change after that review. Follows the A1 architecture (bundle 03): month-end
observation dates, calendar-month windows that include the observation month, no spell / T0.
§9 lists what changes against the workplace code; §10 the data checks still open.

---

## 1. What A2 answers

**"Can we find this customer, and can we reach them?"** — before ability (A1) or
willingness (A3).

```
can we reach them?
├─ yes → negotiate → settle / restructure / pressure          (ability + willingness)
└─ no  → why not?  → chase / field visit / agency / write off   (locatability)
```

Two independent dimensions plus one override:

- **Location** — where the customer is, from what they *do* (logins, spending) and from a
  collector's note that they left the country.
- **Reachability** — whether our calls get through (DCORE contact outcomes).
- **Deceased** — overrides both.

Both dimensions follow one principle: **the latest evidence wins**. Location never reads a
call outcome (except the collector's departure note) and reachability never reads location.

---

## 2. Population and conventions

- **Grain:** one row per `(account_id, observation_date)` of the observation base
  (`crx_cc_obs_base`, `crx_rl_obs_base`): month-end dates, persona months only (in PROD the
  latest inference month). Every row gets a state.
- **Window `W`:** 3 calendar months at 60–180 DPD, 6 at 180+ — the observation month and the
  months before it (`_common.window_months`), as on every axis.
- **Customer level:** location evidence is read across **all accounts of the customer**
  (`cif_id`): every card and every CASA account, not only the scored account.
- **DCORE:** DCORE holds an account only while it is in collections, so its history is the
  collections history. All events up to and including the observation date count; no T0.
- **Call codes:** outbound `OC`, `CB`; inbound `IC`. Administrative notes (`IA`) never count.
- **Mid-month inputs:** until `cc_spine` moves to month ends, `cc_spine`,
  `dcore_observation_spine` and `prm_contract` carry billing dates in PROD (user,
  2026-10-26). A2 never joins them to the base on the date: DCORE events and Way4 snapshots
  are taken on or before the observation date (a month end), the account → agreement map
  ignores the date, and the CC obs base already moves billing dates to month end.

---

## 3. Location

### Evidence

| Evidence | Domestic | Foreign | Age limit |
|---|---|---|---|
| Login (digital banking) | from the UAE | from abroad | none |
| In-person card use — a shop payment or ATM withdrawal — on any of the customer's cards and CASA accounts | in the UAE, not a travel purchase | abroad | none |
| Travel purchase (airline, cruise, travel agency), any channel | — | not dated evidence: feeds the travel rule below | none |
| Collector's note: left the country / out of country / final exit visa | — | foreign, on the note's date | none |

### States

```
latest foreign  = date of the latest foreign evidence (on or before the observation date)
latest domestic = date of the latest domestic evidence

last travel     = date of the latest travel purchase

L1 Skip        there is foreign evidence, dated on or after the latest domestic evidence
L2 Skip        travel rule: there is a travel purchase, the latest domestic evidence is no more
               than 1 month after the last travel purchase (or there is none), and no domestic
               evidence for at least 1 month before the observation date
L3 In Country  latest domestic is later than any foreign evidence (on the same day, foreign
               wins) AND it falls in W
L4 Unknown     no evidence, or the latest evidence is domestic but older than W
```

**Why the travel rule.** A ticket is bought days or weeks before the flight, and the customer
keeps living normally until then, so UAE activity after the purchase is expected and must not
cancel it. A leaver who keeps banking from abroad is already caught by foreign evidence (L1);
the ticket matters for the one who goes silent. The pattern is: UAE activity stops within a
month of buying a ticket and does not resume. The silence guard keeps a customer who bought a
ticket last week and is still active out of Skip. It is checked before In Country: active until
three weeks after a ticket, then quiet for five weeks, reads as gone. A ticket shows intent,
not location, so it counts whatever the channel (online included).

Only in-person card use places the customer: online purchases (a foreign shop can be paid from
the UAE, a UAE shop from abroad) and transfers or remittances (most expats send money home every
month) are not location evidence.

Domestic activity well after a trip (more than a month after the ticket) means the customer came
back or never left: In Country. A foreign
latest evidence stays Skip however old it is — accounts sit in collections for years.

`location_unknown_reason`: `no_evidence` · `domestic_before_window`.

---

## 4. Reachability

### Evidence (DCORE, up to the observation date)

| Term | Meaning |
|---|---|
| confirmed contact | an inbound call, an outbound call with category `SUC`, or a right-party result name on any event |
| attempt date | a date with at least one outbound call |
| failed attempt date | an attempt date where every outbound call was ringing / no answer or a dead line, and no contact was confirmed that day |
| not an attempt | dropped before the date logic: RL legal / repossession codes (`RPO case *`, `Vehicle Repossesed/Under Auction`, `Legal notice Sent`) and admin codes (`Result Not Found`, `Follow up`, `E mail Sent`) (D-A2-17) |

Outcomes off the lists (D-A2-17): `LEFT_MSG` = ringing / no answer (failed); `CALL CONNECTED` without category `SUC` = an attempt that is neither failed nor a contact (it breaks a gone-dark run); `Skip - Under Tracing/Traced` = diagnostic column only, evidence on neither dimension.

### States

```
Non-Reachable  the last 3 attempt dates all failed, the oldest of them is in W,
               and no contact was confirmed after the oldest of them        ("gone dark")
Reachable      a contact was confirmed in W
Unknown        otherwise
```

Non-Reachable is checked first: a fresh run of failed calls outweighs an earlier answered
call. A customer who only calls in is Reachable without any outbound attempt; the minimum of
3 attempt dates guards Non-Reachable only.

`reachability_unknown_reason`: `no_dcore_record` · `no_contact_in_window` (calls exist but
neither rule fires).

---

## 5. Deceased

`deceased_flag` = any of, at any age up to the observation date:

- a DCORE deceased result (DECEASED, DECEASED CLAIMED, DECEASED OR EXPIRED, …) — a relative's
  claim counts until disproved;
- CC only: Way4 block code `D` on the latest contract snapshot;
- `ft_deceased_flag` on the customer's latest demographics row.

`deceased_source` names which source(s) fired.

---

## 6. Output

| Column | Values |
|---|---|
| `location_state` | `skip` · `in_country` · `unknown` |
| `reachability_state` | `reachable` · `non_reachable` · `unknown` |
| `deceased_flag` | 0 / 1 |
| `a2_state` | `deceased`, else `<location>__<reachability>` (10 values) |
| `a2_state_label` | display name: Deceased · Skip – Non-Reachable · … |
| diagnostics | latest domestic / foreign evidence dates and source, travel purchase date, last confirmed contact date, last attempt date, attempt dates in W, unknown reasons, `deceased_source` |

The two dimensions are computed for every row, deceased rows included, so either can be used
alone. Labels follow A1 / A4 (`*_state` lower-case, `*_label` for display).

| Location \ Reachability | Reachable | Non-Reachable | Unknown |
|---|---|---|---|
| **In Country** | negotiate | in the UAE but dodging or wrong number: skip-trace the number, field visit | keep calling |
| **Skip** | abroad but answering: remote settlement, international payment route | left and unreachable: agency / international recovery, legal | signs of leaving, no call evidence: verify departure |
| **Unknown** | answering, location not evidenced: negotiate, ask | not answering, no location evidence: skip-trace both | data gap — treat on other axes |
| **Deceased** | estate / insurance process | | |

---

## 7. Thresholds

| Threshold | Value |
|---|---|
| Window `W` (domestic evidence, confirmed contact, gone-dark recency) | 3 months (60–180), 6 months (180+) |
| Travel rule: last UAE evidence at most this long after the last travel purchase | 1 month |
| Travel rule: silence since the last UAE evidence, at least | 1 month |
| Gone dark | last 3 attempt dates all failed |

Starting values; tuned on the PROD distribution (the unknown reasons show what each moves).

---

## 8. Decisions (user, 2026-10-24)

| # | Decision |
|---|---|
| D-A2-1 | Two independent dimensions + deceased; the latest evidence wins on both. |
| D-A2-2 | Location evidence is customer level: logins, card and CASA spending on all the customer's accounts. A dedicated location data layer is built from transactions (§10). |
| D-A2-3 | Latest evidence foreign → Skip at any age; latest domestic → In Country only within `W`. |
| D-A2-4 | Foreign spend counts only as the latest evidence (no share rule). Travel purchases follow D-A2-15. |
| D-A2-5 | A collector's departure note is foreign evidence on its date; later domestic activity overrides it. |
| D-A2-6 | Salary stop is not location evidence (it stays an A1 signal). |
| D-A2-7 | Non-Reachable = last 3 attempt dates failed (ringing or dead line), oldest in `W`, no contact since; Reachable = confirmed contact in `W`; the 3-attempt minimum guards Non-Reachable only. |
| D-A2-8 | DCORE: all history up to the observation date, no T0 (verified in PROD, §10). |
| D-A2-9 | Deceased: DCORE note (claims included), Way4 `D`, demographics — any age. RL: DCORE + demographics only; the Way4 arm needs `prm_contract` run under the RL model, left out for now (user, 2026-10-27). |
| D-A2-10 | Routing flags (promise to pay, hardship, refusing, field visit) leave A2. |
| D-A2-11 | Output: both dimension columns, `deceased_flag`, and the combined `a2_state` with labels. |
| D-A2-12 | Results are reported per model variant, RL split by product (Personal Loans, Personal Cash Loans, Auto); 180+ also by charge-off-age vintage (early-stage charge-off < 2 years / late-stage charge-off 2+ years), as on the deterioration axis. Model doc: `docs/locatability/a2_locatability_reference.xlsx`. |
| D-A2-13 | Spending is location evidence only when in person: card-present shop payments and ATM withdrawals. Online purchases and transfers / remittances abroad are not (user, 2026-10-25). |
| D-A2-14 | Same-day UAE and foreign evidence: foreign wins (Skip). Evidence is compared by date only, no timestamps (user, 2026-10-25). |
| D-A2-15 | Travel rule (§3 L2): Skip when the last UAE evidence is at most 1 month after the last travel purchase and there has been no UAE evidence for at least 1 month; checked before In Country; any channel; no lookback from the scoring date. Validated in PROD for firing rate and threshold sensitivity (`bundle_helpers/b04_a2/sonnet_a2_v02_travel_prompt.md`) (user, 2026-10-25). |
| D-A2-16 | Credit-card evidence reads the model's scoped cards as they are (`prm_transaction`): CC models the spine cards, RL models all cards of the scoped CIFs. No extra CIF-level card scope for CC models (user, 2026-10-25). |
| D-A2-17 | DCORE outcomes off the lists: `LEFT_MSG` = failed attempt; `CALL CONNECTED` (not `SUC`) = neutral attempt (breaks gone dark, not a contact); `Skip - Under Tracing/Traced` = diagnostic only (a collector status, not a call, mostly domestic skips, and "Traced" means found); RL legal / repossession and admin codes (`Result Not Found`, `Follow up`, `E mail Sent`) dropped (user, 2026-10-26). |

---

## 9. What changes against the workplace code

| Today | New |
|---|---|
| spine + spell table + departure signature (T0, 12 passes) | obs base + location feature + DCORE |
| departure trail = any of travel / last card txn foreign / foreign login / salary stop / DCORE note; UAE login in 90/180 days beats it | latest evidence wins (§3) |
| travel: 3 months before the card block, scored account only (CC) / raw CASA debits (RL) | travel rule (D-A2-15), all the customer's accounts, no lookback from the scoring date |
| login months `< trunc(obs)` (CC) / `<=` (RL) | evidence dated on or before the observation date |
| DCORE window `[t0, observation_date)` | all events up to the observation date |
| Reachable: any confirmed contact since T0; overridden only by 3 ringing events (O17, O46) | confirmed contact in `W`; gone dark (ringing or dead) checked first |
| dead-line rule: *any* failed event in the last 2 dates (O45) | *every* call failed on each of the last 3 dates |
| 3 outbound attempts needed for any reachability state | only for Non-Reachable |
| Way4 exact-date join (O15), demographics without PIT (O16), `cif_id` re-attach (O13) | latest snapshot on or before the observation date; obs base |
| routing flags, `rpc_rate`, `uns_rate`, `spell_id` (O52) | dropped |

---

## 10. Open data checks (workplace Sonnet, before the bundle)

1. **Existing location datasets.** WM and retail.feature_space carry travel / foreign-spend
   features that an earlier check found unfit; re-check them (`feat_cc_txns_rfs` travel &
   tours, `feat_fx_leakage` cross-border outflow, WM equivalents): grain, coverage of our
   customers, whether they flag foreign *location* (not only FX currency) and carry dates.
2. **Location data layer**, if they don't fit: a primary `prm_customer_location_events`
   (one row per login / card / CASA transaction carrying a country or travel MCC: `cif_id`,
   event date, source, domestic / foreign, travel purchase) and a feature table per
   `cif_id` × month end (latest domestic date, latest foreign date + source, latest travel
   purchase date). Needs the country / international columns of the card and CASA
   transaction tables.
3. **DCORE keys** (O14, O49): columns and date grain of `dcore_observation_spine`
   (`account_id` or `contract_id`; billing or month-end dates); whether `agreement_id`
   changes between collections episodes (D-A2-8).
4. **Way4 / demographics grain** (O15, O16): `prm_contract` snapshot dates; rows per CIF in
   `feat_demographics_cif` and its date column.
5. **Login dates** (O50): `month_number` format and whether `last_login_date` is the actual
   login day.

### What the v01 inventory settled (2026-10-25, `bundle_helpers/b04_a2/a2_v01_inventory_results.md`)

| Check | Finding | Consequence |
|---|---|---|
| 1 Existing location features | retail.feature_space: travel = an MCC category, "foreign" = currency mismatch, no merchant country; earlier verdict "derive from raw MCC". WM has three unscreened CIF × week features (`fea_credit_card_international_transactions_by_cif`, `fea_casa_cc_international_spend_by_cif`, `fea_days_since_last_international_case_cc_txns`), foreign = foreign-currency code, IBAN or `transaction_location` | Weekly, CIF-level candidates; PROD coverage (t5) decides. A foreign IBAN is a remittance, not a location |
| 2 Transaction sources | Card: Way4 `is_international` = the `DOMESTIC=` flag in `add_info` (no merchant country; `trans_country_code` < 1% filled); `crx_cc_transactions` is a T0-scoped persona extract. CASA: `wm_pri_labelled_transactions_indicators_by_week` has `mcc_country`, `home_country_flag`, channel, MCC. Supplementary-card spend is not separable from the primary | Credit cards: `prm_transaction` (primary; else Way4 raw via a new primary). It is model-scoped: CC models hold only the delinquent spine cards, RL models all cards of the scoped CIFs (`cc_scope`); used as is (D-A2-16). Debit cards / CASA: either a new primary from the raw CASA table `comp_financial_tran_repos_dly`, or the sibling-repo feature datasets — v02 compares the two |
| 3 DCORE keys | `dcore_observation_spine`: `account_id` (O14 resolved, docs stale), `observation_date` = the spine's billing dates, latest agreement per (account, date) | Month-end bases cannot join on the date (O49 confirmed): map account → all its agreements, events up to the observation date (D-A2-8) |
| 4 Deceased | `prm_contract` = one snapshot per contract per billing date; `D` is not in the documented block-code list but was seen in PROD (T34). `feat_demographics_cif` = one static current row per CIF, uniqueness not enforced | Way4: latest snapshot on or before the observation date. Demographics: max flag per CIF (a death is permanent, so no point-in-time issue) |
| 5 Login | `month_number` = month end (string); raw is one row per session | O50 confirmed; login fixes as in §11 |
| 6 Splits | `rl_spine.loan_type` ∈ {Personal, Personal Cash, Auto}; `chargeoff_age_months` on both spines, < 24 = early-stage, else late-stage (`chargeoff_segment`) | Both available on the spine; carried onto the obs base |

### What the v01 PROD run showed (2026-10-26, `bundle_helpers/b04_a2/a2_v01_results.md`)

| Check | Finding (cc_60_180 / rl_60_180, latest month) | Consequence |
|---|---|---|
| 3 DCORE keys | One agreement per account in both; join on account 99.92% / 100% | D-A2-8 holds: account → agreement, all events up to the observation date. The DCORE spine is still on billing dates (user), so the 99.92% "exact" join must have compared months (v02 Part 0 confirms) |
| DCORE outcomes | The result-name lists cover ~48% / ~42% of event volume; `LEFT_MSG`, `CALL CONNECTED`, `Skip - Under Tracing` and RL legal / repossession codes are on none | Decided D-A2-17 (user, 2026-10-26) |
| Reach preview | ~95% have 6+ outbound dates in 3 months; last 3 dates all failed 38.9% / 19.0%; inbound 12.5% / 16.3% (3 m) | Non-Reachable baseline differs by product; no threshold change |
| 4 Deceased | RL has no `prm_contract`; demographics 0.13% deceased (CC) | RL deceased = DCORE + demographics |
| 5 Login | `month_number` month end, `last_login_date` the real day; 12-month coverage 75% / 82%; history carries `sessionid` | O50 confirmed; O54 fix unchanged; foreign share (≈21%) awaits the O53 split |
| 1–2 Location sources | `feat_fx_leakage` foreign = currency / cross-border transfers; CASA foreign shares rest on an unconfirmed heuristic; Way4 `is_international` = 96% (O59) | `feat_fx_leakage` is not evidence (D-A2-13); card and CASA "abroad" fields decided in v02 |

### What v01 Part 0 and the snippets added (2026-10-27, `a2_v01_results.md` Part 0, handoff 9)

| Check | Finding | Consequence |
|---|---|---|
| Dates | CC DCORE and `prm_contract` on day 9, RL DCORE on month ends; exact = same month = account-only join rates, so the snippet's base had the spine's own dates | Nothing changes: the engine never joins these on the date |
| DCORE bridge (R9) | CC spine: `col_trn_agreement.iagreementseqno` → `agreement_id`, `szlegacyagreementno` = `spine_contracts_way4.personal_account` → contract; inner join on `cc_spine` (its dates); highest `agreement_id` kept | `prm_dcore_account_agreements` = this bridge without dates; the RL route is still open (R9b) |
| Way4 deceased | `D` only in `block_code_2` (232 CC rows) | D-A2-9 Way4 arm = `block_code_2 = 'D'` on the latest snapshot on or before the observation date |
| Logins | RL: no-country rows 245 (0.02%); NULL `sessionid` 0.08%; history 26% duplicate sessionids | O53 / O54 fixes stay but move numbers little; the ~15% foreign login share is mostly real |
| Card / CASA foreign | `prm_transaction` uses the same `DOMESTIC=` parse as `crx_cc_transactions` (96% foreign, O59); `comp_financial_tran_repos_dly` "foreign" 51% CC / 70% RL | v02 must define foreign per source before card or CASA evidence enters the engine |
| Demographics | The pipeline works (user; the mirror copy is outdated, O61 closed); the RL deceased share comes from the A2 bundle's check run (user, 2026-10-27) | D-A2-9 reads `feat_demographics_cif` as planned |

---

## 11. Refactor plan (the A2 bundle — next free number, 06+ — after the §10 checks)

1. **Login pipeline fixes** (`digital_login`, shared with every consumer of the login tables):
   - `stg_digital_login`: `is_foreign_login` = 0 for the UAE, 1 for another country, NULL
     when neither `countrylocation` nor `countrycode` is filled (O53); deduplicate on
     `sessionid` only where it is not NULL (O54).
   - `prm_digital_login_monthly`: adds `last_uae_login_date` and
     `last_foreign_login_date` (the month's latest login of each kind, O56) and
     `unknown_country_login_cnt`; on the month's last login day a foreign login is taken first
     (O55), so the pick is deterministic without timestamps. Same grain and existing columns, so current consumers keep
     working. A2 reads this primary table, never the staging output.
   - Check: per source, rows before / after and the UAE / foreign / unknown-country shares.
2. **Location data layer**: the CIF × month-end location feature built from primary
   datasets only — `prm_digital_login_monthly` (latest UAE / foreign login per month) plus the
   card and CASA primaries §10 settles (a new `prm_customer_spend_location` if none fits).
3. **A2 engine** `a2_locatability/` (location, reachability and deceased signals; state
   classification) with thin CC / RL wrappers on the obs base.
4. **Retire** the old A2 nodes and the departure signatures once nothing else reads them (D1).
5. **Check pipeline**: old vs new A2 crosstab on temporary catalog entries, removed by the
   bundle's cleanup.
