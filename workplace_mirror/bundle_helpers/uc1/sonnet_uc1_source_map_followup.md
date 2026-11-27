# UAT Sonnet follow-up: UC1 source map after the cc_60_180 run

Paste everything below the line into the same UAT Sonnet session that ran `tmp_validation/uc1_source_map/`.

---

Thanks for the cc_60_180 results. Note from a parallel PROD run (RPC check): PCA has no row before 2026-10-01,
so Genesys (to 09-29) and PCA do not overlap; your 'only October-November are PCA-only' stands. Before rl_60_180, fix or explain these, in the same snippet and results files.

F1 Step 6 (in the persona base) looks wrong. 1,013 metadata conversations (0.7%) in the cc_60_180 base does not fit
   your own 26.5% of persona CIFs reached at 07-31, nor our earlier run (32,216 UC1-metadata conversations from CIFs
   scored at 61-180, `tmp_validation/uc1_reach/`). Recount step 6 three ways and show all three: (a) as now; (b) the
   CIF is in the obs base at any month end from March to August; (c) the CIF is in the obs base at the first month
   end on or after the call date, CIF-level (any account of the CIF), not account-level. The RPC check (same day,
   PROD) counted 32,354 staged Genesys conversations on persona CIFs for cards and 6,376 for loans; tie to those. Say which caused the gap
   (month-end match, the obs base's month range, account vs CIF join, other) and use (c) from then on.

F2 Direction. 99% inbound does not fit collections calls, and the RPC check found the raw direction field 100%
   "outbound" in both staging tables. Find which field your count used and why it differs. Show the raw values of the
   direction field(s) you used (Genesys and PCA) with counts, the field's source column, and what each value means
   per the schema or code. If the field is the media direction of a leg, a transfer, or a callback, say so. Recount
   inbound / outbound with the right reading.

F3 Queues. Don't group by keywords. List every distinct queue / campaign / skill name on staged Genesys
   conversations with conversation counts (all, and in the 61-180 persona base by (c)), top 60 by count plus an
   "all other" row; labels only, cells under 10 as "<10". I will mark which are collections.

F4 `other_retail`. From your new table (portfolio code × product type × status × mapped family), map the codes that
   are clearly cards, personal loans, auto, mortgage or non-retail; leave the rest as `unmapped`. Redo waterfall
   steps 3-5 with that mapping and show how far `unmapped` shrinks. List the codes you could not map with counts.

F5 Product link. Your results show each Genesys conversation is tied to an agreement via `contact_id`. Confirm that
   UC1 `metadata` keeps that agreement (or `contact_id`) per conversation, or only the CIF. If it keeps it, the
   UC1 readings could in principle be split by product: say which UC1 tables would need to carry it. Also split
   the method (a1) result: of conversations on 2+ delinquent-product CIFs, the `contact_id` agreement is (i) one of
   the delinquent products, (ii) a current product of the CIF, (iii) a closed one.

Then run rl_60_180, cc_180_plus and rl_180_plus with `parts=("s2", "s3")` and write `summary_uc1_source_map.md` as
in the original deliverables, with F1-F5 folded in (not as an appendix). The summary uses the corrected step 6.
