import json, re, sys, pathlib
D = pathlib.Path(sys.argv[1])  # deck root (holds project/)
extract = sys.argv[2] if len(sys.argv) > 2 else None
deck = json.loads((D / "project/deck.json").read_text())
css = (D / "project/deck.css").read_text()
secs = [(D / f"project/slides/{s}.html").read_text() for s in deck["order"]]
head = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap">
<style>body{{margin:0;background:#888}} section{{width:1920px;height:1080px;position:relative;overflow:hidden;box-sizing:border-box}} aside{{display:none}}
@page{{size:1920px 1080px;margin:0}} section{{break-after:page}}
{css}</style></head><body>"""
tail = "</body></html>"
page = head + "\n".join(secs) + tail
pathlib.Path("page.html").write_text(page)
if extract:
    js = pathlib.Path(extract).read_text()
    pathlib.Path("page_extract.html").write_text(head + "\n".join(secs) + js + tail)
print(len(secs))
