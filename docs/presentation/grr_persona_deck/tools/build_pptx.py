"""Build an editable PPTX from the extracted slide layout (layout.json)."""
import html
import json
import re
import sys

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

SCR = "/private/tmp/claude-501/-Users-vajdbal-Python-Collections/a3a6130c-eea4-43cd-8925-fb47aef93568/scratchpad"
D = f"{SCR}/deck/project"
E = 6350  # EMU per px (1920 px = 13.333 in)
OUT = sys.argv[1]

layout = json.load(open(f"{SCR}/layout.json"))
order = json.load(open(f"{D}/deck.json"))["order"]
prs = Presentation()
prs.slide_width, prs.slide_height = Emu(1920 * E), Emu(1080 * E)
blank = prs.slide_layouts[6]


def rgb(c):
    return RGBColor(*c[:3])


def blend(c, bg=(255, 255, 255)):
    a = c[3] if len(c) > 3 else 1
    return [round(c[i] * a + bg[i] * (1 - a)) for i in range(3)]


def font_name(wt):
    if wt >= 700:
        return "Plus Jakarta Sans", True
    if wt >= 600:
        return "Plus Jakarta Sans SemiBold", False
    if wt >= 500:
        return "Plus Jakarta Sans Medium", False
    return "Plus Jakarta Sans", False


def add_box(sl, it):
    x, y, w, h = it["x"], it["y"], it["w"], it["h"]
    sides = it["sides"]
    vis = [s[0] > 0 and s[1] != "none" and s[2] is not None for s in sides]
    full = all(vis) and len({(s[0], s[1], tuple(s[2])) for s in sides}) == 1
    rad = min(it["rad"], min(w, h) / 2)
    if it["bg"] or full:
        shp = sl.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE if rad > 0.5 else MSO_SHAPE.RECTANGLE,
            Emu(round(x * E)), Emu(round(y * E)), Emu(round(w * E)), Emu(round(h * E)))
        if rad > 0.5:
            shp.adjustments[0] = rad / min(w, h)
        if it["bg"]:
            shp.fill.solid()
            shp.fill.fore_color.rgb = rgb(blend(it["bg"]))
        else:
            shp.fill.background()
        if full:
            bw, bs, bc = sides[0]
            shp.line.color.rgb = rgb(blend(bc))
            shp.line.width = Emu(round(bw * E))
            if bs == "dashed":
                shp.line.dash_style = MSO_LINE.DASH
            elif bs == "dotted":
                shp.line.dash_style = MSO_LINE.ROUND_DOT
        else:
            shp.line.fill.background()
        shp.shadow.inherit = False
        shp.text_frame.text = ""
    if not full:
        for i, (bw, bs, bc) in enumerate(sides):
            if not vis[i]:
                continue
            rx, ry, rw, rh = {0: (x, y, w, bw), 1: (x + w - bw, y, bw, h),
                              2: (x, y + h - bw, w, bw), 3: (x, y, bw, h)}[i]
            ln = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(round(rx * E)), Emu(round(ry * E)),
                                     Emu(max(1, round(rw * E))), Emu(max(1, round(rh * E))))
            ln.fill.solid()
            ln.fill.fore_color.rgb = rgb(blend(bc))
            ln.line.fill.background()
            ln.shadow.inherit = False


def add_wedge(sl, it):
    x, y = it["x"], it["y"]
    pts = [(136, 0), (136, 250)]
    for k in range(1, 21):  # quadratic from (136,250) via (104,64) to (0,0)
        t = k / 20
        px_ = (1 - t) ** 2 * 136 + 2 * (1 - t) * t * 104
        py_ = (1 - t) ** 2 * 250 + 2 * (1 - t) * t * 64
        pts.append((px_, py_))
    fb = sl.shapes.build_freeform(round(x * E), round(y * E), scale=E)
    fb.add_line_segments([(p[0], p[1]) for p in pts], close=True)
    shp = fb.convert_to_shape(round(x * E), round(y * E))
    shp.fill.solid()
    shp.fill.fore_color.rgb = RGBColor(0x07, 0x24, 0x47)
    shp.line.fill.background()
    shp.shadow.inherit = False


