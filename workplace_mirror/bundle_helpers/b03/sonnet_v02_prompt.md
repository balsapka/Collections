# Validation v02: DDS retries

Run it after bundle 03 has built `prm_casa_return_events` in PROD, for `cc_60_180` only. Same flow as v01, with the
folder `tmp_validation/a1_v02/`.

````text
Task: a PROD validation snippet for the CC A1 distress signals. You work in UAT with no data:
you write code and analyse a results file, you never see PROD rows.

Context. Bundle 03 added prm_casa_return_events: the bank's returned-transaction rows from
comp_financial_tran_repos_dly, all CIFs, one row per (tran_id, part_tran_srl_num, tran_date).
A1 distress counts reason_for_excluding in ("CHEQUE RETURNS", "DDS Rejects/Reversal").
v01 found that DDS rows are 100% tran_sub_type=CI, paired debit/credit (codes 445-D /
004-C) on REMITTANCE, with a median of 332 rows per CIF over ~100 days.

Hypotheses:
G1  DDS rows are one failed debit retried, which is real distress: per CIF, the
    debit legs repeat one amount (or a few), arrive at a steady cadence, and the customer's
    CASA balance is below that amount when they happen.
G2  The opposite: DDS rows are bank-side corrections. Amounts vary, the debit is never
    short of balance, and the pattern also shows up for customers who are not delinquent.

A. Write tmp_validation/a1_v02/a1_v02_snippet.py and a README.md.
   Rules (same as v01): catalog.load only; model_id from catalog.load("params:model_id");
   aggregates only, with no ids, card/account numbers, names or narration; top 25 per code
   column; one JSON at context.project_path / "tmp_validation/a1_v02/results_<model_id>.json";
   commit and push only tmp_validation/a1_v02/.
   Datasets: crx_cc_obs_base, prm_casa_return_events, wm_fea_casa_eod_avg_balance,
   crx_cc_a1_ability_b01_check (or the bundle 03 check output).

   Tables (DDS = reason "DDS Rejects/Reversal", debit legs only unless stated; obs-base CIFs,
   last 100 days before the latest observation date):
   u1_amounts (G1/G2)   per CIF: distinct debit amounts, share of debits on the CIF's most
                        common amount, debits per active week. Give p10/p50/p90 of each,
                        and the count of CIFs per band of the "most common amount" share
                        (<50%, 50-80%, 80-100%).
   u2_cadence (G1)      per CIF: the median gap in days between consecutive debit legs,
                        as a histogram (0, 1, 2-6, 7-13, 14-31, 32+).
   u3_balance (G1/G2)   per debit leg: the CASA average balance of the CIF's week
                        (wm_fea_casa_eod_avg_balance) divided by the debit amount, in bands
                        (null, <0.5, 0.5-1, 1-2, 2+). Count legs per band.
   u4_population (G2)   the share of all CIFs in prm_casa_return_events with any DDS row in
                        the last 100 days, vs that share among the obs-base CIFs.

B. Analysis (only when I give you results_cc_60_180.json): for G1-G2 give a verdict
   (CONFIRMED / REJECTED / INCONCLUSIVE), the 3-6 numbers that decide it, and one line on what
   it means for counting DDS as distress. Don't propose code changes. Plain text, under 40
   lines. Save it as tmp_validation/a1_v02/summary.md, then commit and push.
````
