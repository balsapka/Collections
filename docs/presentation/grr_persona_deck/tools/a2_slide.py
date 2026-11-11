"""A2 slide v2: matrix coloured by quality, 180+ positive-signal panel."""
import sys
from pathlib import Path

NAVY, BLUE, GREY = "#072447", "#2765FF", "#4C515A"
H = "font-family:'Plus Jakarta Sans', Arial, sans-serif"
STEPS = ["How they got here", "Can we talk to them", "What we can offer"]
SCORE = {"In Country": 1, "Skip": -1, "Unknown": 0, "Reachable": 1, "Non-Reachable": -1}
COLOR = {2: ("#2E8B57", "#FFFFFF"), -2: ("#C0392B", "#FFFFFF")}
NEUTRAL = ("#FFFFFF", NAVY)
CC = {("In Country", "Reachable"): 8.5, ("In Country", "Non-Reachable"): 13.5, ("In Country", "Unknown"): 1.9,
      ("Skip", "Reachable"): 6.1, ("Skip", "Non-Reachable"): 31.7, ("Skip", "Unknown"): 6.0,
      ("Unknown", "Reachable"): 6.2, ("Unknown", "Non-Reachable"): 22.2, ("Unknown", "Unknown"): 3.2}
RL = {("In Country", "Reachable"): 10.2, ("In Country", "Non-Reachable"): 14.2, ("In Country", "Unknown"): 2.7,
      ("Skip", "Reachable"): 8.0, ("Skip", "Non-Reachable"): 28.5, ("Skip", "Unknown"): 6.5,
      ("Unknown", "Reachable"): 7.7, ("Unknown", "Non-Reachable"): 14.9, ("Unknown", "Unknown"): 6.6}
LOC = ["In Country", "Skip", "Unknown"]
REACH = ["Reachable", "Non-Reachable", "Unknown"]


def steps(active):
    out = []
    for i, name in enumerate(STEPS, 1):
        on = i == active
        circ = f"background:{NAVY}" if on else "border:2px solid #D9D9D6"
        num = "#FFFFFF" if on else "#9295A0"
        out.append(f'<div style="display:flex;align-items:center;gap:10px"><div style="width:40px;height:40px;border-radius:20px;{circ};display:flex;align-items:center;justify-content:center"><p style="font-size:20px;font-weight:600;line-height:1;color:{num}">{i}</p></div><p style="font-size:20px;font-weight:{600 if on else 400};color:{NAVY if on else "#9295A0"}">{name}</p></div>')
        if i < 3:
            out.append('<div style="width:28px;height:2px;background:#D9D9D6"></div>')
    return f'<div style="display:flex;align-items:center;gap:12px">{"".join(out)}</div>'


def label(t):
    return f'<p style="font-size:20px;letter-spacing:2px;text-transform:uppercase;color:{GREY};font-weight:600">{t}</p>'


def chip(t, unknown=False):
    st = f"border:2px dashed #9295A0;color:{GREY};padding:4px 12px" if unknown else f"background:#EEF1F8;color:{NAVY};padding:6px 14px"
    return f'<p style="font-size:20px;font-weight:600;border-radius:8px;white-space:nowrap;{st}">{t}</p>'


def dim_box(title, q, line, chips):
    cs = "".join(chip(c, c == "Unknown") for c in chips)
    return (f'<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-radius:12px;padding:16px 22px;display:flex;flex-direction:column;gap:8px">'
            f'<div style="display:flex;align-items:baseline;gap:14px"><p style="font-size:26px;font-weight:600">{title}</p><p style="font-size:22px;color:{BLUE};font-weight:600">{q}</p></div>'
            f'<p style="font-size:22px;line-height:1.35;color:#4C515A">{line}</p><div style="display:flex;gap:8px">{cs}</div></div>')


def matrix():
    cell = "display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;border-radius:10px;height:104px;border:1px solid #D9D9D6"
    head = "".join(f'<p style="font-size:20px;font-weight:600;text-align:center">{r}</p>' for r in REACH)
    rows = [f'<p></p>{head}']
    for loc in LOC:
        cells = []
        for r in REACH:
            bg, fg = COLOR.get(SCORE[loc] + SCORE.get(r, 0), NEUTRAL)
            cells.append(f'<div style="{cell};background:{bg}"><p style="{H};font-size:36px;font-weight:600;color:{fg}">{CC[(loc, r)]:.1f}%</p><p style="font-size:19px;color:{fg};opacity:0.85">loans {RL[(loc, r)]:.1f}%</p></div>')
        rows.append(f'<p style="font-size:20px;font-weight:600;align-self:center">{loc}</p>{"".join(cells)}')
    grid = f'<div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:10px">{"".join(rows)}</div>'
    return (f'<div style="display:flex;flex-direction:column;gap:10px"><div style="display:flex;justify-content:space-between;align-items:baseline">'
            f'<p style="font-size:22px;font-weight:600">Location × reachability, 61–180</p><p style="font-size:20px;color:{GREY}">% of card accounts · loans below</p></div>'
            f'{grid}</div>')


