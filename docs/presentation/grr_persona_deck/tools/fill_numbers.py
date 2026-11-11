"""Fill deck placeholders from fill_in.md (handoff 59)."""
import re, sys
D = sys.argv[1]

def rd(f): return open(f"{D}/{f}.html").read()
def wr(f, s): open(f"{D}/{f}.html", "w").write(s)
def rep(s, old, new, count=1):
    assert s.count(old) >= count and old in s, (old[:80], s.count(old))
    return s.replace(old, new, count)
def seq(s, vals):
    n = s.count("[__]")
    assert n == len(vals), (n, len(vals))
    for v in vals: s = s.replace("[__]", v, 1)
    return s

# ---------- exec
s = rd("exec")
s = rep(s, '<p style="font-size:26px;line-height:1.3"><b>[__]%</b> of reachable customers at 61–180 show capacity or a track record, worth <b>AED [__]m</b>.</p>',
 '<p style="font-size:26px;line-height:1.3"><b>53%</b> of reachable card customers at 61–180 are credible or able, worth <b>AED 61m</b> (loans 57%, AED 55m).</p>')
s = rep(s, 'Within 91–120 DPD, payment rates range from <b>[__]%</b> to <b>[__]%</b> across personas.',
 'Within 91–120 DPD, card payment rates range from <b>4%</b> to <b>63%</b> across personas.')
s = rep(s, '<b>[__]%</b> of 180+ accounts show at least one positive signal.',
 '<b>12%</b> of 180+ accounts, cards and loans alike, show at least one positive signal.')
s = rep(s, "and at 180+, how many accounts show any positive signal.",
 "and at 180+, how many accounts show any positive signal. The numbers: 53 percent of reachable card customers at 61 to 180 are credible or able, about 61 million dirhams of exposure, 57 percent for loans. Inside the single 91 to 120 bucket, card payment rates run from 4 percent for never-paid and unreachable customers to 63 percent for those who can cure and are credible or able. At 180+, 12 percent of accounts show at least one positive signal, on cards and loans alike.")
assert "[__]" not in s; wr("exec", s)

# ---------- a4 (deck A1 deterioration); one scale for both panels, largest = 60.4
s = rd("a4")
s = rep(s, 'width:83%;height:26px;background:#2E8B57', 'width:71%;height:26px;background:#2E8B57')
s = rep(s, 'width:100%;height:26px;background:#E0A526', 'width:85%;height:26px;background:#E0A526')
s = rep(s, '>52%</p>', '>51%</p>')
s = rep(s, 'width:11%;height:26px;background:#4C515A', 'width:9%;height:26px;background:#4C515A')
dashed = '<div style="flex:1;height:26px;border:2px dashed #D9D9D6;border-radius:4px"></div>'
for w, c in [(53, "#2E8B57"), (100, "#E0A526"), (12, "#4C515A")]:
    s = rep(s, dashed, f'<div style="flex:1;display:flex"><div style="width:{w}%;height:26px;background:{c};border-radius:4px"></div></div>')
s = seq(s, ["32%", "60%", "8%", "33", "11"])
s = rep(s, "of loans that have shown they can cure paid within 3 months, against 11% of the rest.",
 "of card accounts that have shown they can cure paid within 3 months, against 11% of the rest, and the gap holds in every bucket.")
s = rep(s, "of delinquent loans paid for a while, then stopped all at once: an event, not a habit.",
 "of delinquent loans, and six in ten card accounts, paid for a while, then stopped all at once: an event, not a habit.")
s = rep(s, "For loans at 61 to 180, about four in ten have shown they can cure. The back-test shows how much more often they pay.",
 "For loans at 61 to 180, about four in ten have shown they can cure; for cards, about three in ten. They pay far more often: 33 percent of card accounts that can cure paid within three months against 11 percent of the rest, and the gap holds inside every bucket, for example 35 against 12 percent at 91 to 120.")
wr("a4", s)

# ---------- a2: refresh matrix to the new run, 180+ reachable
s = rd("a2")
def cell(old_c, old_l, new_c, new_l, s):
    pat = f'>{old_c}</p><p style="font-size:19px;color:#([0-9A-F]+);opacity:0.85">loans {old_l}</p>'
    m = re.findall(pat, s); assert len(m) == 1, (old_c, old_l, m)
    return re.sub(pat, lambda mm: f'>{new_c}</p><p style="font-size:19px;color:#{mm.group(1)};opacity:0.85">loans {new_l}</p>', s)
