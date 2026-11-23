# UAT Sonnet prompt: UC1 signal export: quick coverage and sample check

Paste everything below the line into the UAT Sonnet session (self-contained: catalog entries and table layout included). Run this before the full exploration prompt
(`sonnet_uc1_full_data_prompt.md`): the current export covers only about 10k conversations and will be refreshed in
the coming days.

---

Goal
The UC1 team's new tables (`.../05_feat/file_store/current/outputs/timelines/`: official `customer_signal_export`
and `proposer_level_observations`) still cover only about 10k conversations. Before any deep analysis, a quick
read: who is covered, and is this sample good enough to make strategic calls on how UC1 joins the persona (fill
inside A1 Unknown / A3 no_promise, discrepancy flags, treatment hints, context), or must we wait for the refresh?
Counts and shares only; no outcome modelling beyond the one selection check (Q5).

New datasets (not in the repo or the catalog yet)
Add this file as it is: `conf/base/catalog/catalog_tmp_uc1_cov.yml`. It uses the path pattern of the existing
`crx_uc1_simple_signal_aggregation` entry, which reads the same folder and works in PROD (no dataset factories: the
workplace Kedro does not resolve them):

```yaml
# Temporary (UC1 quick coverage check); removed in the cleanup.
crx_uc1_customer_signal_export:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/timelines/customer_signal_export"

crx_uc1_proposer_level_observations:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/timelines/proposer_level_observations"
```

The literal PROD folder is
`hdfs://cdpprod/ai_data/sandpit_aacoe/ai_adv/enbd/risk_collections/dev/shared/05_feat/file_store/current/outputs/timelines/<name>`.
The snippet prints both resolved file paths first and stops with a clear message if they differ from it or the load
fails (then the user checks `hdfs dfs -ls` on the literal folder). If the folders are not parquet, say what they
are and read them accordingly.

