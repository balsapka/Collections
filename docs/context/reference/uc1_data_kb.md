# UC1 data knowledge base (call-transcript signals)

Load when a task names UC1 (integration with the persona axes). Describes **what the UC1 data is and
how it is structured**; it does not propose how to use it.

**Evidence labels.** **[V]** = measured on the real file store (PROD runs 2026-11-16, `cc_60_180`;
the table profile is model_id-independent; full numbers in `tmp_validation/uc1_profile/summary.md`).
**[doc]** = from the UC1 team's code/docs (Sam Oliver Schumacher's repo, branch
`origin/eda/explore-dcore` @ `dc75eb7e`, an in-flux EDA branch) — not checked against data.

**Sample warning (read first).** UC1 extraction has so far run on a **sample only**: 11,920 of the
147,004 pooled conversations (8.1%), a purposive, UC2-scoped draw. Every count, prevalence and
coverage figure below is a **sample statistic** and will change on the full run; figures are marked
*(sample)*. Formats, value sets, rules, keys and grain are structural and carry over. The draw was
stratified on the 60-180 population, so 60-180 distributions are taken as broadly representative
until the full run (user, 2026-11-18); §8 lists the extraction-rate differences to check. Legacy-format
extractions are not used by the persona code (user, 2026-11-18). First PROD run of our stated block:
`results/uc1_stated_block.md` §11.

## 1. What UC1 is
- An LLM reads call transcripts (Genesys) and DCORE agent remarks and emits per-conversation
  **signals** (capacity, intent, reason, dispute, request, period, fraud, repayment specifics).
  Intended use (UC1 team): tactic customisation for the individual customer inside an already
  assigned treatment group; UC2 does allocation/triage [doc, `docs/uc1-scope-status.md`].
- UC1 labels are what the customer *said*, not truth; they are time-independent, unlike UC2 risk
  [doc]. The business decision on how outputs are used is pending; allocation is monthly and the
  most recent interaction weighs most [doc].
- Owners: Sam Oliver Schumacher (Group AI, Data & Analytics) builds it; Archita (GRR strategy) owns
  the signal framework; Aanand heads Collections Analytics.

## 2. Where the data is
We read **only** the shared copy
`hdfs://cdpprod/ai_data/sandpit_aacoe/ai_adv/enbd/risk_collections/dev/shared/05_feat/file_store`
(user decision) — never the UC1 team's own write locations. Read with `spark.read.parquet` (no
catalog entries).

