# A3 handoff (round 1)

Items the specialists wrote against the current A3 files (tier A, `cc_a3_payment_credibility/`,
`rl_a3_payment_credibility/`). None is applied on `refactor/persona_review`: the A3 session applies
them while building the A3 bundle (PLAN §2). Diffs are against `d1ad38a` (A3 files are unchanged on
the round-1 merge, so they still apply there).

Shared helpers A3 can now import from the merged tier-L layer (round 1, S1): `_common.string_key`,
`_common.window_start(months, anchor=None)`, `_common.window_agg(..., start=<base date column>)`,
`_common.dcore_account_events`, `_common.segment` / `SEG_60_180` / `SEG_180_PLUS`,
`_common.log_latest_month(..., latest_per_account=)`, `scoring_engine.state_label`,
`scoring_engine.StateLadder`, `_dpd_journey.episode_start`. The target A3 shape (an
`a3_credibility/` engine plus thin CC/RL wrappers) is in `round_1/proposals/S1.md`, "Target A3 shape".

Reviewer verdicts: pending (the round-1 reviews run after this merge); filled in at triage.

## Status after the A3 design-in (S1, 2026-11-05)

`a3_target_shape.md` supersedes S1.md's "Target A3 shape". The A3 rebuild replaces most functions
these items touch, so most are now **superseded**: the intent is carried into the new engine, and the
diff is no longer needed. R-O verdicts are in `round_1/reviews/R-O.md`.

