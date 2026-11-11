import re, sys, json
D = sys.argv[1]
rd = lambda f: open(f"{D}/slides/{f}.html").read()
def wr(f, s): open(f"{D}/slides/{f}.html", "w").write(s)
def rep(s, a, b):
    assert s.count(a) == 1, (a[:90], s.count(a)); return s.replace(a, b)
FONT = "'Plus Jakarta Sans', Arial, sans-serif"
NAVY, BLUE, GREY, MUTED, CARD, LINE = "#072447", "#2765FF", "#4C515A", "#9295A0", "#F3F3F1", "#E6E6E3"

# ---------- tree: drop tier column
s = rd("p2-tree")
s = re.sub(r'<div style="height:46px;display:flex;align-items:center"><p style="font-size:20px;font-weight:600;white-space:nowrap;[^"]*">[^<]*</p></div>', "", s)
s = rep(s, f'<p style="font-size:22px;font-weight:600;color:{GREY};text-align:left">Tier</p>', "")
s = rep(s, "grid-template-columns:400px 240px 1fr 130px 160px 190px;gap:6px 14px", "grid-template-columns:420px 260px 1fr 140px 180px;gap:6px 14px")
s = rep(s, '>A first look</p>', '>The axes together</p>')
s = rep(s, " · tier of each branch's average; accounts are tiered by their full combination", "")
s = rep(s, " As a first look, each branch also carries an illustrative tier: in-house where payments are likely, agency for the large unreachable middle, and the non-workable pool for never-paid customers we cannot reach. The next slide applies the same idea to every account.",
        " The next slides take this one step further, from these branches to every combination of the four axes.")
assert "In-house" not in s and "Non-workable" not in s
wr("p2-tree", s)

# ---------- new helper slide
def stepcard(n, title, body):
    return (f'<div style="background:{CARD};border:1px solid {LINE};border-radius:14px;padding:28px 30px;display:flex;flex-direction:column;gap:16px">'
            f'<div style="display:flex;align-items:center;gap:14px"><div style="width:48px;height:48px;border-radius:24px;background:{NAVY};flex:none;display:flex;align-items:center;justify-content:center"><p style="font-size:24px;font-weight:600;line-height:1;color:#FFFFFF">{n}</p></div>'
            f'<h3 style="font-family:{FONT};font-size:30px;font-weight:600;line-height:1.2">{title}</h3></div>{body}</div>')
p = lambda t, extra="": f'<p style="font-size:24px;line-height:1.4{extra}">{t}</p>'
chip = lambda t: f'<p style="font-size:22px;font-weight:600;background:#FFFFFF;border:1px solid {LINE};border-radius:8px;padding:8px 14px">{t}</p>'
ex = lambda t: f'<div style="background:#EEF1F8;border-radius:10px;padding:16px 20px">{p(t)}</div>'
c1 = stepcard(1, "Describe each account", p("One state on each of the four axes. Together they form a <b>combination</b>.")
              + f'<div style="display:flex;flex-direction:column;gap:8px">{chip("Stopped suddenly")}{chip("Skip · Non-Reachable")}{chip("Low credibility")}{chip("Unknown ability")}</div>'
              + p("576 combinations are possible; 272 occur on cards.", f";color:{GREY}"))
c2 = stepcard(2, "Measure what it paid", p("For each combination: every account in May 2026, everything it paid in June–August, averaged per account.")
              + ex("<b>Example:</b> 400 accounts paid AED 70,000 in total → <b>AED 175 per account</b>. 10% of them paid, AED 1,750 each on average.")
              + p("Observed, not modelled: the average combines how often and how much.", f";color:{GREY}"))
def tierrow(lab, col, rule, dashed=False):
    box = f"border:2px dashed {MUTED};" if dashed else f"background:{col};"
    tc = GREY if dashed else ("#FFFFFF" if col == NAVY else NAVY)
    return (f'<div style="display:flex;align-items:center;gap:14px"><div style="width:190px;flex:none;{box}border-radius:999px;padding:6px 14px;display:flex;justify-content:center">'
            f'<p style="font-size:20px;font-weight:600;color:{tc}">{lab}</p></div><p style="font-size:24px">{rule}</p></div>')
