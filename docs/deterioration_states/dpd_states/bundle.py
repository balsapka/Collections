"""Build BUNDLE.md: every source file of docs/deterioration_states in one markdown file,
for environments that can open .md but not .py files.

    python docs/deterioration_states/run.py bundle                      # from any folder

The bundle starts with instructions and a small extractor script. Running the extractor on
the saved BUNDLE.md recreates every file and checks each against its SHA-256, so nothing
depends on an LLM retyping code correctly.
"""
from __future__ import annotations

import hashlib
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]           # docs/deterioration_states
OUT = ROOT / "BUNDLE.md"

# Shipped files, in reading order. Evidence (validation/), outputs (results/) and the PDF
# are not code and are left out; empty folders are recreated by the extractor.
FILES = [
    "README.md",
    "run.py",
    "METHODOLOGY.md",
    "REVIEW.md",
    "PROMPTS.md",
    "dpd_states/__init__.py",
    "dpd_states/config.py",
    "dpd_states/features.py",
    "dpd_states/states.py",
    "dpd_states/analysis.py",
    "dpd_states/expectations.py",
    "dpd_states/file_mode.py",
    "dpd_states/discover.py",
    "dpd_states/synth.py",
    "dpd_states/run_synthetic.py",
    "dpd_states/selftest.py",
    "dpd_states/bundle.py",
    "snippets/dpd_states_validate.py",
]
EMPTY_DIRS = ["results", "validation"]

LANG = {".py": "python", ".md": "markdown"}

EXTRACTOR = '''"""Recreate docs/deterioration_states/ from BUNDLE.md and verify every file.

Run from the repo root, in this order:

    1. python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md
         -> must end with "N files OK, 0 mismatched"
    2. python -m pip install pandas numpy scikit-learn openpyxl      (once)
    3. python docs/deterioration_states/run.py selftest
         -> must end with "SELFTEST PASSED" (~1 minute)
    4. python docs/deterioration_states/run.py validate
         -> checks + state shares on data/input/dpd_synthetic_data.xlsx (config.py)
    5. optional: python docs/deterioration_states/run.py synthetic
    Spark mode later: snippets/dpd_states_validate.py, main(catalog) (PROMPTS.md P6)

Optional second argument writes somewhere else: extract_bundle.py BUNDLE.md <folder>
"""
import hashlib
import pathlib
import re
import sys

src = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.resolve().parent
lines = src.read_text(encoding="utf-8").split("\\n")
ok = bad = 0
i = 0
while i < len(lines):
    m = re.match(r"^### FILE: `([^`]+)`\\s*$", lines[i])
    if not m:
        i += 1
        continue
    rel = m.group(1)
    meta = lines[i + 1]
    sha = re.search(r"sha256 `([0-9a-f]{64})`", meta).group(1)
    trailing = "trailing newline: yes" in meta
    j = i + 2
    while not lines[j].startswith("`````"):
        j += 1
    fence = re.match(r"^(`+)", lines[j]).group(1)
    k = j + 1
    while lines[k] != fence:
        k += 1
    body = "\\n".join(lines[j + 1:k])
    if body and trailing:
        body += "\\n"
    out = root / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body.encode("utf-8"))
    good = hashlib.sha256(body.encode("utf-8")).hexdigest() == sha
    ok += good
    bad += not good
    print(("OK       " if good else "MISMATCH ") + rel)
    i = k + 1
for d in re.findall(r"^- empty folder: `([^`]+)`", "\\n".join(lines), flags=re.M):
    (root / d).mkdir(parents=True, exist_ok=True)
    (root / d / ".gitkeep").touch()
print(f"\\n{ok} files OK, {bad} mismatched -> {root}")
if not bad:
    print("Next, from the repo root: python docs/deterioration_states/run.py selftest")
    print("then:                     python docs/deterioration_states/run.py validate")
sys.exit(1 if bad else 0)
'''


def _fence(text: str) -> str:
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    return "`" * max(5, longest + 1)


