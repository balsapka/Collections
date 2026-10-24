# A2 — Locatability: methodology (month-end, no T0)

Rewritten 2026-10-24 for bundle 04. It follows the A1 architecture (bundle 03): month-end
observation dates, calendar-month windows that include the observation month, no spell / T0.
The workplace code (`cc_a2_locatability`, `rl_a2_locatability`, the departure signatures) is
the starting point; §9 lists what changes against it. Items marked **[Qn]** are open
questions (§10) — the rule shown is the proposal, not yet a decision.

---

## 1. What A2 answers

**"Can we find this customer, and can we reach them?"** — before ability (A1) or
willingness (A3).

```
can we reach them?
├─ yes → negotiate → settle / restructure / pressure          (ability + willingness)
└─ no  → why not?  → chase / field visit / agency / write off   (locatability)
```

Two independent dimensions (GRR workbook *Axes and States for UC2 — Cards 61-180*, sheet
"A1, A2, A4"):

- **Location** — where the customer is, from what they *do*: logins, transactions, a
  collector's note that they left the country.
- **Reachability** — whether calls get through, from DCORE contact outcomes.

A location signal never decides reachability and a call outcome never decides location,
with one exception: a collector recording "left the country" is a location fact. Deceased
sits above both. One engine serves CC and RL; only the upstream sources differ.

---

## 2. Population and conventions

- **Grain:** one row per `(account_id, observation_date)` of the obs base
  (`crx_cc_obs_base`, `crx_rl_obs_base`): month-end dates, persona months only
  (`crx_persona.persona_start_date` .. `persona_end_date`; in PROD the latest inference
  month). Every row gets a state; rows without a `cif_id` are kept (customer signals absent).
- **Window `W`:** `_common.window_months(model_id)` — **3 calendar months at 60–180, 6 at
  180+**, the observation month and the months before it, up to and including the
  observation date. Every A2 lookback uses `W` unless stated otherwise.
- **Customer-level sources** (logins, CASA, demographics) join on `cif_id`.
- **DCORE scope:** DCORE only holds an account once it is in collections, so its history
  *is* the collections episode. All events of the account's agreement up to and including
  the observation date count; no T0 / collections-entry filter **[Q1]**.
- **Result names** are matched upper-cased and trimmed against the fixed lists in
  `constants.py`: right-party contact (83), ringing (2), dead line (18), departure (3),
  deceased (5); refusing / promise to pay / hardship / field visit are carried as flags only.
- **Call codes:** outbound `OC`, `CB`; inbound `IC`. Administrative notes (`IA`) are never an
  attempt or a contact.

---

## 3. Location signals

| Signal | Definition | Source |
|---|---|---|
| `in_country_flag` | the latest login on or before the observation date is in `W` and from the UAE | `prm_digital_login_monthly` (CIF) |
| `foreign_login_flag` | the latest login on or before the observation date is in `W` and from abroad **[Q4]** | same row |
| `dcore_departure_flag` | a collector recorded a departure result (left the country, out of country, final exit visa) up to the observation date | DCORE |
| `travel_flag` | a travel purchase (MCC 3000–3299, 4411, 4511, 4722, or an airline / airport keyword) in the window **[Q2]** | CC: card transactions; RL: CASA debits (CIF) |
| `last_txn_foreign_flag` | the latest transaction on or before the observation date, within **[Q2]**, was foreign | CC: card transactions; RL: cross-border outflow (FX leakage) |
| ~~`casa_inflow_stop_gap_d > 180`~~ | proposed **dropped** from location **[Q3]** | — |

`departure_trail_flag` = any of `foreign_login_flag`, `dcore_departure_flag`, `travel_flag`,
`last_txn_foreign_flag`.

## 4. Reachability signals

All over DCORE events up to and including the observation date (§2).

| Signal | Definition |
|---|---|
| `contact_attempts_n` | distinct dates with an outbound call (`OC` / `CB`) |
| `last_call_dt` | the latest call event (`OC` / `CB` / `IC`); "fresh" = in `W` |
| confirmed event | an outbound call with category `SUC`, a right-party result name on any event, or an inbound call |
| `contact_confirmed_flag` | a confirmed event in `W` **[Q5]** |
| failed attempt date | an outbound attempt date whose every outbound event is ringing or dead line, with no confirmed event that day |
| `gone_dark_flag` | the last 3 outbound attempt dates are all failed and the oldest of them is in `W` **[Q5]** |
| `last_attempt_confirmed_flag` | the latest call date has a confirmed event |

Diagnostics kept (never change the state): `ringing_dates_n`, `dead_dates_n`, counts behind
each flag, `ptp_flag`, `hardship_flag`, `refusing_n`, `field_visit_flag`.

---

## 5. The states

Asked **in order**; the first "yes" decides.

```
D   Deceased?        deceased_flag (§6)                                    -> Deceased

Location  (independent of reachability)
L1  Skip?            departure_trail_flag AND NOT in_country_flag          -> Skip
L2  In country?      in_country_flag                                       -> In Country
L3  otherwise                                                              -> Unknown

Reachability
R0  Evidence?        no fresh call (last_call_dt not in W), or fewer than 3 outbound
                     attempt dates and no confirmed event in W [Q6]        -> Unknown
R1  Gone dark?       gone_dark_flag                                        -> Non-Reachable
R2  Reached?         contact_confirmed_flag                                -> Reachable
R3  otherwise                                                              -> Unknown

a2_state = "Deceased", or "<location> - <reachability>"
```

