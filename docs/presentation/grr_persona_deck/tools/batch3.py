import re, sys, json
D = sys.argv[1]
rd = lambda f: open(f"{D}/slides/{f}.html").read()
def wr(f, s): open(f"{D}/slides/{f}.html", "w").write(s)
def rep(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a)); return s.replace(a, b)
FONT = "'Plus Jakarta Sans', Arial, sans-serif"
NAVY, BLUE, GREY, CARD, LINE = "#072447", "#2765FF", "#4C515A", "#F3F3F1", "#E6E6E3"
def eyebrow(s, new):
    return re.sub(r'(<p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:#2765FF;font-weight:600">)[^<]*(</p>)', r'\g<1>' + new + r'\2', s, count=1)
def notes(s, new): return rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0), f"<aside>{new}</aside>")

# ---------- summary
def card(label, body, pad="32px 36px"):
    return (f'<div style="display:flex;flex-direction:column;gap:12px;background:{CARD};padding:{pad};border:1px solid {LINE};border-radius:16px">'
            f'<p style="font-size:22px;letter-spacing:2px;text-transform:uppercase;color:{GREY};font-weight:600">{label}</p>{body}</div>')
def stat(num, text):
    return (f'<div style="display:flex;align-items:center;gap:28px;background:{CARD};border:1px solid {LINE};border-radius:12px;padding:18px 28px">'
            f'<div style="flex:none;width:250px"><p style="font-family:{FONT};font-size:52px;font-weight:600;color:{BLUE};white-space:nowrap">{num}</p></div>'
            f'<div style="flex:1"><p style="font-size:26px;line-height:1.35">{text}</p></div></div>')
left = (f'<div style="display:flex;flex-direction:column;gap:24px">'
        + card("Today", '<p style="font-size:26px;line-height:1.4">No model beyond 60 DPD. Cases are allocated by bucket and product, and late buckets hold little behaviour to model.</p>')
        + card("The framework", '<p style="font-size:26px;line-height:1.4">Signals from every data domain, condensed into persona states each month: <b>how they got here</b>, <b>can we talk to them</b>, <b>what we can offer</b>.</p>')
        + '</div>')
right = (f'<div style="display:flex;flex-direction:column;gap:16px"><p style="font-size:22px;letter-spacing:2px;text-transform:uppercase;color:{GREY};font-weight:600">What it shows</p>'
         + stat("4% – 73%", "of card customers make a meaningful payment within the same 91–120 bucket, depending on persona.")
         + stat("60% vs 22%", "of card customers curing now pay within 3 months, against those who cured before.")
         + stat("12%", "of 180+ accounts show a positive signal; one in five of them pays, against under 3% of the rest.")
         + '</div>')
s = rd("exec")
grid_old = re.search(r'<div style="display:grid;grid-template-columns:1fr 1fr 1.3fr;gap:32px">.*?</div>\n</div>\n', s, re.S).group(0)
s = rep(s, grid_old, f'<div style="display:grid;grid-template-columns:680px 1fr;gap:40px">{left}{right}</div>\n')
s = rep(s, "Agree the tiers and the non-workable pool with GRR · combine with UC1 · run the pilot · the bureau salary feed.",
        "Finalise the axes with GRR · integrate UC1 into the final personas · strategy workshop · risk score: with the personas or in Phase 2.")
s = notes(s, "Three messages. One: beyond 60 DPD there is no model; cases are allocated by bucket and product, and the late buckets are where data runs dry. Two: we built synthesized features, signals from every data domain condensed into persona states that answer three questions in order. Three: what it shows. Inside the single 91 to 120 bucket, the share of card customers making a meaningful payment runs from 4 percent to 73 percent depending on the persona. Card customers who are curing now pay within three months 60 percent of the time, against 22 percent for those who cured before. At 180+, 12 percent of accounts show a positive signal, and about one in five of them pays, against under 3 percent of the rest. Next: finalise the axes with GRR, including whether ability ships now or after the bureau feed; integrate UC1 into the final personas; a workshop on collection strategy and how GRR uses the output; and a risk score, alongside the personas if it adds value, otherwise in Phase 2.")
wr("exec", s)

