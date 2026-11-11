import re, sys
D = sys.argv[1]
rd = lambda f: open(f"{D}/{f}.html").read()
def wr(f, s): open(f"{D}/{f}.html", "w").write(s)
def rep(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a)); return s.replace(a, b)

# ---------- summary
s = rd("exec")
s = rep(s, "<b>53%</b> of reachable card customers at 61–180 are credible or able, worth <b>AED 61m</b> (loans 57%, AED 55m).",
        "<b>53%</b> of reachable card customers at 61–180 are credible or able, holding <b>AED 40m</b> outstanding principal (loans 57%, AED 55m).")
s = rep(s, "Within 91–120 DPD, card payment rates range from <b>4%</b> to <b>63%</b> across personas.",
        "Within 91–120 DPD, the share of card customers making a meaningful payment ranges from <b>4%</b> to <b>73%</b> across personas.")
s = rep(s, "<b>12%</b> of 180+ accounts, cards and loans alike, show at least one positive signal.",
        "<b>12%</b> of 180+ accounts show a positive signal; about one in five of them pays, against under 3% of the rest.")
s = rep(s, "Decide where a risk score is still needed · combine with UC1 in a joint workshop · design and run the pilot · the bureau salary feed.",
        "Agree in-house, agency and early-exit tiers · combine with UC1 · design and run the pilot · the bureau salary feed.")
s = rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0),
 "<aside>Three messages. One: beyond 60 DPD there is no model, allocation follows the bucket, and the late buckets are where data runs dry. Two: we built synthesized features, signals from every data domain turned into persona states that answer three questions in order. Three: what it shows. 53 percent of reachable card customers at 61 to 180 are credible or able, holding about 40 million dirhams of outstanding principal; 57 percent for loans. Inside the single 91 to 120 bucket, the share of card customers making a meaningful payment, the risk score's target, runs from 4 percent to 73 percent depending on the persona. At 180+, 12 percent of accounts show a positive signal, and about one in five of them pays within the window, against under 3 percent of the rest. Next: agree with GRR which customers to work in-house, which to send to an agency and which to consider for early exit; combine the framework with the transcript work; design and run the pilot; and the bureau salary feed.</aside>")
wr("exec", s)

# ---------- A1 deterioration
s = rd("a4")
s = rep(s, ">Four in ten delinquent loans have already shown they can cure<", ">Customers curing now pay far more often than any other group<")
dashed = '<div style="flex:1;height:24px;border:2px dashed #D9D9D6;border-radius:4px"></div><p style="font-size:22px;font-weight:600;width:64px;text-align:right">[__]</p>'
s = s.replace(dashed, '<div style="flex:1;display:flex"><div style="width:11%;height:24px;background:#2E8B57;border-radius:4px"></div></div><p style="font-size:22px;font-weight:600;width:64px;text-align:right">7%</p>', 1)
s = rep(s, dashed, '<div style="flex:1;display:flex"><div style="width:42%;height:24px;background:#8CC7A1;border-radius:4px"></div></div><p style="font-size:22px;font-weight:600;width:64px;text-align:right">25%</p>')
s = rep(s, ">33%</p></div><div style=\"flex:1\"><p style=\"font-size:25px;line-height:1.35\">of card accounts with cure behaviour paid within 3 months, against 11% of the rest.",
        ">60%</p></div><div style=\"flex:1\"><p style=\"font-size:25px;line-height:1.35\">of card accounts curing now paid within 3 months, against 22% of those who cured before.")
s = rep(s, ">All figures: production, 31 August 2026, 61–180 DPD unless noted<",
        ">Production, 31 August 2026, 61–180 DPD · paid: meaningful payment within 3 months, back-test<")
s = rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0),
 "<aside>Deterioration reads only the DPD history, so it covers every account. Six questions asked in order; the first yes decides. The states fall into four families. Stabilized customers are curing now: they have stopped falling. Slow rollers and repeat delinquents have cured or paid before, but are falling now. Straight rollers, seasoned or early in life, paid for a while and then stopped all at once, which points to an event rather than a habit: half of loans and six in ten card accounts. Early payment defaults never paid at all. The split matters: 60 percent of card accounts curing now made a meaningful payment within three months, against 22 percent of those who cured before, and the gap is 26 to 49 points in every bucket; for loans 74 against 38 percent. Whatever the path, the next question is whether we can talk to them.</aside>")
wr("a4", s)

# ---------- A3: drop Unknown, fill
s = rd("a3")
s = rep(s, '<div style="display:grid;grid-template-columns:160px 1fr 1fr 1fr 1fr;gap:8px">', '<div style="display:grid;grid-template-columns:160px 1fr 1fr 1fr;gap:8px">')
s = rep(s, '<div style="border:2px dashed #9295A0;border-radius:8px;padding:8px 4px;display:flex;align-items:center;justify-content:center"><p style="font-size:20px;font-weight:600;text-align:center;color:#4C515A">Unknown</p></div>', "")
s = re.sub(r'<div style="border:2px dashed #D9D9D6;border-radius:8px;height:56px;display:flex;align-items:center;justify-content:center"><p style="font-size:26px;font-weight:600;color:#4C515A">[^<]*</p></div>', "", s)
vals = {"Cards 61–180": ["2.5%", "19.4%", "78.0%"], "Loans 61–180": ["4.9%", "27.9%", "67.2%"],
        "Cards 180+": ["0.1%", "2.7%", "97.2%"], "Loans 180+": ["0.3%", "4.3%", "95.4%"]}
