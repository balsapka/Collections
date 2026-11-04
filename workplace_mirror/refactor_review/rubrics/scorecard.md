# Scorecard: the three rubrics side by side

The rubrics stay separate: `efficiency.md` (R-E), `interpretability.md` (R-I), `owner.md` (R-O).
This page only aligns their vocabulary, so a proposal or file can be read across all three.
The rubrics are frozen once the user approves them (U0).

## Themes and weights

| Theme | R-E | R-I | R-O |
|---|---|---|---|
| Size and concepts | E1 Net lines/concepts removed **25** | — | O7 Clarity per line 10 (shared) |
| Data passes and Spark | E2 Passes over data **20** · E4 Idiomatic PySpark 15 | — | O1 PROD operability **18** |
| Abstraction fit | E3 Indirection earns its keep 15 | I3 One idea per function 16 | O7 (shared) |
| Rule traceability | — | I1 Rule traceability **22** · I2 Named constants 14 · I4 Business names 12 | O3 Auditability 16 |
| Docstrings | E6 Comments carry information 5 | I5 Docstring at every boundary 12 | O3 (no history) |
| Cross-axis consistency | E5 Duplication across axes 10 | I7 Same pattern on every axis 8 | O4 One engine, thin wrappers 14 |
| **Fits A3 easily** | E7 10 | I6 16 | O5 14 |
| Change risk and bundling | — | — | O2 Change risk / bundle-ability **18** |
| Kedro and contracts | — | — | O6 Contracts and Kedro 10 |

## Where the reviewers are expected to clash, and who decides

R-O's tie-break: gates and behaviour first, then the smaller, more local diff. After that, R-I
wins on any line that encodes a business rule, threshold or date bound, and R-E wins everywhere
else.

| Clash | R-E | R-I | Resolution |
|---|---|---|---|
| Single-use helper | inline (E3, blocking 3) | keep if it names a rule (I3) | keep when it names a spec rule, otherwise inline |
| Literal vs named constant | fewer names | named constant tied to spec (I2, blocking 3) | named constant for thresholds and labels |
| Line growth | blocking without deletions (4) | accepted for visibility (blocking 7 for the opposite) | allowed for `require_columns` and rule visibility, nothing else |
| Private-helper docstrings | none (E6) | at every boundary (I5) | public functions and modules only, plus private helpers that encode a rule |
| Generic rule loops | welcome | blocking 1 | not for spec rules |

## Shared blocking objections (all three)

- A new Spark action, an extra pass, or a full-lineage count. `log_latest_month` is the only
  allowed action.
- A change to the shared layer that makes A3 harder, such as duplicated anchor or window logic,
  a switch for A3's alternatives, or a broken A3 import.
- A docstring holding history, or one that no longer matches the code.

## Thresholds

- **Proposal:** R-E accepts at a weighted 4.0, rejects below 3.0.
- **File:** R-E targets 3.5, or 4.0 for the shared layer and engines.
- **Round 3 sign-off (R-O):**
  - every criterion 4 or above;
  - no Tier-L file below 3 on O1–O3;
  - the A3 target shape at 4 or above on O5;
  - R-E and R-I averaging 3.5 or above (PLAN §5).
