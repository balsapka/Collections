"""Part 2 rebuilt around the allocation tiers (policy terms), cards 61-180."""
import re, sys
D = sys.argv[1]
rd = lambda f: open(f"{D}/{f}.html").read()
def wr(f, s): open(f"{D}/{f}.html", "w").write(s)
def rep(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a)); return s.replace(a, b)
FONT = "'Plus Jakarta Sans', Arial, sans-serif"
NAVY, BLUE, GREY, MUTED, CARD, LINE = "#072447", "#2765FF", "#4C515A", "#9295A0", "#F3F3F1", "#E6E6E3"
EYEBROW = "Allocation"

def section(sid, headline, body, footer="", notes="", pad="112px 128px 150px", gap=32):
    foot = (f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:22px;color:{GREY}">{footer}</p>' if footer else "")
    return (f'<section id="{sid}" data-transition="fade" style="background:#FFFFFF;color:{NAVY};font-family:{FONT};padding:{pad};display:flex;flex-direction:column;gap:{gap}px">\n'
            f'<div style="display:flex;flex-direction:column;gap:14px"><p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{BLUE};font-weight:600">{EYEBROW}</p>'
            f'<h2 style="font-family:{FONT};font-size:52px;font-weight:600;line-height:1.1">{headline}</h2></div>\n{body}\n{foot}\n<aside>{notes}</aside>\n</section>\n')

def pill(tier):
    if tier == "in":
        return f'<p style="font-size:20px;font-weight:600;white-space:nowrap;background:{NAVY};color:#FFFFFF;border-radius:999px;padding:5px 14px">In-house</p>'
    if tier == "ag":
        return f'<p style="font-size:20px;font-weight:600;white-space:nowrap;background:#EEF1F8;color:{NAVY};border-radius:999px;padding:5px 14px">Agency</p>'
    return f'<p style="font-size:20px;font-weight:600;white-space:nowrap;border:2px dashed {MUTED};color:{GREY};border-radius:999px;padding:3px 12px">Non-workable</p>'

# ---------------- divider
s = rd("div-combined")
s = rep(s, ">The axes together<", ">From persona states to allocation<")
s = rep(s, ">Which combinations fire · Risk score · UC1 · Pilot<", ">In-house, agency or the non-workable pool · Risk score · UC1 · Pilot<")
s = rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0),
        "<aside>Part 2 puts the four axes together to answer the allocation question at 61 to 180: which customers to work in-house, which to place with agencies, and which belong in the policy's non-workable pool. Then whether a risk score is still needed, where the transcript work fits, and how we pilot it.</aside>")
s = s.replace('font-size:96px', 'font-size:88px')
wr("div-combined", s)

