# Terminal transcription: retail.collections.risk_profiling

Branch: `feature/persona_refactor`. Order is chronological: IMG_9541, then IMG_9543 and IMG_9544 (overlap merged).

---

## Part 1: Genesys vs PCA (IMG_9541, 4:59–5:00 AM)

Visible file: `src > enbd_collections > pipelines > retail_loans > spine.py > _build_spine_pipeline`

- Our `uc1_stated` pipeline doesn't read transcripts at all. It reads the UC1 team's outputs from the shared file store.
- The UC1 team's extraction presumably starts from the decrypted staging or primary output. I haven't confirmed that, because their code isn't in this repo.
- Decryption only gives you a plain-text string. Nothing in this repo splits it into agent and customer utterances. The `parse_transcript()` that `Transcript.from_utterance_dicts()` mentions isn't defined here.

If you need to work on raw transcripts yourself, read `prm_transcripts` and don't re-decrypt. It needs the Spark `mongo_decrypt` function and access to PROD, so it won't run in this environment.

I can find where the utterance split should go if you want that.

*Baked for 7s · done 4:59 AM*

> what is the difference between genesys and PCA

*Ran 1 shell command*

Both are staged into the same output schema, so `prm_transcripts` can union them. They differ in where the data comes from and how it's built. This is from the staging code, so the business-level difference between the two systems is my inference.

| | Genesys (`stg_genesys_transcripts`) | PCA (`stg_pca_transcripts`) |
|---|---|---|
| Source table | `ai_rdv_ivr_group_db.fr_recorded_transcripts_raw_mongo` (Mongo copy of recorded calls) | `ai_tdv_ccoanalytics_group_public.conversations`, joined to `agent` and `fr_calls` (CCO Analytics) |
| Text decrypted | `transcript` | `refined_transcript_text`, which is the refined version. The agent email is also decrypted. |
| Decryption | One AES key, selected by `src_sys_name`, `dbname` and `iv`, applied with the `mongo_decrypt` Spark expression | An AES key and a separate IV (`AES_KEY_BASE64_BNK`, `AES_IV_BASE64`) applied with `decrypt_udf`. The node fails loudly unless there is exactly one key row and one IV row. |
| Filter | Valid (`invalidconversationid` not 'true') and fetched (`fetchedtranscript = TRUE`) | `parent_category = financial_remediation` and `status = completed` |
| Dedup | Mongo duplicates collapsed to the latest `updatedat` per `conversationid` | One agent row per id (latest `updated_at`) and one `fr_calls` row per conversation (latest `audit_date`) |
| CIF bridge | `conversationid → fr_genesys_interactions.contact_id → col_trn_agreement.iagreementseqno → szcustomerid` | Direct: `customer_id` is the CIF |
| `call_duration` | NULL | Populated from `fr_calls` |
| `conversationstart` | Passed through | NULL (still pending) |
| `agentemailid` | Passed through | Decrypted from `agent.email` |
| `source` | 'GENESYS' | 'PCA' |

- **Maturity:** the PCA node's docstring calls it work in progress. Only conversations is fully mapped, and `conversationstart` is NULL. Check this before trusting PCA for anything that needs call start time.
- **Scope:** PCA keeps only `financial_remediation` conversations, which is a collections-type category. Genesys has no category filter, so it covers all fetched recorded calls.
- **Duration:** only PCA rows carry a `call_duration`. Any feature that needs duration will be NULL for Genesys rows.
- **Consumers:** use the `source` column if you need to separate the two.

I haven't verified how much the two sources overlap, or whether the same call can appear in both. That would need PROD data.

*Cooked for 11s · done 5:00 AM*

---

## Part 2: cc_60_180 results (IMG_9543 and IMG_9544, done 6:37 AM)

> for which model ids I should run this

*Churned for 8s · done 6:16 AM*

> cc 60 180 rsults are in

*Ran 6 shell commands*

The `cc_60_180` run finished with no errors, and the tie-out matched (147,004 conversations, 54,176 CIFs, 11,920 ledger conversations).

