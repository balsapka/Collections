"""Queued slide edits: A2 headline, ability + credibility layout, four deterioration families."""
import re, sys
D = sys.argv[1]
rd = lambda f: open(f"{D}/{f}.html").read()
def wr(f, s): open(f"{D}/{f}.html", "w").write(s)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (a[:90], s.count(a)); return s.replace(a, b)

def hdr(label, bg, fg, dashed=False):
    box = (f"border:2px dashed #9295A0;" if dashed else f"background:{bg};")
    return (f'<div style="{box}border-radius:8px;padding:8px 4px;display:flex;align-items:center;justify-content:center">'
            f'<p style="font-size:20px;font-weight:600;text-align:center;color:{fg}">{label}</p></div>')
HDRS = (hdr("High", "#2E8B57", "#FFFFFF") + hdr("Moderate", "#E0A526", "#072447")
        + hdr("Low", "#C0392B", "#FFFFFF") + hdr("Unknown", "", "#4C515A", dashed=True))
NOTE_OLD_A1 = 'font-size:22px;line-height:1.4;color:#4C515A;border-left:6px solid #D9D9D6;padding:6px 14px">'
NOTE_NEW = 'font-size:24px;line-height:1.4;color:#4C515A;border-left:6px solid #D9D9D6;padding:8px 16px">'

# ---------- A2 headline
s = rd("a2")
s = rep(s, ">Only one in five customers at 61–180 can be reached<", ">Only one in five card customers at 61–180 can be reached<")
wr("a2", s)

# ---------- ability (a1)
s = rd("a1")
s = rep(s, ">August mix · current rule<", ">August mix<")
s = rep(s, NOTE_OLD_A1, NOTE_NEW)
old_hdr = re.search(r'<div style="display:grid;grid-template-columns:170px 1fr 1fr 1fr 1fr;gap:8px"><p style="font-size:22px"></p>(.*?Unknown</p></div>)', s).group(0)
s = rep(s, old_hdr, '<div style="display:grid;grid-template-columns:160px 1fr 1fr 1fr 1fr;gap:8px"><p style="font-size:22px"></p>' + HDRS)
s = rep(s, " The August mix is from the current rule; the family rule results follow.", "")
wr("a1", s)

# ---------- credibility (a3)
s = rd("a3")
panel_old = re.search(r'<p style="font-size:20px;letter-spacing:2px;text-transform:uppercase;color:#4C515A;font-weight:600">How a customer gets a label</p><div style="display:flex;flex-direction:column;gap:14px">.*?one band down</b></p></div>', s, re.S).group(0)
chip = lambda t: f'<p style="font-size:22px;font-weight:600;border-radius:8px;white-space:nowrap;color:#072447;background:#EEF1F8;padding:8px 16px">{t}</p>'
def row(title, sub, chips):
    return (f'<div style="display:flex;align-items:center;gap:16px"><div style="width:420px"><p style="font-size:24px;font-weight:600">{title}</p>'
            f'<p style="font-size:20px;color:#4C515A">{sub}</p></div><div style="display:flex;gap:8px">{"".join(chip(c) for c in chips)}</div></div>')
band = lambda name, sub, bg, fg: (f'<div style="flex:1;background:{bg};padding:14px 18px;display:flex;flex-direction:column;gap:2px">'
                                  f'<p style="font-size:24px;font-weight:600;color:{fg}">{name}</p><p style="font-size:20px;color:{fg}">{sub}</p></div>')
panel_new = ('<p style="font-size:20px;letter-spacing:2px;text-transform:uppercase;color:#4C515A;font-weight:600">How a customer gets a label</p>'
    '<p style="font-size:22px;color:#4C515A">Three sources earn points; we add them up</p>'
    '<div style="display:flex;flex-direction:column;gap:14px">'
    + row("Promises kept", "last 12 months, on GRR's deadline", ["Kept +2", "Partly +1", "Broken −1"])
    + row("Paying while delinquent", "regular = full amount due in 2+ recent months", ["Regular +2", "Some +1"])
    + row("Record before", "clean = paid as billed before falling behind", ["Clean +1"])
    + '</div><div style="display:flex;border-radius:10px;overflow:hidden">'
    + band("High", "4+ points", "#2E8B57", "#FFFFFF") + band("Moderate", "2–3 points", "#E0A526", "#072447")
    + band("Low", "0–1 points", "#C0392B", "#FFFFFF") + '</div>'
    + f'<p style="{NOTE_NEW}An explicit refusal to pay → <b>one band down</b></p>')