| Id | Status | Where the intent lands |
|---|---|---|
| S1-H1 | superseded | `_rl_string_key` goes with the RL adapter; `build_rl_a3_dues` / `_payments` use `_common.string_key` |
| S1-H2 | **changed** | A3 declares a `scoring_engine.Scorecard` (round 2 item A3-1), not `StateLadder`; the Unknown gate is the Scorecard's "all dimensions silent, no override" (R-I's named-gate condition met) |
| S1-H3 | superseded | the new `classify.build_a3_credibility` logs only through `log_latest_month`; list the dropped `a3_path` / total-rows log in the bundle notes |
| S2-H-01 | carried | `signals._latest_rpc`: one `max(struct(day, not_refusal, disposition))` aggregate; tie rule = Q-28 (`DISPOSITION_RANK` if (b)) |
| S3-A3-H1 | superseded (R-O: R-E's way) | dict inputs and one `TAGS` written once in `create_a3_pipeline`; tags = the normalised set `[crx_persona, crx, a3, payment_credibility, persona_axis]` on every node (Q-15 answered yes; A1, A2, A4 and the full histories already use it), no pipeline-level tags |
| S3-A3-H2 / Q-20 | **settled by the spec** | "Open": all A3 sources are required (D2); `require_columns` in every node, no optional inputs |
| S4-H1 | superseded | as S1-H1 |
| S6-H01 | carried | `window_start` / `window_agg(start=)`; Dim B start = `add_months(episode_start, 1)` (`_onset_bounds`) |
| S6-H02 | pending Q-22 / Q-27 | `signals._in_episode` |
| S6-H03 | **changed** | round 2 item A3-3: `episode_left_censored = left_censored AND history_cropped`; A3 behaviour on those rows = Q-25 |
| S6-H04 | deferred (R-O) | inline in `build_cc_a3_dues`; no shared helper |

New entries required by D-A3-1..21 and the design-in are N-1 … N-6 at the end of this file.

| Id | From | Title | Diff |
|---|---|---|---|
| S1-H1 | S1 | RL A3 uses `_common.string_key` | yes |
| S1-H2 | S1 | CC A3 ladder on `StateLadder` | yes |
| S1-H3 | S1 | CC A3 drops `_log_a3_stats` | yes |
| S2-H-01 | S2 | (A3, tier A) Latest right-party contact as an aggregate | yes |
| S3-A3-H1 | S3 | Dict inputs and one tag set for both A3 pipelines | yes |
| S3-A3-H2 | S3 | A3 schema guards turn a source off quietly (no diff; needs a user decision first) | no |
| S4-H1 | S4 | A3: drop the third `_string_key` copy once a shared one exists | no |
| S6-H01 | S6 | (M) [A3 · `cc_a3_payment_credibility/_signals_common.py:93-97`, RL twin `rl_a3_payment_credibility/nodes.py:437-456`] Window start by `add_months` on month-end dates | no |
| S6-H02 | S6 | (L) [A3 · `cc_a3_payment_credibility/nodes.py:528-529`] DCORE window exclusive at the observation date | no |
| S6-H03 | S6 | (M) [A4 → A3 anchor · `_dpd_journey/core.py:108-141`] What the A4 anchor means on cropped or blind histories | no |
| S6-H04 | S6 | (L) [A3 `_signals_common.resolve_due_amount_m:641-700` vs A1 `cc_a1_ability/nodes.py:14,52-54`] "Oldest open overdue bucket" with two ranges | no |

Notes from the merge:
- S4-H1 is the same change as S1-H1; S1-H1 carries the diff (`_common.string_key` now exists).
- S3-A3-H1 also sets the A3 tags to the normalised set; Q-15 is answered yes and the tier-L tag change (round 2, S3) is applied, so the A3 tags are no longer held. Run selection changes for CC: `crx_persona` now sits on the nodes, not the pipeline.
- S3-A3-H2 waits for Q-S3-7; S6-H02 has a question for the user inside it (exclusive DCORE bound).

Index of the 11 items above; each section below is the specialist's text, unchanged.

## S1-H1  RL A3 uses `_common.string_key`
Files: rl_a3_payment_credibility/nodes.py:53,209-220,246,267
Behaviour: none (same expression).
Change: delete `_rl_string_key` (the third copy), import `string_key`.
Diff:
```diff
diff --git a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/nodes.py b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/nodes.py
index 7987383..f28c78e 100644
--- a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/nodes.py
+++ b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/nodes.py
@@ -50,8 +50,8 @@ from datetime import date
 from dateutil.relativedelta import relativedelta
 from pyspark.sql import DataFrame, Window
 from pyspark.sql import functions as F
-from pyspark.sql import types as T
 
+from enbd_collections.pipelines.crx_persona._common import string_key
 from enbd_collections.pipelines.crx_persona._spine_utils import rl_spine_as_cc_shim
 from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility.nodes import (
     build_a3_commitment_signals,
@@ -206,19 +206,6 @@ def build_rl_a3_strong_negative_signals(  # pylint: disable=too-many-positional-
 # ── Node 2: build_rl_a3_dlq_cycles ───────────────────────────────────────
 
 
-def _rl_string_key(df: DataFrame, col: str = "account_id"):
-    """Double/decimal-safe account_id -> string cast, replicated locally
-    rather than importing rl_full_history.nodes' private _string_key helper
-    (a double/decimal account_id cast straight to string gives
-    "1.23456789E8" and silently zeroes a leftsemi join – the same trap
-    build_rl_full_history already guards against)."""
-    dtype = df.schema[col].dataType
-    c = F.col(col)
-    if isinstance(dtype, (T.DoubleType, T.FloatType, T.DecimalType)):
-        c = c.cast("long")
-    return F.trim(c.cast("string"))
-
-
 def build_rl_a3_dlq_cycles(
     crx_rl_full_history: DataFrame,
     int_loan_master: DataFrame,
@@ -243,7 +230,7 @@ def build_rl_a3_dlq_cycles(
 
     monthly_emi_due and total_paid come from int_loan_master (scoped to
     rl_spine through a broadcast leftsemi, with a double/decimal-safe
-    account_id cast – see _rl_string_key). monthly_emi_asof is monthly_emi_due
+    account_id cast – see _common.string_key). monthly_emi_asof is monthly_emi_due
     forward-filled to the latest non-null value up to that month – the EMI a
     month's payment is judged against when its own row is NULL, and robust to
     the rare EMI change on restructure.
@@ -264,7 +251,7 @@ def build_rl_a3_dlq_cycles(
         nullable), total_paid (double, nullable).
     """
     spine_keys = rl_spine.select(
-        _rl_string_key(rl_spine).alias("account_id")
+        string_key(rl_spine).alias("account_id")
     ).distinct()
     emi = int_loan_master.join(
         F.broadcast(spine_keys), on="account_id", how="leftsemi"
```
Gain: −13 lines.
Risk: needs S1-02 (`_common.string_key`).
Depends on: S1-02.

Verdicts: R-E pending · R-I pending · R-O pending

## S1-H2  CC A3 ladder on `StateLadder`
Files: cc_a3_payment_credibility/nodes.py:47,1105-1108,1326-1353
Behaviour: none. `_a3_state_col` is cell-for-cell `StateLadder.state` (Unknown first; High at
points ≥ HIGH without a strong negative; Moderate at ≥ MODERATE without one or ≥ HIGH with one;
else Low), as `scoring_engine`'s own docstring says it was verified.
Change: one `_LADDER = StateLadder(...)` from the existing constants; `_a3_state_col` keeps its
signature and computes only the Unknown gate.
Diff:
```diff
diff --git a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py
index b64324a..2a898c9 100644
--- a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py
+++ b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py
@@ -45,6 +45,7 @@ from pyspark.sql import Column, DataFrame, Window
 from pyspark.sql import functions as F
 
 from enbd_collections.pipelines.crx_persona._common import log_latest_month
+from enbd_collections.pipelines.crx_persona.scoring_engine import StateLadder
 from enbd_collections.pipelines.crx_persona._spine_utils import join_spine_to_spell
 from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility._signals_common import (
     attribute_payments_to_billing_cycles,
@@ -1106,6 +1107,14 @@ _STATE_HIGH = "payment_credibility_high"
 _STATE_MODERATE = "payment_credibility_moderate"
 _STATE_LOW = "payment_credibility_low"
 _STATE_UNKNOWN = "payment_credibility_unknown"
+_LADDER = StateLadder(
+    high=_STATE_HIGH,
+    moderate=_STATE_MODERATE,
+    low=_STATE_LOW,
+    unknown=_STATE_UNKNOWN,
+    high_from_points=_TAU_A3V2_HIGH_FROM_POINTS,
+    moderate_from_points=_TAU_A3V2_MODERATE_FROM_POINTS,
+)
 
 
 def _join_signals_pair(
@@ -1337,20 +1346,13 @@ def _a3_state_col(
     High: points >= HIGH and no strong negative. Moderate: points >= MODERATE and no
     strong negative, or points >= HIGH knocked down one level by a strong negative.
     """
-    no_sn = ~has_strong_negative
     is_unknown = (
-        (level_a == "thin") & (level_b == "none") & (level_c == "no_record") & no_sn
-    )
-    return (
-        F.when(is_unknown, F.lit(_STATE_UNKNOWN))
-        .when((points_total >= _TAU_A3V2_HIGH_FROM_POINTS) & no_sn, F.lit(_STATE_HIGH))
-        .when(
-            ((points_total >= _TAU_A3V2_MODERATE_FROM_POINTS) & no_sn)
-            | ((points_total >= _TAU_A3V2_HIGH_FROM_POINTS) & has_strong_negative),
-            F.lit(_STATE_MODERATE),
-        )
-        .otherwise(F.lit(_STATE_LOW))
+        (level_a == "thin")
+        & (level_b == "none")
+        & (level_c == "no_record")
+        & ~has_strong_negative
     )
+    return _LADDER.state(points_total, has_strong_negative, is_unknown)
 
 
 def _a3_output(df: DataFrame, dlq_method: str, pre_dlq_method: str) -> DataFrame:
```
Gain: the ladder is defined once across A1 and A3 (O4).
Risk: none in tier L; A3's own tests (workplace Sonnet).
Depends on: none.

Verdicts: R-E pending · R-I pending · R-O pending

## S1-H3  CC A3 drops `_log_a3_stats`
Files: cc_a3_payment_credibility/nodes.py:1539,1550-1570
Behaviour: none on data. Removes three Spark actions over the full lineage (`count`, two
`collect`), the owner rubric's example 3. The same node already logs the latest month through
`log_latest_month` (lines 1540-1546) when `model_id` and `persona_end_date` are given, which the
CC and RL pipelines pass. The `a3_path` breakdown goes with it (log only; list it in the bundle).
Diff:
```diff
diff --git a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py
index b64324a..ede8613 100644
--- a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py
+++ b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py
@@ -1536,7 +1536,6 @@ def build_a3_payment_credibility(  # pylint: disable=too-many-positional-argumen
         df, dlq_payment_evidence_method, pre_dlq_payment_evidence_method
     )
 
-    _log_a3_stats(output)
     if model_id and persona_end_date:
         log_latest_month(
             output,
@@ -1545,26 +1544,3 @@ def build_a3_payment_credibility(  # pylint: disable=too-many-positional-argumen
             persona_end_date,
         )
     return output
-
-
-def _log_a3_stats(df: DataFrame) -> None:
-    """Log state distribution for post-run monitoring."""
-    try:
-        n_total = df.count()
-        state_dist = df.groupBy("a3_state_v1").count().collect()
-        path_dist = df.groupBy("a3_path").count().collect()
-
-        LOG.info("build_a3_payment_credibility: total rows = %d", n_total)
-        for row in state_dist:
-            pct = 100.0 * row["count"] / max(n_total, 1)
-            LOG.info(
-                "  a3_state_v1=%-35s n=%7d  (%.1f%%)",
-                str(row["a3_state_v1"]),
-                row["count"],
-                pct,
-            )
-        LOG.info("  path breakdown:")
-        for row in path_dist:
-            LOG.info("  %-30s n=%d", str(row["a3_path"]), row["count"])
-    except Exception as exc:  # pylint: disable=broad-except
-        LOG.warning("_log_a3_stats: stats collection failed – %s", exc)
```
Gain: −24 lines, 3 actions.
Risk: a PROD reader of the `total rows` / path block loses it (owner blocking 7: list it).
Depends on: none.

Verdicts: R-E pending · R-I pending · R-O pending

## S2-H-01  (A3, tier A) Latest right-party contact as an aggregate
Files: `cc_a3_payment_credibility/nodes.py:561-580` (`_aggregate_disposition`)
Behaviour: none, except that rows tied on date and flag (undefined in the window version) now pick the largest disposition string
Change: `row_number()` over `(account, observation_date)` ordered by `(szactiondate desc, RTP flag asc)` becomes `max(struct(szactiondate, non-RTP flag, _disp))`. Removes the `Window` import from the file. The same pattern fits `_signals_common.py:752` (`due_amount_fallback_m`: latest N months, a window is right there) and is not applicable at `:952` (top-N, not top-1). The `.count()` guards at `nodes.py:176-193,440,1553-1555` are known and are not repeated here.
Diff:
```diff
diff --git a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py
index b64324a..aa19986 100644
--- a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py
+++ b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py
@@ -41,7 +41,7 @@ Notes:
 # pylint: disable=too-many-lines, duplicate-code
 import logging
 
-from pyspark.sql import Column, DataFrame, Window
+from pyspark.sql import Column, DataFrame
 from pyspark.sql import functions as F
 
 from enbd_collections.pipelines.crx_persona._common import log_latest_month
@@ -561,21 +561,21 @@ def _aggregate_disposition(
     # same-day promise followed the refusal.
     last_rpc = (
         window_with_disp.filter(F.col("_disp").isNotNull())
-        .withColumn(
-            "_rpc_rn",
-            F.row_number().over(
-                Window.partitionBy("account_id", "observation_date").orderBy(
-                    F.col("szactiondate").desc(),
-                    F.when(F.col("_disp") == _DISP_RTP, 1).otherwise(0),
+        .groupBy("account_id", "observation_date")
+        .agg(
+            F.max(
+                F.struct(
+                    "szactiondate",
+                    (F.col("_disp") != _DISP_RTP).cast("int").alias("_later"),
+                    "_disp",
                 )
-            ),
+            ).alias("_last")
         )
-        .filter(F.col("_rpc_rn") == 1)
         .select(
             "account_id",
             "observation_date",
-            F.col("_disp").alias("last_rpc_disposition"),
-            F.col("szactiondate").alias("last_rpc_date"),
+            F.col("_last._disp").alias("last_rpc_disposition"),
+            F.col("_last.szactiondate").alias("last_rpc_date"),
         )
     )
```
Gain: 1 window exchange + sort per call removed; in the target `a3_credibility` engine `pit_latest` (S2-01) already gives this shape for any latest-per-key.
Risk: A3 session applies it; the new A3 check pass covers it.
Depends on: none

Verdicts: R-E pending · R-I pending · R-O pending

## S3-A3-H1  Dict inputs and one tag set for both A3 pipelines
Files: cc_a3_payment_credibility/pipeline.py:93-237; rl_a3_payment_credibility/pipeline.py:54-167
Behaviour: none to data. Tags change for CC (`crx_persona` moves from the pipeline to the node tags) and none for RL; node, dataset and output names are unchanged.
Change: all 18 A3 nodes pass `inputs=[...]` positionally (nine CC lists of up to eleven items, `params:` mixed in). The diff converts each to a dict keyed by the
function's own parameter names (generated from the `def` lines of `nodes.py`, so each key is the parameter the position already fed), and gives both pipelines the same
`_TAGS = [crx_persona, crx, a3, payment_credibility, persona_axis]`, dropping the pipeline-level `tags=["crx_persona"]`. The tag names `a3` and `payment_credibility` are kept.
Diff:
```diff
diff --git a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py
index a65fea8..2ab11cd 100644
--- a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py
+++ b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py
@@ -90,7 +90,7 @@ from .nodes import (
     build_a3_pre_dlq_payment_signals_dpd_bucket_movement,
 )
 
-_TAGS = ["crx", "a3", "payment_credibility", "persona_axis"]
+_TAGS = ["crx_persona", "crx", "a3", "payment_credibility", "persona_axis"]
 
 
 def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
@@ -100,17 +100,17 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # ── Dimension A: commitments kept (DCORE PTP / settlement signals) ──
             node(
                 func=build_a3_commitment_signals,
-                inputs=[
-                    "cc_spine",
-                    "crx_cc_spell_table",
-                    "dcore_observation_spine",
-                    "dcore_feat_ptp",
-                    "dcore_feat_settlement",
-                    "dcore_int_ptp",
-                    "dcore_prm_promise_instalments",
-                    "dcore_int_settlement",
-                    "dcore_prm_settlement_schedule_instalments",
-                ],
+                inputs={
+                    "cc_spine": "cc_spine",
+                    "spell_table": "crx_cc_spell_table",
+                    "observation_spine": "dcore_observation_spine",
+                    "feat_ptp": "dcore_feat_ptp",
+                    "feat_settlement": "dcore_feat_settlement",
+                    "int_ptp": "dcore_int_ptp",
+                    "ptp_instalments": "dcore_prm_promise_instalments",
+                    "int_settlement": "dcore_int_settlement",
+                    "settlement_instalments": "dcore_prm_settlement_schedule_instalments",
+                },
                 outputs="crx_cc_a3_commitment_signals",
                 name="build_a3_commitment_signals",
                 tags=_TAGS,
@@ -118,15 +118,15 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # ── Strong negatives: evidence only; the rules run in the combiner ──
             node(
                 func=build_a3_strong_negative_signals,
-                inputs=[
-                    "cc_spine",
-                    "crx_cc_spell_table",
-                    "dcore_observation_spine",
-                    "dcore_prm_followup_outcomes",
-                    "dcore_int_ptp",
-                    "dcore_int_settlement",
-                    "crx_cc_transactions",
-                ],
+                inputs={
+                    "cc_spine": "cc_spine",
+                    "spell_table": "crx_cc_spell_table",
+                    "observation_spine": "dcore_observation_spine",
+                    "followup_outcomes": "dcore_prm_followup_outcomes",
+                    "int_ptp": "dcore_int_ptp",
+                    "int_settlement": "dcore_int_settlement",
+                    "transactions": "crx_cc_transactions",
+                },
                 outputs="crx_cc_a3_strong_negative_signals",
                 name="build_a3_strong_negative_signals",
                 tags=_TAGS,
@@ -135,12 +135,12 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # and waterfall months ──────────────────────────────────────────────
             node(
                 func=build_a3_payment_cycles,
-                inputs=[
-                    "crx_cc_billing",
-                    "crx_cc_balance",
-                    "crx_cc_transactions",
-                    "params:cc_a3_history_floor_date",
-                ],
+                inputs={
+                    "crx_cc_billing": "crx_cc_billing",
+                    "crx_cc_balance": "crx_cc_balance",
+                    "crx_cc_transactions": "crx_cc_transactions",
+                    "history_floor_date": "params:cc_a3_history_floor_date",
+                },
                 outputs="crx_cc_a3_payment_cycles",
                 name="build_a3_payment_cycles",
                 tags=_TAGS,
@@ -150,37 +150,37 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # params:a3_dlq_payment_evidence_method (default single_payment_cycle_count).
             node(
                 func=build_a3_dlq_payment_signals_payment_sum_waterfall,
-                inputs=[
-                    "crx_cc_a3_payment_cycles",
-                    "crx_cc_spell_table",
-                    "cc_spine",
-                    "params:cc_a3_history_floor_date",
-                ],
+                inputs={
+                    "crx_cc_a3_payment_cycles": "crx_cc_a3_payment_cycles",
+                    "crx_cc_spell_table": "crx_cc_spell_table",
+                    "cc_spine": "cc_spine",
+                    "history_floor_date": "params:cc_a3_history_floor_date",
+                },
                 outputs="crx_cc_a3_dlq_payment_signals_payment_sum_waterfall",
                 name="build_a3_dlq_payment_signals_payment_sum_waterfall",
                 tags=_TAGS,
             ),
             node(
                 func=build_a3_dlq_payment_signals_single_payment_cycle_count,
-                inputs=[
-                    "crx_cc_a3_payment_cycles",
-                    "crx_cc_spell_table",
-                    "cc_spine",
-                    "params:cc_a3_history_floor_date",
-                ],
+                inputs={
+                    "crx_cc_a3_payment_cycles": "crx_cc_a3_payment_cycles",
+                    "crx_cc_spell_table": "crx_cc_spell_table",
+                    "cc_spine": "cc_spine",
+                    "history_floor_date": "params:cc_a3_history_floor_date",
+                },
                 outputs="crx_cc_a3_dlq_payment_signals_single_payment_cycle_count",
                 name="build_a3_dlq_payment_signals_single_payment_cycle_count",
                 tags=_TAGS,
             ),
             node(
                 func=build_a3_dlq_payment_signals_dpd_bucket_movement,
-                inputs=[
-                    "crx_cc_a3_payment_cycles",
-                    "crx_cc_full_history",
-                    "crx_cc_spell_table",
-                    "cc_spine",
-                    "params:cc_a3_history_floor_date",
-                ],
+                inputs={
+                    "crx_cc_a3_payment_cycles": "crx_cc_a3_payment_cycles",
+                    "crx_cc_full_history": "crx_cc_full_history",
+                    "crx_cc_spell_table": "crx_cc_spell_table",
+                    "cc_spine": "cc_spine",
+                    "history_floor_date": "params:cc_a3_history_floor_date",
+                },
                 outputs="crx_cc_a3_dlq_payment_signals_dpd_bucket_movement",
                 name="build_a3_dlq_payment_signals_dpd_bucket_movement",
                 tags=_TAGS,
@@ -190,25 +190,25 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # params:a3_pre_dlq_payment_evidence_method (default single_payment_cycle_count).
             node(
                 func=build_a3_pre_dlq_payment_signals_single_payment_cycle_count,
-                inputs=[
-                    "crx_cc_a3_payment_cycles",
-                    "crx_cc_spell_table",
-                    "cc_spine",
-                    "params:cc_a3_history_floor_date",
-                ],
+                inputs={
+                    "crx_cc_a3_payment_cycles": "crx_cc_a3_payment_cycles",
+                    "crx_cc_spell_table": "crx_cc_spell_table",
+                    "cc_spine": "cc_spine",
+                    "history_floor_date": "params:cc_a3_history_floor_date",
+                },
                 outputs="crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                 name="build_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                 tags=_TAGS,
             ),
             node(
                 func=build_a3_pre_dlq_payment_signals_dpd_bucket_movement,
-                inputs=[
-                    "crx_cc_a3_payment_cycles",
-                    "crx_cc_full_history",
-                    "crx_cc_spell_table",
-                    "cc_spine",
-                    "params:cc_a3_history_floor_date",
-                ],
+                inputs={
+                    "crx_cc_a3_payment_cycles": "crx_cc_a3_payment_cycles",
+                    "crx_cc_full_history": "crx_cc_full_history",
+                    "crx_cc_spell_table": "crx_cc_spell_table",
+                    "cc_spine": "cc_spine",
+                    "history_floor_date": "params:cc_a3_history_floor_date",
+                },
                 outputs="crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                 name="build_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                 tags=_TAGS,
@@ -216,23 +216,22 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # ── Combiner: Dimensions A + B + C -> a3_state_v1 ──────────────────
             node(
                 func=build_a3_payment_credibility,
-                inputs=[
-                    "crx_cc_a3_commitment_signals",
-                    "crx_cc_a3_strong_negative_signals",
-                    "crx_cc_a3_dlq_payment_signals_payment_sum_waterfall",
-                    "crx_cc_a3_dlq_payment_signals_single_payment_cycle_count",
-                    "crx_cc_a3_dlq_payment_signals_dpd_bucket_movement",
-                    "crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count",
-                    "crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement",
-                    "params:a3_dlq_payment_evidence_method",
-                    "params:a3_pre_dlq_payment_evidence_method",
-                    "params:model_id",
-                    "params:crx_persona.persona_end_date",
-                ],
+                inputs={
+                    "commitment_signals": "crx_cc_a3_commitment_signals",
+                    "negative_signals": "crx_cc_a3_strong_negative_signals",
+                    "dlq_payment_signals_payment_sum_waterfall": "crx_cc_a3_dlq_payment_signals_payment_sum_waterfall",
+                    "dlq_payment_signals_single_payment_cycle_count": "crx_cc_a3_dlq_payment_signals_single_payment_cycle_count",
+                    "dlq_payment_signals_dpd_bucket_movement": "crx_cc_a3_dlq_payment_signals_dpd_bucket_movement",
+                    "pre_dlq_payment_signals_single_payment_cycle_count": "crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count",
+                    "pre_dlq_payment_signals_dpd_bucket_movement": "crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement",
+                    "dlq_payment_evidence_method": "params:a3_dlq_payment_evidence_method",
+                    "pre_dlq_payment_evidence_method": "params:a3_pre_dlq_payment_evidence_method",
+                    "model_id": "params:model_id",
+                    "persona_end_date": "params:crx_persona.persona_end_date",
+                },
                 outputs="crx_cc_a3_payment_credibility",
                 name="build_a3_payment_credibility",
                 tags=_TAGS,
             ),
         ],
-        tags=["crx_persona"],
     )
diff --git a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py
index c47817e..0aeeb8c 100644
--- a/workplace_mirror/src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py
+++ b/workplace_mirror/src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py
@@ -51,7 +51,7 @@ from .nodes import (
     build_rl_a3_strong_negative_signals,
 )
 
-_TAGS = ["crx", "a3", "payment_credibility", "persona_axis", "crx_persona"]
+_TAGS = ["crx_persona", "crx", "a3", "payment_credibility", "persona_axis"]
 
 
 def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
@@ -62,16 +62,16 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # 24m partition floor, RL-D5 spine) ────────────────────────────────
             node(
                 func=build_rl_a3_commitment_signals,
-                inputs=[
-                    "crx_rl_a4_spine",
-                    "dcore_observation_spine",
-                    "dcore_feat_ptp",
-                    "dcore_feat_settlement",
-                    "dcore_int_ptp",
-                    "dcore_prm_promise_instalments",
-                    "dcore_int_settlement",
-                    "dcore_prm_settlement_schedule_instalments",
-                ],
+                inputs={
+                    "crx_rl_a4_spine": "crx_rl_a4_spine",
+                    "dcore_observation_spine": "dcore_observation_spine",
+                    "feat_ptp": "dcore_feat_ptp",
+                    "feat_settlement": "dcore_feat_settlement",
+                    "int_ptp": "dcore_int_ptp",
+                    "ptp_instalments": "dcore_prm_promise_instalments",
+                    "int_settlement": "dcore_int_settlement",
+                    "settlement_instalments": "dcore_prm_settlement_schedule_instalments",
+                },
                 outputs="crx_rl_a3_commitment_signals",
                 name="build_rl_a3_commitment_signals",
                 tags=_TAGS,
@@ -80,14 +80,14 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # run in the combiner ───────────────────────────────────────────────
             node(
                 func=build_rl_a3_strong_negative_signals,
-                inputs=[
-                    "crx_rl_a4_spine",
-                    "dcore_observation_spine",
-                    "dcore_prm_followup_outcomes",
-                    "params:crx_persona",
-                    "dcore_int_ptp",
-                    "dcore_int_settlement",
-                ],
+                inputs={
+                    "crx_rl_a4_spine": "crx_rl_a4_spine",
+                    "dcore_observation_spine": "dcore_observation_spine",
+                    "followup_outcomes": "dcore_prm_followup_outcomes",
+                    "crx_persona": "params:crx_persona",
+                    "int_ptp": "dcore_int_ptp",
+                    "int_settlement": "dcore_int_settlement",
+                },
                 outputs="crx_rl_a3_strong_negative_signals",
                 name="build_rl_a3_strong_negative_signals",
                 tags=_TAGS,
@@ -96,7 +96,11 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # monthly_emi_due + total_paid ──────────────────────────────────────
             node(
                 func=build_rl_a3_dlq_cycles,
-                inputs=["crx_rl_full_history", "int_loan_master", "rl_spine"],
+                inputs={
+                    "crx_rl_full_history": "crx_rl_full_history",
+                    "int_loan_master": "int_loan_master",
+                    "rl_spine": "rl_spine",
+                },
                 outputs="crx_rl_a3_dlq_cycles",
                 name="build_rl_a3_dlq_cycles",
                 tags=_TAGS,
@@ -106,21 +110,30 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # params:rl_a3_dlq_payment_evidence_method ──────────────────────────
             node(
                 func=build_rl_a3_dlq_payment_signals_payment_sum_waterfall,
-                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
+                inputs={
+                    "crx_rl_a3_dlq_cycles": "crx_rl_a3_dlq_cycles",
+                    "crx_rl_a4_spine": "crx_rl_a4_spine",
+                },
                 outputs="crx_rl_a3_dlq_payment_signals_payment_sum_waterfall",
                 name="build_rl_a3_dlq_payment_signals_payment_sum_waterfall",
                 tags=_TAGS,
             ),
             node(
                 func=build_rl_a3_dlq_payment_signals_single_payment_cycle_count,
-                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
+                inputs={
+                    "crx_rl_a3_dlq_cycles": "crx_rl_a3_dlq_cycles",
+                    "crx_rl_a4_spine": "crx_rl_a4_spine",
+                },
                 outputs="crx_rl_a3_dlq_payment_signals_single_payment_cycle_count",
                 name="build_rl_a3_dlq_payment_signals_single_payment_cycle_count",
                 tags=_TAGS,
             ),
             node(
                 func=build_rl_a3_dlq_payment_signals_dpd_bucket_movement,
-                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
+                inputs={
+                    "crx_rl_a3_dlq_cycles": "crx_rl_a3_dlq_cycles",
+                    "crx_rl_a4_spine": "crx_rl_a4_spine",
+                },
                 outputs="crx_rl_a3_dlq_payment_signals_dpd_bucket_movement",
                 name="build_rl_a3_dlq_payment_signals_dpd_bucket_movement",
                 tags=_TAGS,
@@ -130,14 +143,20 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # params:rl_a3_pre_dlq_payment_evidence_method ──────────────────────
             node(
                 func=build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count,
-                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
+                inputs={
+                    "crx_rl_a3_dlq_cycles": "crx_rl_a3_dlq_cycles",
+                    "crx_rl_a4_spine": "crx_rl_a4_spine",
+                },
                 outputs="crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                 name="build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                 tags=_TAGS,
             ),
             node(
                 func=build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement,
-                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
+                inputs={
+                    "crx_rl_a3_dlq_cycles": "crx_rl_a3_dlq_cycles",
+                    "crx_rl_a4_spine": "crx_rl_a4_spine",
+                },
                 outputs="crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                 name="build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                 tags=_TAGS,
@@ -146,23 +165,22 @@ def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
             # build_a3_payment_credibility, wrapped) ────────────────────────────
             node(
                 func=build_rl_a3_payment_credibility,
-                inputs=[
-                    "crx_rl_a3_commitment_signals",
-                    "crx_rl_a3_strong_negative_signals",
-                    "crx_rl_a3_dlq_payment_signals_payment_sum_waterfall",
-                    "crx_rl_a3_dlq_payment_signals_single_payment_cycle_count",
-                    "crx_rl_a3_dlq_payment_signals_dpd_bucket_movement",
-                    "crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
-                    "crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
-                    "params:rl_a3_dlq_payment_evidence_method",
-                    "params:rl_a3_pre_dlq_payment_evidence_method",
-                    "params:model_id",
-                    "params:crx_persona.persona_end_date",
-                ],
+                inputs={
+                    "commitment_signals": "crx_rl_a3_commitment_signals",
+                    "negative_signals": "crx_rl_a3_strong_negative_signals",
+                    "dlq_payment_signals_payment_sum_waterfall": "crx_rl_a3_dlq_payment_signals_payment_sum_waterfall",
+                    "dlq_payment_signals_single_payment_cycle_count": "crx_rl_a3_dlq_payment_signals_single_payment_cycle_count",
+                    "dlq_payment_signals_dpd_bucket_movement": "crx_rl_a3_dlq_payment_signals_dpd_bucket_movement",
+                    "pre_dlq_payment_signals_single_payment_cycle_count": "crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
+                    "pre_dlq_payment_signals_dpd_bucket_movement": "crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
+                    "dlq_payment_evidence_method": "params:rl_a3_dlq_payment_evidence_method",
+                    "pre_dlq_payment_evidence_method": "params:rl_a3_pre_dlq_payment_evidence_method",
+                    "model_id": "params:model_id",
+                    "persona_end_date": "params:crx_persona.persona_end_date",
+                },
                 outputs="crx_rl_a3_payment_credibility",
                 name="build_rl_a3_payment_credibility",
                 tags=_TAGS,
             ),
         ],
-        tags=["crx_persona"],
     )
```
Gain: the same declaration style as A1/A2/A4 before A3 becomes `a3_credibility/` + wrappers; a swapped dataset in an 11-item list becomes a build-time error.
Risk: `git apply --check` passes on `d1ad38a`; whether the pipelines still build was checked with `refactor_smoke.py` on the scratch clone (same baseline FAIL only).
The node names of CC A3 are `build_a3_*` while RL is `build_rl_a3_*` and A1/A2/A4 are `build_crx_<p>_...`; a rename changes `--nodes` selection, so it is left out.
Depends on: the A3 session

Verdicts: R-E pending · R-I pending · R-O pending

## S3-A3-H2  A3 schema guards turn a source off quietly (no diff; needs a user decision first)
Files: cc_a3_payment_credibility/nodes.py:104-196 (`dcore_feat_ptp`, `dcore_feat_settlement`, `_SPINE_REQUIRED`), rl_a3_payment_credibility/nodes.py
Behaviour: possible (a missing column gives NULL signals and an Unknown state instead of a failed run)
Change: DESIGN D2 says missing required columns fail loud via `require_columns`, and only sources not yet in PROD are explicit optional params. The A3 guards log a warning
and null the columns; R-O's O1 anchor 1 names exactly this pattern. In the A3 rebuild each guard should become either `require_columns(...)` or an explicit optional input.
Which guards are real optional sources is a user decision (see Q-S3-7).
Diff: none
Gain: A3 follows D2.
Risk: a PROD run that today degrades quietly would stop.
Depends on: Q-S3-7

```
Q-S3-7 [A3 · cc_a3_payment_credibility/nodes.py:104-196] Schema guards on dcore_feat_ptp / dcore_feat_settlement / observation spine null the signals instead of failing.
Now: warning log, signal columns NULL, state falls to `payment_credibility_unknown`. Expected (D2): fail loud, unless the source is not yet in PROD.
Options: (a) keep, they are PROD-tolerant by design; (b) `require_columns`, explicit optional for the sources not in PROD.
Recommendation: (b) in the A3 rebuild, for the sources that exist in PROD today. | Impact: a PROD run with a missing column stops instead of producing Unknown.
Answer:
```

Verdicts: R-E pending · R-I pending · R-O pending

## S4-H1  A3: drop the third `_string_key` copy once a shared one exists
Files: workplace_mirror/src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/nodes.py:208-219
Behaviour: none
Change: `_rl_string_key` is the same function as `_dpd_journey/spark.py::_string_key` and `rl_full_history/nodes.py::_string_key`. After S1 puts one copy in a module both A3 and the A4 history can import (see F-1), A3 imports it and deletes its 12 lines, including the comment about not importing a private helper.
Diff: pending S1's choice of module (the import line cannot be written before that).
Gain: 12 lines and a rule ("a double/decimal id is cast to long before string") that lives in one place.
Risk: none expected; the helper is identical.
Depends on: S1 shared-helper decision

Verdicts: R-E pending · R-I pending · R-O pending

## S6-H01 (M) [A3 · `cc_a3_payment_credibility/_signals_common.py:93-97`, RL twin `rl_a3_payment_credibility/nodes.py:437-456`] Window start by `add_months` on month-end dates
Now: windows are `billing_date > greatest(t0, add_months(observation_date, -N), floor)` and
`<= observation_date`. On month-end observation dates Spark does not snap (S6-Q07): for
`2026-11-30` and N = 3 the start is `2026-08-30`, so a cycle or event dated `2026-08-31` falls in
the "3-month" window (a fourth month); for `2026-08-31` it is `2026-05-31`, which excludes May.
The window length then depends on the month. D-A3-2 writes the Dimension B start as
`greatest(anchor, observation_date − N months)`.
Spec/expected: D-A3-6 "as A1 and A2 do (`_common.window_months`)": calendar months, the
observation month included.
Recommendation: the redesigned A3 takes the window start from `_common` (first day of the
observation month minus N − 1 months), then `greatest` with the anchor; say so in D-A3-2.
Impact: CC rows whose previous-month billing date is on a day after the observation month's last
day (billing days 29–31) at 30-day / February observation months.

Verdicts: R-E pending · R-I pending · R-O pending

## S6-H02 (L) [A3 · `cc_a3_payment_credibility/nodes.py:528-529`] DCORE window exclusive at the observation date
Now: `szactiondate < observation_date`; D-A3-2 writes `[anchor, observation_date)`. A2 and the A1
EOSB diagnostic read DCORE events `<= observation_date`. With month-end dates, the last day of
the month counts for A2 reachability but not for A3 commitments / refusals.
Recommendation: one rule for both axes (inclusive, as A2), stated in D-A3-2; ask the user if the
exclusive bound was intended.
Impact: events on the last day of each month.

Verdicts: R-E pending · R-I pending · R-O pending

## S6-H03 (M) [A4 → A3 anchor · `_dpd_journey/core.py:108-141`] What the A4 anchor means on cropped or blind histories
Now: `months_before_spell` is the index of the current spell's start **within the kept history**
(after the CC floor 2024-01, a truncation or the source start). For a cropped history that starts
delinquent (`left_censored`), it is 0: the "spell start" is the first kept month, not the real one.
D-A3-2 uses it as the anchor for Dimension C (the 12 months before it), the Dimension B start and
the DCORE windows. For these rows the 12 months before the anchor lie before the floor, so
Dimension C reads `no_record`, and the DCORE / commitment window starts at the floor instead of
the real episode start. A4 also has no row at all for S6-Q01 rows and (today) for CC obs-base
dates (S6-Q05).
Recommendation: the A3 redesign states the anchor for `history_cropped & starts_delinquent` rows
(e.g. anchor unknown → Dimension C `no_record` flagged as "censored", and windows from the
observation-date lookback only), and D-A3-10's measurement counts these rows separately. Needs
S6-Q05 settled first (A4 on the obs base).
Impact: A4 `unknown` rows (large at 180+: "99% of the gt2y vintage" per `params.py`), plus every
CC row whose spell started before 2024-01.

Verdicts: R-E pending · R-I pending · R-O pending

## S6-H04 (L) [A3 `_signals_common.resolve_due_amount_m:641-700` vs A1 `cc_a1_ability/nodes.py:14,52-54`] "Oldest open overdue bucket" with two ranges
Now: A1's anchor is the oldest non-zero of `overdue_bucket_01..06` (S1 excludes OVD_07 =
181–210 and OVD_08). A3's due amount is the oldest non-zero of `07..01`, then `minimum_due`
(OVD_08 excluded, D-A3-12 handles it). At 60–180 OVD_07 is normally 0, so the two agree on almost
every row; at 180+ A1 has no anchor while A3 needs one.
Recommendation: if S1 extracts a shared "oldest open bucket" helper, it takes the bucket range as a
parameter (A1: 01–06; A3: 01–07 + `minimum_due`); no behaviour change. Ask the user only if a
single range is wanted.
Impact: none if parameterised.

