"""Deterioration page (deck A1): families green / amber / grey, shares as stacked rows."""
import sys
sys.path.insert(0, sys.argv[2])
from axis_helpers import *  # noqa: F401,F403

FAM = {"cure": ("#2E8B57", "#FFFFFF"), "stopped": ("#E0A526", NAVY), "never": ("#4C515A", "#FFFFFF")}
NAMES = {"cure": "Shown they can cure", "stopped": "Paid, then stopped suddenly", "never": "Never paid"}
STATES = {"cure": "stabilized · slow roller · repeat delinquent", "stopped": "seasoned and early-life straight rollers",
          "never": "early payment default"}


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
    ("Fell to 61+ fast, in the first year?", "Early-life straight roller", "fell fast, early", "stopped"),
    ("Otherwise", "Slow roller", "fell slowly, paying on the way", "cure"),
]
rows = "".join(
    f'<div style="display:flex;align-items:center;gap:14px"><div style="width:34px;height:34px;border-radius:17px;flex:none;'
    f'background:{NAVY};display:flex;align-items:center;justify-content:center"><p style="font-size:18px;font-weight:600;line-height:1;color:#FFFFFF">{i}</p></div>'
    f'<p style="font-size:22px;width:560px;line-height:1.25">{q}</p><p style="font-size:26px;color:{BLUE}">→</p>{fchip(st, tag, fam)}</div>'
    for i, (q, st, tag, fam) in enumerate(ladder, 1))
how = (f'<p style="font-size:22px;color:#4C515A">Read from the DPD history alone, so it covers every account. Asked in order; the first “yes” decides.</p>'
       f'<div style="display:flex;flex-direction:column;gap:8px">{rows}</div>')


def fam_row(key, share, states=True):
    bg, _ = FAM[key]
    if share is None:
        bar = '<div style="flex:1;height:26px;border:2px dashed #D9D9D6;border-radius:4px"></div>'
        val = "[__]"
    else:
        bar = (f'<div style="flex:1;display:flex"><div style="width:{share / 51.5 * 100:.0f}%;height:26px;background:{bg};border-radius:4px"></div></div>')
        val = f"{share:.0f}%"
    sub = f'<p style="font-size:18px;color:{GREY}">{STATES[key]}</p>' if states else ""
    return (f'<div style="display:flex;align-items:center;gap:14px">'
            f'<div style="width:16px;height:16px;border-radius:3px;background:{bg};flex:none"></div>'
            f'<div style="width:300px;display:flex;flex-direction:column"><p style="font-size:22px;font-weight:600">{NAMES[key]}</p>{sub}</div>'
            f'{bar}<p style="font-size:22px;font-weight:600;width:64px;text-align:right">{val}</p></div>')


mix = (f'<div style="display:flex;flex-direction:column;gap:12px"><p style="font-size:22px;font-weight:600">Loans 61–180</p>'
       + fam_row("cure", 42.8) + fam_row("stopped", 51.5) + fam_row("never", 5.7) + '</div>'
       + f'<div style="display:flex;flex-direction:column;gap:10px"><p style="font-size:22px;font-weight:600">Cards 61–180</p>'
       + fam_row("cure", None, False) + fam_row("stopped", None, False) + fam_row("never", None, False) + '</div>')
OUT.joinpath("a4.html").write_text(slide(
    "a4", "A1 · Deterioration", "states", 1,
    "Four in ten delinquent loans have already shown they can cure",
    how, mix,
    [("[__]%", "of loans that have shown they can cure paid within 3 months, against [__]% of the rest."),
     ("Half", "of delinquent loans paid for a while, then stopped all at once: an event, not a habit.")],
    "All figures: production, 31 August 2026, 61–180 DPD unless noted",
    "Deterioration reads only the DPD history, so it covers every account. Six questions asked in order; the first yes decides. "
    "The states fall into three families. Stabilized customers, slow rollers and repeat delinquents have already shown they can cure: they paid on the way down, stopped falling, or cured before. "
    "Straight rollers, seasoned or early in life, paid for a while and then stopped all at once, which points to an event rather than a habit: half of loans. "
    "Early payment defaults never paid at all. For loans at 61 to 180, about four in ten have shown they can cure. "
    "The back-test shows how much more often they pay. Whatever the path, the next question is whether we can talk to them."))
print("ok")
