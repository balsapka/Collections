**Step 4.** Check that the warnings are gone and nothing else moved:

```bash
kedro registry list 2>&1 | grep -c "contains '.'"
```

It prints `0`. `git status` shows only `src/enbd_collections/pipelines/crx_persona/a3_credibility/check.py`.