c3 = stepcard(3, "Rank and cut", p("The 159 combinations with at least 10 accounts (97% of cards), ranked by AED per account:")
              + f'<div style="display:flex;flex-direction:column;gap:12px">{tierrow("In-house", NAVY, "AED 1,250 and above")}{tierrow("Agency", "#EEF1F8", "between")}{tierrow("Non-workable", "", "under AED 175", True)}</div>'
              + p("Illustrative cut-offs from the data; GRR would set them from the commission rate card and in-house cost.", f";color:{GREY}"))
body = f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px;flex:1">{c1}{c2}{c3}</div>'
method = (f'<section id="p2-method" data-transition="fade" style="background:#FFFFFF;color:{NAVY};font-family:{FONT};padding:112px 128px 150px;display:flex;flex-direction:column;gap:32px">\n'
          f'<div style="display:flex;flex-direction:column;gap:14px"><p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{BLUE};font-weight:600">A first look</p>'
          f'<h2 style="font-family:{FONT};font-size:52px;font-weight:600;line-height:1.1">How an account gets a tier: by what its combination actually paid</h2></div>\n{body}\n'
          f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:22px;color:{GREY}">Cards 61–180 · back-test May → June–August 2026, in-sample · combinations under 10 accounts are left unassigned (3% of cards)</p>\n'
          '<aside>How the tiers on the next slide are built, in three steps. First, every account has one state on each of the four axes: its deterioration family, its locatability cell, its credibility band and its ability band. Together these form a combination; 576 are possible and 272 actually occur on cards. Second, for each combination we take every account in May and add up everything it paid in June to August, then divide by the number of accounts. That gives the amount collected per account, an observed average that combines how often accounts paid and how much they paid; for example, 400 accounts paying 70,000 dirhams is 175 dirhams per account. Third, we rank the 159 combinations large enough to judge, 97 percent of card accounts, and cut the list: 1,250 dirhams and above in-house, under 175 the non-workable pool, agency in between. The cut-offs are illustrations from the data; GRR would set them from the agency commission rate card and the in-house cost. Every account then takes the tier of its combination.</aside>\n</section>\n')
open(f"{D}/slides/p2-method.html", "w").write(method)

# ---------- tier slide: definition box, headline
s = rd("p2-combos")
s = rep(s, ">A first look: the personas could give the policy's non-workable pool a definition<", ">The personas could give the policy's non-workable pool a definition<")
who = re.search(r'<div style="display:flex;flex-direction:column;gap:10px"><p style="font-size:24px;line-height:1.35"><b>In-house:</b>.*?</div>', s, re.S).group(0)
s = rep(s, who, f'<div style="border-left:6px solid {NAVY};background:#EEF1F8;border-radius:8px;padding:18px 22px;display:flex;flex-direction:column;gap:8px">'
               f'<p style="font-size:24px;line-height:1.4"><b>Definition:</b> accounts whose persona combination has returned under AED 175 in 3 months (about 0.5% of principal).</p>'
               f'<p style="font-size:24px;line-height:1.4;color:{GREY}">In practice: stopped paying suddenly (79%) or never paid (20%), and not reachable.</p></div>')
s = s.replace("The policy already refers a non-workable pool, the non-contactable and least probable to pay, to external agencies, but it does not define it.",
              "The policy already refers a non-workable pool, the non-contactable and least probable to pay, to external agencies, based on internal assessments, but it does not define it. The personas offer a definition: accounts whose combination of states has returned under 175 dirhams in three months, about half a percent of principal. In practice, customers who stopped paying suddenly or never paid, and whom we cannot reach.")
wr("p2-combos", s)

# ---------- appendix wording
s = rd("p2-action")
s = rep(s, ">Stopped suddenly or never paid, not reachable, no sign of credibility or ability<", ">Stopped suddenly or never paid, not reachable<")
s = rep(s, "cannot be reached and show no sign of credibility or ability:", "and cannot be reached:")
wr("p2-action", s)

# ---------- index
p_ = f"{D}/deck.json"; j = json.load(open(p_))
order = [x for x in j["order"] if x != "roadmap"]
i = order.index("p2-tree"); order.insert(i + 1, "p2-method")
j["order"] = order
open(p_, "w").write(json.dumps(j, indent=2, ensure_ascii=False) + "\n")
print(order)
