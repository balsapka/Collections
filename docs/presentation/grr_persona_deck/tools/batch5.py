import re, sys, json
D = sys.argv[1]
rd = lambda f: open(f"{D}/slides/{f}.html").read()
def wr(f, s): open(f"{D}/slides/{f}.html", "w").write(s)
def rep(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a)); return s.replace(a, b)
def notes(s, new): return rep(s, re.search(r"<aside>.*?</aside>", s, re.S).group(0), f"<aside>{new}</aside>")
FONT = "'Plus Jakarta Sans', Arial, sans-serif"
NAVY, BLUE, GREY, CARD, LINE = "#072447", "#2765FF", "#4C515A", "#F3F3F1", "#E6E6E3"

# ---------- risk score (out-of-sample)
s = rd("p2-score")
s = rep(s, ">A risk score could still add value: it would rank customers within the personas<", ">Personas rank payers far better than the bucket; a model adds a little on top<")
tbl_old = re.search(r"<table.*?</table>", s, re.S).group(0)
rows = [("DPD bucket only (today)", "0.65", "0.62", False), ("Personas", "0.83", "0.77", True), ("Personas × DPD bucket", "0.84", "0.77", False), ("Simple model (axis states + bucket)", "0.84", "0.78", False)]
th = lambda t, a, w: f'<th style="width:{w}%;text-align:{a}">{t}</th>'
tbl = (f'<table style="font-size:26px;color:{NAVY}"><tr>' + th("Ranking customers by", "left", 60) + th("Cards", "right", 20) + th("Loans", "right", 20) + "</tr>"
       + "".join(f'<tr><td>{"<b>"+a+"</b>" if b else a}</td><td style="text-align:right">{"<b>"+c+"</b>" if b else c}</td><td style="text-align:right">{"<b>"+l+"</b>" if b else l}</td></tr>' for a, c, l, b in rows) + "</table>")
s = rep(s, tbl_old, tbl)
s = rep(s, "Tree branches = the end points of the tree slide (family × reachable × credible or able). 0.5 = chance, 1.0 = perfect.",
        "Out-of-sample: 5 folds by account, January–May 2026 cohorts. 0.5 = chance, 1.0 = perfect.")
right_old = re.search(r'<div style="display:flex;flex-direction:column;gap:22px"><div style="background:#F3F3F1.*?</div></div></div>\n', s, re.S).group(0)
box = lambda t, sub: (f'<div style="background:{CARD};border:1px solid {LINE};border-radius:12px;padding:22px 28px;display:flex;flex-direction:column;gap:8px">'
                      f'<p style="font-size:28px;font-weight:600">{t}</p><p style="font-size:24px;line-height:1.4;color:{GREY}">{sub}</p></div>')
right = (f'<div style="display:flex;flex-direction:column;gap:20px">'
         + box("Personas beat the bucket in every test", "+0.17 on cards, +0.14 on loans. The top 20% of card accounts by persona hold 54% of the money collected (bucket: 30%).")
         + box("The bucket adds almost nothing within personas", "+0.01 on cards, +0.00 on loans.")
         + f'<div style="background:#EEF1F8;border-radius:12px;padding:22px 28px"><p style="font-size:26px;line-height:1.4">A risk score would add about <b>+0.02</b> over the personas. <b>Decision:</b> with the personas if that gain is worth the build, otherwise Phase 2.</p></div>'
         + '</div></div>\n')
s = rep(s, right_old, right)
s = rep(s, "Paid = meaningful payment within 3 months (the risk score's target) · in-sample, back-test month",
        "Paid = meaningful payment within 3 months (the risk score's target) · strict and rolling time splits give the same picture")
s = notes(s, "Is a risk score still worth building? We tested out-of-sample: the payment rates of each view were learned on some accounts and months and scored on others, January to May 2026, in five folds, and confirmed with time splits. Ranking power is the area under the curve, where 0.5 is chance and 1 is perfect. The DPD bucket alone reaches 0.65 on cards and 0.62 on loans. The personas reach 0.83 and 0.77: far better, in every test, and the top fifth of card accounts by persona hold 54 percent of the money collected, against 30 percent by bucket. Adding the bucket to the personas adds almost nothing. A simple model on the axis states and the bucket adds about two points of AUC over the personas. So a risk score would add a little, consistently. The decision: build it alongside the personas if that gain is worth the effort, otherwise in Phase 2.")
wr("p2-score", s)

# ---------- tier slide: OOS card numbers, persona wording
s = rd("p2-combos")
vals = {"In-house": ("11%", "44%", "9.75%", "17%", "48%", "10.0%"),
        "Agency": ("54%", "46%", "2.6%", "54%", "46%", "2.7%"),
        "Non-workable": ("32%", "4.6%", "0.47%", "29%", "6%", "0.56%")}
