7. **Before re-running A1**, keep a copy of the current output. In a Kedro notebook
   (`kedro jupyter notebook`, from any folder in the repo):

   ```python
   import sys, pathlib
   _c = pathlib.Path.cwd()
   ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
   sys.path.insert(0, str(ROOT / "data" / "input" / "mirror_bundles"))
   from b01_a1_engine_check import main
   main(catalog, step="snapshot")
   ```

8. Rebuild the observation base and the A1 axis (terminal):

   ```bash
   kedro run --pipeline=crx_cc_obs_base
   ```

   ```bash
   kedro run --pipeline=crx_cc_a1_ability_v2
   ```

9. Compare old vs new (same notebook) and paste the printed `B01 OUTPUT` block back:

   ```python
   main(catalog, step="compare")
   ```

10. Repeat 7–9 for the other CC segment: set `model_id` in `conf/dev/globals_dev.yml`
    (`cc_60_180` ↔ `cc_180_plus`), restart the notebook kernel, run again.
