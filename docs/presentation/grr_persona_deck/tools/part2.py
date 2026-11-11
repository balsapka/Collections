"""Part 2 slides in the template style: combinations, path tree, action, score, UC1, pilot, next steps."""
import sys
from pathlib import Path

S = Path(sys.argv[1])
NAVY, ACC, GREY, MUTE, CARD, LINE = "#072447", "#2765FF", "#4C515A", "#9295A0", "#F3F3F1", "#E6E6E3"
G, A, R = "#2E8B57", "#E0A526", "#C0392B"
FONT = "font-family:'Plus Jakarta Sans', Arial, sans-serif"


def page(sid, eyebrow, title, body, notes, footer="", gap=36):
    foot = (f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:{GREY}">{footer}</p>\n'
            if footer else "")
    return (f'<section id="{sid}" data-transition="fade" style="background:#FFFFFF;color:{NAVY};{FONT};padding:112px 128px 150px;'
            f'display:flex;flex-direction:column;gap:{gap}px">\n'
            f'<div style="display:flex;flex-direction:column;gap:14px"><p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{ACC};font-weight:600">{eyebrow}</p>'
            f'<h2 style="{FONT};font-size:56px;font-weight:600;line-height:1.1">{title}</h2></div>\n'
            f'{body}\n{foot}<aside>{notes}</aside>\n</section>\n')


def stat(big, text):
    return (f'<div style="background:{CARD};border-radius:14px;padding:28px 32px;display:flex;flex-direction:column;gap:8px">'
            f'<p style="{FONT};font-size:72px;font-weight:600;line-height:1;color:{ACC}">{big}</p>'
            f'<p style="font-size:26px;line-height:1.35">{text}</p></div>')


# 1 combinations
hdr = ["#", "Deterioration", "Locatability", "Credibility", "Ability", "Share", "Paid in 3 m"]
wid = [6, 22, 20, 15, 13, 11, 13]
th = "".join(f'<th style="width:{w}%;text-align:{"right" if i > 4 else "left"}">{h}</th>' for i, (h, w) in enumerate(zip(hdr, wid)))
trs = "".join(f'<tr><td>{i}</td><td>[__]</td><td>[__]</td><td>[__]</td><td>[__]</td><td style="text-align:right">[__]%</td><td style="text-align:right">[__]%</td></tr>' for i in range(1, 9))
combos = (f'<div style="display:grid;grid-template-columns:520px 1fr;gap:56px">'
          f'<div style="display:flex;flex-direction:column;gap:20px">'
          + stat("[__]", "of about 400 possible combinations cover 80% of card accounts at 61–180")
          + stat("[__]", "combinations are empty or almost empty (under 0.5% of accounts)")
          + f'</div><div style="display:flex;flex-direction:column;gap:12px"><p style="font-size:24px;font-weight:600">Largest combinations · cards 61–180</p>'
          f'<table style="font-size:24px;color:{NAVY}"><tr>{th}</tr>{trs}</table></div></div>')
(S / "p2-combos.html").write_text(page(
    "p2-combos", "The axes together", "A few combinations hold most of the book", combos,
    "Four axes allow about four hundred combinations: three deterioration families, nine location and reachability cells, four credibility bands and four ability bands. In practice a small number of them hold most of the book, and many are empty. This slide shows how concentrated it is and lists the largest combinations with their size and how often they paid in the following three months. Numbers come from the persona table run."))