for a in [("13.5%","14.2%","13.6%","14.2%"),("6.1%","8.0%","6.2%","8.1%"),("6.0%","6.5%","6.1%","6.8%"),
          ("6.2%","7.7%","6.3%","7.9%"),("22.2%","14.9%","22.3%","14.9%"),("3.2%","6.6%","3.4%","6.8%")]:
    s = cell(*a, s)
s = seq(s, ["3.7"])
s = rep(s, "of 180+ accounts are reachable, a positive signal for finding those still worth working.",
 "of 180+ card accounts are reachable (loans 4.8%), a positive signal for finding those still worth working.")
s = rep(s, "At 180+ we look only for positives, and being reachable counts as one.",
 "At 180+ we look only for positives, and being reachable counts as one: 3.7 percent of card accounts and 4.8 percent of loans.")
wr("a2", s)

# ---------- a3: add Unknown column, fill
s = rd("a3")
s = rep(s, 'grid-template-columns:150px 1fr 1fr 1fr;gap:10px', 'grid-template-columns:110px 1fr 1fr 1fr 1fr;gap:10px')
low_hdr = '<div style="background:#C0392B;border-radius:8px;padding:10px 0;display:flex;justify-content:center"><p style="font-size:22px;font-weight:600;color:#FFFFFF">Low</p></div>'
s = rep(s, low_hdr, low_hdr + '<div style="border:2px dashed #9295A0;border-radius:8px;padding:8px 0;display:flex;justify-content:center"><p style="font-size:22px;font-weight:600;color:#4C515A">Unknown</p></div>')
box = '<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-radius:8px;height:72px;display:flex;align-items:center;justify-content:center"><p style="font-size:30px;font-weight:600">[__]%</p></div>'
ubox = '<div style="border:2px dashed #D9D9D6;border-radius:8px;height:72px;display:flex;align-items:center;justify-content:center"><p style="font-size:30px;font-weight:600;color:#4C515A">[__]%</p></div>'
s = rep(s, box*3 + '<div style="display:flex;align-items:center"><p style="font-size:22px;font-weight:600">Loans</p></div>',
        box*3 + ubox + '<div style="display:flex;align-items:center"><p style="font-size:22px;font-weight:600">Loans</p></div>')
s = rep(s, box*3 + '</div>', box*3 + ubox + '</div>')
s = rep(s, '<p style="font-size:20px;color:#4C515A">From the updated credibility run</p>', '')
s = seq(s, ["2.5","19.4","66.5","11.5","4.9","27.9","60.6","6.6","42","90","59"])
s = rep(s, "how often High and Low credibility customers roll further.",
 "how often High and Low credibility customers roll further: 42 percent against 90 percent for cards.")
s = rep(s, "Many customers have no concluded promise yet,", "59 percent of card customers have no concluded promise yet,")
wr("a3", s)

# ---------- a1 (deck A4 ability), current rule
s = rd("a1")
s = rep(s, ">August mix<", ">August mix · current rule<")
s = seq(s, ["0.2","14.4","28.9","56.6","0.3","8.9","44.7","46.1","0.0","6.2","6.4","87.4","0.0","3.5","6.9","89.5","57","6"])
s = rep(s, "of loan accounts at 180+ show the means to pay: a positive signal.",
 "of card accounts at 180+ show the means to pay: a positive signal.")
s = rep(s, "At 180+, Moderate or High ability counts as a positive signal.",
 "The August mix is from the current rule; the family rule results follow. 57 percent of card customers at 61 to 180 show no evidence of their money yet. At 180+, Moderate or High ability counts as a positive signal: 6 percent of card accounts.")
wr("a1", s)

# ---------- p2-combos
s = rd("p2-combos")
s = rep(s, "A few combinations hold most of the book", "57 of 432 combinations hold 80% of the card book")
s = rep(s, "of about 400 possible combinations cover 80% of card accounts at 61–180",
        "of 432 possible combinations cover 80% of card accounts at 61–180")
s = rep(s, "combinations are empty or almost empty (under 0.5% of accounts)",
        "of 432 are empty, and 242 more hold under 0.5% of accounts each")
