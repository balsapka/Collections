# UAT Sonnet prompt: UC1 collector card, follow-up to the gates and EDA runs (plans, handler map, collector spread, handover inside 61-180, reading age)

Paste everything below the line into the UAT Sonnet session. Run cc_60_180 first, then rl_60_180. 180+ is not run.

---

Goal
Your last two jobs (`tmp_validation/uc1_card_gates/`, `tmp_validation/uc1_card_eda/`, summaries of 2026-11-28) left
gaps that decide whether UC1 earns its rows on the collector card. This job closes them:
- Plans: what the `settlement_type` codes are, who proposes a plan and when, and a waiver measure that is not set on
  almost every plan.
- Handler map: name the handler of far more read calls than today's 28% (cards) / 11% (loans).
- Collector spread: is the spread between collectors real or noise once months are pooled?
- Handover inside 61-180: most read calls happened before the customer reached 61 days, so the 98% "another handler"
  mostly compares the early caller with the 61+ collector. Allocation is monthly (one collector holds an account for
  the month): inside 61-180, does that collector make or hear the call?
- Collector reaction (E6) again, with the handler map and plans.
- Reading age: 84% of card-view customers have a value but no call date. Find the date of the evidence.
- Said against data (E4) recounted with the full matrix below.
Exploration only: no change to the pipeline, the persona, another catalog file or the registry. The job must rerun
unchanged when UC1 has read more calls (derive every date range from the data).

Decisions already made (do not reopen)
- Everything in the gates and EDA prompts still holds (conversation = RPC-check class "conversation"; per-call
  values for G2 / E6, `estimated_value` for the card view; persona = `crx_persona.master` output of
  `<model_id>.persona_e2e`; display names Deterioration, Locatability, Credibility, Ability; UC1 `confidence` not
  used; what counts: at least 5 points, cells of 100, 95% interval excludes 0, else "too thin").
- Handler of a DCORE action = `dcore_prm_followup_outcomes.agent_id` (= `szuserid`).
- Plan codes: never guess what a code means. A code gets a meaning only from a code list found in the catalog or
  from the config table `SETTLEMENT_LEVELS`, which the user fills from DCORE ops (empty at first).
- Collector spread: months pooled from 2026-03 to the latest full month, at least 30 rows per collector (config;
  the user has not decided this, so also print how many collectors reach 10, 20 and 30).
- No collector, agent, account, CIF, agreement or conversation id and no e-mail leaves PROD. Collectors appear only
  as counts and quantiles of collector-level figures. The handler map is never written to a results file.

Part s1: plans and waivers (run first)
1. Look for a code list for `settlement_type` in the catalog (DCORE / RPS master or lookup tables). If one exists,
   print code, description and count; descriptions are vocabulary and may appear.
2. Profile each code (cards and loans; plans from 2026-03 and all plans): count; share with an amount agreed below
   the total due and the median discount %; median number of instalments and tenor; share with a schedule in
   `rps_cur_schedule`; share with a waiver row.
3. Plan date and actor: `dcore_prm_settlement_summary` has `proposed_ts` for 35% / 30% and `authorised_ts` for 0%.
   Load raw `rps_cur_header` (name the catalog entry) and give the fill rate of `dtproposedon`, `szproposedby`,
   `szuserid`, `szauthrizedby`. Also give the share of proposers and authorisers who are DCORE conversation users
   (that is, collectors).
4. Waiver: distribution of the waived amount as % of the outstanding, per waiver or fee code if one exists. Propose
   in one line a rule that separates a real concession from routine fee lines. Put it in the config as
   `WAIVER_RULE`, use it in g1b and e6b and name it in the summary; the user may change it.
Until `SETTLEMENT_LEVELS` is filled, g1b and e6b report "any plan" (all codes pooled) and each code on its own.

Part h1: handler map
Map a Genesys agent to a DCORE user: the `agentemailid` local part (before `@`, lower case) = `szuserid` (lower
case). Check whether the UC1 index `agent_id` equals the staging `agentemailid`.
- Validate on read calls where the same-day DCORE conversation row on the CIF gives one handler: agreement rate.
  Last run: 91.6% (n=5,423) cards / 84.4% (n=403) loans.
