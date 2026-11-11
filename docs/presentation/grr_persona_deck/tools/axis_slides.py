"""Generate the four axis slides on one shared template."""
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
NAVY, BLUE, MID, LOW, UNK, GREY = "#072447", "#2765FF", "#6FA3D6", "#4C515A", "#C9D3DF", "#4C515A"
H = "font-family:'Plus Jakarta Sans', Arial, sans-serif"
STEPS = ["How they got here", "Can we talk to them", "What we can offer"]


def steps(active):
    out = []
    for i, name in enumerate(STEPS, 1):
        on = i == active
        circ = (f"background:{NAVY}" if on
                else "border:2px solid #D9D9D6")
        out.append(
            f'<div style="display:flex;align-items:center;gap:10px">'
            f'<div style="width:40px;height:40px;border-radius:20px;{circ};display:flex;align-items:center;justify-content:center">'
            f'<p style="font-size:20px;font-weight:600;line-height:1;color:{"#FFFFFF" if on else "#9295A0"}">{i}</p></div>'
            f'<p style="font-size:20px;font-weight:{600 if on else 400};color:{NAVY if on else "#9295A0"}">{name}</p></div>')
        if i < 3:
            out.append('<div style="width:28px;height:2px;background:#D9D9D6"></div>')
    return f'<div style="display:flex;align-items:center;gap:12px">{"".join(out)}</div>'


def tag(kind):
    text = "States · decided by rules" if kind == "states" else "Score · points → band"
    return (f'<p style="font-size:18px;font-weight:600;letter-spacing:2px;text-transform:uppercase;'
            f'padding:6px 14px;border-radius:999px;border:2px solid {BLUE};color:{BLUE}">{text}</p>')


def label(text):
    return (f'<p style="font-size:20px;letter-spacing:2px;text-transform:uppercase;color:{GREY};'
            f'font-weight:600">{text}</p>')


def chip(text, sub=None, unknown=False, width=None):
    w = f"width:{width}px;" if width else ""
    if unknown:
        style = f"border:2px dashed #9295A0;padding:6px 14px"
        color = GREY
    else:
        style = f"background:#EEF1F8;padding:8px 16px"
        color = NAVY
    if sub is None:
        return f'<p style="{w}font-size:22px;font-weight:600;border-radius:8px;white-space:nowrap;color:{color};{style}">{text}</p>'
    return (f'<div style="{w}border-radius:8px;{style};display:flex;flex-direction:column">'
            f'<p style="font-size:22px;font-weight:600;white-space:nowrap;color:{color}">{text}</p>'
            f'<p style="font-size:18px;color:{GREY}">{sub}</p></div>')


def stacked(title, segs):
    bar = "".join(
        f'<div style="width:{p}%;background:{c};height:44px"></div>' for _, p, c in segs)
    legend = "".join(
        f'<div style="display:flex;align-items:center;gap:8px"><div style="width:16px;height:16px;'
        f'background:{c};border-radius:3px"></div><p style="font-size:20px">{n} <b>{p:g}%</b></p></div>'
        for n, p, c in segs)
    return (f'<div style="display:flex;flex-direction:column;gap:10px"><p style="font-size:22px;font-weight:600">{title}</p>'
            f'<div style="display:flex;width:100%;border-radius:6px;overflow:hidden">{bar}</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:8px 20px">{legend}</div></div>')


def hbars(title, rows, scale):
    out = [f'<p style="font-size:22px;font-weight:600">{title}</p>']
    for n, p in rows:
        val = f"{p:g}%" if isinstance(p, (int, float)) else p
        width = int(p * scale) if isinstance(p, (int, float)) else 0
        out.append(
            f'<div style="display:flex;align-items:center;gap:14px"><p style="font-size:22px;width:170px">{n}</p>'
            f'<div style="width:{width}px;height:34px;background:{BLUE};border-radius:4px"></div>'
            f'<p style="font-size:22px;font-weight:600">{val}</p></div>')
    return f'<div style="display:flex;flex-direction:column;gap:12px">{"".join(out)}</div>'


def insight(big, text):
    return (f'<div style="display:flex;align-items:center;gap:28px;background:#F3F3F1;border:1px solid #E6E6E3;'
            f'border-radius:12px;padding:24px 32px"><div style="flex:none;min-width:max-content"><p style="{H};font-size:60px;font-weight:600;color:{BLUE};'
            f'white-space:nowrap">{big}</p></div><div style="flex:1"><p style="font-size:25px;line-height:1.35">{text}</p></div></div>')


