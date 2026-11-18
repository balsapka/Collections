# Terminal summary - a1_card_cif (cc_60_180)

Claude Code terminal output, branch `feature/persona_refactor`.

## Tail of the file viewed in the terminal (lines 4-10 shown, +53 lines collapsed)

```
4
5 ## Verdict
6
7 Both raw tables are SCD2 **change logs** (client: 24.9M rows over 3,272 load dates, a load date holds about 0.1% of the
8 clients; contract: 2.2B rows, 3,276 load dates). `prm_card_contracts` has 70,433 contracts (1.6% of 4,519,794) under
9 more than one CIF (96.4% under 2, 3.5% under 3). Every one of them is explained by time-ordered change, none by two
10 CIFs held at once:
… +53 lines
└ Allowed by auto mode
```

## Reply

● I wrote `tmp_validation/a1_card_cif/summary_cc_60_180.md` but haven't committed it.

**Verdict.** All 70,433 multi-CIF card contracts come from changes over time. None come from two CIFs held at once. Both raw tables are change logs, so a contract keeps every CIF it ever had.
- H3 only (36,310; 51.6%): the contract moved to another client_idt, and each of those clients has one CIF.
- H1 only (28,278; 40.1%): the client's ident_number changed.
- H3 and H1 together (4,089; 5.8%): the contract moved client, and that client also changed CIF.
- H2 (1,756; 2.5%): the contract's client has overlapping valid ranges, alone or with H3. No client or contract shares a load date, so these are probably version-boundary overlaps. I can't tell from aggregates whether any is truly simultaneous.
- Timing: the changes cluster in 2019 and 2023, and none are after 2024. This is legacy history, not an ongoing flow.

**Spine and F4.**
- Only 610 of the 128,927 persona contract-months belong to a multi-CIF contract.
- The spine's CIF equals the point-in-time CIF in 128,926 of 128,927 months (609 of 610 on the multi-CIF ones). Against the latest CIF it matches 607 of 610.
- At the latest month, 52,345 F4 card rows (1.5%) sit under a non-point-in-time CIF.
- Fewer than 10 of the 19,292 scored accounts have xp_current or xp_instalment_max affected, under either rule. The wrong rows sit on CIFs that are almost all not scored.

**Recommended rule.** Use the point-in-time CIF per month end. The changes are sequential, and it agrees with the spine. It also handles the 4.0% of contracts that switch back to an earlier client, which "latest" cannot. "Latest CIF" is an acceptable cheaper fallback for the persona only. The spine's CIF can't be the primary rule because it covers just 0.6% of F4 card rows. I did not code any of this.

**Open items.**
- `ident_type` has 18 values and I didn't cross-tab it. The roughly 1% of ident_number values that aren't 8 digits may not be CIFs.
- The F4 effect on scored accounts is only known as "between 0 and 9", because the cells are suppressed.

I can commit and push the summary, or start on the rule change for the next A1 bundle.

✻ Crunched for 51s · done 10:37 AM

```
◆ Sonnet | mode: auto | ● 12% | feature/persona_refactor untracked:2 stash:1 | retail.collections.risk_profiling | tkn: 188.1K in: 274 op: 187.8K
Today Overall Usage burn: 0.0% tkn: 189.0K in: 276 op: 188.7K
▶▶ auto mode on (shift+tab to cycle)
```
