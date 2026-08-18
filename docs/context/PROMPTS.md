# Session Prompts

Copy-paste prompts for running this programme. **For the human, not the LLM** — these
are what you type to open a session.

Context is cleared between sessions, so every prompt is self-contained. Swap the task
ID and go.

---

## 1. Start a task (leg A)

```
Read docs/context/00_START_HERE.md and docs/context/TASKS.md, then do T01.

Follow the session protocol: one task only, log the result to RESULTS.md and update the status in TASKS.md when done.
```

What comes back depends on the task:

| Task type | Result |
|---|---|
| No round trip (T01, T16) | Finished work product → status `done` |
| Diagnostic | A snippet module in `docs/context/snippets/` → status `in-progress (snippet out)` |
| Build task | Pipeline code **plus** a validation snippet → status `in-progress` |

---

## 2. Results came back (leg B)

After running the snippet in a Kedro notebook and pulling the results file into UAT:

```
Read docs/context/00_START_HERE.md, docs/context/TASKS.md, and the T02 card in docs/context/tasks/.

I ran the PROD snippet and pulled the results into UAT — they're in docs/context/results/. Read the results file, check its scope field, then complete leg B:

- state which branch of the card's decision rule the result takes
- log the headline number, the decision, and the results file path to RESULTS.md
- update the status in TASKS.md
- if anything changes a plan assumption, note it under "Proposed amendments" rather than re-planning

One task only — don't start the next.
```

**If the output was small enough to paste** rather than written to a file, replace the
second paragraph with:

```
I ran the PROD snippet. Here is the output:

=== T02 OUTPUT START ===
<paste>
=== T02 OUTPUT END ===
```

Naming the card explicitly saves a lookup through TASKS.md. Asking it to *state which
branch* forces a commitment rather than a narration of the numbers — that is what the
decision rules on the cards are for.

---

## 3. The snippet failed

Schema mismatch, missing catalog entry, wrong scope dataset name. This is still leg A —
it needs fixing, not interpreting:

```
Read docs/context/00_START_HERE.md, docs/context/TASKS.md, and the T02 card in docs/context/tasks/.

The T02 snippet failed in PROD. Output:

<paste the error / schema mismatch>

Fix the snippet in docs/context/snippets/ and hand it back. Keep the task in-progress.
```

---

## 4. Running the snippet (in a Kedro notebook)

Works from any notebook location — `notebooks/local/` or elsewhere. CWD is never used:

```python
import sys, pathlib
_c = pathlib.Path.cwd()
ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
sys.path.insert(0, str(ROOT / "docs" / "context" / "snippets"))

from t02_transaction_retention import main
result = main(catalog)
```

`main()` prints a summary, writes a results file to `docs/context/results/` when the
output is too big to paste, and returns the payload so you can inspect it without a
re-run. If it wrote a file: commit and push from PROD, pull in UAT, then use prompt 2.

---

## 5. Parallel windows

Tasks with no unmet dependencies can run simultaneously. Check the `Depends` column in
`TASKS.md` — anything showing `—` is startable now.

**The batching trick:** most diagnostics hand you a snippet rather than an answer, so
open several windows at once, collect all the snippets, then **run them in one PROD
sitting**. One PROD access clears three or four diagnostics. Tasks needing no round
trip (T01, T16) are worth a window of their own — they produce finished work while the
others are out.

---

## 6. Useful variants

**Check where things stand:**
```
Read docs/context/TASKS.md and docs/context/RESULTS.md, then summarise: what is done, what is in-progress with a snippet out, and what is startable now.
```

**Question a plan decision** (rather than doing a task):
```
Read docs/context/00_START_HERE.md and docs/context/reference/domain_and_decisions.md.

<your question>

If this contradicts a settled decision (S-list) or a rejected approach (X-list), say which and why, and propose the amendment in RESULTS.md rather than acting on it.
```