---

Verdicts: R-E pending · R-I pending · R-O pending


## New entries (S1, A3 design-in, 2026-11-05)

## N-1  `_dcore_codes.REFUSING` split (D-A3-20)
Files: `crx_persona/_dcore_codes.py:168-188` (tier X here; the A3 session ships it, A3 only uses these sets)
Behaviour: A3 only, by decision D-A3-20 (refusal narrowed; dispute a diagnostic; hang-up to the avoidance diagnostics; `CUSTOMER MISBEHAVED` dropped).
Diff (against the mirror copy; check `REFUSING` has no other importer first: today only A3):
```diff
-REFUSING = {
-    "CUSTOMER HUNG UP",
-    "CUSTOMER MISBEHAVED",
-    "CUSTOMER_HUNG_UP",
-    "DISPUTE",
-    "KSA/DISPUTE",
-    "KSA/REFUSE TO PAY",
-    "REFUSE TO PAY",
-    "REFUSED TO PAY",
-    "REWRITE NOT AGREED",
-}
+# A3 (D-A3-20): explicit refusal, the stated-intent negative.
+REFUSAL = {"KSA/REFUSE TO PAY", "REFUSE TO PAY", "REFUSED TO PAY", "REWRITE NOT AGREED"}
+# A3 diagnostic column only: a contested debt is not unwillingness.
+DISPUTE = {"DISPUTE", "KSA/DISPUTE"}
+# A3 avoidance diagnostic (D-A3-19): hang-up as the latest right-party contact.
+HUNG_UP = {"CUSTOMER HUNG UP", "CUSTOMER_HUNG_UP"}
```
The comment block above `REFUSING` (lines 168-177) goes with it. Every name stays in `RIGHT_PARTY_CONTACT`.