- Share of read calls with a handler: same-day row only, map only, either. Last run: 28.1% / 11.1%.
- Use the map wherever g2b and e6b need the call's handler. Where the map and the same-day row disagree, take the
  same-day row and count the cases.
Keep the map in memory. If you must save it, use an explicit temporary catalog entry that the cleanup removes.

Part g1b: collector spread, pooled
Per collector, over the pooled months, for conversations on accounts in the base:
- promise follows within 14 days;
- promise amount as % of the outstanding;
- days to the promise date;
- days to the next attempt;
- any plan within 14 days, and each decoded plan type;
- waiver (by `WAIVER_RULE`);
- escalation.
Standardise each collector's figure for their mix of product x DPD bucket x month: the observed figure minus the
figure expected from the base rates of their mix. Report:
- the collector quantiles (p10 / p25 / p50 / p75 / p90), the number of collectors and the share of variance between
  collectors;
- split-half reliability: the correlation across collectors between their figure on odd and on even calendar days
  (Spearman-Brown corrected; only collectors with the minimum in both halves).

Reading: "varies by collector" needs an interquartile range of at least 10 points for a share (25% of the median for
an amount or gap) **and** a reliability of at least 0.5. The same range with a lower reliability reads "spread is
noise". Otherwise "little spread", or "set by rule" (70% or more on one value). These cut-offs are our judgement,
so show the numbers. Who chose a plan: the share proposed by a collector, from part s1.

Part g2b: handover inside 61-180
Anchor = a read call where the customer has an account in 61-180 on the call date. Use the most precise source you
find (a DPD or bucket field in `dcore_prm_allocation_state`, snapshots every 4 days; else in the base at the month
end before the call), say which and print the count. Last run: 1,013 / 936 calls in the base at the call's month
end. Per product:
- the call's handler known (h1): share;
- allocated collector: allocation is monthly, so each account has one collector for the month. Find the field that
  holds it (for example in `dcore_prm_allocation_state`); name it and give its fill rate. Report the share of
  anchors whose call was made by the collector allocated to the account that month. Also report how often that
  collector holds the customer's conversations in the month: cards looked like a dialer (top handler 50%), loans
  like an owner (100%). Only if no allocation field exists, fall back to the top handler of the customer's DCORE
  conversations in the 30 days before the call (at least 60% cards / 80% loans, 2 or more), and say so;
- next conversation: days to it (bands as before), handled by the call's handler, by the allocated collector (if not
  the call's handler), or by someone else;
- already in the remarks: for each signal of the call, a UC1 remark reading on the same CIF within 0-3 days after
  the call (`crx_uc1_proposer_level_observations`, source `remark`, partition at the latest `snapshot_date`). Does
  it name the same level, another level, or is there no remark reading? Say in one line that "no remark reading" is
  not the same as "no remark" (UC1 drops remark days it cannot map).
One line per product: is the person who works the account next someone who did not hear the call?

Part e6b: collector reaction, again
As part e6 of the gates job: per signal value and actor (call's handler on the day; call's handler days 1-14;
another handler days 1-14), the levers in the 14 days after the call. Add "any plan" and each decoded plan type,
and the waiver by `WAIVER_RULE`. Use the h1 handler. Run it twice: on the gates job's anchors (b) and on the g2b
anchors (61-180 on the call date). Same readings ("lost at handover", "travels", "no reaction seen", "too thin"), but
show "another handler only" as its own reading, as you did last time.

Part a1: reading age
For each card-view customer (export `snapshot_date`) and signal: the date of the latest observation that carries the
signal in `crx_uc1_proposer_level_observations` (same partition; any source), its source (transcript / remark) and
whether it names the level shown in `estimated_value`. Age = snapshot minus that date, in bands 0-30, 31-90, 91-180
and over 180 days. Report:
- age bands by source;
- the share where the latest observation names another level than `estimated_value`;
- why customers had no call date last time (one line, with counts);
- the date of the customer's latest conversation of any kind (transcript or DCORE conversation row), as a
  comparison.

