"""
Runner script for Email Thread Distiller.
Called by the Claude Code email-distiller agent.

Usage:
    python3 scripts/run_email.py <path_to_file>
    python3 scripts/run_email.py --text "pasted email content"
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.utils.file_extract import extract_text
from lib.utils.llm_client import call_llm
from lib.utils.output_writer import write_output
from lib.prompts.email_system import EMAIL_SYSTEM


def run(email_text: str, model: str | None = None) -> str:
    print("[Email Agent] Distilling email thread...")
    user_msg = (
        "Below is an email thread related to a bank collections / credit risk project. "
        "Distill it as instructed.\n\n"
        "--- EMAIL THREAD START ---\n"
        f"{email_text}\n"
        "--- EMAIL THREAD END ---"
    )
    return call_llm(EMAIL_SYSTEM, user_msg, model=model, max_tokens=4096)


def main():
    parser = argparse.ArgumentParser(description="Email Thread Distiller")
    parser.add_argument("file", nargs="?", help="Path to email file (.eml, .txt)")
    parser.add_argument("--text", help="Paste email content directly")
    parser.add_argument("--model", default=None, help="Override Claude model")
    args = parser.parse_args()

    if args.text:
        email_text = args.text
        source = "direct_input"
    elif args.file:
        print(f"Extracting text from: {args.file}")
        email_text = extract_text(args.file)
        source = args.file
    else:
        print("ERROR: Provide a file path or --text argument.")
        sys.exit(1)

    print(f"  Input: {len(email_text):,} characters")
    if not email_text.strip():
        print("ERROR: No content to process.")
        sys.exit(1)

    result = run(email_text, model=args.model)
    path = write_output("email_summary", result, source)
    print(f"  -> Saved: {path}")
    print("Done.")


if __name__ == "__main__":
    main()