## N-2  Parameters (D-A3-3)
Files: `conf/base/parameters/parameters_crx_persona.yml:25-71`
Change: delete `a3_dlq_payment_evidence_method`, `a3_pre_dlq_payment_evidence_method`,
`rl_a3_dlq_payment_evidence_method`, `rl_a3_pre_dlq_payment_evidence_method` and their comment blocks;
keep `cc_a3_history_floor_date` (D-A3-10). Parameter keys go by user decision (D-A3-3), so PLAN rule 5 is met.

## N-3  Catalog (D-A3-3, design-in)
Files: `catalog_crx.yml` (A3 block not fully photographed: needs the workplace copy)
Change: drop the waterfall / bucket-movement datasets (3 per product); add `crx_<p>_a3_episode`,
`crx_<p>_a3_instalments` (Q-32); `crx_<p>_a3_dues` / `_payments` stay memory datasets. Kept names:
`crx_<p>_a3_commitment_signals`, `_strong_negative_signals`, `_dlq_payment_signals_single_payment_cycle_count`,
`_pre_dlq_payment_signals_single_payment_cycle_count`, `crx_cc_a3_payment_cycles`, `crx_rl_a3_dlq_cycles`,
`crx_<p>_a3_payment_credibility` (dropping the method suffix is a rename: ask at bundle time).