Part e4b: said against data, full matrix (card view; uses the a1 ages)
- Ability. "One stated level" means one capacity level (no tie, not `not-detected` or `N/A`); shares use only
  customers with one stated level.

  | Stated capacity | Ability High or Moderate | Ability Low | Ability Unknown |
  |---|---|---|---|
  | full | Matches | Says more than data shows | Data can't see income |
  | partial | Matches | Matches | Data can't see income |
  | none | Says less than data shows | Matches | Data can't see income |

  Customers with no single stated level: a separate count, outside the shares.
- Promises: the cells of the EDA job (High or Moderate / Low with promises on record / no promise on record x will
  pay / did not offer to pay). Shares use only customers with one stated intent level.
- Both fields by product and age band. Mark the cells that reach 100 customers.

Tie-outs (print first; a mismatch goes to the top of the summary; never adjust numbers to match)
Month end 2026-07-31, 61-180, cards / loans, valid while UC1's read calls end 2026-07-16 (after a UC1 refresh, print
the new values and mark them "moved"):
- accounts 18,397 / 3,728;
- UC1 reading of any age, frame definition, 3,525 / 679;
- gates anchors (b) 17,781 / 3,217;
- card-view customers at the export snapshot 4,161 / 728;
- read calls with a same-day DCORE handler 28.1% / 11.1%.

Rules
- Loading: `catalog.load` only; never `spark.read` or a path. Reuse `tmp_validation/uc1_card_gates/`,
  `tmp_validation/uc1_card_eda/`, `tmp_validation/uc1_reach/` (frame `uc1_reach_frame`), `tmp_validation/uc1_refresh/`
  and `tmp_validation/uc1_rpc_check/` by importing their helpers. Do not edit them. The manual 50-account check stays
  in `uc1_card_gates` (`--manual-sample`); do not copy it.
- Catalog: temporary, explicit entries only, in `conf/base/catalog/catalog_tmp_uc1_full.yml` (no dataset-factory
  patterns). No other catalog, pipeline or registry change. None is better.
- `model_id` = `catalog.load("params:model_id")`: never hardcoded, no override argument, in every output file name.
- Dates: `cc_spine`, `dcore_observation_spine` and `prm_contract` carry mid-month billing dates in PROD. Never join
  them on the date (use on-or-before, or `last_day` first). The Spark session is GMT; name the timestamp you use.
- Aggregates only in results files and summaries: no ids, e-mails or names; no transcript, remark or note text;
  cells under 10 shown as "<10". Code, result and queue names are vocabulary and may appear.
- A part that fails records its error and the rest still runs. Parts, in this order: `s1,h1,g1b,g2b,e6b,a1,e4b`.
- New tracked folder `tmp_validation/uc1_card_followup/`; commit only that folder.

Deliverables
1. The snippet in `tmp_validation/uc1_card_followup/`:
   - a config block at the top (`SETTLEMENT_LEVELS` empty, `WAIVER_RULE`, collector minimum, windows, fallback owner cut-offs,
     cut-offs, parts);
   - one results pair per model_id (`uc1_card_followup_<model_id>.json` + `.md`), tie-outs first;
   - a README with one command per model_id and the `settlement_type` code table from part s1 with an empty
     "meaning" column for DCORE ops.
2. After the user commits the PROD results, write `summary_uc1_card_followup.md`, under 150 lines:
   - a. Tie-outs per model_id, or "all match".
   - b. Verdict in five lines:
     - plans: codes known or still open, and who proposes;
     - handler map: coverage before and after;
     - collector spread: which levers really vary by collector;
     - inside 61-180: does the next handler (or the allocated collector) hear the call;
     - E6: any reaction that survives a handover.
   - c. s1: code profile table, plan date and actor fill, `WAIVER_RULE` and what it keeps.
   - d. h1: agreement and coverage.
   - e. g1b: lever x reading per product, with quantiles and reliability, and collectors at 10 / 20 / 30.
   - f. g2b: allocated collector, next handler, already in the remarks, per product.
   - g. e6b: one table per signal for each anchor set, with the reading.
   - h. a1 + e4b: age by source, the full matrices with shares, and what is still missing.
