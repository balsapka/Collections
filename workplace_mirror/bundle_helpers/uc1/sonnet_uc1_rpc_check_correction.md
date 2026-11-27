# Correction to paste into the running UAT Sonnet RPC-check session

Paste everything below the line into the Sonnet session running `tmp_validation/uc1_rpc_check/`.

---

Correction to the prompt (no need to restart; fold it in where it matters):
- The prompt says Genesys runs until before August and PCA from August on. That is wrong. A source-map run on PROD
  (cc_60_180, 2026-11-27) found raw Genesys and `stg_genesys_transcripts` both run to 2026-09-29 (staging rebuilt
  2026-11-12; ~64k August-September conversations UC1 never saw). PCA (`stg_pca_transcripts`) is 100% outbound,
  `financial_remediation` only (13% of raw PCA), CIF = `customer_id` direct, no `contact_id` / queue,
  `conversationstart` NULL (use the conversation date it does have, and say which). Only October-November are
  PCA-only.
- Genesys links to the CIF via `conversationid → fr_genesys_interactions.contact_id → col_trn_agreement.iagreementseqno
  → szcustomerid` (inner join: ~94k valid conversations without `contact_id` never reach staging). Report that loss
  under R3, and note in R2 that a transcript "without a CIF" cannot exist in staging by construction.
- In R2 and R4 treat Genesys and PCA as overlapping sources for August-September, not a hand-over; report calls in
  both (same CIF and day). The R3 "hand-over" item becomes: overlap months, and the first PCA-only month.
- The source-map run saw 99% of staged Genesys as "inbound"; that reading is under check. Don't rely on the direction
  field to separate inbound from outbound until you have checked its raw values; if you use it, show them.