cell = lambda v: f'<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-radius:8px;height:56px;display:flex;align-items:center;justify-content:center"><p style="font-size:26px;font-weight:600">{v}</p></div>'
for lab, v in vals.items():
    m = re.search(r'(<p style="font-size:22px;font-weight:600">' + re.escape(lab) + r'</p></div>)((?:<div style="background:#F3F3F1;[^>]*><p[^>]*>[^<]*</p></div>){3})', s)
    assert m, lab
    s = s.replace(m.group(0), m.group(1) + "".join(cell(x) for x in v))
s = rep(s, "42 percent against 90 percent for cards.", "42 percent against 90 percent for cards. At 180+ almost everyone is Low: 97 percent of cards and 95 percent of loans.")
wr("a3", s)

# ---------- tree, four families
s = rd("p2-tree")
s = rep(s, ">The book, along the decision path<", ">Family and reachability split payment rates from 3% to 68%<")
grid_old = re.search(r'<div style="display:grid;grid-template-columns:400px 280px 1fr 140px 180px;gap:8px 14px">.*?</div></div>\n', s, re.S).group(0)
H = 46
def hdr(t, al="left"): return f'<p style="font-size:22px;font-weight:600;color:#4C515A;text-align:{al}">{t}</p>'
def fam(name, share, col, span): return (f'<div style="grid-row:span {span};background:#F3F3F1;border-left:8px solid {col};border-radius:10px;padding:0 18px;display:flex;align-items:center">'
                                        f'<p style="font-size:24px;font-weight:600">{name} <span style="color:#4C515A">· {share}</span></p></div>')
reach = lambda span: f'<div style="grid-row:span {span};background:#EEF1F8;border-radius:10px;padding:0 18px;display:flex;align-items:center"><p style="font-size:24px;font-weight:600">Reachable</p></div>'
leaf = lambda t: f'<div style="height:{H}px;border:1px solid #E6E6E3;border-radius:10px;padding:0 18px;display:flex;align-items:center"><p style="font-size:22px">{t}</p></div>'
num = lambda v: f'<div style="height:{H}px;display:flex;align-items:center;justify-content:end"><p style="font-size:24px;font-weight:600">{v}</p></div>'
nr = (f'<div style="height:{H}px;background:#F3F3F1;border-radius:10px;padding:0 18px;display:flex;align-items:center"><p style="font-size:24px;font-weight:600">Not reachable</p></div>'
      f'<div style="height:{H}px;padding:0 18px;display:flex;align-items:center"><p style="font-size:22px;color:#4C515A">agency or early exit</p></div>')
def block(name, share, col, cred, neither, notr):
    return (fam(name, share, col, 3) + reach(2) + leaf("Credible or able") + num(cred[0]) + num(cred[1])
            + leaf("Neither") + num(neither[0]) + num(neither[1]) + nr + num(notr[0]) + num(notr[1]))
g = ('<div style="display:grid;grid-template-columns:420px 260px 1fr 140px 180px;gap:6px 14px">'
     + hdr("1 · How they got here") + hdr("2 · Can we talk to them") + hdr("3 · The nuance") + hdr("Share", "right") + hdr("Paid in 3 m", "right")
     + block("Curing now", "7%", "#2E8B57", ("4.1%", "68%"), ("0.4%", "52%"), ("2.1%", "44%"))
     + block("Cured or paid before", "25%", "#8CC7A1", ("3.4%", "40%"), ("2.7%", "30%"), ("19.0%", "16%"))
     + block("Paid, then stopped suddenly", "60%", "#E0A526", ("3.5%", "34%"), ("6.1%", "22%"), ("50.8%", "8%"))
     + fam("Never paid", "8%", "#4C515A", 2)
     + f'<div style="height:{H}px;background:#EEF1F8;border-radius:10px;padding:0 18px;display:flex;align-items:center"><p style="font-size:24px;font-weight:600">Reachable</p></div>'
     + leaf("Any") + num("0.6%") + num("14%")
     + nr + num("6.8%") + num("3%")
     + '</div>\n')
s = rep(s, grid_old, g)
s = rep(s, "paid = any payment in the next 3 months (back-test) · – = too few accounts", "paid = meaningful payment within 3 months (back-test)")
s = rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0),
 "<aside>The same book, split in the order a case meets the framework: first how they got here, then whether we can talk to them, then, for the reachable, whether they show credibility or the means to pay. Each end point shows its share of card accounts and how often it made a meaningful payment in the following three months. Customers curing now pay most whatever else is true: 68 percent when reachable and credible or able, still 44 percent when we cannot reach them. At the other end, those who stopped suddenly and cannot be reached are half the card book and pay 8 percent; never-paid customers we cannot reach pay 3 percent. Reachability splits every family. These end points are the building blocks for the allocation tiers on the next slide.</aside>")
wr("p2-tree", s)
print("ok")