s = rep(s, panel_old, panel_new)
# mix: two blocks, 61-180 and 180+
mix_old = re.search(r'<div style="display:flex;flex-direction:column;gap:12px"><p style="font-size:22px;font-weight:600">61–180 DPD</p>.*?</div></div></div>\n</div>', s, re.S).group(0)
cell = lambda v, dashed=False: ((f'<div style="border:2px dashed #D9D9D6;border-radius:8px;height:60px;display:flex;align-items:center;justify-content:center"><p style="font-size:28px;font-weight:600;color:#4C515A">{v}</p></div>') if dashed else
    (f'<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-radius:8px;height:60px;display:flex;align-items:center;justify-content:center"><p style="font-size:28px;font-weight:600">{v}</p></div>'))
lab = lambda t: f'<div style="display:flex;align-items:center"><p style="font-size:22px;font-weight:600">{t}</p></div>'
GRID = '<div style="display:grid;grid-template-columns:96px 1fr 1fr 1fr 1fr;gap:10px">'
def mrow(name, vals): return lab(name) + "".join(cell(v) for v in vals[:3]) + cell(vals[3], True)
sub = lambda t: f'<p style="font-size:22px;font-weight:600">{t}</p>'
mix_new = ('<div style="display:flex;flex-direction:column;gap:12px">' + GRID + '<p style="font-size:22px"></p>' + HDRS + '</div>'
    + sub("61–180 DPD") + GRID + mrow("Cards", ["2.5%", "19.4%", "66.5%", "11.5%"]) + mrow("Loans", ["4.9%", "27.9%", "60.6%", "6.6%"]) + '</div>'
    + sub("180+") + GRID + mrow("Cards", ["[__]%"] * 4) + mrow("Loans", ["[__]%"] * 4) + '</div>'
    + '</div></div>\n</div>')
s = rep(s, mix_old, mix_new)
s = rep(s, "of card customers made no concluded promise in 12 months: untested, not bad.",
        "of card customers made no promise to pay in the last 12 months: their credibility rests on payments alone.")
s = rep(s, "59 percent of card customers have no concluded promise yet, so their record is untested rather than bad: this is where the transcript signals will add the most.",
        "59 percent of card customers made no promise to pay in the last twelve months, so their credibility rests on payments alone: this is where the transcript signals will add the most. The mix also shows 180+.")
wr("a3", s)

# ---------- four deterioration families
G, LG, A, GR = "#2E8B57", "#8CC7A1", "#E0A526", "#4C515A"
s = rd("a4")
for st, sub_ in [("Repeat delinquent", "been here before"), ("Slow roller", "fell slowly, paying on the way")]:
    s = rep(s, f'background:#2E8B57;padding:8px 16px;display:flex;flex-direction:column"><p style="font-size:22px;font-weight:600;white-space:nowrap;color:#FFFFFF">{st}</p><p style="font-size:18px;color:#FFFFFF">{sub_}</p>',
            f'background:{LG};padding:8px 16px;display:flex;flex-direction:column"><p style="font-size:22px;font-weight:600;white-space:nowrap;color:#072447">{st}</p><p style="font-size:18px;color:#072447">{sub_}</p>')
