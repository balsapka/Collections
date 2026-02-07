"""
Runner script for Synthesizer — Final Brief Generator.
Reads all outputs from output/ and produces a consolidated project brief.

Usage:
    python3 scripts/run_synthesizer.py [--model MODEL]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.llm_client import call_llm
from src.utils.output_writer import write_output, load_all_outputs
from src.prompts.synthesizer_system import SYNTHESIZER_SYSTEM


def run(model: str | None = None) -> str:
    print("[Synthesizer] Collecting agent outputs...")
    sections = []

    for agent_prefix, label in [
        ("policy_extract", "POLICY EXTRACTION REPORTS"),
        ("policy_analysis", "POLICY ANALYSIS REPORTS"),
        ("policy_questions", "STAKEHOLDER QUESTIONS"),
        ("email_summary", "EMAIL THREAD SUMMARIES"),
        ("data_profile", "DATA PROFILES"),
    ]:
        docs = load_all_outputs(agent_prefix)
        if docs:
            sections.append(f"## {label}\n")
            for doc in docs:
                sections.append(f"### Source: {doc['filename']}\n{doc['content']}\n")

    if not sections:
        print("ERROR: No agent outputs found in output/ directory. Run agents first.")
        sys.exit(1)

    combined = "\n".join(sections)
    print(f"  Collected {len(sections)} sections, {len(combined):,} chars total")

    if len(combined) > 120_000:
        print("  Warning: Combined output very large, trimming...")
        combined = combined[:120_000] + "\n\n... (truncated)"

    user_msg = (
        "Below are all analyst reports from the document processing pipeline. "
        "Synthesize them into a single Data Science Project Brief as instructed.\n\n"
        f"{combined}"
    )
    return call_llm(SYNTHESIZER_SYSTEM, user_msg, model=model, max_tokens=8192)


def main():
    parser = argparse.ArgumentParser(description="Synthesizer — Final Brief Generator")
    parser.add_argument("--model", default=None, help="Override Claude model")
    parser.add_argument("--pdf", action="store_true", help="Also export output as PDF")
    args = parser.parse_args()

    result = run(model=args.model)
    path = write_output("project_brief", result, pdf=args.pdf)
    print(f"  -> Saved: {path}")
    print("Done.")


if __name__ == "__main__":
    main()
