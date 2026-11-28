# UAT Sonnet prompt: UC1 on the collector card, EDA (which stated fields to keep, merge or drop)

Paste everything below the line into the UAT Sonnet session. Run cc_60_180 first, then rl_60_180. Skip 180+ (UC1
reads almost no 180+ customers).

---

Goal
We plan to show a few UC1 fields on the collector card: what the customer said, beside the persona. This job
decides which fields earn a row. Five questions:
- E1 Do two fields say the same thing (then one leaves the card)? With it E2: which level pairs are unexpected.
- E3 How stable is each field from one call to the next?
- E4 How do "what the customer said" and "what the data shows" line up, and how large is each cell?
- E5 Do the values of a field differ on outcomes other than payment?
- E9 Does a customer-level reading fit each account of a customer with several products?
Exploration only: no change to the pipeline, the persona, another catalog file or the registry. The job must rerun
unchanged when UC1 has read more calls (derive month ends and date ranges from the data).

Decisions already made (do not reopen)
- Two views. Card view = `crx_uc1_customer_signal_export` (`estimated_value` at its `snapshot_date`; print the
  date) with the persona at the same month end. Call view = the per-call values (`crx_uc1_extracted_signals`) with
  the persona at the month end of the call's month, pooled over all month ends that have persona output.
- Persona = `crx_persona.master` output of `<model_id>.persona_e2e` (name the dataset you load). Code axis names
  differ from display names: in code A1 = ability, A4 = deterioration. Use the display names (Deterioration,
  Locatability, Credibility, Ability) in the summary.
- Signals: `delinquency_reason`, `payment_capacity`, `payment_intent`, `payment_period`, `repayment_specifics`
  (three slots), `request`, `dispute`. Leave out `fraudulent_customer`.
- Values as they are. A tie (`|` in `estimated_value`), `not-detected` and `N/A` are their own rows, never forced
  into a level.
- UC1's `confidence` is not used: no filter, no split, no verdict built on it. It is UC1's own measure of how
  clearly one level wins, and most stated values are LOW. Print its distribution per signal once, beside the
  tie-outs, and nothing more.
- Reading age (snapshot or month end minus the last call that carried the signal): 0-30, 31-90, 91-180, over 180
  days. Every card-view table also by age band.
- What counts (config block): a difference counts when it is at least 5 points, both cells have at least 100
  customers and its 95% interval excludes 0. "Same" needs the interval inside +-5 points. Anything else is "too
  thin", never "no difference". Every table shows n and the interval.
- Level maps for E4 (config block): capacity full / partial / none = can pay in full / can pay part / cannot pay
  now; intent payback_full, partial, with_delay = will pay; no_payment = did not offer to pay.
- Reference figures from UC1's own knowledge base (their sample to 2026-07-16; report if you are far off, do not
  force a match): consecutive calls with a value, capacity 1,703 pairs, same 61.5%; intent 2,628 pairs, same 63.6%;
  median gap 4 days; calls carrying both capacity and intent 5,789.

Part e1 (+ e2): overlap between fields
All pairs of signals, call view (calls carrying both) and card view (customers with both): level crosstab with
counts and row %, Cramér's V (bias-corrected) and, per level pair, lift with n (lift of 2 or more with n of 100 or
more is "unexpected": list those). Reading per pair: V of 0.5 or more = "say the same thing" (our judgement; show
V); name the field that would add least if one had to go.

Part e3: stability between calls
Consecutive calls of one customer that both carry the signal: same / changed and the level-to-level table, by gap
(0-7, 8-30, 31-90, over 90 days), by same agent against a different agent (`agent_id` in the UC1 index), and by
calendar month of the second call. `script_launch_dates` in the config is
empty; if the user fills it, add before / after each date. Reading per signal: "stable" when at least 80% stay the
same at gaps up to 30 days (our judgement), else "moves": then say whether it moves less with the same agent.

Part e4: said against data
Build two fields in the snippet only (config tables, not in any pipeline):
- Ability: stated capacity x Ability (High / Moderate / Low / Unknown). Cells: Matches; Says more than data shows
  (full x Low); Says less than data shows (cannot pay x High or Moderate); Data can't see income (Unknown).
- Promises: stated intent x promise record (Credibility High or Moderate / Credibility Low with promises on record
  / no promise on record; from `crx_<p>_a3_promise_events`, `<p>` = cc / rl). In the call view use only promises
  made strictly before the call's date: a promise taken on that same call must not count as the record.