mix_old = re.search(r'<div style="display:flex;flex-direction:column;gap:24px"><p style="font-size:20px;letter-spacing:2px;text-transform:uppercase;color:#4C515A;font-weight:600">August mix</p>.*?</div></div></div>\n</div>', s, re.S).group(0)
def frow(col, name, sub_, w, v):
    bar = (f'<div style="flex:1;display:flex"><div style="width:{w}%;height:24px;background:{col};border-radius:4px"></div></div>' if w is not None
           else '<div style="flex:1;height:24px;border:2px dashed #D9D9D6;border-radius:4px"></div>')
    sp = f'<p style="font-size:18px;color:#4C515A">{sub_}</p>' if sub_ else ""
    return (f'<div style="display:flex;align-items:center;gap:14px"><div style="width:16px;height:16px;border-radius:3px;background:{col};flex:none"></div>'
            f'<div style="width:300px;display:flex;flex-direction:column"><p style="font-size:22px;font-weight:600">{name}</p>{sp}</div>{bar}'
            f'<p style="font-size:22px;font-weight:600;width:64px;text-align:right">{v}</p></div>')
mix_new = ('<div style="display:flex;flex-direction:column;gap:20px"><p style="font-size:20px;letter-spacing:2px;text-transform:uppercase;color:#4C515A;font-weight:600">August mix</p>'
    '<div style="display:flex;flex-direction:column;gap:10px"><p style="font-size:22px;font-weight:600">Loans 61–180</p>'
    + frow(G, "Curing now", "stabilized", 17, "10%") + frow(LG, "Cured or paid before", "slow roller · repeat delinquent", 54, "33%")
    + frow(A, "Paid, then stopped suddenly", "seasoned and early-life straight rollers", 85, "51%") + frow(GR, "Never paid", "early payment default", 9, "6%")
    + '</div><div style="display:flex;flex-direction:column;gap:10px"><p style="font-size:22px;font-weight:600">Cards 61–180</p>'
    + frow(G, "Curing now", "", None, "[__]") + frow(LG, "Cured or paid before", "", None, "[__]")
    + frow(A, "Paid, then stopped suddenly", "", 100, "60%") + frow(GR, "Never paid", "", 12, "8%")
    + '</div></div>\n</div>')
s = rep(s, mix_old, mix_new)
s = rep(s, "of card accounts that can cure paid within 3 months, against 11% of the rest.",
        "of card accounts curing now or cured before paid within 3 months, against 11% of the rest.")
s = rep(s, "The states fall into three families. Stabilized customers, slow rollers and repeat delinquents have already shown they can cure: they paid on the way down, stopped falling, or cured before.",
        "The states fall into four families. Stabilized customers are curing now: they have stopped falling. Slow rollers and repeat delinquents have cured or paid before: they paid on the way down or cured once, but are falling now.")
s = rep(s, "For loans at 61 to 180, about four in ten have shown they can cure; for cards, about three in ten. They pay far more often: 33 percent of card accounts that can cure",
        "For loans at 61 to 180, about four in ten are curing now or have cured before: one in ten curing now, a third with a history; for cards, about three in ten. They pay far more often: 33 percent of card accounts in these two families")
wr("a4", s)

# ---------- idea slide (questions)
s = rd("questions")
box = lambda col, t, sub_: (f'<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-left:8px solid {col};border-radius:10px;padding:12px 18px;display:flex;flex-direction:column;gap:2px">'
                            f'<p style="font-size:24px;font-weight:600">{t}</p><p style="font-size:20px;color:#4C515A">{sub_}</p></div>')
old = ('<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-left:8px solid #2E8B57;border-radius:10px;padding:14px 18px;display:flex;flex-direction:column;gap:2px">'
       '<p style="font-size:24px;font-weight:600">Shown they can cure</p><p style="font-size:20px;color:#4C515A">stabilized · slow roller · repeat delinquent</p></div>')
s = rep(s, old, box(G, "Curing now", "stabilized") + box(LG, "Cured or paid before", "slow roller · repeat delinquent"))
s = s.replace('border-left:8px solid #E0A526;border-radius:10px;padding:14px 18px', 'border-left:8px solid #E0A526;border-radius:10px;padding:12px 18px')
s = s.replace('border-left:8px solid #4C515A;border-radius:10px;padding:14px 18px', 'border-left:8px solid #4C515A;border-radius:10px;padding:12px 18px')
wr("questions", s)
print("ok")
