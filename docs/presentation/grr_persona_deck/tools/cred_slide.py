"""Credibility page (deck A3): placeholders until the updated A3 run; within-band insight."""
import sys
sys.path.insert(0, sys.argv[2])
from axis_helpers import *  # noqa: F401,F403

G, A, R = "#2E8B57", "#E0A526", "#C0392B"
bands = [("High", "4+ points", 2, G), ("Moderate", "2–3", 2, A), ("Low", "0–1", 2, R)]
how = scorecard(
    [("Promises kept", "last 12 months, on GRR's deadline", ["Kept +2", "Partly +1", "Broken −1"]),
     ("Paying while delinquent", "regular = full amount due in 2+ recent months", ["Regular +2", "Some +1"]),
     ("Record before", "clean = paid as billed before falling behind", ["Clean +1"])],
    bands,
    [note("An explicit refusal to pay → <b>one band down</b>")])


def head(t, bg, fg):
    return f'<div style="background:{bg};border-radius:8px;padding:10px 0;display:flex;justify-content:center"><p style="font-size:22px;font-weight:600;color:{fg}">{t}</p></div>'


def cell():
    return '<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-radius:8px;height:72px;display:flex;align-items:center;justify-content:center"><p style="font-size:30px;font-weight:600">[__]%</p></div>'


grid = ('<div style="display:grid;grid-template-columns:150px 1fr 1fr 1fr;gap:10px">'
        '<p style="font-size:22px"></p>' + head("High", G, "#FFFFFF") + head("Moderate", A, NAVY) + head("Low", R, "#FFFFFF")
        + '<div style="display:flex;align-items:center"><p style="font-size:22px;font-weight:600">Cards</p></div>' + cell() + cell() + cell()
        + '<div style="display:flex;align-items:center"><p style="font-size:22px;font-weight:600">Loans</p></div>' + cell() + cell() + cell()
        + '</div>')
mix = (f'<div style="display:flex;flex-direction:column;gap:12px"><p style="font-size:22px;font-weight:600">61–180 DPD</p>{grid}'
       f'<p style="font-size:20px;color:{GREY}">From the updated credibility run</p></div>')
s = slide(
    "a3", "A3 · Payment credibility", "score", 3,
    "Within the same bucket, credible customers roll far less",
    how, mix,
    [("[__]% vs [__]%", "of card customers at 91–120 DPD rolled further: High vs Low credibility."),
     ("[__]%", "of card customers made no concluded promise in 12 months: untested, not bad.")],
    "Roll rates: back-test, 3-month outcomes compared within each DPD band",
    "Credibility is about this customer on this debt. Three sources earn points: promises kept in the last twelve months, judged on GRR's deadline; paying while delinquent, two points for paying the full amount due in two or more months and one for any payment of 100 dirhams or more; and the record before delinquency. "
    "Four points or more is High, two or three Moderate, below two Low. An explicit refusal moves one band down. "
    "Because points build up as customers pay, and paying keeps the bucket low, we compare outcomes within the same DPD band: at 91 to 120 days, how often High and Low credibility customers roll further. "
    "Many customers have no concluded promise yet, so their record is untested rather than bad: this is where the transcript signals will add the most.")
OUT.joinpath("a3.html").write_text(s)
print("ok")