def build() -> Path:
    parts = []
    tree = ["docs/deterioration_states/"] + [f"├── {f}" for f in FILES] + [f"├── {d}/" for d in EMPTY_DIRS]
    total = 0
    for rel in FILES:
        raw = (ROOT / rel).read_bytes()
        text = raw.decode("utf-8")
        total += text.count("\n")
        sha = hashlib.sha256(raw).hexdigest()
        trailing = "yes" if text.endswith("\n") else "no"
        body = text[:-1] if text.endswith("\n") else text
        fence = _fence(text)
        lang = LANG.get(Path(rel).suffix, "")
        parts.append(f"### FILE: `{rel}`\n"
                     f"sha256 `{sha}` · {text.count(chr(10))} lines · trailing newline: {trailing}\n\n"
                     f"{fence}{lang}\n{body}\n{fence}\n")

    doc = f"""# Deterioration states — full source bundle

## Run this (from the repo root)

```bash
# 1. recreate every file and verify checksums      -> "N files OK, 0 mismatched"
python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md

# 2. dependencies (once)
python -m pip install pandas numpy scikit-learn openpyxl

# 3. self-test on synthetic data                    -> "SELFTEST PASSED"  (~1 min)
python docs/deterioration_states/run.py selftest

# 4. validate on the real file                      -> checks + state shares
#    reads data/input/dpd_synthetic_data.xlsx, column dpd_history_str (config.py),
#    crops to the history window (reliable from 2024-01; 24-month extract -> 24), keeps buckets 4-7
python docs/deterioration_states/run.py validate
#    another file and/or sample size:
#    python docs/deterioration_states/run.py validate data/input/other_file.xlsx 50000

# 5. optional: synthetic method-validation report
python docs/deterioration_states/run.py synthetic
```

Step 1 needs `extract_bundle.py` — create it from the **Extractor** section below the first
time. Step 4 prints the checks between `=== DPD_STATES OUTPUT START ===` and `END` and writes
`docs/deterioration_states/results/dpd_states_file_<file>_<date>.json` + `.md` (aggregates
only) — paste the printed block back, or follow PROMPTS.md P0 -> P2 with Sonnet.

If it fails: "column ... not in" -> check COL_DPD in `dpd_states/config.py`; "look like
numbers" -> the Excel column is stored as numbers (digits lost), re-save it as text;
"No module named openpyxl" -> step 2; snapshot not Aug 2026 -> set SNAPSHOT_MONTH in config.

Spark mode (later, for outcomes / production), in a Kedro notebook — PROMPTS.md P6:

```python
import sys, pathlib
_c = pathlib.Path.cwd()
ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "snippets"))
from dpd_states_validate import main
main(catalog, check_only=True)   # dry run: schema, counts, orientation (aggregates)
result = main(catalog)           # full validation incl. backtest -> results/
```

---

Generated {date.today().isoformat()} by `dpd_states/bundle.py`. {len(FILES)} files, {total:,} lines.
This one markdown file contains **every source file** of `docs/deterioration_states/`, for
environments where `.py` files cannot be opened. Regenerate it after any change with
`python docs/deterioration_states/run.py bundle`.

## Instructions for the assistant recreating the files (read first)

1. **Do not retype the code.** Long files retyped by hand (or by a model) pick up small
   errors. Instead:
   - save this whole file, unchanged, as `docs/deterioration_states/BUNDLE.md` in the
     workplace repository (copy the **raw** markdown — e.g. GitHub's "Copy raw file"
     button — not the rendered page, which drops the code fences);
   - create `docs/deterioration_states/extract_bundle.py` with the extractor below;
   - run `python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md`.
2. The extractor writes every file and checks its SHA-256. It must end with
   **"N files OK, 0 mismatched"**. A mismatch means the copy of this markdown was altered
   (line endings, smart quotes, a rendered instead of raw copy) — recopy the raw file;
   do not hand-fix the code.
3. Then run the self-test — from any folder, e.g. the repo root:
   `python docs/deterioration_states/run.py selftest` → must print **SELFTEST PASSED**
   (needs pandas, numpy, scikit-learn; ~1 minute). Do not use `python -m dpd_states...`
   from the repo root: the package sits inside `docs/deterioration_states/`, so Python
   will not find it there.
4. Only after that, follow `PROMPTS.md` (P0 → P1 → P2). The only files to edit are
   `dpd_states/config.py` and the marked `<<FILL-IN>>` spot in
   `snippets/dpd_states_validate.py`.
5. Fallback, only if no script can be run: create each file below verbatim from its code
   block (the text between the fence lines, nothing else), then run the extractor's
   checksum part to confirm.

## Extractor

`````python
{EXTRACTOR.rstrip()}
`````

## Folder structure

```
{chr(10).join(tree)}
```

- empty folder: `results`
- empty folder: `validation`

`results/` receives the real-data outputs; `validation/` holds the synthetic evidence
(regenerate with `python docs/deterioration_states/run.py selftest` and `... run.py synthetic`).

## Files

{chr(10).join(parts)}"""
    OUT.write_text(doc, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    p = build()
    print(p, f"{p.stat().st_size / 1024:.0f} KB")
