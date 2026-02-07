"""
Writes agent output to markdown files in the output/ directory.
"""

import os
import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"


def write_output(agent_name: str, content: str, input_file: str = "") -> str:
    """Write agent output to a timestamped markdown file. Returns the output path."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_stem = Path(input_file).stem if input_file else "manual"
    filename = f"{agent_name}_{input_stem}_{timestamp}.md"
    out_path = OUTPUT_DIR / filename

    header = (
        f"<!-- Agent: {agent_name} | Source: {input_file or 'N/A'} "
        f"| Generated: {datetime.now().isoformat()} -->\n\n"
    )

    out_path.write_text(header + content, encoding="utf-8")
    return str(out_path)


def load_all_outputs(agent_name: str | None = None) -> list[dict]:
    """Load all output files, optionally filtered by agent name. Used by synthesizer."""
    results = []
    if not OUTPUT_DIR.exists():
        return results

    for f in sorted(OUTPUT_DIR.glob("*.md")):
        if agent_name and not f.name.startswith(agent_name):
            continue
        results.append({
            "filename": f.name,
            "content": f.read_text(encoding="utf-8"),
        })
    return results