Per field and view: customers per cell, share, which cells reach 100 customers (they can be a pilot subgroup) and
which do not; by product and age band. No payment outcome here.

Part e5: outcomes other than payment
Call view, windows from the call's date. Per signal value against the signal's other values, within product, raw
and standardised over DPD bucket and segment (name the segment field you use from the master):
- another conversation within 30 days (DCORE result class "conversation" of `tmp_validation/uc1_rpc_check/`, or a
  transcript);
- a promise logged within 14 days; of concluded ones, kept;
- after a `request`: a reschedule, settlement or waiver within 60 days;
- after a `dispute`: closed, and days to close;
- at the next month end: rolled / stayed / cured (DPD bucket in the master);
- agency placement within 90 days; a discount or waiver within 90 days.
Where DCORE does not hold an outcome, write "not available" and name what is missing. Reading per value: "differs"
(counts on at least one outcome, same sign in the first and second half of the months), "same everywhere" (every
outcome inside +-5 points: a merge candidate, name the neighbour value), "too thin". Lost job, cannot pay and
dispute are never merge candidates; show their numbers anyway. State the number of comparisons made and how many
count, so chance hits can be judged.

Part e9: does a customer-level reading fit the account?
For accounts in the base whose customer has more than one delinquent product: product family of the customer's last
read call (its `contact_id` agreement, method of the source map run) against the account's family: same / other /
unknown; by signal. Also the share of such customers among all customers with a reading. Reading: other + unknown
over 20% = the card should name the product of the call.

Tie-outs (print first; a mismatch goes to the top of the summary; never adjust numbers to match)
Month end 2026-07-31, 61-180, cards / loans, valid while UC1's read calls end 2026-07-16 (after a UC1 refresh print
the new values and mark them "moved"): accounts 18,397 / 3,728; UC1 reading of any age 19.2% / 18.2% (3,528 / 680);
reading under 90 days 7.1% / 8.2%; Genesys transcript in the last 90 days 10.5% / 13.3%.

Rules
- Loading: `catalog.load` only; never `spark.read` or a path. Reuse `tmp_validation/uc1_reach/` (frame
  `uc1_reach_frame`), `tmp_validation/uc1_refresh/` (Genesys call to CIF) and `tmp_validation/uc1_rpc_check/`
  (result classes) where they give what is needed; do not edit them.
- Catalog: temporary, explicit entries only, in `conf/base/catalog/catalog_tmp_uc1_full.yml` (no dataset-factory
  patterns: the workplace Kedro does not resolve them). No other catalog, pipeline or registry change. None is better.
- `model_id` = `catalog.load("params:model_id")`: never hardcoded, no override argument, in every output file name.
  The user switches model in `globals_dev.yml`.
- Dates: `cc_spine`, `dcore_observation_spine` and `prm_contract` carry mid-month billing dates in PROD: never join
  them on the date (on-or-before, or `last_day` first).
- UC1 is per customer (CIF), the persona per account: count customers, and say how an account row gets its reading.
- Aggregates only in results files and summaries: no account, CIF, agreement, conversation or agent ids or names;
  no transcript, remark or note text; cells under 10 as "<10". Signal levels are vocabulary and may appear.
- A part that fails records its error; the rest still runs. Parts: `e1,e3,e4,e5,e9`.
- New tracked folder `tmp_validation/uc1_card_eda/`; commit only that folder.

Deliverables
1. The snippet in `tmp_validation/uc1_card_eda/`: config block at the top (level maps, cut-offs, windows, age
   bands, `script_launch_dates`, parts); one results pair per model_id (`uc1_card_eda_<model_id>.json` + `.md`),
   tie-outs first; a README with one command per model_id.
2. After the user commits the PROD results: `summary_uc1_card_eda.md`, under 150 lines:
   - a. Tie-outs per model_id, or "all match"; the snapshot date and the month ends used.
   - b. Verdict table, one row per card field (reason, capacity, intent, period, repayment details, request,
     dispute): keep / merge values / show its month / drop / too thin to say, with the one number behind it.
   - c. E1: the V table and the unexpected level pairs. E3: share staying the same by gap, and same against
     different agent.
   - d. E4: the two cell tables with counts, card view and call view; cells that reach 100.
   - e. E5: per signal, the values that differ and on what; merge candidates; the count of comparisons.
   - f. E9: the mismatch share and the reading.
   - g. What could not be computed, and what each missing source would unlock.
