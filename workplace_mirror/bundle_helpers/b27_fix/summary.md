**What this bundle does.** Two fixes to bundle 25's check, to apply now, on top of bundle 25 (bundle 26 may come before or after; they touch different files).

- **Check outputs are saved.** The `"{name}__b25"` catalog pattern did not resolve in the workplace: every rerun dataset fell back to MemoryDataset. Nothing was saved, and each comparison recomputed the whole chain from the raw tables (`compare_a1` ran over 30 minutes; repeated "Broadcasting large task binary" warnings). `tmp_b25_check.yml` is replaced by `catalog_tmp_b25_check.yml`: 64 explicit entries (36 cc, 34 rl, 6 shared), same HDFS folder `.../<model_id>/<persona>/b25_check/<name>`, Spark parquet, overwrite.
- **A4 UDF warning.** Both Python UDFs in the A4 engine (`_dpd_journey/spark.py`) are marked non-deterministic. Spark had copied the UDF's output into a join condition (`ExtractPythonUDFFromJoinCondition`), which turned the join into a cross join, and it ran the UDF several times per row. Output unchanged: A4 chain spec and the golden harness (188 datasets) pass.

Bundle 25's step 7 and step 8 stay as they are; this bundle's cleanup replaces bundle 25's.