# 2 tree
fam = [("Shown they can cure", G), ("Paid, then stopped suddenly", A), ("Never paid", "#4C515A")]
cells = []
H = "height:54px"
for name, col in fam:
    cells.append(f'<div style="grid-row:span 3;background:{CARD};border-left:8px solid {col};border-radius:10px;padding:0 18px;display:flex;align-items:center"><p style="font-size:24px;font-weight:600">{name} <span style="color:{GREY}">· [__]%</span></p></div>')
    cells.append(f'<div style="grid-row:span 2;background:#EEF1F8;border-radius:10px;padding:0 18px;display:flex;align-items:center"><p style="font-size:24px;font-weight:600">Reachable</p></div>')
    cells.append(f'<div style="{H};border:1px solid {LINE};border-radius:10px;padding:0 18px;display:flex;align-items:center"><p style="font-size:24px">Credible or able</p></div>')
    cells += [f'<div style="{H};display:flex;align-items:center;justify-content:end"><p style="font-size:24px;font-weight:600">[__]%</p></div>'] * 2
    cells.append(f'<div style="{H};border:1px solid {LINE};border-radius:10px;padding:0 18px;display:flex;align-items:center"><p style="font-size:24px">Neither</p></div>')
    cells += [f'<div style="{H};display:flex;align-items:center;justify-content:end"><p style="font-size:24px;font-weight:600">[__]%</p></div>'] * 2
    cells.append(f'<div style="{H};background:{CARD};border-radius:10px;padding:0 18px;display:flex;align-items:center"><p style="font-size:24px;font-weight:600">Not reachable</p></div>')
    cells.append(f'<div style="{H};padding:0 18px;display:flex;align-items:center"><p style="font-size:24px;color:{GREY}">route decision</p></div>')
    cells += [f'<div style="{H};display:flex;align-items:center;justify-content:end"><p style="font-size:24px;font-weight:600">[__]%</p></div>'] * 2
heads = "".join(f'<p style="font-size:22px;font-weight:600;color:{GREY};text-align:{a}">{h}</p>' for h, a in
                [("1 · How they got here", "left"), ("2 · Can we talk to them", "left"), ("3 · The nuance", "left"), ("Share", "right"), ("Paid in 3 m", "right")])
tree = (f'<div style="display:grid;grid-template-columns:400px 280px 1fr 140px 180px;gap:8px 14px">{heads}{"".join(cells)}</div>')
(S / "p2-tree.html").write_text(page(
    "p2-tree", "The axes together", "The book, along the decision path", tree,
    "The same book, split in the order a case meets the framework: first how they got here, then whether we can talk to them, then, for the reachable, whether they show credibility or the means to pay. Each end point shows its share of accounts and how often it paid in the following three months. This keeps deterioration in the picture and lets the segments come from the data.",
    footer="Cards 61–180 · share of accounts; paid = any payment of AED 100+ in the next 3 months", gap=28))

# 3 action
acts = [("Can cure · Reachable · Credible", "Convert fast: a plan or settlement through a skilled agent", "Already paying something; nobody at 60+ simply forgot."),
        ("Stopped suddenly · Reachable · Some means", "A hardship plan or restructure", "Most likely an event, not a habit."),
        ("Reachable · Not credible · Some means", "Firm handling and early escalation", "Can pay, but promises are not kept."),
        ("Non-Reachable or Skip", "Route by reason: tracing or an agency", "No conversation is possible in-house."),
        ("Never paid", "Fraud and identity check first", "No repayment was ever made."),
        ("180+ with a positive signal", "Lift out of the pool for an in-house attempt", "Payment is still possible.")]
cards = "".join(
    f'<div style="background:{CARD};border-radius:14px;padding:26px 28px;display:flex;flex-direction:column;gap:10px">'
    f'<p style="font-size:22px;font-weight:600;color:{ACC}">{p}</p>'
    f'<h3 style="{FONT};font-size:30px;font-weight:600;line-height:1.25">{t}</h3>'
    f'<p style="font-size:24px;line-height:1.35;color:{GREY}">{w}</p>'
    f'<div style="flex:1"></div><p style="font-size:24px;font-weight:600">[__]% of accounts · AED [__]m</p></div>'
    for p, t, w in acts)
(S / "p2-action.html").write_text(page(
    "p2-action", "The axes together", "Where the action is: six segments, six hypotheses",
    f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px">{cards}</div>',
    "The segments that are both sizeable and distinct in outcome, each with a treatment hypothesis for GRR to test, not a prescription. None of these customers simply forgot to pay. Those who have shown they can cure, can be reached and are credible are already paying something: they need a fast conversion, not a reminder. A sudden stop with some means points to an event, so a hardship plan. Reachable customers with means who do not keep promises need firm handling. Those we cannot reach need a route, tracing or an agency, chosen by the reason. Never-paid accounts start with a fraud and identity check. At 180+, customers with a positive signal are lifted out of the pool for an in-house attempt.",
    footer="Hypotheses for the GRR workshop, to be tested in the pilot"))