def add_text(sl, it, bgc):
    runs = it["runs"]
    paras, cur = [], []
    for r in runs:
        if r.get("br"):
            paras.append(cur)
            cur = []
        else:
            cur.append(dict(r))
    paras.append(cur)
    # collapse whitespace across runs, trim paragraph ends
    for p in paras:
        prev_space = True
        for r in p:
            t = r["t"]
            if prev_space:
                t = t.lstrip(" ")
            r["t"] = t
            if t:
                prev_space = t.endswith(" ")
        for r in reversed(p):
            r["t"] = r["t"].rstrip(" ")
            if r["t"]:
                break
    single = it["lines"] <= 1
    x, y, w, h = it["x"], it["y"], it["w"], it["h"]
    if single and it.get("tr"):
        tr = it["tr"]
        # keep the element box for alignment, but use the real text line for the vertical position
        y, h = tr["y"], tr["h"]
    slack = 0 if single else max(6, w * 0.03)
    if it["align"] in ("center",):
        x -= slack / 2
    elif it["align"] in ("right", "end"):
        x -= slack
    tb = sl.shapes.add_textbox(Emu(round(x * E)), Emu(round(y * E)), Emu(round((w + slack) * E)), Emu(round(h * E)))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = not single
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = MSO_ANCHOR.TOP if not single else MSO_ANCHOR.MIDDLE
    al = {"center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT, "end": PP_ALIGN.RIGHT}.get(it["align"], PP_ALIGN.LEFT)
    for pi, p in enumerate(paras):
        para = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
        para.alignment = al
        para.line_spacing = Pt(it["lh"] * 0.5)
        para.space_before = para.space_after = Pt(0)
        for r in p:
            if not r["t"]:
                continue
            run = para.add_run()
            run.text = r["t"]
            f = run.font
            name, bold = font_name(r["wt"])
            f.name = name
            f.bold = bold
            f.italic = r["it"]
            f.size = Pt(round(r["size"] * 0.5 * 2) / 2)
            if r["color"]:
                f.color.rgb = rgb(blend(r["color"], bgc))
            rpr = run._r.get_or_add_rPr()
            if r["ls"]:
                rpr.set("spc", str(round(r["ls"] * 0.5 * 100)))
            if r["strike"]:
                rpr.set("strike", "sngStrike")


for si, (S, sid) in enumerate(zip(layout, order), 1):
    assert S["id"] == sid, (S["id"], sid)
    sl = prs.slides.add_slide(blank)
    bgc = tuple(blend(S["bg"])) if S["bg"] else (255, 255, 255)
    if "gradient" in (S["bgimg"] or ""):
        cols = [tuple(int(v) for v in m) for m in re.findall(r"rgb\((\d+), (\d+), (\d+)\)", S["bgimg"])]
        fill = sl.background.fill
        fill.gradient()
        fill.gradient_angle = 30
        stops = fill.gradient_stops
        stops[0].color.rgb = RGBColor(*cols[0])
        stops[0].position = 0
        stops[1].color.rgb = RGBColor(*cols[-1])
        stops[1].position = 1.0
        bgc = cols[1] if len(cols) > 2 else cols[0]
    elif S["bg"]:
        sl.background.fill.solid()
        sl.background.fill.fore_color.rgb = rgb(bgc)
    for it in S["items"]:
        if it["k"] == "box":
            add_box(sl, it)
        elif it["k"] == "svg":
            if it["wedge"]:
                add_wedge(sl, it)
            else:
                im = Image.open(f"{SCR}/pptx_png/s{si:02d}.png")
                crop = im.crop((round(it["x"] * 2), round(it["y"] * 2), round((it["x"] + it["w"]) * 2), round((it["y"] + it["h"]) * 2)))
                fn = f"{SCR}/pptx_png/chart_{si:02d}.png"
                crop.save(fn)
                sl.shapes.add_picture(fn, Emu(round(it["x"] * E)), Emu(round(it["y"] * E)), Emu(round(it["w"] * E)), Emu(round(it["h"] * E)))
        elif it["k"] == "text":
            add_text(sl, it, bgc)
    m = re.search(r"<aside>(.*?)</aside>", open(f"{D}/slides/{sid}.html").read(), re.S)
    if m:
        sl.notes_slide.notes_text_frame.text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1)))).strip()

for sl in prs.slides:
    for shp in sl.shapes:
        st = shp._element.find(qn("p:style"))
        if st is not None:
            shp._element.remove(st)
prs.core_properties.title = "Synthesized Features"
prs.save(OUT)
print("saved", OUT, len(prs.slides))