### The chain

- Genesys is not over before August. Raw and staging both run to 2026-09-29. Staging was rebuilt on 2026-11-12, so it holds about 64k August–September conversations that UC1 metadata (last refreshed 2026-11-16, ending 07-16) never saw. Only October and November are PCA-only.
- Where the conversations go.

| Step | Conversations |
|---|---|
| Raw mongo | 359,910 |
| Valid and fetched | 333,715 |
| Resolved to a CIF | 239,233 |
| In UC1 metadata | 147,004 |

- Why they drop.
  - 94,260 valid conversations have no `contact_id`, meaning no agreement was logged.
  - 222 have a `contact_id` that isn't in `col_trn_agreement`.
  - 92,229 are staged but not in UC1 metadata. About 78k of those are after 07-16; the other 14k are March–June conversations that UC1 left out.
- UC1 metadata CIFs. Every UC1 metadata conversation has a CIF, because staging inner-joins to the agreements.

### Who calls

- Direction. 99% of staged conversations are inbound; only 0.9% are outbound.
- Queue groups. The keyword groups are useless. Every queue lands in "other" (the raw table has 7.7% "service", but none of those reach staging). I need the real queue labels to say which are collections.
- PCA. It is 100% outbound, and only 13% of raw PCA conversations survive the `financial_remediation` filter.

### The waterfall (UC1 metadata)

- Customers. 76.6% have an open retail product at the call date, 28.3% are delinquent, and 48.3% are open and current.
- Delinquent calls. Most are 1–30 DPD. Cards at 61+ DPD are about 1.5k conversations.
- `cc_60_180` base. Only 1,013 conversations (0.7%) are in it, and 583 of those were extracted and are in the export.
- Persona CIFs. 26.5% at the 07-31 month end were reached by a conversation, and only 5.1% by an extracted one.
- PCA. It reaches 1.5% of persona CIFs.

### Tying a conversation to a product (among conversations whose CIF has 2+ delinquent products)

| Method | Resolves to one product |
|---|---|
| Agreement behind `contact_id`, family level | 72.7% |
| Agreement behind `contact_id`, account level | 25.4% (74.6% none, likely cards) |
| Queue / campaign name | 44.5% |
| DCORE follow-up within ±1 day | 54.6% (persona scope only) |
| Promise on the same day | 17.8% (DCORE promise logged) or 7.7% (A3 promise events) |
| Promise amount within 10% of overdue or instalment | 0% |
| Transcript amount | 1.2% |

- Verdict. Genesys can be tied to a family (about 73% with the `contact_id` agreement, and 20% resolve to several), but UC1 promises can't be product-attributed. PCA has no `contact_id` or queue at all, so it's weaker still.
- Multi-product CIFs. 17.9% of `cc_60_180` accounts have more than one delinquent product. Same-day DCORE outcomes on two agreements disagree on a promise in 0.8% of cases.

### What I don't trust yet

- `other_retail` rows. 59.8% of the product rows come from the `col_trn_agreement` snapshot as `other_retail`. That bucket probably includes unmapped portfolio codes. It inflates "open product" (66% of persona accounts show more than one) and steps 3–4 of the waterfall. The own-account check is clean, though: 0% of the base's own cards are missing as delinquent.
- Method a2. The account-level match is low because the agreement's legacy number doesn't match the contract id for cards.
- Table formatting. A `|` in the "not in base" table broke its layout. I fixed it by joining with `/` instead.

I added a table of the `col_trn_agreement` snapshot by portfolio code, product type, status and mapped family, so the `other_retail` bucket can be read directly. It is untested.

I haven't written `summary_uc1_source_map.md` yet. It waits for the other three models. I changed the snippet after your run, and it still passes `py_compile`, `black` and `pylint`. Run `rl_60_180` next with `main(catalog, parts=("s2", "s3"))`.

Can you give me the queue and campaign labels? I can then group them and say how many conversations are collections, which would settle the inbound-versus-collections question.

*Cooked for 1m 11s · done 6:37 AM*
