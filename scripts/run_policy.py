"""
Runner script for Policy Document Analyzer.
Called by the Claude Code policy-analyzer agent.

Usage:
    python3 scripts/run_policy.py <path_to_file> [--passes 1,2,3] [--model MODEL]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.file_extract import extract_text
from src.utils.llm_client import call_llm
from src.utils.output_writer import write_output
from src.prompts.policy_system import PASS1_EXTRACT, PASS2_ANALYZE, PASS3_QUESTIONS


def run_pass1(document_text: str, model: str | None = None) -> str:
    print("[Pass 1/EXTRACT] Extracting policy structure...")
    if len(document_text) > 80_000:
        print(f"  Document is {len(document_text):,} chars — processing in full")
    user_msg = (
        "Below is the full text of a bank collections/delinquency policy document. "
        "Extract all structured information as instructed.\n\n"
        "--- DOCUMENT START ---\n"
        f"{document_text}\n"
        "--- DOCUMENT END ---"
    )
    return call_llm(PASS1_EXTRACT, user_msg, model=model, max_tokens=8192)


def run_pass2(document_text: str, pass1_output: str, model: str | None = None) -> str:
    print("[Pass 2/ANALYZE] Analyzing for data science implications...")
    user_msg = (
        "## EXTRACTED POLICY STRUCTURE (from Pass 1)\n\n"
        f"{pass1_output}\n\n---\n\n"
        "## ORIGINAL DOCUMENT (for reference)\n\n"
        f"{document_text[:40_000]}\n"
        "\n\nProduce your data science analysis based on the extraction above."
    )
    return call_llm(PASS2_ANALYZE, user_msg, model=model, max_tokens=8192)


def run_pass3(pass1_output: str, pass2_output: str, model: str | None = None) -> str:
    print("[Pass 3/QUESTIONS] Generating stakeholder questions...")
    user_msg = (
        "## EXTRACTED POLICY STRUCTURE\n\n"
        f"{pass1_output}\n\n---\n\n"
        "## DATA SCIENCE ANALYSIS\n\n"
        f"{pass2_output}\n\n---\n\n"
        "Based on the above extraction and analysis, generate your prioritized questions."
    )
    return call_llm(PASS3_QUESTIONS, user_msg, model=model, max_tokens=4096)


def main():
    parser = argparse.ArgumentParser(description="Policy Document Analyzer")
    parser.add_argument("file", help="Path to the policy document (PDF, DOCX, TXT)")
    parser.add_argument("--passes", default="1,2,3", help="Comma-separated pass numbers (default: 1,2,3)")
    parser.add_argument("--model", default=None, help="Override Claude model")
    args = parser.parse_args()

    passes = [int(p.strip()) for p in args.passes.split(",")]

    print(f"Extracting text from: {args.file}")
    doc_text = extract_text(args.file)
    print(f"  Extracted {len(doc_text):,} characters")

    if not doc_text.strip():
        print("ERROR: No text could be extracted from the file.")
        sys.exit(1)

    p1 = p2 = None

    if 1 in passes:
        p1 = run_pass1(doc_text, model=args.model)
        path = write_output("policy_extract", p1, args.file)
        print(f"  -> Saved: {path}")

    if 2 in passes:
        if p1 is None:
            from src.utils.output_writer import load_all_outputs
            prev = load_all_outputs("policy_extract")
            if prev:
                p1 = prev[-1]["content"]
            else:
                print("ERROR: Pass 2 requires Pass 1 output. Run pass 1 first.")
                sys.exit(1)
        p2 = run_pass2(doc_text, p1, model=args.model)
        path = write_output("policy_analysis", p2, args.file)
        print(f"  -> Saved: {path}")

    if 3 in passes:
        if p1 is None or p2 is None:
            from src.utils.output_writer import load_all_outputs
            if p1 is None:
                prev = load_all_outputs("policy_extract")
                p1 = prev[-1]["content"] if prev else None
            if p2 is None:
                prev = load_all_outputs("policy_analysis")
                p2 = prev[-1]["content"] if prev else None
            if not p1 or not p2:
                print("ERROR: Pass 3 requires Pass 1+2 outputs. Skipping.")
                sys.exit(1)
        p3 = run_pass3(p1, p2, model=args.model)
        path = write_output("policy_questions", p3, args.file)
        print(f"  -> Saved: {path}")

    print("\nDone. Outputs saved to output/ directory.")


if __name__ == "__main__":
    main()
