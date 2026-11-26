# UAT Sonnet prompt: UC1 reach, three details (paste back the answer)

Paste everything below the line into the UAT Sonnet session that ran `tmp_validation/uc1_reach/`.

---

From the PROD results of `tmp_validation/uc1_reach/` (and, for part C, the saved frame `uc1_reach_frame` via
`main(catalog, rebuild=False)` or a pandas load), give me only these, compact, for cc_60_180 and rl_60_180. Same rules
as the run: aggregates only, cells under 10 as "<10", n beside every share.

A. `Q0.flow` and `Q0.chain_cif`, every month end 03-31 .. 08-31 (not only 07-31). Add one line per month: the last
   date in the Genesys store and in UC1 metadata with a call for these CIFs.

B. `Q2.agelimit` (and `Q1.agelimit` if it exists): paid_due next month for non_reachable + unknown, C1 split by the age
   of the stated ability / intent evidence (under 90 days vs 91-180 vs over 180) and of the reason evidence (under 90,
   91-180, over 180), against C3. One row per signal × age band: n, paid_due [95%], difference vs C3 [95%].

C. A new cut from the frame (no rerun of the build): split C3 into C3s = a Genesys store call in the 90 days that UC1
   did not read, and C3r = a right-party contact only (no store call). For non_reachable + unknown, t = 04-30 .. 07-31:
   paid_due and money next month for C1, C1 strong positive, C3s, C3r, C4, and C1 - C3s with intervals (200 account
   resamples). Then the same three rows inside the non-workable pool only (C1, C3s, C3r).

Answer in under 60 lines, tables only, plus one line per part on anything that could not be computed.
