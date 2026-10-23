- For each model_id that was checked (cc_60_180, cc_180_plus): set it in
  conf/dev/globals_dev.yml, then in a Kedro notebook delete the HDFS snapshot copy:
    import sys, pathlib
    _c = pathlib.Path.cwd()
    ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
    sys.path.insert(0, str(ROOT / "data" / "input" / "mirror_bundles"))
    from b01_a1_engine_check import main
    main(catalog, step="cleanup")
  Restore model_id in globals_dev.yml to what it was before.
