# A2 — Locatability: methodology

Written 2026-10-23 from the workplace code (`cc_a2_locatability`, `rl_a2_locatability`), which
is the authoritative definition — there is no separate business spec. Section 7 lists where
the code is questionable; those are open decisions, not part of the definition.

---

## 1. Where this sits among the persona axes

A2 answers **"can we find this customer, and can we reach them?"** — before anyone asks
whether they can pay (A1) or will pay (A3). It is the gate in the collections tree:

```
can we reach them?
├─ yes → negotiate → settle / restructure / pressure      (ability + willingness)
└─ no  → why not?  → chase / field visit / agency / write off   (locatability)
```

GRR asked for two plain dimensions instead of one mixed waterfall (workbook *Axes and States
for UC2 — Cards 61-180*, sheet "A1, A2, A4"):

- **Location** — where the customer is, from what they *do*: logins, card and account
  transactions, salary, a collector's note that they left the country.
- **Reachability** — whether calls get through, from collections contact outcomes (DCORE).

The two are kept independent: a location signal never decides reachability and a call
outcome never decides location (with one exception — a collector recording "left the
country" is a location fact). Deceased sits above both.

One derivation (`build_a2_locatability`) serves CC and RL; only the upstream signal tables
differ by product.

---

## 2. Population and data conventions

- **Grain:** one row per `(account_id, observation_date)` of the model spine (`cc_spine`,
  `rl_spine` via `crx_rl_a4_spine`) — the state is re-assessed at every scoring date.
- **Segments:** `cc_60_180`, `cc_180_plus`, `rl_60_180`, `rl_180_plus` (`model_id` from
  globals). Two windows depend on the segment (§5): 180+ accounts have far thinner digital
  and call activity, so a 90-day window leaves most of them Unknown.
- **Customer-level sources** (logins, CASA, bureau, demographics) join on `cif_id`
  (CC: contract → client → CIF; RL: on the spine).
- **DCORE window:** contact events from the start of the current delinquency (`t0`, when
  the account entered collections) up to, not including, the observation date.
- **Logins:** `prm_digital_login_monthly`, one row per CIF and month. The latest month
  before the observation month is used (CC observes mid-month, so the observation month is
  excluded; RL observes at month-end, so it is included).
- **Result names** are matched upper-cased and trimmed against fixed lists in
  `cc_a2_locatability/constants.py`:

  | List | Size | Examples |
  |---|---|---|
  | Right-party contact | 83 | ACCOUNT PAID, APPRECIATIONS, BALCON WOP 12 MONTHS, … |
  | Ringing | 2 | RINGING NO REPLY, RINGING NO RESPONSE |
  | Not reachable (dead line) | 18 | CUSTOMER NOT CONTACTABLE, ININ-OUTBOUND-INVALID-PHONE-NUMBER, MOBILE SWITCHED OFF, … |
  | Departure | 3 | LEFT THE COUNTRY, OUT OF COUNTRY, KSA/NATHEER-CROSSING FINAL EXIT VISA |
  | Deceased | 5 | DECEASED, DECEASED CLAIMED, DECEASED OR EXPIRED, … |
  | Refusing, promise to pay, hardship, field visit | 9 / 26 / 19 / 1 | carried as flags, not used by the state |

- **Call codes:** outbound = `OC` (outbound call), `CB` (callback); inbound = `IC`
  (customer called us). Administrative notes (`IA`) never count as an attempt or as recent
  contact.

---

## 3. Signals used by the states

### Location

| Signal | Definition | Source |
|---|---|---|
| `in_country_flag` | the latest login is from the UAE and at most `tau_recent` days before the observation date | logins |
| `departure_trail_flag` | any of the five below | — |
| ↳ `travel_mcc_flag_h2` | a travel purchase in the 3 months before `t0`: MCC 3000–3299, 4411, 4511, 4722, or an airline / airport keyword in the merchant name | CC: card transactions; RL: CASA debits |
| ↳ `last_txn_foreign_flag` | CC: the last card transaction before the observation date was foreign. RL: cross-border outflow in the `t0` month | CC: card transactions; RL: FX-leakage feature |
| ↳ `foreign_login_flag` | the latest login before the observation date was from abroad (no lower time bound) | logins |
| ↳ `casa_inflow_stop_gap_d > 180` | the last salary credit to CASA was more than 180 days before the `t0` month | CASA transactions |
| ↳ `dcore_departure_flag` | a collector recorded a departure result (left the country, final exit visa) | DCORE |

### Reachability

| Signal | Definition |
|---|---|
| `contact_attempts_n` | distinct dates with an outbound call (`OC`/`CB`) in the DCORE window |
| `label_event_gap_d` | days from the latest call event (`OC`/`CB`/`IC`) to the observation date |
| `contact_confirmed_flag` | any confirmed two-way contact in the window: an outbound call with a SUC outcome, a right-party result name on any event, or an inbound call |
| `gone_contact_flag` | the last 2 outbound attempt dates produced only dead-line or ringing results and no confirmed contact |
| `last_attempt_contact_flag` | the latest call event was itself a confirmed contact |
| `recent_avoidance_flag` | the last 3 outbound attempt dates were all ringing, none confirmed, and the oldest of them is at most `tau_label` days old |

### Deceased

`deceased_flag_v2` = any of: a DCORE deceased result in the window; CC only — a Way4 block
code `D` on the contract (`prm_contract.block_code_1/2`) on the observation date;
`ft_deceased_flag` in the customer demographics.

---

## 4. The states

Asked **in order**; the first "yes" decides.

```
Q0  Deceased?        deceased_flag_v2                                   -> Deceased

Location  (independent of reachability)
L1  Skip?            departure trail AND NOT in country                  -> Skip
L2  In country?      UAE login within tau_recent                         -> In Country
L3  otherwise                                                            -> Unknown
                     (in-country evidence beats a departure trail: a recent UAE login
                      outranks older travel or a stopped salary)

Reachability
R0  Enough evidence? fewer than 3 outbound attempt dates, or the latest call is more
                     than tau_label days old                             -> Unknown
R1  Gone dark?       recent_avoidance_flag                               -> Non-Reachable
                     (checked before R2: three fresh unanswered calls outweigh an
                      old confirmed contact)
R2  Reached?         contact_confirmed_flag                              -> Reachable
R3  Dead line?       gone_contact_flag AND the latest call was not a confirmed contact
                                                                         -> Non-Reachable
R4  otherwise                                                            -> Unknown

a2_state = "Deceased", or "<location> - <reachability>"
```

`location_state` and `reachability_state` are emitted as their own columns (computed even
for deceased rows), so either dimension can be used alone. 3 × 3 + 1 = **10 states**.

### What the states mean and the action they point to

| Location \ Reachability | Reachable | Non-Reachable | Unknown |
|---|---|---|---|
| **In Country** | Normal collections: negotiate | In the UAE but dodging or wrong number: skip-trace the number, field visit | Not enough calls yet: keep calling |
| **Skip** | Abroad but answering: remote settlement, international payment route | Left and unreachable: agency / international recovery, legal | Signs of leaving, no call evidence: verify departure (immigration, employer) |
| **Unknown** | Answering, location not evidenced: negotiate, ask | Not answering, no location evidence: skip-trace both | No evidence of either: data gap — treat on other axes |
| **Deceased** | — | — | — : estate / insurance process |

### Diagnostic columns

`location_unknown_reason` (no login on record / recent login but foreign / login older than
the window / other), `reachability_guard_triggered` (insufficient attempts / stale
evidence), the counts behind every flag, and `ptp_flag`, `hardship_flag`, `refusing_n`,
`field_visit_flag` for routing — none of them change the state.

---

## 5. Thresholds

| Threshold (`constant`) | Value | Why |
|---|---|---|
| Location recency (`_TAU_RECENT_D_BY_MODEL_ID`) | **90 days** (60–180), **180 days** (180+) | At 90 days, 90% of cc_180_plus was location Unknown (T29 EDA, 2026-10-07): that segment logs in far less (11.5% have any login before the observation date) |
| Reachability staleness (`_TAU_LABEL_D_BY_MODEL_ID`) | **90 days** (60–180), **180 days** (180+) | Same thin-cadence argument for calls |
| Minimum attempts (`_TAU_A_ATTEMPTS`) | **3 outbound attempt dates** | Fewer is not a pattern; flat across segments |
| Dead-line window (`_TAU_NOT_REACHABLE_N`) | **last 2 attempt dates** | — [CONFIRM] |
| Recent-avoidance window (`_TAU_RECENT_AVOIDANCE_N`) | **last 3 attempt dates, all ringing** | User's threshold (2026-10-22). Ringing only — a dead line is a different failure (wrong number), handled by R3 |
| Salary stop for departure (`casa_inflow_stop_gap_d`) | **> 180 days** | — |
| Unknown model_id | falls back to 90 days | soft default |

---

## 6. CC vs RL

| | CC | RL |
|---|---|---|
| Spine / base | `cc_spine` + spell table + `crx_cc_departure_signature` | `crx_rl_a4_spine` + `crx_rl_departure_signature` |
| Travel purchases | card transactions | CASA debit transactions |
| Foreign transaction | last card transaction foreign | cross-border outflow in the `t0` month (FX-leakage feature) |
| Login window | observation month excluded (mid-month dates) | observation month included (month-end dates) |
| DCORE scope | full history | 24-month partition floor before the persona start |
| Deceased sources | DCORE + Way4 block code + demographics | DCORE + demographics (no Way4 equivalent) |

---

## 7. Open questions and known issues (decisions needed)

| # | Issue | Ref |
|---|---|---|
| Q1 | Spine rows can multiply when `cif_id` is re-attached from the spine without `distinct` | O13 |
| Q2 | The DCORE spine schema check looks for `account_id` while the docs say `contract_id`; if wrong, every contact signal is NULL and reachability is all Unknown | O14 |
| Q3 | Way4 deceased joins on the exact observation date — likely why cc_180_plus matched zero rows | O15 |
| Q4 | Demographics deceased has no point-in-time filter and may multiply rows | O16 |
| Q5 | `recent_avoidance_flag` compares a count of ringing *events* (3) with a count of *dates* — several calls on one date break it | O17 |
| Q6 | `contact_confirmed_n` double-counts outbound SUC events that are also on the right-party list (harmless for the flag, wrong as a count) | O18 |
| Q7 | Departure trail mixes windows: travel / salary gap anchored on `t0`, foreign login with no lower bound. With spells deprecated (design review D5), all move to the observation date — the windows need agreeing | DESIGN_REVIEW §6 |
| Q8 | `foreign_login_flag` (departure) and `in_country_flag` read the same latest login; a stale foreign login therefore marks a trail even years later | — |
| Q9 | Inbound calls confirm contact but do not count as attempts; an account that only calls in is Unknown until 3 outbound attempts exist | — |
