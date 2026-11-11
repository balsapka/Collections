"""Deterioration (deck A1) and credibility (deck A3) pages, latest agreed content."""
import sys
sys.path.insert(0, sys.argv[2])
from axis_helpers import *  # noqa: F401,F403

G, A, R = "#2E8B57", "#E0A526", "#C0392B"
FAM = {"cure": (BLUE, "#FFFFFF"), "stopped": ("#6FA3D6", "#FFFFFF"), "never": ("#4C515A", "#FFFFFF")}


def fchip(text, sub, fam, width=300):
    bg, fg = FAM[fam]
    return (f'<div style="width:{width}px;border-radius:8px;background:{bg};padding:8px 16px;display:flex;flex-direction:column">'
            f'<p style="font-size:22px;font-weight:600;white-space:nowrap;color:{fg}">{text}</p>'
            f'<p style="font-size:18px;color:{fg}">{sub}</p></div>')


ladder = [
    ("Nothing paid since the first months?", "Early payment default", "bad from the start", "never"),
    ("Holding at one level for months?", "Stabilized", "stopped falling", "cure"),
    ("Back within a year of curing?", "Repeat delinquent", "been here before", "cure"),
    ("Fell to 61+ fast, after a year of good history?", "Seasoned straight roller", "sudden stop", "stopped"),
    ("Fell to 61+ fast, in the first year?", "Early-life straight roller", "fell fast, early", "never"),
    ("Otherwise", "Slow roller", "fell slowly, paying on the way", "cure"),
]
rows = "".join(
    f'<div style="display:flex;align-items:center;gap:14px"><div style="width:34px;height:34px;border-radius:17px;flex:none;'
    f'background:{NAVY};display:flex;align-items:center;justify-content:center"><p style="font-size:18px;font-weight:600;line-height:1;color:#FFFFFF">{i}</p></div>'
    f'<p style="font-size:22px;width:560px;line-height:1.25">{q}</p><p style="font-size:26px;color:{BLUE}">→</p>{fchip(st, tag, fam)}</div>'
    for i, (q, st, tag, fam) in enumerate(ladder, 1))
det_how = (f'<p style="font-size:22px;color:#4C515A">Read from the DPD history alone, so it covers every account. Asked in order; the first “yes” decides.</p>'
           f'<div style="display:flex;flex-direction:column;gap:8px">{rows}</div>')
fams = [("Shown they can cure", FAM["cure"][0]), ("Paid well, then stopped", FAM["stopped"][0]), ("Never established", FAM["never"][0])]
det_mix = (stacked("Loans 61–180", [("Shown they can cure", 42.8, FAM["cure"][0]), ("Paid well, then stopped", 33.9, FAM["stopped"][0]),
                                    ("Never established", 23.3, FAM["never"][0])])
           + '<div style="display:flex;flex-direction:column;gap:10px"><p style="font-size:22px;font-weight:600">Cards 61–180</p>'
             '<div style="height:44px;border:2px dashed #D9D9D6;border-radius:6px"></div><p style="font-size:20px;color:#4C515A">[__] from the persona table run</p></div>')
OUT.joinpath("a4.html").write_text(slide(
    "a4", "A1 · Deterioration", "states", 1,
    "Four in ten delinquent loans have already shown they can cure",
    det_how, det_mix,
    [("[__]%", "of loans that have shown they can cure paid within 3 months, against [__]% of the rest."),
     ("1 in 3", "loans paid well for over a year, then stopped all at once: a life event, not a habit.")],
    "",
    "Deterioration reads only the DPD history, so it covers every account. Six questions asked in order; the first yes decides. "
    "The states fall into three families. Stabilized customers, slow rollers and repeat delinquents have already shown they can cure: they paid on the way down, stopped falling, or cured before. "
    "Seasoned straight rollers paid well for over a year and then stopped all at once, which points to a life event. "
    "Early payment defaults and early-life rollers never established a repayment record. For loans at 61 to 180, about four in ten have shown they can cure. "
    "The back-test shows how much more often they pay. Whatever the path, the next question is whether we can talk to them."))

# credibility
bands = [("High", "4+", 2, G), ("Moderate", "2–3", 2, A), ("Low", "0–1", 2, R)]
cred_how = scorecard(
    [("Promises kept", "last 12 months, on GRR's deadline", ["Kept +2", "Partly +1", "Broken −1"]),
     ("Paying while delinquent", "recent months", ["2+ full dues +2", "Any payment +1"]),
     ("Record before", "12 months before delinquency", ["Paid as billed +1"])],
    bands,
    [note("An explicit refusal to pay → <b>one band down</b>"),
     note("No delinquency record to judge yet → <b>Unknown</b>", True)])
cred_mix = (stacked("Cards 61–180", [("High", 2.3, G), ("Moderate", 15.6, A), ("Low or Unknown", 82.1, "#D9A39C")])
            + stacked("Loans 61–180", [("High", 2.2, G), ("Moderate", 22.1, A), ("Low or Unknown", 75.7, "#D9A39C")]))
s = slide(
    "a3", "A3 · Payment credibility", "score", 3,
    "Every point of credibility lowers the roll rate",
    cred_how, cred_mix,
    [("95% → 34%", "of card customers roll to a worse bucket: zero points vs four or more."),
     ("82%", "of card customers made no concluded promise in 12 months: untested, not bad.")],
    "Roll rate: back-test, states May 2026, outcomes to Aug 2026, earlier rule version",
    "Credibility is about this customer on this debt. Three sources earn points: promises kept in the last twelve months, judged on GRR's deadline; paying while delinquent; and the record before delinquency. "
    "Four points or more is High, two or three Moderate, below two Low. An explicit refusal moves one band down. "
    "Back-tested: card customers with zero points rolled 95% of the time, four or more points 34%. Most card customers have no concluded promise yet, so their record is untested, not bad: "
    "this is where the transcript signals will add the most.")
# keep scorecard band order High first: reverse the band strip and chip order already high-first
OUT.joinpath("a3.html").write_text(s)
print("ok")
