# UC1 source map: summary (all four model_ids)

Sources: `uc1_source_map_<model_id>.md` for cc_60_180, rl_60_180, cc_180_plus, rl_180_plus (PROD, snippet
2026-11-27a, follow-up F1-F5 included). Counts are conversations unless stated. Everything here is data
understanding; no pipeline, A1-A4 or UC1 rule changed.

## a. Tie-out
All match: 147,004 metadata conversations, 54,176 CIFs, 11,920 extracted conversations (cc_60_180 and
rl_60_180; the 180+ runs skipped S1 and the tie-out numbers repeat).

## b. The chain, and where product is known
1. **Raw Genesys, encrypted not masked.** The transcript and the ANI are AES-encrypted (decrypted in staging);
   `conversationid`, `contact_id`, direction, queue, campaign and wrap-up are in clear. 359,910 raw
   conversations, 333,715 valid and fetched.
2. **The CIF comes from the agreement, not a phone lookup.** Staging joins
   `fr_genesys_interactions.contact_id` to `col_trn_agreement.iagreementseqno` and takes `szcustomerid`. 94,260
   valid conversations (28%) have no `contact_id` and never reach staging; 222 have one that is not an
   agreement. Result: 239,233 staged conversations, every one with a CIF (74,756 CIFs). Staging then drops
   `contact_id`.
3. **Staging is a full rebuild** (`overwrite`), last written 2026-11-12, and it runs to 2026-09-29. UC1
   `metadata` was refreshed 2026-11-16 but ends 2026-07-16.
4. **UC1 tables** (`metadata`, `extracted_signals`, remarks, evidence, posteriors, `customer_signal_export`)
   carry the CIF only; no table has an agreement, contact or account column (S3.5). Conversation-grain tables
   join on `conversationid`; the CIF-grain tables (evidence, posteriors, export) do not.
5. **Product is known only before UC1:** the agreement behind `contact_id` (family via `cportfoliocode`) and
   the queue. After UC1 it is gone.
6. **PCA** (October 1 - November 11) gives the CIF directly (`customer_id`) and has no agreement, queue or
   campaign: 51,109 staged, all outbound, only 13% of the 401,685 raw PCA conversations
   (`financial_remediation` + completed; 87% of raw are inbound).

| month | raw interactions | staging | UC1 metadata | PCA staging (raw, all categories) |
|---|---|---|---|---|
| 2026-03 | 38,321 | 32,493 | 28,381 | - |
| 2026-04 | 54,107 | 43,358 | 39,197 | - |
| 2026-05 | 39,680 | 31,238 | 28,534 | - |
| 2026-06 | 52,146 | 39,782 | 36,528 | - |
| 2026-07 | 37,717 | 27,752 | 14,364 | - |
| 2026-08 | 42,850 | 33,402 | - | - |
| 2026-09 | 48,571 | 31,208 | - | - |
| 2026-10 | - | - | - | 33,231 (304,206) |
| 2026-11 (to 11-11) | - | - | - | 17,878 (97,479) |

- **Genesys does not stop before August.** Raw and staging hold about 64,600 August-September conversations
  that UC1 has not read; only October-November are PCA-only.
- **The three gaps.** Staging not rerun: none (staging reaches the raw end). UC1 not refreshed: about 78,000
  of the 92,229 staged conversations that are not in metadata are after 07-16. Filtering: the 94,260 without
  `contact_id`, 26,195 invalid or unfetched, and about 14,000 March-June conversations that are staged but not
  in UC1 (reason not visible).
- **They are collections calls.** The mongo `originatingdirection` of every staged conversation is `outbound`.
  `interactions.direction` is `inbound/outbound` for 81% (a combined value the schema does not explain) and
  `outbound` for 4%. My first reading "99% inbound" was my own label mapping matching `inbound/outbound` as
  inbound: wrong, withdrawn. The queues are collections: `FRESHFLOW` 56% (early delinquency), cards (`XCARDS`,
  `CARDS`) 31%, loans (`XLOANS`) 7%, `PREDUE` 5% (before the due date). Wrap-ups are promise to pay, left
  message, settlement, wrong number.

## c. Where the 147,004 go

Steps 3-5 come from the cc_60_180 run: the card DPD source `prm_billing` is scoped by `model_id`, so the other
runs see fewer cards (33,634 card rows in cc_60_180, 6,481 rl_60_180, 1,409 cc_180_plus, 1,045 rl_180_plus).

| step | conversations | share | CIFs |
|---|---|---|---|
| all UC1 metadata conversations | 147,004 | 100% | 54,176 |
| CIF in the customer base (no CIF: 0) | 147,004 | 100% | 54,176 |
| an open retail product at the call date (overdraft counts) | 112,598 | 76.6% | 41,399 |
| ... none delinquent (current / cured) | 70,960 | 48.3% | 29,343 |
| ... delinquent (1-30 DPD or worse) | 41,638 | 28.3% | 15,771 |
| in the cc_60_180 persona base (6c) | 1,013 | 0.7% | 598 |
| in the rl_60_180 persona base (6c) | 936 | 0.6% | 414 |
| in the cc_180_plus persona base (6c) | 450 | 0.3% | 258 |
| in the rl_180_plus persona base (6c) | 194 | 0.1% | 68 |
| 6c and extracted and in the export (cc60 / rl60 / cc180 / rl180) | 583 / 533 / 148 / 111 | 0.4% / 0.4% / 0.1% / 0.1% | 305 / 232 / 83 / 35 |