# ---------------- tree with tier tags
s = rd("p2-tree")
s = s.replace(f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{BLUE};font-weight:600">The axes together</p>',
              f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{BLUE};font-weight:600">{EYEBROW}</p>')
s = rep(s, "grid-template-columns:420px 260px 1fr 140px 180px;gap:6px 14px", "grid-template-columns:400px 240px 1fr 130px 160px 190px;gap:6px 14px")
s = rep(s, f'<p style="font-size:22px;font-weight:600;color:{GREY};text-align:right">Paid in 3 m</p>',
        f'<p style="font-size:22px;font-weight:600;color:{GREY};text-align:right">Paid in 3 m</p><p style="font-size:22px;font-weight:600;color:{GREY};text-align:left">Tier</p>')
s = s.replace(f'<div style="height:46px;padding:0 18px;display:flex;align-items:center"><p style="font-size:22px;color:{GREY}">agency or early exit</p></div>',
              '<div style="height:46px"></div>')
# append a tier cell after each paid cell (pattern: share num + paid num). Order of leaves in file:
tiers = ["in", "in", "ag",   # curing now: cred, neither, NR
         "in", "ag", "ag",   # cured before
         "in", "ag", "ag",   # stopped suddenly
         "ag", "nw"]         # never paid: reachable any, NR
num_re = re.compile(r'(<div style="height:46px;display:flex;align-items:center;justify-content:end"><p style="font-size:24px;font-weight:600">[^<]*</p></div>)(<div style="height:46px;display:flex;align-items:center;justify-content:end"><p style="font-size:24px;font-weight:600">[^<]*</p></div>)')
it = iter(tiers)
s, n = num_re.subn(lambda m: m.group(1) + m.group(2) + f'<div style="height:46px;display:flex;align-items:center">{pill(next(it))}</div>', s)
assert n == 11, n
s = rep(s, ">Family and reachability split payment rates from 3% to 68%<", ">Family and reachability split payment rates from 3% to 68%<")
s = rep(s, "Cards 61–180 · share of accounts; paid = meaningful payment within 3 months (back-test)",
        "Cards 61–180 · paid = meaningful payment within 3 months (back-test) · tier of each branch's average; accounts are tiered by their full combination")
s = rep(s, "These end points are the building blocks for the allocation tiers on the next slide.",
        "Each branch carries the tier of its average: in-house where payments are likely and worth our collectors' time, agency for the large unreachable middle, and the non-workable pool for never-paid customers we cannot reach. The next slide tiers every account by its full combination.")
wr("p2-tree", s)

# ---------------- tier slide (replaces combos)
pts = [(0, 0), (10, 35.3), (20, 55.2), (30, 68.2), (50, 85.6), (80, 97.2), (100, 100)]
W, H, L, T = 560, 400, 70, 20
X = lambda v: L + v / 100 * W
Y = lambda v: T + H - v / 100 * H
poly = " ".join(f"{X(a):.0f},{Y(b):.0f}" for a, b in pts)
svg = (f'<svg aria-label="Capture curve: share of money collected by share of card accounts ranked by expected collections" viewBox="0 0 {L+W+30} {T+H+70}" style="width:660px;height:490px">'
       f'<line x1="{L}" y1="{T+H}" x2="{L+W}" y2="{T+H}" stroke="{MUTED}" stroke-width="2"/>'
       f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+H}" stroke="{MUTED}" stroke-width="2"/>'
       f'<line x1="{L}" y1="{T+H}" x2="{L+W}" y2="{T}" stroke="#D9D9D6" stroke-width="2" stroke-dasharray="8 8"/>'
       f'<polyline points="{poly}" fill="none" stroke="{BLUE}" stroke-width="5"/>'
       f'<line x1="{X(20):.0f}" y1="{T+H}" x2="{X(20):.0f}" y2="{Y(55.2):.0f}" stroke="{NAVY}" stroke-width="2" stroke-dasharray="4 6"/>'
       f'<line x1="{L}" y1="{Y(55.2):.0f}" x2="{X(20):.0f}" y2="{Y(55.2):.0f}" stroke="{NAVY}" stroke-width="2" stroke-dasharray="4 6"/>'
       f'<circle cx="{X(20):.0f}" cy="{Y(55.2):.0f}" r="9" fill="{NAVY}"/>'
       f'<text x="{X(20)+18:.0f}" y="{Y(55.2)+8:.0f}" font-size="26" font-weight="600" fill="{NAVY}" font-family="Plus Jakarta Sans, Arial">top 20% → 55% of money</text>'
       + "".join(f'<text x="{X(v):.0f}" y="{T+H+34}" font-size="22" fill="{GREY}" text-anchor="middle" font-family="Plus Jakarta Sans, Arial">{v}%</text>' for v in (0, 20, 50, 80, 100))
       + "".join(f'<text x="{L-12}" y="{Y(v)+8:.0f}" font-size="22" fill="{GREY}" text-anchor="end" font-family="Plus Jakarta Sans, Arial">{v}%</text>' for v in (0, 50, 100))
       + f'<text x="{L+W/2:.0f}" y="{T+H+66}" font-size="22" fill="{GREY}" text-anchor="middle" font-family="Plus Jakarta Sans, Arial">card accounts, ranked by expected collections</text>'
       + '</svg>')