# ---------- roadmap, four steps
def step(n, title, sub, last=False):
    line = "#FFFFFF" if last else "#E6E6E3"
    return (f'<div style="display:flex;flex-direction:column;gap:14px"><div style="display:flex;align-items:center;gap:12px"><div style="width:56px;height:56px;border-radius:28px;background:{NAVY};flex:none;display:flex;align-items:center;justify-content:center"><p style="font-size:26px;font-weight:600;line-height:1;color:#FFFFFF">{n}</p></div><div style="flex:1;height:3px;background:{line}"></div></div>'
            f'<h3 style="font-family:{FONT};font-size:30px;font-weight:600;line-height:1.2">{title}</h3><p style="font-size:24px;line-height:1.35;color:{GREY}">{sub}</p>'
            f'<div style="background:{CARD};border-radius:10px;padding:12px 16px;display:flex;flex-direction:column;gap:4px"><p style="font-size:22px;color:{GREY}">Owner: [__]</p><p style="font-size:22px;color:{GREY}">Date: [__]</p></div></div>')
s = rd("roadmap")
g_old = re.search(r'<div style="display:grid;grid-template-columns:repeat\(5, 1fr\);gap:24px">.*</div></div></div>\n', s, re.S).group(0)
g = ('<div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:32px">'
     + step(1, "Finalise the persona axes", "with GRR: 3 of 4 agreed; ability ships now (about half of customers visible) or after the bureau feed, early next year")
     + step(2, "UC1 into the final personas", "transcript signals join the nuance step")
     + step(3, "Collection strategy workshop", "how GRR uses the output; which decisions each persona supports")
     + step(4, "Risk score model", "with the personas if it adds value, otherwise Phase 2", last=True)
     + '</div>\n')
s = rep(s, g_old, g)
s = rep(s, ">From framework to pilot<", ">From persona axes to collection strategy<")
s = notes(s, "Four steps from here. First, finalise the persona axes with GRR: three of the four are agreed, and for ability we decide whether to ship it now, seeing about half of customers, or after the bureau salary feed arrives early next year. Second, integrate the transcript work, UC1, into the final personas. Third, a workshop on collection strategy: how GRR uses the output and which decisions each persona supports; the allocation view in this deck is a starting point for that discussion. Fourth, the risk score model: alongside the personas if the results show it adds value, otherwise in Phase 2.")
wr("roadmap", s)

# ---------- divider
s = rd("div-combined")
s = rep(s, ">From persona states to allocation<", ">What the personas could support<")
s = rep(s, ">In-house, agency or the non-workable pool · Risk score · UC1 · Pilot<", ">A first look at allocation · Risk score · UC1<")
s = notes(s, "Part 2 is a first look, not a plan. It shows what the persona states could support once the axes are final: a view of allocation at 61 to 180, whether a risk score still adds value, and where the transcript work fits. None of it has been agreed with GRR; it is material for the strategy workshop.")
wr("div-combined", s)

# ---------- tree
s = eyebrow(rd("p2-tree"), "A first look")
s = s.replace("Each branch carries the tier of its average: in-house where payments are likely and worth our collectors' time, agency for the large unreachable middle, and the non-workable pool for never-paid customers we cannot reach. The next slide tiers every account by its full combination.",
              "As a first look, each branch also carries an illustrative tier: in-house where payments are likely, agency for the large unreachable middle, and the non-workable pool for never-paid customers we cannot reach. The next slide applies the same idea to every account.")
wr("p2-tree", s)

# ---------- tier slide (fix pills in table, soften)
s = eyebrow(rd("p2-combos"), "A first look")
s = rep(s, ">The framework defines the policy's non-workable pool: a third of card accounts, under 5% of the money<",
        ">A first look: the personas could give the policy's non-workable pool a definition<")
labels = {"In-house": NAVY, "Agency": BLUE, "Non-workable": GREY}
for lab, col in labels.items():
    m = re.search(r'<td><div style="display:flex"><p [^>]*>' + lab + r'</p></div></td>', s)
    assert m, lab
    s = s.replace(m.group(0), f'<td><span style="color:{col}"><b>{lab}</b></span></td>')
s = notes(s, "A first look at what the personas could support; nothing here has been discussed with GRR. The policy already refers a non-workable pool, the non-contactable and least probable to pay, to external agencies, but it does not define it. Ranking every combination of the four axes by expected collections, what its accounts paid in dirhams in the three months after the back-test month, the top fifth of card accounts bring in 55 percent of the money while holding 19 percent of the principal. Cut illustratively into three groups: in-house, 11 percent of accounts and 44 percent of the money; agency, 54 percent and 46 percent; and a non-workable pool, a third of accounts, under 5 percent of the money, recovering half a percent of principal, yet still taking nearly 11 call days per account. The cut-offs are illustrations from the data; the commission rate card and the in-house cost would set them properly. Loans show the same pattern.")
wr("p2-combos", s)

