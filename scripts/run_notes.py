"""
Runner script for Meeting Notes Summarizer & Insight Creator.
Called by the Claude Code notes-summarizer agent.

Usage:
    python3 scripts/run_notes.py <path_to_file>
    python3 scripts/run_notes.py --text "pasted notes content"
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.file_extract import extract_text
from src.utils.llm_client import call_llm
from src.utils.output_writer import write_output
from src.prompts.notes_system import NOTES_SYSTEM


def run(notes_text: str, model: str | None = None) -> str:
    print("[Notes Agent] Summarizing discussion notes and extracting insights...")
    user_msg = (
        "Below are hand-written notes from a verbal discussion related to a bank "
        "collections / credit risk project. Summarize and extract insights as instructed.\n\n"
        "--- NOTES START ---\n"
        f"{notes_text}\n"
        "--- NOTES END ---"
    )
    return call_llm(NOTES_SYSTEM, user_msg, model=model, max_tokens=4096)


def main():
    parser = argparse.ArgumentParser(description="Meeting Notes Summarizer & Insight Creator")
    parser.add_argument("file", nargs="?", help="Path to notes file (.md, .txt)")
    parser.add_argument("--text", help="Paste notes content directly")
    parser.add_argument("--model", default=None, help="Override Claude model")
    parser.add_argument("--pdf", action="store_true", help="Also export output as PDF")
    args = parser.parse_args()

    if args.text:
        notes_text = args.text
        source = "direct_input"
    elif args.file:
        print(f"Extracting text from: {args.file}")
        notes_text = extract_text(args.file)
        source = args.file
    else:
        print("ERROR: Provide a file path or --text argument.")
        sys.exit(1)

    print(f"  Input: {len(notes_text):,} characters")
    if not notes_text.strip():
        print("ERROR: No content to process.")
        sys.exit(1)

    result = run(notes_text, model=args.model)
    path = write_output("notes_summary", result, source, pdf=args.pdf)
    print(f"  -> Saved: {path}")
    print("Done.")


if __name__ == "__main__":
    main()