# 4 risk score
srows = ["Can cure · Reachable · Credible", "Stopped suddenly · Reachable", "Reachable · Not credible", "Not reachable", "Never paid", "180+ pool"]
trs = "".join(f'<tr><td>{r}</td><td style="text-align:right">[__]%</td><td style="text-align:right">[__] pts</td><td style="text-align:right">[__]</td></tr>' for r in srows)
score = (f'<div style="display:grid;grid-template-columns:560px 1fr;gap:56px">'
         f'<div style="display:flex;flex-direction:column;gap:20px">'
         f'<p style="font-size:30px;line-height:1.4;font-weight:600">A score earns its place only where outcomes still vary inside a segment.</p>'
         f'<p style="font-size:26px;line-height:1.45;color:{GREY}">For each segment we measure how far 3-month outcomes still spread across customers, and whether a score would rank them better than the DPD band alone.</p>'
         f'<div style="background:#EEF1F8;border-radius:12px;padding:20px 24px"><p style="font-size:26px;line-height:1.4">Where it does, the score ranks customers <b>within</b> the segment. It does not replace the segment.</p></div></div>'
         f'<div style="display:flex;flex-direction:column;gap:12px"><table style="font-size:24px;color:{NAVY}">'
         f'<tr><th style="width:46%;text-align:left">Segment</th><th style="width:16%;text-align:right">Size</th><th style="width:20%;text-align:right">Outcome spread</th><th style="width:18%;text-align:right">Score adds value?</th></tr>{trs}</table></div></div>')
(S / "p2-score.html").write_text(page(
    "p2-score", "The axes together", "Is a risk score still needed?", score,
    "The original risk model predicted cure and roll well but gave no segmentation. Now that the segments exist, the question is narrower: inside each segment, do outcomes still vary enough that ranking customers would change what we do? For each segment we look at the spread of three-month outcomes and whether a score ranks customers better than the DPD band alone. Where it does, a score ranks within that segment; where it does not, the segment is enough. The 180+ pool is the most likely place a score adds value."))

# 5 UC1
sig = ["Stated intent to pay", "Change in income or job", "Hardship reason", "Dispute", "Promise made on the call", "Third-party contact"]
pills = "".join(f'<p style="font-size:24px;font-weight:600;background:#EEF1F8;border-radius:8px;padding:10px 16px">{x}</p>' for x in sig)
step = lambda n, t, s, hi=False: (f'<div style="display:flex;align-items:center;gap:16px;background:{"#EEF1F8" if hi else CARD};border-radius:12px;padding:16px 20px">'
                                  f'<div style="width:48px;height:48px;border-radius:24px;background:{NAVY};flex:none;display:flex;align-items:center;justify-content:center"><p style="font-size:24px;font-weight:600;line-height:1;color:#FFFFFF">{n}</p></div>'
                                  f'<div style="display:flex;flex-direction:column"><p style="font-size:26px;font-weight:600">{t}</p><p style="font-size:22px;color:{GREY}">{s}</p></div></div>')
uc1 = (f'<div style="display:grid;grid-template-columns:640px 1fr;gap:56px">'
       f'<div style="display:flex;flex-direction:column;gap:14px">'
       + step(1, "How did they get here?", "A1 · Deterioration")
       + step(2, "Can we talk to them?", "A2 · Locatability")
       + step(3, "What can we offer?", "A3 Credibility · A4 Ability · <span style=\"color:#2765FF\">UC1 Conversations</span>", True)
       + f'</div><div style="display:flex;flex-direction:column;gap:20px">'
       f'<p style="font-size:26px;font-weight:600">What transcripts can add to the nuance</p>'
       f'<div style="display:flex;flex-wrap:wrap;gap:12px">{pills}</div>'
       + stat("[__]%", "of accounts at 61–180 had a conversation in the last 3 months: where UC1 can add evidence")
       + '</div></div>'
       f'<div style="border-left:8px solid {ACC};padding:6px 0 6px 28px"><p style="font-size:28px;line-height:1.4"><b>Next:</b> a joint UC1 + UC2 workshop with GRR to define the final personas and the decision each supports.</p></div>')
(S / "p2-uc1.html").write_text(page(
    "p2-uc1", "The axes together", "Where UC1 comes in", uc1,
    "The transcript work, UC1, joins in the nuance step, next to credibility and ability. It only applies where a conversation took place, which is exactly the reachable population that passes the gate. Transcripts add what the data cannot: what the customer said about their intent, their income, hardship, disputes and promises. The next step is a joint workshop with GRR to turn UC1 and UC2 together into the final personas and the decision each one supports.", gap=30))