`location_state` and `reachability_state` are separate columns (computed for deceased rows
too). 3 × 3 + 1 = **10 states**; `a2_state_label` carries display names as on A1 / A4.

| Location \ Reachability | Reachable | Non-Reachable | Unknown |
|---|---|---|---|
| **In Country** | negotiate | in the UAE but dodging or wrong number: skip-trace the number, field visit | keep calling |
| **Skip** | abroad but answering: remote settlement, international payment route | left and unreachable: agency / international recovery, legal | signs of leaving, no call evidence: verify departure |
| **Unknown** | answering, location not evidenced: negotiate, ask | not answering, no location evidence: skip-trace both | data gap — treat on other axes |
| **Deceased** | — | — | estate / insurance process |

Diagnostic columns: `location_unknown_reason` (no login on record / login older than `W` /
other), `reachability_unknown_reason` (no DCORE record / no fresh call / too few attempts /
no pattern).

---

## 6. Deceased

`deceased_flag` = any of:

- DCORE: a deceased result name (DECEASED, DECEASED CLAIMED, …) up to the observation date
  **[Q7]**;
- Way4 (CC only): block code `D` on `block_code_1` / `block_code_2`, latest contract
  snapshot in the observation month (`pit_latest`, not an exact-date join);
- demographics: `ft_deceased_flag = 1` on the latest `feat_demographics_cif` row on or
  before the observation date (one row per CIF).

---

## 7. Thresholds

| Threshold | Value | Note |
|---|---|---|
| Window `W` | 3 months (60–180), 6 months (180+) | replaces the 90 / 180-day `tau_recent` and `tau_label` |
| Minimum outbound attempt dates | 3 | flat across segments |
| Gone dark | last 3 attempt dates all failed | replaces the 2-date dead-line rule and the 3-ringing override **[Q5]** |

---

## 8. CC vs RL

| | CC | RL |
|---|---|---|
| Base | `crx_cc_obs_base` | `crx_rl_obs_base` |
| Travel / foreign transaction | card transactions | CASA debits; cross-border outflow |
| Way4 deceased | yes | — (no equivalent) |
| DCORE | same rules; RL keeps a partition floor `persona_start − 24 months` (performance) | |

---

## 9. What changes against the current code

| Today | Bundle 04 |
|---|---|
| spine + spell table + departure signature (T0) | obs base; departure-trail columns from a lean shared builder |
| CC mid-month dates; login month `< trunc(obs)` | month ends; latest login `<= observation_date` |
| DCORE window `[t0, observation_date)` | all agreement events `<= observation_date` |
| recency 90 / 180 days | `W` = 3 / 6 calendar months |
| travel: 3 months before the card block (`t0 + days_to_dpd60`) | **[Q2]** |
| departure salary stop > 180 days (own raw-regex salary) | dropped **[Q3]** |
| foreign login: latest ever | latest, in `W` **[Q4]** |
| `gone_contact_flag`: any dead / ringing event in the last 2 dates (O45) | every event failed on the last 3 dates **[Q5]** |
| confirmed contact: any since T0, outranks a dead line (O46) | in `W`; gone dark outranks it **[Q5]** |
| recent avoidance: 3 ringing *events* (O17) | dates, not events |
| Way4 exact-date join (O15), demographics without PIT (O16) | `pit_latest` |
| `rpc_rate`, `uns_rate`, `spell_id` | dropped (unused / spell) |

---

## 10. Open questions (user decides)

| # | Question | Proposal |
|---|---|---|
| Q1 | DCORE scope without T0: does an account keep the same `agreement_id` across collections episodes (cure, then re-entry)? If yes, events of an earlier episode count. | All events `<= observation_date`; Sonnet facts check how many accounts have events before their current episode |
| Q2 | Travel and foreign-transaction window. Cards are blocked from ~60 DPD, so `W` before the observation date holds almost no card transactions. | Look back 12 calendar months before the observation month, any travel purchase; the latest transaction within those 12 months for "foreign" |
| Q3 | Salary stop as departure. A salary that stopped is job loss as often as departure, it uses a second salary definition (raw regex vs A1's WM salary) and it duplicates A1. | Drop it from the trail |
| Q4 | Stale foreign login. Today the latest login ever counts, so one foreign login years ago marks a trail for good. | Only a login in `W` counts; an older foreign login is diagnostics only |
| Q5 | Reachability rules. Today `gone_contact_flag` fires on *any* dead / ringing event in the last 2 dates (O45); a confirmed contact any time since T0 keeps an account Reachable while every later call hits a dead line (O46); only *ringing* can override it. | One "gone dark" rule (last 3 attempt dates all failed — ringing or dead, oldest in `W`) above "confirmed contact in `W`" |
| Q6 | Inbound-only customers: someone who only calls in is Unknown until 3 outbound attempts exist. | A confirmed event in `W` skips the 3-attempt minimum |
| Q7 | "DECEASED CLAIMED" (a relative's claim, unverified) counts as deceased. | Keep (collections treat it as deceased until disproved), or split out a `deceased_claimed` flag |
| Q8 | In-country evidence is logins only (11.5% of cc_180_plus log in). Domestic CASA activity (ATM / POS in the UAE, CIF level) would add evidence. | Add it if an existing prm / feat dataset carries the country of CASA debits; otherwise leave for later |
| Q9 | `dcore_observation_spine` and `prm_contract` are joined on `(account_id, observation_date)`; after the move to month ends these dates may not match (O49). | Map account → agreement without the date (or by month); Sonnet facts check the keys |
