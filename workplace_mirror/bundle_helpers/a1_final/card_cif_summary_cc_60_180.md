# a1_card_cif summary, cc_60_180

Source: `results_cc_60_180.md` (run 2026-11-18). Aggregates only.

## Verdict

Both raw tables are SCD2 **change logs** (client: 24.9M rows over 3,272 load dates, a load date holds about 0.1% of the
clients; contract: 2.2B rows, 3,276 load dates). `prm_card_contracts` has 70,433 contracts (1.6% of 4,519,794) under
more than one CIF (96.4% under 2, 3.5% under 3). Every one of them is explained by time-ordered change, none by two
CIFs held at once:

| Cause | Contracts | Share of 70,433 |
|---|---|---|
| H3 only: contract moved to another `client_idt`, each client has one CIF | 36,310 | 51.6% |
| H1 only: the client's `ident_number` changed, one client per contract | 28,278 | 40.1% |
| H3 and H1 together (moved client, and that client changed CIF) | 4,089 | 5.8% |
| H2 (client with overlapping valid ranges), alone or with H3 | 1,674 + 82 | 2.5% |

- **H1 holds** for 43,961 clients (1.0%) with more than one `ident_number`: 0 share a load date, 95.6% have
  non-overlapping valid ranges; 98.8% changed once; the old value returns for 1.3%. Changes cluster in 2019 (37%) and
  2023 (27%); none after 2024, so this is legacy history, not an ongoing flow.
- **H3 holds** for 40,482 contracts (0.9%) with more than one `client_idt`: 100% never share a load date, 95.8% sequential;
  4.0% switch back to an earlier client.
- **H2 (several CIFs at once) is not shown.** No client or contract shares a load date. The 4.4% / 4.2% with overlapping
  valid ranges (1,940 clients, 1,702 contracts) overlap only in valid time, most likely at version boundaries; I cannot
  tell from aggregates whether any is truly simultaneous.

## Against the spine and F4

- `cc_spine` never carries two CIFs for a contract-month (<10). Only 610 of its 128,927 persona contract-months (0.5%)
  belong to a multi-CIF contract.
- Spine CIF equals (a) the point-in-time CIF in 128,926 of 128,927 (609 of 610 multi-CIF months), (b) the latest CIF in
  128,924 (607 of 610), (c) one of the CIFs of `prm_card_contracts` in all. Point-in-time and latest CIF differ in only 2
  of the 610 months.
- F4 at 2026-08-31: of 3,456,861 card rows, 52,345 (1.5%; 48,100 current) sit under a CIF other than the point-in-time
  one. Of 19,292 scored accounts, 79 (0.4%) have their own contract under several CIFs, but **fewer than 10 scored
  accounts** have `xp_current` or `xp_instalment_max` touched by such a card, under either rule (cells suppressed).
  The wrong rows sit on CIFs that are almost all not scored: the effect on this persona is negligible; it is real for
  any other consumer of all CIFs (1.5% of card rows).
- Only 19,355 card rows (0.6%) have their contract in `cc_spine` that month; of those, 82 (0.4%) are under a CIF other
  than the spine's.

## Recommended rule

**Point-in-time CIF per month end** for the card branch of F4: per `(contract, month_end)`, the latest contract version and
then the latest client version with valid-from on or before that month end (as built in B4, `edp_effectivestartdate` for
the client, `record_date_from` for the contract, `edp_modifiedts` as tie-break). Reasons: the changes are sequential
(95.6% / 95.8%), so a point-in-time pick is well defined; it agrees with `cc_spine` in 609 of 610 multi-CIF months and 128,926
of 128,927 overall; it also handles the 4.0% of contracts that switch back, which "latest" cannot. The latest CIF is an
acceptable cheaper fallback for the persona (3 of 610 multi-CIF months differ from the spine) but wrong for history.
Using the spine's CIF is not a rule for the product primary: it covers 0.6% of F4 card rows; keep it as a consistency
check. Not coded.

## Gaps

- F4 effect cells on scored accounts are `<10`; the exact count is between 0 and 9.
- `ident_type` has 18 values in `raw_stg_client` and was not cross-tabbed; 99% of `ident_number` are 8 digits, but the
  others (6, 9, 11, 19 characters, about 1%) may be other identity types, not CIFs. Worth a filter check.
- Valid-time overlaps (1,940 clients) are not explained; the load-date range test assumes each version is present
  between its first and last load date.
- Partition column reported as `edp_activeind` (first input file), not the load date.
- 311 contract rows have an empty `client_idt` (0.0%); no client rows have an empty `ident_number` (<10).
- Persona base is small (128,927 contract-months, 19,292 scored), so month-level shares on multi-CIF contracts rest on 610 months.