th = lambda t, a="right", w="": f'<th style="{w}text-align:{a}">{t}</th>'
rows = [("in", "In-house", "11%", "44%", "9.75%", "11.7"), ("ag", "Agency", "54%", "46%", "2.6%", "11.8"), ("nw", "Non-workable pool", "32%", "4.6%", "0.47%", "10.9")]
table = (f'<table style="font-size:24px;color:{NAVY}"><tr>' + th("Tier", "left", "width:34%;") + th("Accounts", w="width:15%;") + th("Money collected", w="width:19%;")
         + th("Recovery, 3 m", w="width:17%;") + th("Call days", w="width:15%;") + "</tr>"
         + "".join(f'<tr><td><div style="display:flex">{pill(k)}</div></td><td style="text-align:right">{a}</td><td style="text-align:right">{m}</td><td style="text-align:right">{r}</td><td style="text-align:right">{c}</td></tr>' for k, _, a, m, r, c in rows)
         + "</table>")
who = (f'<div style="display:flex;flex-direction:column;gap:10px">'
       f'<p style="font-size:24px;line-height:1.35"><b>In-house:</b> mostly curing now or cured before, with a credible or able customer.</p>'
       f'<p style="font-size:24px;line-height:1.35"><b>Non-workable:</b> stopped suddenly (79%) or never paid (20%), and not reachable.</p></div>')
callout = (f'<div style="display:flex;align-items:center;gap:24px;background:{CARD};border:1px solid {LINE};border-radius:12px;padding:20px 28px">'
           f'<div style="flex:none;min-width:max-content"><p style="font-family:{FONT};font-size:56px;font-weight:600;color:{BLUE};white-space:nowrap">10.9</p></div>'
           f'<div style="flex:1"><p style="font-size:24px;line-height:1.35">call days per account in 3 months still go to the non-workable pool, almost as many as in-house.</p></div></div>')
body = (f'<div style="display:grid;grid-template-columns:660px 1fr;gap:56px;flex:1">'
        f'<div style="display:flex;flex-direction:column;gap:8px"><p style="font-size:22px;font-weight:600;color:{GREY}">Share of money collected</p>{svg}</div>'
        f'<div style="display:flex;flex-direction:column;gap:22px">{table}{who}{callout}</div></div>')
wr("p2-combos", section("p2-combos", "The framework defines the policy's non-workable pool: a third of card accounts, under 5% of the money", body,
    footer="Cards 61–180 · ranked by expected collections (amount collected per account in 3 months, back-test, in-sample) · cut-offs AED 1,250 / 175 · 3% unassigned · loans: recovery 7.9% / 2.9% / 0.7%",
    notes="The policy already refers a non-workable pool, the non-contactable and least probable to pay, to external agencies, but it does not define it. The framework does. We rank every combination of the four axes by expected collections: what its accounts paid, in dirhams, in the three months after the back-test month. The top fifth of card accounts bring in 55 percent of the money collected while holding only 19 percent of the outstanding principal. Cut into three tiers: in-house, 11 percent of accounts, 44 percent of the money, recovering almost 10 percent of principal in three months; agency, 54 percent of accounts and 46 percent of the money; and the non-workable pool, a third of accounts, under 5 percent of the money, recovering half a percent, yet still taking nearly 11 call days per account. The cut-offs are hypotheses from the data: GRR has the commission rate card and the in-house cost that would set them properly. Loans show the same pattern."))