# 6 pilot
col = lambda t, items: (f'<div style="background:{CARD};border-radius:14px;padding:28px 30px;display:flex;flex-direction:column;gap:14px">'
                        f'<h3 style="{FONT};font-size:34px;font-weight:600">{t}</h3>'
                        + "".join(f'<div style="border-left:4px solid {ACC};padding:2px 0 2px 14px"><p style="font-size:24px;line-height:1.35">{i}</p></div>' for i in items) + '</div>')
pilot = (f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px">'
         + col("Design", ["Champion / challenger on 2–3 segments", "Persona-led allocation vs business as usual", "Random split within each segment", "3 months"])
         + col("Measure", ["Cure and roll rate", "Amount collected / exposure", "Promises kept and contact rate", "Cost per AED collected", "180+: recovery of the flagged group vs the rest"])
         + col("Guardrails", ["Same policy limits and compliance rules", "Minimum sample per arm: [__]", "Monthly readout", "Stop rule if worse than business as usual"])
         + '</div>')
(S / "p2-pilot.html").write_text(page(
    "p2-pilot", "The axes together", "Pilot and measure", pilot,
    "How we prove it works. A champion and challenger test on two or three segments: within each segment, customers are split at random between persona-led allocation and business as usual, for three months. We measure cure and roll rates, the amount collected against exposure, promises kept, contact rate and cost per dirham collected; at 180+, the recovery of the flagged group against the rest. The same policy limits apply to both arms, with a monthly readout and a stop rule."))

# 7 next steps
steps7 = [("Persona table in production", "all four axes, monthly"), ("Segment workshop with GRR", "UC1 + UC2 together"),
          ("Pilot design", "segments, arms, metrics"), ("Pilot", "3 months"), ("Readout", "scale up; decide on a risk score")]
tl = "".join(
    f'<div style="display:flex;flex-direction:column;gap:14px">'
    f'<div style="display:flex;align-items:center;gap:12px"><div style="width:56px;height:56px;border-radius:28px;background:{NAVY};flex:none;display:flex;align-items:center;justify-content:center"><p style="font-size:26px;font-weight:600;line-height:1;color:#FFFFFF">{i}</p></div>'
    f'<div style="flex:1;height:3px;background:{LINE if i < 5 else "#FFFFFF"}"></div></div>'
    f'<h3 style="{FONT};font-size:30px;font-weight:600;line-height:1.2">{t}</h3><p style="font-size:24px;color:{GREY}">{s}</p>'
    f'<div style="background:{CARD};border-radius:10px;padding:12px 16px;display:flex;flex-direction:column;gap:4px"><p style="font-size:22px;color:{GREY}">Owner: [__]</p><p style="font-size:22px;color:{GREY}">Date: [__]</p></div></div>'
    for i, (t, s) in enumerate(steps7, 1))
(S / "roadmap.html").write_text(page(
    "roadmap", "Next steps", "From framework to pilot",
    f'<div style="display:grid;grid-template-columns:repeat(5, 1fr);gap:24px">{tl}</div>',
    "Five steps from here. Put the persona table into production for all four axes, monthly. Workshop the segments with GRR, bringing UC1 and UC2 together. Design the pilot: which segments, the arms and the metrics. Run it for three months. Read it out, decide whether to scale, and decide where a risk score is still needed."))

# divider
(S / "div-combined.html").write_text(
    f'<section id="div-combined" data-transition="fade" style="background:{NAVY};color:#FFFFFF;{FONT};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:32px">\n'
    f'<p style="font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#8FAFFF">Part 2</p>\n'
    f'<h2 style="{FONT};font-size:96px;font-weight:600;line-height:1.05">The axes together</h2>\n'
    f'<p style="font-size:36px;line-height:1.4;color:#C9D2E3">Which combinations fire · Risk score · UC1 · Pilot</p>\n'
    f'<aside>The four axes combined: which combinations actually occur, where the action is, whether a risk score is still needed, where the transcript work fits, and how we pilot and measure it.</aside>\n</section>\n')
print("ok")