s = rep(s, "Largest combinations · cards 61–180", "Largest combinations · cards 61–180 · NR = Non-Reachable")
hdr_old = re.search(r'<tr><th style="width:6%.*?</tr>', s).group(0)
hdr = ('<tr><th style="width:22%;text-align:left">Deterioration</th><th style="width:25%;text-align:left">Locatability</th>'
       '<th style="width:13%;text-align:left">Credibility</th><th style="width:13%;text-align:left">Ability</th>'
       '<th style="width:11%;text-align:right">Share</th><th style="width:16%;text-align:right">Paid in 3 m</th></tr>')
s = rep(s, hdr_old, hdr)
s = re.sub(r"<tr><td>\d</td>", "<tr>", s)
rows = [("Stopped suddenly","Skip · NR","Low","Unknown","13.8","3.5"),
        ("Stopped suddenly","Unknown · NR","Low","Unknown","6.1","5.5"),
        ("Stopped suddenly","Skip · NR","Low","Low","5.1","6.6"),
        ("Never paid","Unknown · NR","Unknown","Unknown","2.8","0.4"),
        ("Can cure","Skip · NR","Low","Unknown","2.5","7.7"),
        ("Stopped suddenly","In Country · NR","Low","Unknown","2.4","10.4"),
        ("Stopped suddenly","Skip · Unknown","Low","Unknown","2.4","4.5"),
        ("Stopped suddenly","In Country · NR","Low","Low","2.4","18.2")]
s = seq(s, ["57", "135"] + [v for r in rows for v in r])
s = rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0),
 "<aside>Four axes allow 432 combinations: three deterioration families, nine location and reachability cells, four credibility bands and four ability bands. In practice 297 occur on cards at 61 to 180, and just 57 of them cover 80 percent of accounts; 135 never occur and 242 more hold under half a percent each. The largest combinations tell the story of the book: almost all are customers we cannot reach, with low credibility and little visible ability, and they pay rarely, between 0.4 and 18 percent in the following three months. That is why the decision path starts with the gate.</aside>")
wr("p2-combos", s)

# ---------- p2-tree
s = rd("p2-tree")
s = seq(s, ["32","7.5","58","3.1","35","21.2","21",
            "60","3.5","34","6.1","23","50.8","8",
            "8","0.1","–","0.5","12","6.8","3"])
s = rep(s, ">–%<", ">–<")
s = rep(s, "paid = any payment of AED 100+ in the next 3 months", "paid = any payment of AED 100+ in the next 3 months (back-test) · – = too few accounts")
s = rep(s, "This keeps deterioration in the picture and lets the segments come from the data.",
 "Reading it: among customers who have shown they can cure, are reachable and are credible or able, 58 percent paid; among those who stopped suddenly and cannot be reached, 8 percent. Reachability splits every family: within can-cure, 21 percent paid when we cannot reach them. Half of the card book is stopped suddenly and not reachable. This keeps deterioration in the picture and lets the segments come from the data.")
wr("p2-tree", s)

# ---------- p2-action (cards 61-180)
s = rd("p2-action")
vals = [("6.3","36","61"),("1.5","7","28"),("1.1","6","40"),("72.2","373","13"),("7.5","60","5")]
for sh, aed, pd in vals:
    s = rep(s, '<p style="font-size:24px;font-weight:600">[__]% of accounts · AED [__]m</p>',
            f'<p style="font-size:24px;font-weight:600">{sh}% of cards · AED {aed}m</p><p style="font-size:24px;color:#4C515A">{pd}% paid in 3 months</p>')
s = rep(s, '<p style="font-size:24px;font-weight:600">[__]% of accounts · AED [__]m</p>',
        '<p style="font-size:24px;font-weight:600">12% of 180+ accounts</p><p style="font-size:24px;color:#4C515A">38.8k cards · 6.8k loans</p>')
s = rep(s, "Hypotheses for the GRR workshop, to be tested in the pilot",
        "Hypotheses for the GRR workshop, to be tested in the pilot · cards 61–180 unless noted; 11% mixed cases not shown")
s = rep(s, "At 180+, customers with a positive signal are lifted out of the pool for an in-house attempt.",
 "At 180+, customers with a positive signal, 12 percent of accounts, are lifted out of the pool for an in-house attempt. Shares, exposure and paid rates are for cards at 61 to 180; the loan paid measure is still being checked.")