# ---------------- hypotheses per tier (p2-action)
def tcard(k, who_, hyp, policy, nums):
    return (f'<div style="background:{CARD};border-radius:14px;padding:26px 28px;display:flex;flex-direction:column;gap:12px">'
            f'<div style="display:flex">{pill(k)}</div>'
            f'<p style="font-size:22px;color:{GREY};line-height:1.35">{who_}</p>'
            f'<h3 style="font-family:{FONT};font-size:30px;font-weight:600;line-height:1.25">{hyp}</h3>'
            f'<p style="font-size:22px;line-height:1.35;color:{GREY}">{policy}</p><div style="flex:1"></div>'
            f'<p style="font-size:24px;font-weight:600">{nums[0]}</p><p style="font-size:24px;color:{GREY}">{nums[1]}</p></div>')
cards = (tcard("in", "Curing now or cured before, reachable, credible or able", "Convert through skilled collectors: settlement, restructure or deferral",
               "Policy tools: CARES settlements, loan restructure, deferral", ("11% of cards · AED 40m", "50% paid in 3 months"))
         + tcard("ag", "Stopped suddenly or cured before, not reachable", "Place with agencies at 61–180, skip tracing where they look abroad",
                 "Policy: referral by product, DPD stage, contactability and strategy", ("54% of cards · AED 213m", "17% paid in 3 months"))
         + tcard("nw", "Stopped suddenly or never paid, not reachable, no sign of credibility or ability", "Free collector time: refer to agencies or stop calling",
                 "Policy: non-workable pool to agencies (HOD approval), or no calling with dunning as for Dead Beat accounts", ("32% of cards · AED 138m", "4% paid in 3 months")))
bar = (f'<div style="display:flex;align-items:center;gap:28px;background:{NAVY};border-radius:14px;padding:22px 32px">'
       f'<p style="font-size:22px;letter-spacing:2px;text-transform:uppercase;color:#8FAFFF;font-weight:600;white-space:nowrap">180+</p>'
       f'<p style="font-size:26px;line-height:1.4;color:#FFFFFF">The 12% with a positive signal: lift out of the pool for an in-house attempt. About one in five pays, against under 3% of the rest.</p></div>')
body = f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;flex:1">{cards}</div>{bar}'
wr("p2-action", section("p2-action", "Each tier has a treatment the policy already allows", body,
    footer="Hypotheses for the GRR workshop, to be tested in the pilot · cards 61–180; AED = outstanding principal; paid = meaningful payment",
    notes="Each tier comes with a treatment hypothesis, and every treatment is one the policy already provides; nothing here is a new process. In-house customers are curing now or have cured before, can be reached and are credible or able: half of them pay within three months, so skilled collectors should convert them with the existing tools, the CARES settlements, a restructure or a deferral. The agency tier is mostly customers who stopped suddenly or cured before and cannot be reached: place them with agencies at 61 to 180, with skip tracing where they appear to be abroad. The non-workable pool is customers who stopped suddenly or never paid, cannot be reached and show no sign of credibility or ability: the policy allows either referral to agencies with HOD approval, or no calling with dunning only, as it does for Dead Beat accounts. At 180+, the 12 percent with a positive signal are lifted out of the pool for an in-house attempt."))

# ---------------- risk score
rowsA = [("DPD bucket alone", "0.65", "0.61"), ("Allocation tiers", "0.74", "0.67"), ("Decision-tree branches", "0.77", "0.67"), ("Branches + bucket", "0.81", "0.73")]
tbl = (f'<table style="font-size:26px;color:{NAVY}"><tr>' + th("Ranking customers by", "left", "width:56%;") + th("Cards", w="width:22%;") + th("Loans", w="width:22%;") + "</tr>"
       + "".join(f'<tr><td>{a}</td><td style="text-align:right">{"<b>"+c+"</b>" if i==3 else c}</td><td style="text-align:right">{l}</td></tr>' for i, (a, c, l) in enumerate(rowsA)) + "</table>")
left = (f'<div style="display:flex;flex-direction:column;gap:18px"><p style="font-size:24px;font-weight:600;color:{GREY}">How well each view ranks who pays (AUC)</p>{tbl}'
        f'<p style="font-size:22px;color:{GREY};line-height:1.4">0.5 = no better than chance, 1.0 = perfect. In-sample, back-test month.</p></div>')