for lab, (a0, m0, r0, a1, m1, r1) in vals.items():
    pat = (f'<b>{lab}</b></span></td><td style="text-align:right">{a0}</td><td style="text-align:right">{m0}</td><td style="text-align:right">{r0}</td>')
    s = rep(s, pat, f'<b>{lab}</b></span></td><td style="text-align:right">{a1}</td><td style="text-align:right">{m1}</td><td style="text-align:right">{r1}</td>')
s = rep(s, "accounts whose persona combination has returned under AED 175 in 3 months (about 0.5% of principal).",
        "accounts whose persona has returned under AED 175 in 3 months (about 0.5% of principal).")
s = rep(s, "Cards 61–180 · ranked by AED collected per account in 3 months (back-test, in-sample) · cuts AED 1,250 / 175 · loans: 7.9 / 2.9 / 0.7% recovery",
        "Cards 61–180 · table out-of-sample (5 folds, Jan–May 2026); call days: August · cuts AED 1,250 / 175 · loans: same order, thresholds less stable")
s = rep(s, ">top 20% → 55% of money<", ">top 20% → 54% of money<")
s = notes(s, "A first look at what the personas could support; nothing here has been discussed with GRR. The policy already refers a non-workable pool, the non-contactable and least probable to pay, to external agencies, based on internal assessments, but it does not define it. The personas offer a definition: accounts whose persona has returned under 175 dirhams in three months, about half a percent of principal. In practice, customers who stopped paying suddenly or never paid, and whom we cannot reach. Tested on unseen months and accounts, the top fifth of card accounts by persona hold 54 percent of the money collected. The illustrative cut-offs give three groups: in-house, 17 percent of accounts and 48 percent of the money, recovering about 10 percent of principal in three months; agency, 54 percent and 46 percent; and the non-workable pool, 29 percent of accounts, about 6 percent of the money, recovering just over half a percent, yet still taking nearly 11 call days per account. The groups keep their order on every unseen month. On loans the order holds too, but the exact thresholds move more because the loan book is smaller; pooling months or a smoothed score would steady them. The cut-offs are illustrations; the commission rate card and the in-house cost would set them properly.")
wr("p2-combos", s)

# ---------- helper slide wording
s = rd("p2-method")
s = rep(s, ">How an account gets a tier: by what its combination actually paid<", ">How an account gets a tier: by what its persona actually paid<")
s = rep(s, "One state on each of the four axes. Together they form a <b>combination</b>.", "One state on each of the four axes. Together they form its <b>persona</b>.")
s = rep(s, "576 combinations are possible; 272 occur on cards.", "576 personas are possible; 272 occur on cards.")
s = rep(s, "For each combination: every account in May 2026", "For each persona: every account in May 2026")
s = rep(s, "The 159 combinations with at least 10 accounts (97% of cards), ranked by AED per account:", "The 159 personas with at least 10 accounts (97% of cards), ranked by AED per account:")
s = rep(s, "back-test May → June–August 2026, in-sample · combinations under 10 accounts are left unassigned (3% of cards)",
        "back-test May → June–August 2026; the tiers hold on unseen months (Jan–May 2026) · personas under 10 accounts are left unassigned (3% of cards)")
s = s.replace("Together these form a combination; 576 are possible", "Together these form its persona; 576 are possible").replace("for each combination we take", "for each persona we take").replace("we rank the 159 combinations", "we rank the 159 personas").replace("takes the tier of its combination", "takes the tier of its persona")
wr("p2-method", s)

# ---------- summary stat
s = rd("exec")
s = rep(s, ">4% – 73%</p></div><div style=\"flex:1\"><p style=\"font-size:26px;line-height:1.35\">of card customers make a meaningful payment within the same 91–120 bucket, depending on persona.",
        ">54% vs 30%</p></div><div style=\"flex:1\"><p style=\"font-size:26px;line-height:1.35\">of money collected sits in the top 20% of card accounts ranked by persona, against ranked by DPD bucket.")
s = rep(s, "Inside the single 91 to 120 bucket, the share of card customers making a meaningful payment runs from 4 percent to 73 percent depending on the persona.",
        "Tested on unseen months, the top fifth of card accounts ranked by persona hold 54 percent of the money collected, against 30 percent when ranked by DPD bucket.")
wr("exec", s)

# ---------- tree -> appendix
s = rd("p2-tree")
s = rep(s, ">The axes together</p>", ">Appendix · Illustrative grouping, not a proposal</p>")
s = rep(s, " The next slides take this one step further, from these branches to every combination of the four axes.",
        " This is an illustrative simplification, not a proposal: it merges personas, ignoring location and combining credibility and ability bands. How personas are grouped for strategy is for the GRR workshop.")
wr("p2-tree", s)
p_ = f"{D}/deck.json"; j = json.load(open(p_))
order = [x for x in j["order"] if x != "p2-tree"]
i = order.index("div-appendix"); order.insert(i + 1, "p2-tree")
j["order"] = order
open(p_, "w").write(json.dumps(j, indent=2, ensure_ascii=False) + "\n")
print(order)