assert "[__]" not in s; wr("p2-action", s)

# ---------- p2-score
s = rd("p2-score")
s = rep(s, "Is a risk score still needed?", "A risk score still has room, inside every segment")
s = rep(s, "For each segment we measure how far 3-month outcomes still spread across customers, and whether a score would rank them better than the DPD band alone.",
 "For each segment we measure how far 3-month payment rates still differ across DPD bands, and how well the band alone ranks customers.")
tbl_old = re.search(r"<table.*?</table>", s, re.S).group(0)
R = [("Can cure · Reachable · Credible","6.3%","18.8","0.56","Yes"),
     ("Stopped suddenly · Reachable","1.5%","11.3","0.55","Yes"),
     ("Reachable · Not credible","1.1%","25.1","0.60","Yes"),
     ("Not reachable","72.2%","18.1","0.68","Yes"),
     ("Never paid","7.5%","8.7","0.73","Yes"),
     ("180+ pool","all 180+","–","–","Not testable")]
th = lambda w, a, t: f'<th style="width:{w}%;text-align:{a}">{t}</th>'
tbl = ('<table style="font-size:24px;color:#072447"><tr>' + th(40,"left","Segment") + th(15,"right","Size") +
       th(17,"right","Paid spread") + th(11,"right","AUC") + th(17,"right","Room?") + "</tr>")
for seg, sz, sp, auc, v in R:
    col = "#2E8B57" if v == "Yes" else "#4C515A"
    tbl += (f'<tr><td>{seg}</td><td style="text-align:right">{sz}</td><td style="text-align:right">{sp if sp=="–" else sp+" pts"}</td>'
            f'<td style="text-align:right">{auc}</td><td style="text-align:right"><span style="color:{col}">{v}</span></td></tr>')
tbl += "</table>"
s = rep(s, tbl_old, tbl + '<p style="font-size:22px;line-height:1.4;color:#4C515A">Cards 61–180, back-test. Paid spread = gap in 3-month paid rate between DPD bands; AUC = how well the band alone ranks. Room = spread ≥ 15 pts or AUC ≥ 0.65. At 180+ every account sits in one band.</p>')
s = rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0),
 "<aside>The original risk model predicted cure and roll well but gave no segmentation. Now that the segments exist, the question is narrower: inside each segment, do outcomes still vary enough that ranking customers would change what we do? The answer is yes in every segment at 61 to 180. Payment rates still differ by 9 to 25 points between DPD bands inside a segment, so the segments do not remove the need to rank. The largest prize is the not-reachable group, 72 percent of cards. At 180+ the test cannot be read yet, because every account sits in the same band; there a score would rank the whole pool, which is where it is most likely to add value.</aside>")
assert "[__]" not in s; wr("p2-score", s)

# ---------- p2-uc1
s = rd("p2-uc1")
s = seq(s, ["41"])
s = rep(s, "of accounts at 61–180 had a conversation in the last 3 months: where UC1 can add evidence",
        "of card accounts at 61–180 (52% of loans) had a conversation in the last 3 months: where UC1 can add evidence")
s = rep(s, "which is exactly the reachable population that passes the gate.",
        "which is exactly the reachable population that passes the gate: 41 percent of card accounts and 52 percent of loans at 61 to 180 had a right-party contact in the last three months, against 4 to 6 percent at 180+.")
wr("p2-uc1", s)

# ---------- p2-pilot
s = rd("p2-pilot")
s = rep(s, '<p style="font-size:24px;line-height:1.35">3 months</p>',
        '<p style="font-size:24px;line-height:1.35">3 months; small segments pooled across months</p>')
s = rep(s, "Minimum sample per arm: [__]", "Sample per arm: 800–1,500 accounts for a 5-pt lift")
s = rep(s, "The same policy limits apply to both arms, with a monthly readout and a stop rule.",
 "The same policy limits apply to both arms, with a monthly readout and a stop rule. To detect a 5 point lift we need about 800 to 1,500 accounts per arm. On cards only the never-paid and not-reachable segments fill both arms in one month; the reachable segments need two to three months pooled, or a larger target lift such as 10 points, which needs about a quarter of the sample.")
assert "[__]" not in s; wr("p2-pilot", s)
print("ok")