right = (f'<div style="display:flex;flex-direction:column;gap:22px">'
         f'<div style="background:{CARD};border:1px solid {LINE};border-radius:12px;padding:24px 28px;display:flex;flex-direction:column;gap:8px"><p style="font-size:28px;font-weight:600">Personas rank far better than the bucket</p><p style="font-size:24px;line-height:1.4;color:{GREY}">+0.09 to +0.12 on cards, +0.06 on loans.</p></div>'
         f'<div style="background:{CARD};border:1px solid {LINE};border-radius:12px;padding:24px 28px;display:flex;flex-direction:column;gap:8px"><p style="font-size:28px;font-weight:600">The bucket still adds something on top</p><p style="font-size:24px;line-height:1.4;color:{GREY}">Inside each card tier, payment rates still differ by 10–21 points between DPD buckets.</p></div>'
         f'<div style="background:#EEF1F8;border-radius:12px;padding:24px 28px"><p style="font-size:26px;line-height:1.4">So a score would rank customers <b>within</b> tiers, most of all in the agency tier, half the book. It does not replace the tiers.</p></div></div>')
body = f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:56px">{left}{right}</div>'
wr("p2-score", section("p2-score", "A score would rank within the tiers, not replace them", body,
    footer="Paid = meaningful payment within 3 months · tiers and AUCs in-sample; an out-of-sample check comes before the workshop",
    notes="Is a risk score still needed? We compare how well different views rank who pays, using the area under the curve, where 0.5 is chance and 1 is perfect. The DPD bucket alone reaches 0.65 on cards. The allocation tiers reach 0.74, the decision-tree branches 0.77, and branches plus bucket 0.81. On loans the same order holds at lower levels. So the personas rank customers far better than the bucket, and the bucket still adds something on top: inside every card tier, payment rates differ by 10 to 21 points between DPD buckets. A score therefore has a role ranking customers within the tiers, most of all in the agency tier, which holds half the book. These figures are in-sample; we will check them on a different month before the workshop."))

# ---------------- UC1
s = rd("p2-uc1")
s = s.replace(f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{BLUE};font-weight:600">The axes together</p>',
              f'<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{BLUE};font-weight:600">{EYEBROW}</p>')
s = rep(s, ">Where UC1 comes in<", ">UC1 adds most where we already talk to customers<")
old = re.search(r'<div style="background:#F3F3F1;border-radius:14px;padding:28px 32px;display:flex;flex-direction:column;gap:8px"><p[^>]*>41%</p>.*?</div>', s, re.S).group(0)
bars = "".join(
    f'<div style="display:flex;align-items:center;gap:16px"><div style="width:200px;display:flex">{pill(k)}</div><div style="flex:1;display:flex"><div style="width:{v}%;height:28px;background:{c};border-radius:4px"></div></div><p style="font-size:24px;font-weight:600;width:70px;text-align:right">{v}%</p></div>'
    for k, v, c in (("in", 89, NAVY), ("ag", 45, BLUE), ("nw", 16, MUTED)))
new = (f'<div style="background:{CARD};border-radius:14px;padding:24px 28px;display:flex;flex-direction:column;gap:14px">'
       f'<p style="font-size:24px;font-weight:600">Right-party contact in the last 3 months, cards 61–180</p>{bars}'
       f'<p style="font-size:22px;color:{GREY}">All cards 41% · loans 52%</p></div>')
s = rep(s, old, new)
s = rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0),
 "<aside>The transcript work, UC1, joins in the nuance step, next to credibility and ability. It only applies where a conversation took place, and that differs sharply by tier: 89 percent of in-house card accounts had a right-party contact in the last three months, 45 percent of the agency tier, and only 16 percent of the non-workable pool. So transcripts will add most where we already talk to customers, sharpening the in-house and agency decisions, and little in the non-workable pool. They add what the data cannot: what the customer said about intent, income, hardship, disputes and promises. The next step is a joint workshop with GRR to turn UC1 and UC2 together into the final personas and the decision each one supports.</aside>")