What the two tables hold (from the UC1 team's description):
- `customer_signal_export`: one row per `cif_id` × `signal` at one `snapshot_date`, overwritten on each run. Each
  customer with any observation has 10 rows: 7 categorical signals (payment_capacity, payment_intent,
  delinquency_reason, payment_period, dispute, request, fraudulent_customer) and 3 repayment slots
  (`repayment_specifics:amount_mentioned`, `:date_specific`, `:plan_structure_mentioned`). Columns: `snapshot_date`,
  `cif_id` (string), `signal`, `estimated_value` (the headline level; tied levels joined by `|`; `not-detected`),
  `confidence` (HIGH / MEDIUM / LOW / N/A), `latest_value`, `agent_remark_value`, `average_value`, `average_count`,
  `historic_consistency`, `supporting_data`. Customers with no observation have no rows.
- `proposer_level_observations`: the evidence behind it, partitioned by `snapshot_date`
  (`.../proposer_level_observations/snapshot_date=YYYY-MM-DD/`). Each partition holds the full history up to its
  own date: filter to one partition, never add rows across partitions. One row per `cif_id` × `observation_id`
  (one customer on one calendar day, `cif_id|YYYY-MM-DD`) × `signal` × `source` (`transcript` / `remark`) ×
  `level`. Columns used here: `snapshot_date`, `cif_id`, `observation_id`, `observed_at` (midnight of the day),
  `signal`, `source`, `level`. No conversation id: count conversations from `crx_uc1_metadata` if needed.

Decided, to follow
- model_ids: all four (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus). Our book per model = crx_<p>_obs_base.
- UC2 persona = the combination of the four axis states at a month end: A1 (crx_<p>_a1_ability), A2
  (crx_<p>_a2_locatability), A3 (crx_<p>_a3_payment_credibility), A4 (crx_<p>_a4_deterioration). Persisted
  outputs as they are; say which state column you read from each.
- A CIF is covered at a month end if it has any observation in `proposer_level_observations` (latest partition
  only; never add rows across partitions) dated strictly before the month end; also report "ever, up to the
  snapshot". Split transcript vs remark wherever cheap.
- Bar the later decisions need: n ≥ 100 account-months per cell, in both products. Use it to judge the sample.

Questions
Q1 Size. Distinct CIFs, customer-days, and conversations (if countable; say from which table) in the export and in
   the evidence table; snapshot_date; date range of observations; observations per month, transcript vs remark.
Q2 Who they are. Share of UC1 CIFs found in each of the four obs bases (any month, and at the snapshot month end),
   and in none. For the CIFs in none: what they hold (cards, personal / auto / other loans, mortgage, CASA only),
   and whether they are current or delinquent at the snapshot, from whatever product / DPD source is in the
   catalog (say which). Product types inside our bases: card product and loan product type (find the columns;
   say which), covered vs book.
Q3 Coverage of the book. Per model_id and month end: account-months and accounts covered, and share of the book;
   by DPD band. At the snapshot: share with a non-`not-detected` estimate for payment_capacity and payment_intent,
   and HIGH confidence among them.
Q4 Persona coverage. At the latest month end with coverage (and pooled over the month ends since coverage
   starts): every observed persona combination (A1 × A2 × A3 × A4), its book size, covered n and share. Then:
   - how many personas exist, how many have ≥ 1 / ≥ 30 / ≥ 100 covered account-months, and what share of the
     book sits in personas reaching 100;
   - the same per single axis state (A1 Unknown, A3 no_promise, ... per model_id), since the fill and flag
     decisions are read inside one state;
   - covered mix vs book mix per axis state (pp difference), and the largest gaps.
Q5 Selection, in one table per model_id: within each A3 level and each A1 state, paid_due over the next month
   (as the A3 results run) of covered vs not-covered account-months. Plus who gets a conversation: covered share
   by DPD band, A2 state and A4 state (are the called customers the reachable, early or deteriorating ones?).
Q6 Readiness. For each integration job, can this sample support a decision now? A job is supportable if its target
   cells reach n ≥ 100 in both products of a book (60-180 or 180+):
   - fill A1 Unknown by stated capacity (able / partly / not stated / unable cells inside A1 Unknown);
   - fill A3 no_promise by stated intent (payback_full / partly-or-later / no_payment cells inside no_promise);
   - flags: transcript promise with no DCORE promise on the CIF within ±7 days; stated dispute with the A3
     dispute flag false;
   - treatment: request / reason / period counts by A1 × A3.
   Also the projection: if the refresh covers all calls in `crx_uc1_metadata` (legacy-only extractions dropped),
   how many covered account-months per cell would there be (scale by calls per CIF, or count CIFs with any call)?

Rules
catalog.load only (the two new tables through the temporary entries above); model_id =
catalog.load("params:model_id"), in every output file name. Aggregates only: no account / CIF / conversation / agent
ids, no free text; cells under 10 as "<10". A question that fails records its error and the rest still runs.
Literal date filters right after catalog.load; scope UC1 tables to the model's CIFs first (except Q2's "in none");
broadcast small tables; no row-level collect. New tracked folder `tmp_validation/uc1_cov/`; commit only that folder
and the temporary catalog file. No pipeline, other catalog or registry change.

Deliverables
1. Snippet + README_uc1_cov.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_uc1_cov_<model_id>.md.
3. Back in UAT: summary_uc1_cov.md, pasted back to Claude. All model_ids together, one table per question with a
   model_id column, numbers only inside tables, under 200 lines (the full persona list stays in the results files;
   the summary shows the top 20 personas by book size and the counts in Q4). End with verdict lines:
   - how big the sample is and who it covers (Q1, Q2);
   - coverage of the book at 60-180 and 180+ (Q3);
   - how many personas are usable (n ≥ 100) and what share of the book they hold (Q4);
   - is the sample selected, and in which direction (Q5);
   - per integration job: decide now / wait for the refresh / will stay too thin even after a full run (Q6);
   - overall: good enough for strategic calls on integration, yes or no, and what the refresh must add.
