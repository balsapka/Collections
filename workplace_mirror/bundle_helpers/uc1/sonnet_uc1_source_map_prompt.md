# UAT Sonnet prompt: UC1 source map (Genesys → CIF → product, and where the 147k conversations go)

Paste everything below the line into the UAT Sonnet session. Run all four model_ids (cc_60_180 first); the
waterfall in S2 is the same for all four apart from the last rows, so it may run once on the full Genesys side.

---

Goal
We use UC1 readings beside the persona, but we do not have a clean picture of the UC1 data chain. Answer three
things, concisely, from the code and the data. Data understanding only: no pipeline, catalog or registry change.

S1 Source and linking (mostly from code and schemas, then confirmed on data)
   - The chain from a Genesys conversation to a UC1 reading: every table in order (`stg_genesys_transcripts`, UC1
     `metadata`, `extracted_signals`, `agent_remarks_extracted_signals`, `proposer_level_observations`,
     `customer_signal_export`, and any we have missed), with grain, key and date field for each.
   - How a conversation gets its `cif_id`: which field (phone/ANI lookup, CRM id from the IVR, agent-entered, other),
     where the lookup table lives, and the share of conversations with no CIF, several CIFs, or a CIF not in the
     bank's customer base.
   - Whether anything identifies the account or product of a conversation: any account / agreement / card / loan
     field, queue, skill, campaign, IVR menu or call type in Genesys or `metadata`. Name each field and its fill rate.
   - Raw vs staging. Raw Genesys transcripts are masked; our `stg_genesys_transcripts` ends 2026-08-29 and UC1
     `metadata` 2026-07-16, while the user knows of 150,000+ transcripts including September and October. From the
     staging node's code and the data: which raw source(s) staging reads; what is masked in raw (text only, or
     the phone / customer ids too) and how staging still gets a CIF (an unmasked id column, a separate lookup
     table, a hashed key, other); when the staging output was last written (partition or file dates) and whether
     it is incremental or a full rebuild. Monthly conversation counts side by side: raw, staging, UC1 `metadata`,
     with the first and last date of each; say which gap is "staging not rerun", which is "UC1 not refreshed",
     and which is filtering (no CIF, masking, dedup).
   - Whether the conversations are all collections calls: split by direction (inbound / outbound) and queue or
     campaign group (collections / service / sales / other), as far as the fields allow.

S2 Why 147,004 conversations in UC1 metadata, but only a share in our spines
   A waterfall of conversations and of CIFs (UC1 metadata, 2026-03-06 .. 07-16; then the same for
   `stg_genesys_transcripts` to its last date), each step with counts and share of the start:
   1. all conversations / distinct CIFs;
   2. no CIF, or CIF not found in the customer base;
   3. CIF with no retail credit product open at the call date;
   4. CIF with a retail product, none delinquent at the call date (current / cured);
   5. delinquent, by product family × DPD bucket at the call date: product = credit card, retail loan (personal
      finance), auto, mortgage / home finance, other retail, non-retail (SME / corporate) if visible; DPD = 1-30,
      31-60, 61-90, 91-180, 181+, written off. A CIF with several products counts once per product (say so), plus a
      second table with one row per conversation using the worst-DPD product;
   6. in the persona obs base for a model_id (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus) at the nearest month
      end on or after the call date;
   7. extracted by UC1 (ledger) and present in `customer_signal_export`.
   Then one table: for conversations NOT in any persona base, product family × DPD bucket, so we can see what the
   other ~X% are (e.g. 1-60 collections, products we do not score, service calls of current customers).