def panel():
    rows = [("Reachable", "[__]", "[__]"), ("In Country", "[__]", "[__]"), ("In Country × Reachable", "[__]", "[__]")]
    trs = "".join(f'<tr><td style="padding:2px 0">{a}</td><td style="text-align:right">{b}</td><td style="text-align:right">{c}</td></tr>' for a, b, c in rows)
    return (f'<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-left:8px solid #2E8B57;border-radius:12px;padding:14px 24px;display:flex;flex-direction:column;gap:4px">'
            f'<p style="font-size:22px;font-weight:600">180+ · positive signals <b style="font-weight:400;color:{GREY};font-size:20px">· reachable counts as one</b></p>'
            f'<table style="font-size:22px;color:{NAVY};width:100%"><tr><th style="text-align:left;width:60%"></th><th style="text-align:right;color:{GREY}">Cards</th><th style="text-align:right;color:{GREY}">Loans</th></tr>{trs}</table></div>')


def insight(big, text):
    return (f'<div style="display:flex;align-items:center;gap:28px;background:#F3F3F1;border:1px solid #E6E6E3;border-radius:12px;padding:18px 32px">'
            f'<div style="flex:none;min-width:max-content"><p style="{H};font-size:56px;font-weight:600;color:{BLUE};white-space:nowrap">{big}</p></div><div style="flex:1"><p style="font-size:24px;line-height:1.35">{text}</p></div></div>')


how = (dim_box("Location", "Where were they last seen?", "Logins and in-person card use show where they are; a travel purchase or collector note signals they have left. The latest evidence wins.", ["In Country", "Skip", "Unknown"])
       + dim_box("Reachability", "Do our calls connect?", "Recent call days all failed, no contact since → Non-Reachable. A recent contact → Reachable.", ["Reachable", "Non-Reachable", "Unknown"])
       + f'<p style="font-size:22px;line-height:1.4;color:{NAVY};background:#EEF1F8;border-radius:8px;padding:12px 16px"><b>The gate:</b> only Reachable customers go on to step 3.</p>')

html = f'''<section id="a2" data-transition="fade" style="background:#FFFFFF;color:{NAVY};font-family:'Plus Jakarta Sans', Arial, sans-serif;padding:96px 128px 140px;display:flex;flex-direction:column;gap:32px">
<div style="display:flex;flex-direction:column;gap:14px">
<div style="display:flex;align-items:center;justify-content:space-between">
<div style="display:flex;align-items:center;gap:20px"><p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{BLUE};font-weight:600">A2 · Locatability</p><p style="font-size:18px;font-weight:600;letter-spacing:2px;text-transform:uppercase;padding:6px 14px;border-radius:999px;border:2px solid {BLUE};color:{BLUE}">States · decided by rules</p></div>
{steps(2)}
</div>
<h2 style="{H};font-size:50px;font-weight:600;line-height:1.1">Only one in five customers at 61–180 can be reached</h2>
</div>
<div style="display:grid;grid-template-columns:760px 1fr;gap:56px;flex:1">
<div style="display:flex;flex-direction:column;gap:14px">{label("How a customer gets a label")}{how}</div>
<div style="display:flex;flex-direction:column;gap:14px">{label("August mix")}{matrix()}</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px">{insight("1 in 3", "look abroad and do not answer, the largest group on cards and loans alike: candidates for tracing or an agency.")}{insight("[__]%", "of 180+ accounts are reachable, a positive signal for finding those still worth working.")}</div>
<aside>Locatability is the gate. Two rules: where did we last see the customer, from logins and in-person card use, with travel purchases and collector notes as signs of departure, latest evidence wins; and do our calls connect. The matrix shows how they combine. Only about one in five card customers and one in four loan customers at 61 to 180 are reachable, and only they go on to the nuance step. The largest group, about a third, look abroad and do not answer: these are candidates for tracing or an agency rather than in-house calls. At 180+ we look only for positives, and being reachable counts as one.</aside>
</section>
'''
Path(sys.argv[1]).write_text(html)
print("ok")