def scorecard(rows, bands, extra):
    out = []
    for name, sub, chips in rows:
        cs = "".join(chip(c) for c in chips)
        out.append(
            f'<div style="display:flex;align-items:center;gap:16px"><div style="width:300px"><p style="font-size:24px;'
            f'font-weight:600">{name}</p><p style="font-size:18px;color:{GREY}">{sub}</p></div>'
            f'<div style="display:flex;gap:8px">{cs}</div></div>')
    band = "".join(
        f'<div style="flex:{f};background:{c};padding:10px 14px"><p style="font-size:22px;font-weight:600;'
        f'color:#FFFFFF">{n}</p><p style="font-size:18px;color:#FFFFFF">{pts}</p></div>' for n, pts, f, c in bands)
    out.append(
        f'<div style="display:flex;align-items:center;gap:16px;margin-top:6px"><p style="width:300px;font-size:24px;'
        f'font-weight:600">Total points →</p><div style="display:flex;flex:1;border-radius:8px;overflow:hidden">{band}</div></div>')
    out.extend(extra)
    return f'<div style="display:flex;flex-direction:column;gap:14px">{"".join(out)}</div>'


def note(text, unknown=False):
    border = "border:2px dashed #9295A0" if unknown else "border-left:6px solid #D9D9D6"
    return f'<p style="font-size:22px;line-height:1.4;color:#4C515A;{border};padding:8px 14px;border-radius:6px">{text}</p>'


def slide(sid, eyebrow, kind, step, headline, how, mix, insights, footer, notes):
    return f'''<section id="{sid}" data-transition="fade" style="background:#FFFFFF;color:{NAVY};font-family:'Plus Jakarta Sans', Arial, sans-serif;padding:96px 128px 140px;display:flex;flex-direction:column;gap:32px">
<div style="display:flex;flex-direction:column;gap:14px">
<div style="display:flex;align-items:center;justify-content:space-between">
<div style="display:flex;align-items:center;gap:20px"><p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{BLUE};font-weight:600">{eyebrow}</p>{tag(kind)}</div>
{steps(step)}
</div>
<h2 style="{H};font-size:50px;font-weight:600;line-height:1.1">{headline}</h2>
</div>
<div style="display:grid;grid-template-columns:980px 1fr;gap:64px;flex:1">
<div style="display:flex;flex-direction:column;gap:16px">{label("How a customer gets a label")}{how}</div>
<div style="display:flex;flex-direction:column;gap:24px">{label("August mix")}{mix}</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px">{"".join(insight(*i) for i in insights)}</div>
<p style="position:absolute;left:128px;bottom:56px;width:1664px;font-size:22px;color:{GREY}">{footer}</p>
<aside>{notes}</aside>
</section>
'''


# ---- A4 ------------------------------------------------------------------
ladder = [
    ("Bad from the start: nothing paid since, within 3 months of opening?", "Early payment default", "never settled"),
    ("Holding at one level for most of the last 6 months?", "Stabilized", "partial payer"),
    ("Back in arrears within 12 months of curing?", "Repeat delinquent", "recurring"),
    ("Current to 61+ in 3 months, after a year of good history?", "Seasoned straight roller", "sudden stop"),
    ("Current to 61+ in 3 months, within the first year?", "Early-life straight roller", "never settled"),
    ("Otherwise: fell slowly, paying on the way", "Slow roller", "partial payer"),
]
rows = "".join(
    f'<div style="display:flex;align-items:center;gap:14px"><div style="width:34px;height:34px;border-radius:17px;flex:none;'
    f'background:{NAVY};display:flex;align-items:center;justify-content:center"><p style="font-size:18px;font-weight:600;line-height:1;color:#FFFFFF">{i}</p></div>'
    f'<p style="font-size:22px;width:590px;line-height:1.25">{q}</p><p style="font-size:26px;color:{BLUE}">→</p>{chip(s, g, width=290)}</div>'
    for i, (q, s, g) in enumerate(ladder, 1))
a4_how = (f'<p style="font-size:22px;color:#4C515A">Read from the monthly DPD path only. Asked in order; the first “yes” decides.</p>'
          f'<div style="display:flex;flex-direction:column;gap:8px">{rows}</div>'
          + note("History not visible (cropped, or a restructured loan we cannot link) → <b>Unknown</b>", True))
