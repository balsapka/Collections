Fixes the temporary bundle 06 check so it finishes in PROD. The old A2 output in PROD still has the
earlier single-state schema (`a2_state_v1`), so `compare_a2_outputs` could not find
`location_state`; it now compares on whichever schema the old output has (old `a2_state_v1` ×
new location and × new reachability). `describe_a2_rules` also logs reachability × last contact
(in the window / before it / never), to show how many Non-Reachable rows had a contact in the
window. A new log node `explain_crx_<p>_a2_b06_reach` (`B06 REACH`) explains the reachability move: it
rebuilds reachability from the same DCORE calls under the earlier rule (any contact ever is
Reachable unless the last 3 call days only rang out, admin entries kept as calls), then applies
each change in turn — dead lines / invalid numbers / LEFT_MSG count as failed, admin and legal
entries ignored, the contact must fall in the window — logging the state mix and the moves at
every step, and checks that the last step equals the engine's `reachability_state`. Only
`b06_check.py` and the check pipeline change; the engine and its output are untouched.
