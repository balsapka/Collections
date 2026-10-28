Fixes the temporary bundle 06 check so it finishes in PROD. The old A2 output in PROD still has the
earlier single-state schema (`a2_state_v1`), so `compare_a2_outputs` could not find
`location_state`; it now compares on whichever schema the old output has (old `a2_state_v1` ×
new location and × new reachability). `describe_a2_rules` also logs reachability × last contact
(in the window / before it / never), to show how many Non-Reachable rows had a contact in the
window. Only `a2_locatability/b06_check.py` changes; the engine and its output are untouched.
