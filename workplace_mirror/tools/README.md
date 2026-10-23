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

   → `workplace_mirror/bundles/NN_<slug>.md`. `src/` and `conf/` changes are bundled as
   source (replaced / deleted files carry their base version for the safety check);
   `--helper` files (e.g. `bundle_helpers/b01_*.py`) go to the workplace's gitignored
   `data/input/mirror_bundles/`; `--run-file` / `--cleanup-file` add the bundle's own PROD
   steps and cleanup lines.
4. Commit and push the bundle.

## Workplace side

Every bundle starts with a **Steps** section: the exact commands, in order, from the
workplace repo root. In short: branch → save the bundle raw to
`data/input/mirror_bundles/` (gitignored) → write `apply_bundle.py` from the bundle →
`--check` → `--apply` → the bundle's PROD run and check → paste the output back. Helpers
(PROD check snippets, their results) also land in `data/input/mirror_bundles/`; nothing
there is ever committed. Each bundle ends with a **Cleanup prompt** for the workplace
assistant that deletes that folder and any temporary PROD data the check created.

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
