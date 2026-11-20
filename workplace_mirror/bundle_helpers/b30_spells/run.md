No persona output changes, so there is no comparison run.

**Step 7.** In PROD, after the pull, confirm the persona pipelines still resolve (no data is read):

```bash
kedro registry list | grep crx_
```

Paste back the list. Then the cleanup prompt.
