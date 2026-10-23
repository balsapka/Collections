# Moving mirror changes to the workplace repo

The workplace repo can only read `.md` files from this GitHub repo, so every change ships as a
**mirror bundle**: one markdown file holding the changed files plus a script that writes them
safely. Nobody retypes code.

## Here (this repo)

1. `workplace_mirror/src/...` is a verbatim copy of the workplace code (photo transcriptions).
   The commit that matches the workplace today is the **base**.
2. Make the change in `workplace_mirror/`, one sub-task per commit (or a few).
3. Build the bundle from base to head:

   ```bash
   python workplace_mirror/tools/make_bundle.py --base <base-commit> --slug a1_engine --title "Extract the shared A1 engine" --summary-file notes.md
   ```

   → `workplace_mirror/bundles/NN_<slug>.md`. Only `src/` and `conf/` files are bundled. Each
   replaced or deleted file carries its base version too, so the workplace side can check it.
4. Commit and push the bundle.

## Workplace side

```bash
git checkout -b crx/<slug>                      # never on main (the script refuses)
# GitHub -> bundle -> "Copy raw file" -> save as docs/mirror_bundles/NN_<slug>.md
# first time only: create docs/mirror_bundles/apply_bundle.py from the bundle's "Apply script" section
python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/NN_<slug>.md --check   # CHECK PASSED
python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/NN_<slug>.md --apply   # APPLY PASSED
git add -A src conf && git commit -m "Mirror bundle NN: <title>"
```

Then run the bundle's PROD check (parity or distribution snippet, when it has one) before
merging the branch.

## What protects the running code

| Guard | What it catches |
|---|---|
| SHA-256 per block | a damaged copy (rendered page, smart quotes, lost lines) → `DAMAGED`, nothing written |
| base hash per replaced/deleted file | the workplace file differs from what was photographed (someone's edit, or a transcription typo) → `CONFLICT` + diff, nothing written |
| branch / dirty-file check | applying on main, or over uncommitted work in a touched file |
| compile + import of every touched module and `pipeline_registry` | a broken import or a module still referenced after deletion → `APPLY FAILED`, undo with `--revert` |
| `--revert` | restores the exact committed bytes, removes added files; leaves files edited after apply alone |
| branch + PROD check before merge | behaviour: parity (refactors must match old outputs) or a before/after distribution |

**On a CONFLICT:** photograph the workplace file again (or send the printed diff). If it's a
transcription typo, fix the mirror's base commit history going forward (re-baseline: commit the
corrected file as a new base) and rebuild the bundle. If it's a real workplace change (e.g. the
DE's credibility work), re-photograph and rebase the mirror change on it.

Line endings don't matter (CRLF and LF hash the same). Modules the DE owns
(`cc_a3_payment_credibility`, `rl_a3_payment_credibility`) are never put in a bundle.