S3 Products within a CIF
   - Share of persona-base accounts (each model_id, 07-31) whose CIF holds more than one delinquent product, and more
     than one product of any status; the common combinations (card + loan, two cards, ...).
   - How UC1 attributes a reading when the CIF has several products: confirm from the UC1 code whether any step is
     account- or product-level, or whether every signal is CIF-level (our current understanding: CIF-level only).
   - Can a conversation be tied to one product? Test, and report the share each method resolves to exactly one
     product among the CIF's delinquent ones:
     (a) a product / account field in Genesys or `metadata` (if S1 finds one);
     (b) the queue / campaign, if it is product-specific;
     (c) DCORE follow-up on the same CIF the same day (± 1 day): the agreement(s) it was logged on — one agreement,
         several, none;
     (d) DCORE promise logged the same day: which agreement; does the promise amount line up with that agreement's
         overdue or instalment (within 10%)?
     (e) repayment amounts mentioned in the transcript (`repayment_specifics:amount_mentioned`, numeric only) against
         each product's overdue / instalment (within 10%): one match, several, none.
   - For multi-product CIFs, how often the readings would plausibly differ by product: e.g. same-day DCORE outcomes
     on two agreements of the CIF that disagree (promise on one, refusal or nothing on the other).

Decided (do not reopen)
- UC1 outputs are taken as the UC1 team delivers them; we only measure.
- Promises are product-dependent (DCORE logs them per agreement): any UC1 promise use needs a product link; S3
  measures whether one exists. No UC1 reading enters A1–A4.
- UC1 metadata ends 2026-07-16; the Genesys store starts about 2026-03-06. DCORE `szconversationid` is not the
  Genesys id (66 of 37,219 July follow-ups matched); try it again only as a check.
- Known numbers to tie out (print first, report mismatches at the top, never adjust): UC1 metadata 147,004
  conversations / 54,176 CIFs; extracted ledger 11,920 conversations.

Rules
- Loading: `catalog.load` only. Reuse `tmp_validation/uc1_refresh/` (store → CIF) and `tmp_validation/uc1_reach/`
  (frame, DCORE loaders); do not rebuild what they give. Product and DPD at the call date from existing prm / feat
  datasets (spines, contract tables); if a product family has no prm source, say so rather than reading raw.
- Temporary catalog entries only in `conf/base/catalog/catalog_tmp_uc1_full.yml`, explicit (no dataset factories).
- model_id = `catalog.load("params:model_id")`, in every output file name.
- Aggregates only: no CIF, account, agreement, conversation, phone or agent ids; no transcript, remark or note text;
  queue / campaign names only as group labels; cells under 10 shown as "<10".
- A part that fails records its error; the rest still runs.
- New tracked folder `tmp_validation/uc1_source_map/`; commit only that folder.

Deliverables
1. The snippet, pushed from UAT, in `tmp_validation/uc1_source_map/`: config block at the top (dates, match windows,
   parts `s1,s2,s3`); results per model_id (`uc1_source_map_<model_id>.json` + `.md`); a README with one command per
   model_id and the S1 field list (table, field, meaning, fill rate).
   Also in the README, before the snippet: ready-to-paste `hdfs dfs` commands the user runs on PROD to see when
   `stg_genesys_transcripts` was last written (e.g. `hdfs dfs -ls -t` on its path, `hdfs dfs -stat "%y"` on the
   newest files / partitions), with the full path taken from the catalog entry; the same for the raw Genesys
   source(s) staging reads and for UC1 `metadata`. Say in one line per command what to read off the output.
2. After the user commits the PROD results: `summary_uc1_source_map.md`, under 100 lines, plain English, in order:
   - a. Tie-out mismatches, or "all match".
   - b. The chain in 5-8 lines: raw Genesys (masked) → staging (how the CIF survives masking, last run) → UC1
     tables → export; where product is or is not known. One table: monthly counts raw / staging / metadata.
   - c. The 147k waterfall as one table, and one line naming the biggest groups outside our spines (product × DPD).
   - d. Multi-product CIFs: share per model_id; whether UC1 is CIF-level only; the best method to tie a conversation
     to a product and its resolution rate; verdict in one line on whether promises from UC1 can be product-attributed.
   - e. What could not be computed, and why.
