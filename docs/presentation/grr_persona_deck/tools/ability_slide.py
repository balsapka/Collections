"""Ability slide (deck A4, in progress): R3 evidence families + bureau dependency."""
import sys
from pathlib import Path

NAVY, BLUE, GREY = "#072447", "#2765FF", "#4C515A"
GREEN, AMBER, RED, AMBER_BG = "#2E8B57", "#E0A526", "#C0392B", "#FBF1DA"
H = "font-family:'Plus Jakarta Sans', Arial, sans-serif"
STEPS = ["How they got here", "Can we talk to them", "What we can offer"]


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


def family(name, strong):
    return (f'<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-radius:10px;padding:16px 20px;display:flex;flex-direction:column;gap:6px">'
            f'<p style="font-size:24px;font-weight:600">{name}</p><p style="font-size:20px;line-height:1.3;color:#4C515A;white-space:nowrap">{strong}</p></div>')


def band(name, rule, bg, fg):
    return (f'<div style="flex:1;background:{bg};padding:14px 18px;display:flex;flex-direction:column;gap:2px">'
            f'<p style="font-size:24px;font-weight:600;color:{fg}">{name}</p><p style="font-size:20px;color:{fg}">{rule}</p></div>')


def mix_row(name):
    return (f'<div style="display:flex;align-items:center;gap:16px"><p style="font-size:22px;width:170px">{name}</p>'
            f'<div style="flex:1;height:36px;border:2px dashed #D9D9D6;border-radius:6px"></div>'
            f'<p style="font-size:22px;font-weight:600;width:60px">[__]</p></div>')


def mix_table():
    def head(t, bg, fg, dashed=False):
        st = f"border:2px dashed #9295A0;color:{GREY}" if dashed else f"background:{bg};color:{fg}"
        return f'<div style="{st};border-radius:8px;padding:8px 0;display:flex;justify-content:center"><p style="font-size:22px;font-weight:600">{t}</p></div>'
    cell = '<div style="background:#F3F3F1;border:1px solid #E6E6E3;border-radius:8px;height:56px;display:flex;align-items:center;justify-content:center"><p style="font-size:26px;font-weight:600">[__]%</p></div>'
    rows = "".join(f'<div style="display:flex;align-items:center"><p style="font-size:22px;font-weight:600">{r}</p></div>' + cell * 4
                   for r in ["Cards 61–180", "Loans 61–180", "Cards 180+", "Loans 180+"])
    return ('<div style="display:grid;grid-template-columns:170px 1fr 1fr 1fr 1fr;gap:8px">'
            + '<p style="font-size:22px"></p>' + head("High", GREEN, "#FFFFFF") + head("Moderate", AMBER, NAVY)
            + head("Low", RED, "#FFFFFF") + head("Unknown", "", "", True) + rows + '</div>')


families = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">'
            + family("Income", "Regular salary, ours or bureau")
            + family("Money in", "Money arriving or held, not salary")
            + family("Spending", "The customer's own spending")
            + family("Other products", "Activity on their other products")
            + '</div>')
strip = (f'<div style="display:flex;align-items:stretch;gap:12px">'
         f'<div style="flex:3;display:flex;border-radius:10px;overflow:hidden">'
         + band("High", "2+ strong", GREEN, "#FFFFFF")
         + band("Moderate", "1 strong", AMBER, NAVY)
         + band("Low", "some evidence, none strong", RED, "#FFFFFF")
         + '</div>'
         f'<div style="flex:1;border:2px dashed #9295A0;border-radius:10px;padding:12px 16px;display:flex;flex-direction:column;gap:2px">'
         f'<p style="font-size:24px;font-weight:600;color:{GREY}">Unknown</p><p style="font-size:20px;color:{GREY}">no evidence</p></div></div>')
how = (label("How a customer gets a label")
       + f'<p style="font-size:22px;color:#4C515A">Four evidence families; we count how many are strong*</p>'
       + families
       + strip
       + f'<p style="font-size:22px;line-height:1.4;color:#4C515A;border-left:6px solid #D9D9D6;padding:6px 14px">A cheque bounce or returned direct debit → <b>one band down</b></p>')

mix = (label("August mix")
       + mix_table()
       + f'<div style="background:{AMBER_BG};border-left:8px solid {AMBER};border-radius:12px;padding:20px 26px;display:flex;flex-direction:column;gap:8px">'
       f'<p style="font-size:24px;font-weight:600">Needs: GRR\'s bureau salary feed</p>'
       f'<p style="font-size:22px;line-height:1.4;color:#4C515A">About a third of customers have no CASA with us, and half never had a salary credit here. Without a regular bureau salary feed they stay Unknown; with it, income becomes visible across the book.</p></div>')

def insight(big, text):
    return (f'<div style="display:flex;align-items:center;gap:28px;background:#F3F3F1;border:1px solid #E6E6E3;border-radius:12px;padding:20px 32px">'
            f'<div style="flex:none;min-width:max-content"><p style="{H};font-size:56px;font-weight:600;color:{BLUE};white-space:nowrap">{big}</p></div>'
            f'<div style="flex:1"><p style="font-size:24px;line-height:1.35">{text}</p></div></div>')


insights = ('<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px">'
            + insight("[__]%", "of card customers at 61–180 show no evidence of their money yet.")
            + insight("[__]%", "of loan accounts at 180+ show the means to pay: a positive signal.")
            + '</div>')

html = f'''<section id="a1" data-transition="fade" style="background:#FFFFFF;color:{NAVY};font-family:'Plus Jakarta Sans', Arial, sans-serif;padding:96px 128px 140px;display:flex;flex-direction:column;gap:30px">
<div style="display:flex;flex-direction:column;gap:14px">
<div style="display:flex;align-items:center;justify-content:space-between">
<div style="display:flex;align-items:center;gap:20px"><p style="font-size:24px;letter-spacing:3px;text-transform:uppercase;color:{BLUE};font-weight:600">A4 · Ability</p><p style="font-size:18px;font-weight:600;letter-spacing:2px;text-transform:uppercase;padding:6px 14px;border-radius:999px;background:{AMBER};color:{NAVY}">In progress</p></div>
{steps(3)}
</div>
<h2 style="{H};font-size:50px;font-weight:600;line-height:1.1">Ability tells us what a customer can realistically be offered</h2>
</div>
<div style="display:grid;grid-template-columns:900px 1fr;gap:64px;flex:1">
<div style="display:flex;flex-direction:column;gap:14px">{how}</div>
<div style="display:flex;flex-direction:column;gap:16px">{mix}</div>
</div>
{insights}
<p style="position:absolute;left:128px;bottom:56px;width:1664px;font-size:22px;color:#4C515A">* Strong = regular and above the floor in at least 2 of the last 3 months (floor: AED 3,000 or twice the amount due); at 180+: 3 of the last 6 months</p>
<aside>Ability is work in progress. The approach: four families of evidence, income, other money arriving or held (a balance that survives the sweep counts), the customer's own spending, and activity on their other products. We count how many are strong: two or more is High, one is Moderate, some evidence but nothing strong is Low, and no evidence at all is Unknown. A bounced cheque or returned direct debit moves the customer one band down. The axis depends on one thing we do not control: about a third of customers have no current or savings account with us and half never had a salary credit here, so without GRR's bureau salary feed many stay Unknown. At 180+, Moderate or High ability counts as a positive signal.</aside>
</section>
'''
Path(sys.argv[1]).write_text(html)
print("ok")