```text
Table (paths under root;  | Grain                | Columns / notes           | Size [V] *(sample)*
`current/outputs/`        |                      |                           |
omitted for the last      |                      |                           |
four)                     |                      |                           |
--------------------------+----------------------+---------------------------+-----------------------
`index`                   | 1 row per            | `conversationid`,         | 147,004 rows, 54,176
                          | conversation         | `cif_id` (string),        | CIFs, ~183 agents
                          |                      | `agent_id` (= agent       |
                          |                      | email, never null)        |

`metadata`                | 1 row per            | see §3                    | 147,004 rows (1:1 with
                          | conversation         |                           | index)

`extracted_signals`       | 1 row per extracted  | `conversationid`,         | 11,920 rows, all
                          | conversation         | `signals_json`,           | present in
                          |                      | `model_version` (no       | index/metadata
                          |                      | `extraction_version` in   |
                          |                      | the shared copy)          |

`agent_remarks_extracted_ | 1 row per            | `remark_day_key`,         | 6,118 rows, 5,745
signals`                  | (`remark_day_key`,   | `conversationid`,         | conversations, 6,090
                          | `conversationid`)    | `signals_json`,           | remark days, 1,131
                          |                      | `model_version`,          | CIFs
                          |                      | `extraction_version` (2   |
                          |                      | values)                   |

`uc2/signal_corroboration | per (`cif_id`,       | verdict column            | 9,736 rows, 2,610
`                         | `observation_date`,  | `agree_disagree_abstain`  | CIFs,
                          | `signal`,            |                           | 2026-03-07..2026-07-16
                          | `signal_level`,      |                           |
                          | `feature_name`)      |                           |

`timelines/*`             | —                    | do not exist in the       | —
                          |                      | shared copy (the UC1      |
                          |                      | team's `latest_flags`, `s |
                          |                      | imple_signal_aggregation` |
                          |                      | ,                         |
                          |                      | `signal_level_conflicts`) |
```

`current/` is an append-only ledger without `run_id`; duplicates are prevented by promote-refusal
and selection anti-join, not in-place dedup [doc]. `model_version` = the effective LLM model id;
`extraction_version` = a pipeline identity string, null for older rows [doc]. The persisted
`model_version` can differ from the configured one [doc].

**Keys and grain.** `conversationid` (Genesys id; the latest `updatedat` row is kept per id because
the source inserts a second row when the agent email resolves) joins index/metadata/signals; 0
duplicates [V]. `cif_id` is an 8-digit string (leading-zero preservation unconfirmed).
`remark_day_key = "<cif_id>|YYYY-MM-DD"` from the remark activity day; the collector is deliberately
not in the key (assumes one agent writes per customer-day, unverified). **A conversation maps to a
customer, not to an account/agreement**, so UC1 is CIF-level; there is no account link. Remark days
with no nearby conversation are dropped upstream as `unmapped`; remark rows carry the mapped
`conversationid` [doc]. 52% of remark days have a same-day transcript for the CIF, 62% within 3 days
*(sample)*; remark days range 2021-12-26..2026-10-14, i.e. beyond the call window [V].

## 3. `metadata` columns
Conversation: `conversationid`, `conversationstart` (timestamp; 2026-03-06..2026-07-16 [V]),
`call_duration` (long, seconds = end - start; p50 262 s, p95 779 s; p99 is an artefact of 688,136
[V]), `group_ids` (always null), `cif_id`, `utterance_count` (p50 35 [V]),
`conversation_month_worst_dpd_bucket` (string; max-DPD-rank bucket across the CIF's spine rows in
the call's calendar month; **null for 77.7% [V]**: no spine row for that CIF-month). DPD buckets
seen [V]: `0 DPD`, `1-30 DPD`, `31-60 DPD`, `61-90 DPD`, `91-120 DPD`, `121-150 DPD`, `151-180 DPD`,
`180+ DPD` — the store is **not** limited to 60-180. Rank map: 0 DPD=0, 1-30=1, 31-60=2, 61-90=3,
91-120=4, 121-150=5, 151-180=6, 180+=7 [doc].

Repayment behaviour — **per CIF, repeated on all its conversations; null for 77.5% [V]** (outside
the temporal-overlap gate: the repayment window must overlap the earliest transcript) [doc]:
`entry_rank` (first observed rank per contract, max across contracts), `final_rank` (last observed,
max across contracts), `completeness = entry_rank - final_rank` (positive = net improvement; null if
no contract has more than one observation), `fully_repaid = (final_rank == 0)` over all contracts,
`entry_rank_at_response_delinquent`, `has_current_while_delinquent`, `n_observed_months`,
`first_observed_date`, `last_observed_date`, dynamic `had_product_*` (seen:
`had_product_credit_card`, `had_product_loan`). Assumes unbroken monthly sequences. Values
*(sample)* [V]: `entry_rank` is 0 for 31,833 of 33,084 non-null rows; `final_rank` 7 for 6,442;
`fully_repaid` true 6,481 / false 26,603.

PTP/settlement relative to the call [doc; value sets [V]]. Event time: PTP
`coalesce(dtacceptpromise, dtupdtimestamp, dtpromisestart)`, settlement `coalesce(dtproposedon,
dtauthrizedon)`. `prior` = event < call start (strict), `future` = event > call start (strict),
`within_window` = |calendar-day delta| ≤ 15 (inclusive). Columns:
`has_prior_/has_future_/has_ptp_or_settlement_within_window` (boolean, never null),
`prior_/future_/ptp_within_window_count` and `prior_/future_/settlement_within_window_count` (long),
`nearest_ptp_or_settlement_abs_days` (int; null 23.6%), `nearest_ptp_or_settlement_ts`.
`ptp_30d_has_{broken,fulfilled,other,no_event}` (booleans): from `ptp_trn_promisedetail` rows with
`dtpromise` in `[call - 30 d, call)` (strictly prior); `cstatus` B → broken, F → fulfilled, other
non-null → other; the three can coexist; `no_event` is true iff no event in the window (a
null-`cstatus` event sets none of the three and `no_event` = false). CIF-level, any agreement,
booleans only. *(sample)* no_event 75.0%, any broken 18.2%, any fulfilled 7.6%. These come from the
same DCORE promise tables the A3 pipeline already uses and inherit the DCORE PTP/settlement logging
gap.

## 4. The signals and the `signals_json` format

### 4.1 Signal dictionary (guide v0.2.2, `schema.py`) [doc; levels confirmed in the data [V]]
Eight signals + `notes` (free text; empty in all remark rows, non-empty in 52% of transcript rows
*(sample)*; not for use). Each signal is `"NA"` (not detected; "when in doubt use NA") or a list of
detections.

```text
Signal                | Levels                          | Order (worse  | Definition notes
                      |                                 | → better)     |
----------------------+---------------------------------+---------------+----------------------------
`payment_capacity`    | none, partial, full             | none <        | amount dimension only ("can
                      |                                 | partial <     | they pay?"), no timing;
                      |                                 | full          | independent of intent
                      |                                 |               | (`none` with `payback_full`
                      |                                 |               | is valid)

`payment_intent`      | no_payment, with_delay,         | no_payment <  | what the customer will do;
                      | partial, payback_full           | {with_delay = | "capacity but refusing" =
                      |                                 | partial} <    | no_payment; not-yet-asked =
                      |                                 | payback_full  | NA

`delinquency_reason`  | lost_employment,                | unordered     | why they cannot pay; self-
                      | reduced_employment,             |               | employed = has_employment;
                      | has_employment,                 |               | salary timing is not a
                      | increased_obligations           |               | reason (goes to
                      |                                 |               | `payment_period`);
                      |                                 |               | bank/system failure →
                      |                                 |               | `dispute`

`dispute`             | system_problem,                 | unordered     | customer contests the
                      | customer_scammed, other         |               | debt/charges or blames
                      |                                 |               | failures (system_problem:
                      |                                 |               | bank error, payment not
                      |                                 |               | reflected, auto-debit
                      |                                 |               | failure); no `none` level;
                      |                                 |               | waiver ask = `request`;
                      |                                 |               | customer-volunteered only

`request`             | `detected` (+ `request_type`)   | binary        | asks for something beyond a
                      |                                 |               | standard arrangement; one
                      |                                 |               | detection per distinct
                      |                                 |               | thing requested;
                      |                                 |               | `request_type` is omitted
                      |                                 |               | (not null) when ambiguous;
                      |                                 |               | observed values:
                      |                                 |               | information, restructure,
                      |                                 |               | deferral, waiver,
                      |                                 |               | settlement, escalation,
                      |                                 |               | callback (not in the guide)
                      |                                 |               | [V]

`payment_period`      | salary_cycle_dependent, weeks,  | implied       | time needed to arrange
                      | months_or_longer                | timing scale, | payment;
                      |                                 | not in the    | "immediately/today" → NA;
                      |                                 | rank dict     | salary in 3 weeks gives
                      |                                 |               | both
                      |                                 |               | `salary_cycle_dependent`
                      |                                 |               | and `weeks`

`fraudulent_customer` | detected                        | binary        | "Tier 2 interpreted";
                      |                                 |               | mutually exclusive with
                      |                                 |               | `dispute.customer_scammed`
                      |                                 |               | for the same event; 0 of
                      |                                 |               | 10,483 current-format
                      |                                 |               | transcript rows, <10 of
                      |                                 |               | 6,118 remark rows
                      |                                 |               | *(sample)* [V]

`repayment_specifics` | `amount_mentioned:<n>`,         | n/a           | Stage 2: runs only if
                      | `date_specific:<YYYY-MM-DD>`,   |               | intent, capacity (≠ none),
                      | `plan_structure_mentioned`      |               | period or request fired;
                      |                                 |               | amount = comma-integer or
                      |                                 |               | %, no currency;
                      |                                 |               | `plan_structure_mentioned`
                      |                                 |               | needs a per-period figure
                      |                                 |               | or duration;
                      |                                 |               | `date_specific` = earliest
                      |                                 |               | named date in a single
                      |                                 |               | customer turn, expected to
                      |                                 |               | co-occur with a
                      |                                 |               | `payment_period` level
                      |                                 |               | (enforced in
                      |                                 |               | `signal_permutations()`,
                      |                                 |               | not in the validator)
```

22 enumerated base levels. The **extended draft schema** (`schema_extended.py`: extra reason levels
medical_hardship, bereavement, eosb_transition, salary_delay; extra dispute levels; fields
`institutional_protection`, `safety_flag`, `settlement_structure_preference`) is **not in the data**
[V: every row has exactly the 9 base keys].

Pipeline [doc]: Stage 0 gate (`signal_worthy / no_contact / early_termination /
no_customer_content`; `process:false` outputs matter for agency routing) → Stage 1 (signals 1-7) →
Stage 2 (`repayment_specifics`). Remark path: one customer-day (`remark_date` + numbered lines),
Stage 0 classifier (`customer_stated` proceeds; `agent_action / system_data / ambiguous` stop),
single-shot call, same levels; agent judgement tags alone give NA, agent-suggested amounts/dates are
never signals, hedges/agent characterisation/relative-resolved dates are `low`; remark dedup is one
detection per level (low if supporting lines disagree), unlike transcripts. Remark `payment_period`
is derived from the day-gap to the stated date (<7 d none, ~7-60 `weeks`, >~60 `months_or_longer`).

### 4.2 Two formats in one column, discriminated by `model_version` [V]
```text
                              | Current (`gemma-4-31b-bedrock`) | `legacy`
------------------------------+---------------------------------+------------------------------------
share of transcript rows      | 10,483 (87.9%); remarks: 100%   | 1,437 (12.1%)
*(sample)*                    |                                 |

top level                     | exactly 9 keys (8 signals +     | the same 9 keys
                              | `notes`)                        |

signal value                  | `"NA"` or a list of `{level,    | `"NA"` or a flat string; no
                              | confidence, indexes[,           | confidence, no spans
                              | request_type]}`                 |

multi-values                  | several detection objects       | joined with `", "` (`"partial,
                              |                                 | none"`, `"payback_full,
                              |                                 | with_delay"`, `"detected,
                              |                                 | detected"`,
                              |                                 | `"salary_cycle_dependent,
                              |                                 | weeks"`); order not significant

`repayment_specifics`         | detections such as              | joined string of
                              | `amount_mentioned:2,000`        | `amount_mentioned:1,000` /
                              |                                 | `date_specific:2026-09-25` /
                              |                                 | `plan_structure_mentioned` (up to
                              |                                 | ~150 chars). Amounts contain `,`
                              |                                 | without a space → split on `", "`

`fraudulent_customer`         | list or NA                      | NA in all 1,437 rows
```

0 parse failures in either format; in the current format every signal value is `"NA"` or a list (no
other strings). `confidence ∈ {high, low}` only [V] (the UC1 delivery table later uses
high/medium/low as an aggregation output). `indexes` are `[start, stop]` utterance spans (0-based,
inclusive; ≥1 customer turn per guide, not enforced in code); mostly 1-3 spans per detection. Same
level + same confidence in one transcript = one detection with merged spans; a different level or a
different confidence = a separate detection.

### 4.3 What the sample shows about the signals *(sample)* [V]
- Conversations with a detection (list format, i.e. excluding legacy), of 11,920: capacity 5,829
  (49%), intent 7,398 (62%), delinquency_reason 4,419 (37%), repayment_specifics 4,878 (41%),
  request 3,894 (33%), payment_period 3,743 (31%), dispute 1,780 (15%), fraud 0. Legacy rows add
  non-"NA" values (levels only): capacity ~770, intent ~935, reason ~500, dispute ~375,
  repayment_specifics ~730, request ~675, period ~560. 3,446 conversations (28.9%) have no
  list-format detection (includes all 1,437 legacy rows); 8,474 (71.1%) have at least one.
- Share of detections with `low` confidence: capacity 43% (partial 51%, full 42%, none 3%), intent
  8%, delinquency_reason 12%, dispute 12%, request 2%, payment_period 7%, repayment_specifics 10%.
- Levels (high/low): capacity partial 1,480/1,530, full 1,319/969, none 531/18; intent payback_full
  3,065/394, with_delay 2,132/162, partial 1,667/59, no_payment 139/12; reason has_employment
  1,687/334, lost_employment 1,192/34, increased_obligations 764/156, reduced_employment 575/34;
  dispute system_problem 1,413/190, other 128/20, customer_scammed 64/<10; period
  salary_cycle_dependent 1,843/40, weeks 1,947/213, months_or_longer 143/30; `request_type`
  information 1,412, restructure 990, settlement 570, waiver 506, deferral 481, escalation 170,
  callback 25 (30 detections have none).
- Within-transcript multiple levels of one signal: capacity 0.3%, intent 3.1%, reason 7.9%, period
  12.6%, repayment_specifics 27.6%.
- Co-occurrence (calls with both): capacity & intent 5,789; intent & repayment_specifics 4,825;
  reason & intent 4,241; capacity & repayment_specifics 4,207; reason & capacity 3,811.
- Remarks: intent 2,283 detections (mostly with_delay), request 1,585, repayment_specifics 1,732
  (`date_specific` 94% low), reason 1,431 (has_employment mostly low), capacity only 169 (none 131,
  partial 33).

## 5. Time structure and call-to-call behaviour *(sample)* [V]
- Calls per CIF (all 147k): p50 1, p75 3, p95 8, p99 50; 26,869 of 54,176 CIFs have ≥2 calls, 16,963
  ≥3. Signal-bearing calls: 4,680 CIFs with ≥1, 1,827 (39%) with ≥2; p99 26.
- Consecutive signal-bearing calls are close in time: median 4 days apart, p75 11, p95 50.
- Resolved capacity between consecutive calls (1,703 pairs): same 61.5%, improved 19.4%, worsened
  19.1%; intent (2,628 pairs): 63.6%, 17.5%, 18.9%. Per the UC1 team the movement is partly **what
  the agent asked** (script changes, new remediation products), not customer change.
- On the persona grid, rows with ≥2 resolved calls strictly before the observation date within 90
  days: capacity 628 (46% of rows with ≥1), intent 821 (52%). Among them all calls agree in 57% /
  58%; the latest call equals the most conservative in 80% / 81%; the latest differs from the most
  conservative (almost always better than the worst) in 20% / 19%; window length (60/90/120 d)
  changes this little.

## 6. How UC1 aggregates (UC1 team's logic) [doc]
```text
Step                         | What                               | Status
-----------------------------+------------------------------------+----------------------------------
Phase 1 — within one         | conflict resolution per signal     | signed off (GRR)
transcript                   |                                    |

Phase 2.1 — vs structured    | UC2 corroboration (§7)             | built for 3 statements
data                         |                                    |

Phase 2.2 — vs agent remarks | stability of remark-signals vs     | in progress; transcript has
                             | transcript-signals                 | precedence, remark alone only
                             |                                    | when no transcript exists

Phase 3.1 — Latest /         | latest conversation + Yes/No/none  | designed
Historic consistency         | consistency                        |

Phase 3.2 — simple historic  | modal level + count over a window  | built upstream; tables absent in
                             | (e.g. 90 d); ties → latest         | our shared copy

Phase 3.3 — Estimated value  | time-weighted; confidence =        | open; recency windows to be
+ Confidence                 | diversity of captures (diverse →   | parameterisable; business-rule
                             | LOW)                               | workshop pending
```

**Signed-off conflict rule** (`conflict_resolution.py`): pick the maximum of `(confidence: high >
low; for ordered signals the most conservative level; latest span (max stop, then max start); level
string)`. `repayment_specifics` is resolved slot-wise (`:amount_mentioned`, `:date_specific`,
`:plan_structure_mentioned`); `request_type` creates no conflicts; the other levels are kept as
`conflicting_signals`. The milestone doc says "last observed wins", but the code ranks confidence
and (for capacity/intent) conservatism before recency, matching the sign-off wording. Sam reported
that changing the order of these steps moved results little. Ordered-signal ranks used: capacity
none 0 < partial 1 < full 2; intent no_payment 0 < with_delay 1 = partial 1 < payback_full 2.

UC1 plan for the per-CIF deliverable: 7 signals + 3 `repayment_specifics` levels; columns Supporting
Data (agree/disagree with rationale) · agent_remark_value · Latest · Historic Consistency · Average
value (count) · Estimated value · Confidence (Latest only for repayment_specifics). The full target
table (`data/input/UC1/output_schema.md`): 55 fields per `(cif_id, account_id, observation_date)` —
`persona`, `collection_action` (value sets due **Dec 11**, not yet defined), `SF_1..4`
(Deterioration, Locatability, Payment credibility, Ability), `last_transcript_date`,
`transcript_count`, then detected/not-detected + high/medium/low confidence pairs for each level of
delinquency_reason, dispute, fraudulent_customer, payment_capacity, payment_intent, payment_period,
repayment_specifics and request.

Meeting decisions (`data/input/uc1_review.md`): conflict hierarchy signed off; worst-DPD for
multi-product customers matches Collections' customer-level logic; the business prefers the customer
view over the conversation view; closure/restructure after a remediation solution should generally
read as resolution, not "unknown". Open: time aggregation / recency windows (workshop); validation
design (stronger-LLM reference on ≈2k extractions + 50-150 human labels; reusing PCA labels rejected
as circular); signal co-occurrence is of interest where *unexpected* and cohort-segmented.

## 7. Corroboration (UC1 team's check of UC1 statements against our UC2 features) [doc; cells [V]]
Scope: `delinquency_reason:lost_employment`, `payment_capacity:none`, `payment_capacity:full` only.
Verdict Agree / Disagree / Abstain = consistent / inconsistent / cannot see — **not accuracy**;
Abstain dominates. Evidence as of the last month-end before the call month (1-2 months old). Tally:
one vote per independent check, no weights (decision 2026-11-04); same-key same-day conflicting
verdicts collapse to Abstain; F4 (collector note) is non-independent and not published; F1 was
replaced by F7 (2026-11-06).

```text
Check | Feature                         | Level           | Rule                  | Cells *(sample)*
      |                                 |                 |                       | [V]
------+---------------------------------+-----------------+-----------------------+------------------
F7    | `sal_recent_3m_avg_aed`,        | lost_employment | Disagree if recent    | Agree 290 /
      | `sal_earlier_6m_avg_aed`        |                 | salary > 0; Agree if  | Disagree 496 /
      |                                 |                 | earlier > 0 and       | Abstain 439
      |                                 |                 | recent 0              |

F2    | `a1_state`, `a1_points_total`   | none / full     | none: Agree if low &  | none 14 / 10 /
      | (our A1)                        |                 | points ≤ 0, Disagree  | 525; full:
      |                                 |                 | if moderate/high;     | Disagree 59 /
      |                                 |                 | full: Disagree only   | Abstain 2,229
      |                                 |                 | if low                |

F3    | `casa_balance`                  | none            | Agree < AED 500,      | 334 / <10 / 214
      |                                 |                 | Disagree ≥ AED 10,000 |
      |                                 |                 | (fixed amounts)       |

F5    | `returned_events_3m`            | none / full     | none: Agree if ≥ 1;   | none 117 / 0 /
      |                                 |                 | full: Disagree if ≥ 1 | 432; full:
      |                                 |                 |                       | Disagree 353 /
      |                                 |                 |                       | Abstain 1,935

F6    | `ptp_broken_rate_3m`            | full            | Disagree if rate ≥    | Disagree 32 /
      |                                 |                 | 0.5                   | Abstain 2,256
```

UC1 team's own findings [doc]: F7 Disagree does not separate said vs not-said (40.5% vs 41.4%);
salary verdicts change for 21-38% of judged conversations when re-read three months later; possible
double-counting across checks (F2 is built on the same salary/balance/failed-payment inputs as
F3/F5/F7) is unconfirmed. **F2 reads our own A1 state**, so UC1 capacity is partly validated against
our own axis.

## 8. Selection and coverage *(sample)* [V]
**What selected the 11,920 extracted calls** (rate of calls with ≥1 list-format detection): by DPD
bucket of the call month — 61-90 36%, 91-120 44%, 121-150 44%, 151-180 40%, 180+ 27%, 31-60 18%,
1-30 7%, 0 DPD 6%, none 4%; by call month — Mar-May ~3%, Jun 6.9%, **Jul 22%**; PTP history — any
prior PTP/settlement 7.4% vs none 2.3%; `ptp_30d` broken 10.2%, other 10.8%, fulfilled 9.0%, no
event 4.4%; repayment behaviour present 11.9% vs absent 4.0%; CIFs with 6+ calls 7.9% vs 1 call
2.9%; very short calls (<60 s) 0.9%, <10 utterances 1.8%. Upstream the draw was stratified by entry
rank, direction and product, UC2-scoped (spine DPD 60-180 at selection), and anti-joined against the
extraction ledger; ~44% of the 147k corpus does not map to UC2 customers [doc].

**Reach on the persona spine (`cc_60_180`; 128,927 account × month-end rows, 42,508 CIFs,
2026-01..08; calls exist only 2026-03-06..2026-07-16).** Share of rows with a usable (≥1 list-format
detection) call strictly before the observation date within 30/60/90/120/180 days: 0.2% / 0.8% /
1.4% / 1.8% / 2.2% (capacity 0.1 / 0.6 / 1.1 / 1.4 / 1.6%; intent 0.2 / 0.7 / 1.2 / 1.6 / 1.9%);
remark days within 90 d 0.7%. By A2 `reachability_state` (any, 90 d): Reachable 1,018 of 33,355 rows
(3.1%), Non-Reachable 763 of 81,561 (0.9%), Unknown 54 of 14,011 (0.4%) — **42% of reached rows are
A2 Non-Reachable** (Genesys calls and DCORE contact outcomes are different channels; A2 reads
DCORE). Only 14% of the file-store CIFs are in this spine; for those, a call of any kind (all 147k
pooled calls, extracted or not) lies within 90 days before the observation date for 44% of rows, so
even full extraction leaves call-based reach at single-digit percent of spine rows. Other model_ids'
reach is not measured.

## 9. Raw transcript source (context) [doc]
`AI_RDV_IVR_GROUP_DB.FR_RECORDED_TRANSCRIPTS_RAW_MONGO`: a Mongo extract appended as rows (1-2 per
`conversationid`), pre-filtered `fetchedtranscript=true`; 299,702 rows → 162,427 after dedup (the
raw table; our `index` holds 147,004 conversations). Fields include `conversationid`, `cif_id`,
`conversationstart/end`, `originatingdirection` (inbound/outbound), `agentemailid` (~54% populated
in raw rows), `transcript_decrypt` (the NLP text). Text is never used or stored in our repo.

## 10. Caveats
1. LLM output with **no ground truth**; the validation plan is not executed; the UC1 team's
   dashboard odds ratios are exploratory and not significant.
2. Agent questioning shapes what is observable; script changes shift distributions; remark evidence
   is second-hand.
3. The sample is purposive and UC2-scoped; signal rates are not population rates.
4. Two output formats; `model_version` can mix; unseen future versions are possible.
5. CIF-level only; one conversation may concern several agreements; no account link.
6. The PTP/repayment-behaviour metadata columns derive from DCORE/spine data we already use.
7. UC1 coverage is conditional on a call having happened; it cannot describe the unreached
   (`personas.md` §6).
8. UC1 team's risks: borrowed LLM token / no official production access; Model Risk (CBUAE) not
   consulted; hurdle/HMM uncertainty work is design/theory only, nothing fitted; milestone
   checkmarks and RFC "delivered" lists disagree on status.
9. Failure modes the UC1 team found on 20 reviewed early extractions (17 with failures):
   agent-speech misattribution, template artefacts, temporal-reasoning errors, inference instead of
   extraction. The current guide and Stage 0 were the response; not re-evaluated.

## 11. Not measured (settle on the full run)
Spine reach for `cc_180_plus` and `rl_*`; whether full extraction changes the legacy share,
confidence mix or detection rates; agent effects (same agent across customers); any
signal-vs-outcome relationship (no outcome join has been run); the `Unknown`-reason split of A2 for
reached rows.