# ---------- risk score
s = eyebrow(rd("p2-score"), "Risk score")
s = rep(s, ">A score would rank within the tiers, not replace them<", ">A risk score could still add value: it would rank customers within the personas<")
s = rep(s, "So a score would rank customers <b>within</b> tiers, most of all in the agency tier, half the book. It does not replace the tiers.",
        "<b>Decision:</b> build it alongside the personas if an out-of-sample test confirms the gain; otherwise Phase 2.")
s = rep(s, "Paid = meaningful payment within 3 months · tiers and AUCs in-sample; an out-of-sample check comes before the workshop",
        "Paid = meaningful payment within 3 months (the risk score's target) · in-sample, back-test month")
s = notes(s, "Is a risk score still worth building? We compare how well different views rank who pays, using the area under the curve, where 0.5 is chance and 1 is perfect. The DPD bucket alone reaches 0.65 on cards; the illustrative tiers 0.74, the decision-tree branches 0.77, and branches plus bucket 0.81. Loans follow the same order at lower levels. So the personas rank customers far better than the bucket, and the bucket still adds something on top: inside each card tier, payment rates differ by 10 to 21 points between DPD buckets. A score would therefore rank customers within the personas rather than replace them. The decision: build it alongside the personas if an out-of-sample test confirms the gain; otherwise it moves to Phase 2.")
wr("p2-score", s)

# ---------- UC1
s = eyebrow(rd("p2-uc1"), "UC1")
s = rep(s, "a joint UC1 + UC2 workshop with GRR to define the final personas and the decision each supports.",
        "integrate UC1 into the final personas, then a strategy workshop with GRR on the decisions each supports.")
s = notes(s, "The transcript work, UC1, joins in the nuance step, next to credibility and ability. It only applies where a conversation took place, and that differs sharply across the illustrative tiers: 89 percent of in-house card accounts had a right-party contact in the last three months, 45 percent of the agency group and 16 percent of the non-workable pool. So transcripts will add most where we already talk to customers. They add what the data cannot: what the customer said about intent, income, hardship, disputes and promises. Next, UC1 is integrated into the final personas, followed by a strategy workshop with GRR on the decisions each persona supports.")
wr("p2-uc1", s)

# ---------- treatments and pilot -> appendix
s = eyebrow(rd("p2-action"), "Appendix · A first look")
s = rep(s, ">Each tier has a treatment the policy already allows<", ">What each group could mean, for discussion<")
s = rep(s, "Hypotheses for the GRR workshop, to be tested in the pilot · cards 61–180; AED = outstanding principal; paid = meaningful payment",
        "For discussion in the strategy workshop; not agreed with GRR · cards 61–180; AED = outstanding principal; paid = meaningful payment")
s = s.replace("Each tier comes with a treatment hypothesis, and every treatment is one the policy already provides; nothing here is a new process.",
              "For discussion only, not agreed with GRR. Each illustrative group is paired with a treatment the policy already provides; nothing here is a new process.")
wr("p2-action", s)
s = eyebrow(rd("p2-pilot"), "Appendix · A first look")
s = rep(s, ">Pilot: test each tier against business as usual<", ">How a pilot could test it, if the strategy workshop takes it forward<")
s = s.replace("The pilot tests each tier against business as usual", "For discussion only. If the strategy workshop takes the allocation view forward, a pilot could test each group against business as usual")
wr("p2-pilot", s)

# ---------- index: order and section text
p = f"{D}/deck.json"; j = json.load(open(p))
order = [x for x in j["order"] if x not in ("p2-action", "p2-pilot", "p2-combos", "p2-tree")]
i = order.index("div-combined"); order[i+1:i+1] = ["p2-tree", "p2-combos"]
i = order.index("div-appendix"); order[i+1:i+1] = ["p2-action", "p2-pilot"]
j["order"] = order
j["sections"]["s3"]["description"] = "What the personas could support: a first look at allocation, the risk score, UC1"
j["sections"]["s4"]["description"] = "Appendix: possible treatments and pilot, signals, rules, governance"
open(p, "w").write(json.dumps(j, indent=2, ensure_ascii=False) + "\n")
print(order)