wr("p2-uc1", s)

# ---------------- pilot
def col(title, items):
    return (f'<div style="background:{CARD};border-radius:14px;padding:28px 30px;display:flex;flex-direction:column;gap:14px"><h3 style="font-family:{FONT};font-size:32px;font-weight:600">{title}</h3>'
            + "".join(f'<div style="border-left:4px solid {BLUE};padding:2px 0 2px 14px"><p style="font-size:24px;line-height:1.35">{t}</p></div>' for t in items) + '</div>')
body = (f'<div style="display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:24px">'
        + col("Test in each tier", ["<b>In-house:</b> skilled collectors and settlements vs business as usual",
                                   "<b>Agency:</b> placement at 61–180 vs in-house calling",
                                   "<b>Non-workable:</b> agency referral or dunning only vs business as usual (hold-out)",
                                   "Random split within each tier, 3 months"])
        + col("Measure", ["Meaningful payment and roll rate", "Amount collected per account", "Recovery of outstanding principal", "Call days and cost per AED collected", "180+: the flagged group vs the rest"])
        + col("Size and guardrails", ["Cards: agency and non-workable fill both arms in one month", "In-house needs a 10-pt target; loans need 10 pts and pooling",
                                     "Same policy and compliance rules", "Monthly readout and a stop rule"])
        + '</div>')
wr("p2-pilot", section("p2-pilot", "Pilot: test each tier against business as usual", body,
    footer="Sample per arm (cards, 5-pt lift): agency 970, non-workable 375; in-house 388 at a 10-pt lift · two-sided α 0.05, 80% power",
    notes="The pilot tests each tier against business as usual, with a random split inside each tier for three months. In the in-house tier, skilled collectors with the settlement tools against the current process. In the agency tier, placement with agencies at 61 to 180 against in-house calling. In the non-workable pool, the two treatments the policy allows, agency referral or dunning only, against business as usual: a hold-out that shows exactly what is lost, if anything, by taking collector time away. We measure meaningful payments and roll rates, the amount collected per account, recovery of outstanding principal, and the call days and cost per dirham collected; at 180+, the flagged group against the rest. On cards, the agency and non-workable tiers fill both arms in a single month for a five point lift; the in-house tier needs a ten point target, and loans need a ten point target and pooling over months. The same policy and compliance rules apply to every arm, with a monthly readout and a stop rule."))

# ---------------- roadmap
s = rd("roadmap")
for a, b in [(">Segment workshop with GRR<", ">Workshop with GRR<"), (">UC1 + UC2 together<", ">tiers, non-workable definition, UC1 + UC2<"),
             (">Pilot design<", ">Inputs and checks<"), (">segments, arms, metrics<", ">commission rate card, in-house cost, out-of-sample test<")]:
    s = rep(s, a, b)
s = rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0),
        "<aside>Five steps from here. Put the persona table into production for all four axes, monthly. Workshop with GRR: agree the tiers and the framework as the definition of the non-workable pool, bringing UC1 and UC2 together. Get the inputs that set the cut-offs properly, the agency commission rate card and the in-house cost per account, and check the tiers on a different month. Run the pilot for three months. Read it out, decide whether to scale, and decide where a risk score ranks within the tiers.</aside>")
wr("roadmap", s)

# ---------------- summary Next bar
s = rd("exec")
s = rep(s, "Agree in-house, agency and early-exit tiers · combine with UC1 · design and run the pilot · the bureau salary feed.",
        "Agree the tiers and the non-workable pool with GRR · combine with UC1 · run the pilot · the bureau salary feed.")
s = rep(s, "Next: agree with GRR which customers to work in-house, which to send to an agency and which to consider for early exit;",
        "Next: agree with GRR which customers to work in-house, which to place with agencies, and use the framework to define the policy's non-workable pool;")
wr("exec", s)
print("ok")
