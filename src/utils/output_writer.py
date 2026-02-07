"""
Writes agent output to markdown files (and optionally PDF) in the output/ directory.
"""

import os
import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"


def write_output(agent_name: str, content: str, input_file: str = "", pdf: bool = False) -> str:
    """Write agent output to a timestamped markdown file. Optionally export PDF. Returns the .md path."""
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

    if pdf:
        pdf_path = out_path.with_suffix(".pdf")
        _export_pdf(content, pdf_path, agent_name, input_file)
        print(f"  -> PDF:  {pdf_path}")

    return str(out_path)


def _export_pdf(markdown_text: str, pdf_path: Path, agent_name: str, source: str) -> None:
    """Convert markdown content to PDF via markdown + weasyprint."""
    try:
        import markdown
        from weasyprint import HTML
    except ImportError:
        print("  Warning: PDF export requires 'markdown' and 'weasyprint'. "
              "Install with: pip install markdown weasyprint")
        return

    html_body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code", "toc"],
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 11pt;
         line-height: 1.5; color: #1a1a1a; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
  h1 {{ font-size: 18pt; border-bottom: 2px solid #2c3e50; padding-bottom: 6px; }}
  h2 {{ font-size: 14pt; color: #2c3e50; margin-top: 24px; }}
  h3 {{ font-size: 12pt; color: #34495e; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 9pt; }}
  th, td {{ border: 1px solid #bdc3c7; padding: 6px 8px; text-align: left; }}
  th {{ background-color: #ecf0f1; font-weight: 600; }}
  code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-size: 9pt; }}
  pre {{ background: #f4f4f4; padding: 12px; border-radius: 4px; overflow-x: auto; font-size: 9pt; }}
  .header {{ color: #7f8c8d; font-size: 8pt; margin-bottom: 20px; }}
</style></head><body>
<div class="header">Agent: {agent_name} | Source: {source or 'N/A'} | {timestamp}</div>
{html_body}
</body></html>"""

    HTML(string=full_html).write_pdf(str(pdf_path))


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