## N-4  `build_cc_acct_windows` on the episode (D-A3-1, -18, O89)
Files: `cc_raw_extract/nodes.py:67-131` (tier K; current workplace file needed, D-A3-18)
Change: the per-account window starts at `min(episode_start) − 13 months` from `crx_cc_a3_episode`
(12 months of Dim C plus one cycle), floored at `cc_a3_history_floor_date` minus 35 days, through the
last observation date; `crx_cc_spell_table` is no longer read. No diff: the photographed copy predates the DE's work.

## N-5  RL 24-month follow-up floor (O69)
Files: `rl_a3_payment_credibility/nodes.py:183`
Change: replaced by `constants.DCORE_MAX_MONTHS` in `_in_episode` and a params-derived partition floor, both products (Q-30).

## N-6  Findings that disappear with the rebuild
O66 (duplicate reason loop), O67 (ticket history), O68 (repeated docstring line, pylint pragma), O70–O76,
O78, O79, O81, O82 (D-A3-8), O83, O85: the code they point at is not rebuilt. O77 → D-A3-10 check; O80
→ P9; O84 → constants with sheet references; O86–O88 → the CC dues / payments wrapper (O87's `.distinct()`
and O88's dedupe are in tier K `cc_raw_extract` and stay open for the A3 bundle).
