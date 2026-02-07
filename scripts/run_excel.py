"""
Runner script for Excel/Data File Profiler.
Called by the Claude Code data-profiler agent.

Usage:
    python3 scripts/run_excel.py <path_to_file>
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.file_extract import get_excel_profile, extract_text
from src.utils.llm_client import call_llm
from src.utils.output_writer import write_output
from src.prompts.excel_system import EXCEL_SYSTEM


def run(file_path: str, model: str | None = None) -> str:
    print("[Excel Agent] Profiling data file...")
    try:
        profile = get_excel_profile(file_path)
        profile_text = json.dumps(profile, indent=2, default=str)
    except Exception as e:
        print(f"  Warning: Pandas profiling failed ({e}), falling back to text extraction")
        profile_text = extract_text(file_path)

    raw_preview = extract_text(file_path)
    if len(raw_preview) > 10_000:
        raw_preview = raw_preview[:10_000] + "\n... (truncated)"

    user_msg = (
        "Below is a data profile and raw preview of a dataset "
        "from a bank's collections/delinquency operations.\n\n"
        "## STRUCTURED PROFILE\n"
        f"```json\n{profile_text}\n```\n\n"
        "## RAW DATA PREVIEW\n"
        f"```\n{raw_preview}\n```\n\n"
        "Produce your data assessment as instructed."
    )
    return call_llm(EXCEL_SYSTEM, user_msg, model=model, max_tokens=4096)


def main():
    parser = argparse.ArgumentParser(description="Excel/Data File Profiler")
    parser.add_argument("file", help="Path to Excel (.xlsx/.xls) or CSV file")
    parser.add_argument("--model", default=None, help="Override Claude model")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: File not found: {args.file}")
        sys.exit(1)

    result = run(args.file, model=args.model)
    path = write_output("data_profile", result, args.file)
    print(f"  -> Saved: {path}")
    print("Done.")


if __name__ == "__main__":
    main()
