**What this bundle does.** The A1 income rule compares levels when only AECB salary is present, and a
new check measures this and the refreshed alerts together. Bundle 09's check is already gone.

- **`income_level`** (`a1_ability/classify.py`): with no internal salary of AED 1,000 or more in the
  window or the prior window, the 25% check compares the average of the months with a value, not
  the totals. AECB alerts arrive only on a change, and the payment validation showed rows failing
  the total check on sparse months behave like Stable, while real falls behave like Weak. Any row
  with internal salary in either window keeps the total check, so a stopped salary still shows.
- **Check** (`a1_ability/b12_check.py`, pipelines `crx_cc_a1_ability_b12_check`,
  `crx_rl_a1_ability_b12_check`): blocks `B12 OUTPUT`, `REPORT`, `SOURCES` and `AECB`. `OUTPUT` compares
  with the current `crx_<p>_a1_ability`, so it shows the refreshed alerts and this rule together.
  `AECB` adds a last step, `s3_level_check`, which isolates the rule.
- No output column changes. Expected for `cc_60_180` (rough, before the alert refresh): about 680
  accounts move from Weak to Stable. The refresh also raises August's salary and bounces.