- **Step 6 is small because of the month-end match, not the join.** 6c (CIF in the base at the first month end
  on or after the call) = 1,013; 6d (last month end before the call) = 1,733; 6b (CIF in the base at any month
  end March-August) = 26,058 (17.7%, 7,342 CIFs) for cc_60_180, 4,784 rl_60_180, 1,179 cc_180_plus, 848
  rl_180_plus. Callers are mostly early-delinquent: most delinquent calls are 1-30 DPD and the CIF reaches 61+
  later. The earlier 32,216 counted any month end. Conversations carry no account, so the join is by CIF.
- **Biggest groups outside the cc_60_180 base** (worst product): open, none delinquent 48.6%; no open product
  23.6%; card 1-30 DPD 12.5%; loan 1-30 8.1%; auto 1-30 2.6%; card 31-60 2.1%. Delinquent at 61+ DPD: cards
  1,473, retail loans 529 (5b grid, worst-DPD product); "other_retail" at 181+ (about 400) is overdraft.
- **Portfolio codes.** `other_retail` is overdraft (`O` / `OD`, 2.1M open agreements), not an unknown. Only
  code `S` (21,051 agreements, mostly loans) stays `unmapped`; it changes steps 3-5 by 1 conversation.
- **Persona CIFs reached** (07-31, a conversation in 2026-03-06 .. 07-16): cc_60_180 26.5% of 17,854 CIFs,
  rl_60_180 27.0% of 3,338; cc_180_plus 0.1% of 297,178; rl_180_plus 0.3% of 52,374. With an extracted
  conversation: 5.1%, 10.6%, 0.0%, 0.2%. PCA reaches 1.5-1.8% of the 60-180 CIFs and 0.1% of the 180+ ones.
  UC1 touches the 180+ books almost not at all. PCA waterfall: 3.4% no CIF, 8.2% CIF not in the base, 4.9%
  delinquent.

## d. Several products in a CIF, and tying a conversation to one
- **Share of persona accounts whose CIF has more than one delinquent product:** cc_60_180 17.9% (3,289 of
  18,397; card + loan 7.8%, two cards 5.2%); cc_180_plus 19.9% (63,095 of 316,738; two cards 8.2%, card + loan
  5.0%); rl_60_180 66.8% (2,491 of 3,728; card + loan 35.3%); rl_180_plus 53.1% (29,084 of 54,819; card + loan
  28.5%). The rl figures are upper bounds: DCORE overdraft agreements count as products. More than one product
  of any status: 66%, 58%, 93%, 90%; overdraft inflates all. Own-account check: 0-0.7% of base accounts not
  seen as delinquent.
- **UC1 is CIF-level only** (S3.5). No step is account- or product-level.
- **Resolution (CIFs with 2+ delinquent products; 4,777 / 3,520 / 1,623 / 1,538 conversations): exactly one
  product, cc60 / rl60 / cc180 / rl180:**

| method | exactly one product |
|---|---|
| a1 agreement behind `contact_id`, family level | 72.7% / 82.8% / 63.0% / 60.5% |
| a2 same, account level | 25.4% / 30.1% / 64.7% / 43.8% (card account numbers often do not match) |
| b queue names a product (cards, loans) | 44.5% / 48.5% / 44.5% / 44.7% |
| c DCORE follow-up within 1 day (persona scope only) | 54.6% / 31.0% / 11.0% / 12.5% |
| d1 DCORE promise the same day | 17.8% / 4.9% / 2.1% / 1.2% |
| d3 promise amount within 10% of overdue or instalment | 0% / 3.0% / 0% / 0.8% |
| e amount in the transcript within 10% | 1.2% / 1.2% / 2.2% / 1.0% |

- **a1 split** (delinquent product / current / closed / not matchable by account number): cc60 25.4 / 0.4 /
  7.3 / 67.0%; rl60 30.1 / 0.3 / 4.6 / 65.0%; cc180 64.7 / 0.6 / 2.6 / 32.1%; rl180 43.8 / <1 / 3.4 / 52.2%.
- **Would readings differ by product?** Same-day DCORE outcomes on two agreements disagree on a promise in
  0.8% / 0.4% / 0.1% / <10 (cc60 / rl60 / cc180 / rl180) of CIF-days with 2+ agreements; right-party contact
  1.0% / 0.6% / 0.2% / <10. Low.
- **Verdict:** UC1 promises cannot be product-attributed today: UC1 keeps no agreement. The `contact_id`
  agreement gives the product family for 61-83% of multi-product conversations (best method in every run), but
  a UC1 promise needs the agreement added to `metadata`, and for CIF-grain tables to their key. The 180+ bases
  are barely read by UC1, so the question matters mostly for 60-180.

## e. Not computed, and why
- **Card DPD at the call date in the 180+ runs and rl_60_180:** `prm_billing` is scoped by `model_id`, so
  steps 3-5 are taken from cc_60_180 only.
- **Raw table write dates:** the `hdfs dfs` commands in the README must be run by the user; staging
  (2026-11-12) and metadata (2026-11-16) times are known.
- **Product at the call date for overdraft and unmapped agreements:** current snapshot only. SME / corporate
  products: no source.
- **Account-level tie for cards:** the agreement legacy number does not equal the card contract id; needs a
  card contract link.
- **Why about 14,000 March-June staged conversations are missing from UC1:** not visible from our side.
- **Which queues are collections:** all listed queues look collections; the user marks them. The meaning of
  `direction = inbound/outbound` is undocumented.
- **Persona bases across all four models in one table:** they cannot be loaded together.
