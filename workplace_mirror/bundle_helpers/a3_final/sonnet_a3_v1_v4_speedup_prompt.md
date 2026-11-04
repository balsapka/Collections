# A3: speed up the V1–V4 snippet (follow-up prompt for the UAT Sonnet)

Send the block below after `sonnet_a3_v1_v4_prompt.md` if the PROD run is too slow (the first run took
over an hour for one model_id). Runs needed now: cc_60_180 and rl_60_180 only; 180+ later, V2 at most.

````text
The A3 V1–V4 snippet took over an hour for one model_id. Make it faster without changing any
definition or output:
- Restrict every DCORE, instalment and transaction read to the population's accounts / agreements
  (broadcast the latest-month population) and to the date range needed, before any join.
- Build each per-row table once (population x candidate flags x A1/A2/A4 states x A3 inputs),
  persist it, and derive every crosstab and every V4 threshold variant from that one table instead of
  recomputing joins per output.
- No .count() / .collect() inside loops; collect only the final aggregates.
Report the new runtime in the README.
````
