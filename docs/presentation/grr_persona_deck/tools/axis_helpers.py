"""Generate the four axis slides on one shared template."""
import sys
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
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