a4_mix = (hbars("Loans 61–180 · by journey group", [("Never settled", 23.3), ("Sudden stop", 33.9),
                                                     ("Partial payer", 33.7), ("Recurring", 9.1)], 9)
          + '<p style="font-size:22px;color:#4C515A">Cards 61–180: [__] (from the persona table run)</p>')
OUT.joinpath("a4.html").write_text(slide(
    "a4", "A4 · Deterioration", "states", 1,
    "Half of delinquent loans rolled to 61+ without paying a month",
    a4_how, a4_mix,
    [("51%", "of loans at 61–180 are straight rollers: current to 61+ in three months, nothing paid on the way."),
     ("1 in 4", "went bad within the first year (early payment default or early-life roller): never settled.")],
    "Production, 31 Aug 2026 · retail loans 61–180, 3,985 accounts, restructured loans joined to their originals · cards: from the persona table",
    "Deterioration reads only the DPD path, so it covers every account, including those with no other data. "
    "Six questions asked in order, the first yes decides. The seven states group into four journeys: never settled, sudden stop, partial payer and recurring. "
    "For loans at 61 to 180, half are straight rollers: current to 61 plus in three months without paying. A quarter never settled: they went bad within their first year. "
    "Whatever the path, the next question is whether we can talk to them. Card figures come from the persona table run."))

# ---- A2 ------------------------------------------------------------------
def dim_box(title, q, lines, chips):
    cs = "".join(chip(c, unknown=(c == "Unknown")) for c in chips)
    ls = "".join(f'<p style="font-size:21px;line-height:1.35;color:#4C515A">{l}</p>' for l in lines)
    return (f'<div style="flex:1;background:#F3F3F1;border:1px solid #E6E6E3;border-radius:12px;padding:22px;display:flex;'
            f'flex-direction:column;gap:12px"><p style="font-size:24px;font-weight:600">{title}</p>'
            f'<p style="font-size:21px;color:{BLUE};font-weight:600">{q}</p>{ls}<div style="display:flex;gap:8px;flex-wrap:wrap">{cs}</div></div>')


routes = "".join(chip(r, unknown=(r == "Unconfirmed")) for r in ["Deceased", "Abroad", "Gone dark", "Reachable", "Unconfirmed"])
a2_how = (
    f'<div style="display:flex;gap:20px">'
    + dim_box("Location", "Where were they last seen? Latest evidence wins.",
              ["Logins, in-person card use, departure notes.", "Online spend, transfers and salary don't count."],
              ["In Country", "Skip", "Unknown"])
    + dim_box("Reachability", "Did the last call days connect?",
              ["Last 3 call days failed, none since (6 at 180+) → Non-Reachable.", "A contact in the window → Reachable."],
              ["Reachable", "Non-Reachable", "Unknown"])
    + '</div>'
    + note("<b>Deceased</b> overrides both: collector note, card block or customer record.")
    + f'<div style="display:flex;align-items:center;gap:12px"><p style="font-size:22px;font-weight:600;white-space:nowrap">Route, first match →</p>{routes}</div>')
a2_mix = (stacked("Cards 61–180 · location", [("In Country", 24, BLUE), ("Skip", 44, LOW), ("Unknown", 32, UNK)])
          + stacked("Cards 61–180 · reachability", [("Reachable", 21, BLUE), ("Non-Reachable", 68, LOW), ("Unknown", 11, UNK)])
          + '<p style="font-size:22px;color:#4C515A">Loans 61–180: Skip 43% · Non-Reachable 58%</p>')
OUT.joinpath("a2.html").write_text(slide(
    "a2", "A2 · Locatability", "states", 2,
    "2 in 3 card customers no longer answer, and the share is growing",
    a2_how, a2_mix,
    [("2 in 3", "card customers at 61–180 failed their last three call days with no contact since."),
     ("+31% · −9%", "Jan → Aug: the book grew by 31% while reachable customers fell 9%, to about 4,000.")],
    "Production, 31 Aug 2026 · 19,292 cards, 3,985 loans · trend Jan–Aug 2026 · logic accepted by GRR 30 Oct 2026",
    "Locatability is the gate. Two rules: where did we last see the customer, using logins, in-person card use and departure notes, latest evidence wins; "
    "and did the last call days connect. Deceased overrides both. Together they give the route: deceased, abroad, gone dark, reachable or unconfirmed. "
    "In August two thirds of 61 to 180 cards failed their last three call days. From January to August the book grew from 14,700 to 19,300 while reachable customers fell from 4,400 to 4,000: "
    "all of the growth went to customers we cannot reach. Only the reachable go on to the nuance."))

