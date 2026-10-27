# Gather the open REQUESTS snippets into one file

For the workplace Sonnet 5.5 in UAT. It replaces the photo requests R4, R5, R8, R9, R10 and R11
(`workplace_mirror/REQUESTS.md`). Photograph or transcribe the one file it writes,
`tmp_validation/mirror_requests/snippets.md`, into `pics/`.

````text
Goal. Copy a few code snippets and catalog entries, verbatim, into one Markdown file so they can
be transferred to the mirror repo in a single photo batch. Read only; change no code. If a
location below is wrong, find the right one and say where it was.

Write tmp_validation/mirror_requests/snippets.md. For each item: a heading with the item id, the
file path and the exact line range, then the text in a fenced block exactly as in the file (no
reformatting, no elisions inside a block). If an item does not exist, write NOT FOUND and where
you looked. Keep the whole file under 350 lines; when an item is longer than its budget, keep
the parts named in the item and mark each cut with "# … lines N–M omitted".

R5  pipelines/bureau/staging.py: the node that builds stg_aecb_salary_history and the function
    it calls (where the columns are selected / renamed) — the column names are what matters
    (file id, reference month, provider number, salary amount, transfer count, EDP load date).
    Budget 40 lines.
R8  the node(...) block in the pipeline file that builds feat_demographics_cif; and the catalog
    entry of raw_beneficiary_cards (whichever catalog file holds it). Budget 25 lines.
R9  nodes/staging/dcore/stg_dcore_observation_spine.py: the part that gets agreement_id and
    joins it to the spine (roughly lines 24-92); and the raw catalog entry (catalog_raw_dcore.yml)
    of the table that maps an agreement to its account / contract. Budget 90 lines.
R10 the final select / return of prm_cc.build_contract (block-code columns) and of the node in
    prm_demographics.py that sets deceased_flag (its key column and deceased_flag). Budget 40
    lines.
R11 the final select of prm_cc.build_transaction and the lines that parse DOMESTIC= from
    add_info. Budget 40 lines.
R4  the output of this command, run from the repo root (paste the output, not the command's
    matches from __pycache__):
      grep -rnE "crx_cc_departure_signature|crx_cc_payment_trajectory|crx_cc_utilisation_features|crx_rl_departure_signature|crx_cc_departure_pass" src conf notebooks 2>/dev/null | grep -v "\.pyc" | grep -vE "/crx_persona/|catalog_crx\.yml"
    Budget 40 lines; empty output means nothing outside the persona code reads them — say so.

Commit and push only tmp_validation/mirror_requests/.
````