# ---- A1 ------------------------------------------------------------------
bands = [("Low", "0–1", 2, LOW), ("Moderate", "2–3", 2, MID), ("High", "4", 1, BLUE)]
a1_how = scorecard(
    [("Income", "salary, ours or bureau, vs the amount due", ["None 0", "Weak 1", "Stable 2"]),
     ("Liquidity", "CASA balance, external card payments", ["None 0", "Weak 1", "Adequate 2"])],
    bands,
    [note("A cheque bounce or direct-debit return in the window → <b>one band down</b>"),
     note("No money movement we can see (no CASA with us, or a dormant one) → <b>Unknown</b>: missing data, not low ability", True),
     '<p style="font-size:20px;color:#4C515A">Window: the last 3 months (6 at 180+)</p>'])
a1_mix = (stacked("Cards 61–180", [("High", 0.2, BLUE), ("Moderate", 14.4, MID), ("Low", 28.9, LOW), ("Unknown", 56.6, UNK)])
          + '<p style="font-size:22px;color:#4C515A">Loans 61–180: Unknown 46%</p>')
OUT.joinpath("a1.html").write_text(slide(
    "a1", "A1 · Ability", "score", 3,
    "Where we can see capacity, customers cure four times as often",
    a1_how, a1_mix,
    [("4×", "High cured within 3 months at 33.6%, Unknown at 7.9% (cards 61–180)."),
     ("57%", "of cards at 61–180 are Unknown: we cannot see their money. The bureau salary feed is the fix.")],
    "Mix: production 31 Aug 2026, 19,292 cards · cure: 2026 month ends, earlier rule version, High = 161 accounts (refresh from the persona back-test)",
    "Ability is a score. Income and liquidity each earn zero to two points against a floor of AED 3,000 or twice the amount due; four points is High, two or three Moderate, below two Low. "
    "A bounced cheque or returned direct debit moves the customer one band down. When we cannot see any of the customer's money, the state is Unknown: that is missing data, not low ability. "
    "Where we see capacity it matters: High cures four times as often as Unknown. The limit is coverage: 57% of 61 to 180 cards are Unknown, mostly with no CASA with us. "
    "The bureau salary feed is the fix."))

# ---- A3 ------------------------------------------------------------------
bands3 = [("Low", "0–1", 2, LOW), ("Moderate", "2–3", 2, MID), ("High", "4+", 2, BLUE)]
a3_how = scorecard(
    [("Promises kept", "last 12 months, on GRR's deadline", ["Kept +2", "Partly +1", "Broken −1"]),
     ("Paying while delinquent", "recent months", ["2+ full dues +2", "Any payment +1"]),
     ("Record before", "12 months before delinquency", ["Paid as billed +1"])],
    bands3,
    [note("An explicit refusal to pay → <b>one band down</b>"),
     note("Delinquency episode not visible in the history → <b>Unknown</b>", True)])
a3_mix = (stacked("Cards 61–180", [("High", 2.3, BLUE), ("Moderate", 15.6, MID), ("Low or Unknown", 82.1, LOW)])
          + '<p style="font-size:22px;color:#4C515A">Loans 61–180: High 2.2% · Moderate 22.1%</p>')
OUT.joinpath("a3.html").write_text(slide(
    "a3", "A3 · Payment credibility", "score", 3,
    "Every point of credibility lowers the roll rate",
    a3_how, a3_mix,
    [("95% → 34%", "cards rolling to a worse bucket: zero points vs four or more."),
     ("82%", "made no concluded promise in 12 months: their track record is untested, not bad.")],
    "States 31 May 2026, outcomes to 31 Aug 2026, 60–180 DPD · roll by points: earlier rule version · mix: GRR deadline rules (bundle 20, being applied)",
    "Credibility is about this customer on this debt. Three sources earn points: promises kept in the last twelve months, judged on GRR's deadline; paying while delinquent; and the record before delinquency. "
    "Moderate from two points, High from four, both GRR decisions. An explicit refusal moves one band down. "
    "Back-tested: customers with zero points rolled 95% of the time, four or more points 34%. Most customers have no concluded promise yet, so their record is untested, not bad: "
    "this is where the transcript signals will add the most."))
print("ok")
