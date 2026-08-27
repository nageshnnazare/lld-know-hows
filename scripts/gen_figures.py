#!/usr/bin/env python3
"""Generate the guide's SVG figures, tuned to the htmler blue theme.

The kit's grey/purple house style is re-hued to htmler's blue-forward palette.
Because the figures are inlined as static base64 images (no page CSS reaches
them), every colour is chosen to work on BOTH the dark (#0b0d12) and light
(#ffffff) themes at once. The trick: a mid-slate around luminance ~0.2 gives
roughly 4.3:1 contrast three ways — white text sitting on the fill, and the
same colour used as ink on either background.

  * slate blue  #6B7B94  (neutral boxes, connectors, axes, labels)
  * blue        #3E7CC0  (highlighted / "after" boxes)         + dark #2F5F98
  * teal        #1F918C  (positive "result" accent)
  * amber       #D9922B  (warning / spill; dark text on fill)
  * red         #D65A5F  (problem callouts)
  * muted       #9AA0B4  (captions)
  * white       #FFFFFF  (text inside dark fills)
  * 1.5pt wide rules, Aptos / system sans font stack

Run:  python3 scripts/gen_figures.py
Output: <chapter>/figures/*.svg
"""
import base64
import io
import os
import re

# ── House-style constants (htmler blue theme, dual light/dark legible) ───────
GREY = "#6B7B94"
GREY_D = "#55637A"
PURPLE = "#3E7CC0"
PURPLE_D = "#2F5F98"
TEAL = "#1F918C"
AMBER = "#D9922B"
RED = "#D65A5F"
WHITE = "#FFFFFF"
LIGHT = "#9AA0B4"
INK_DARK = "#1F2433"  # text on light (amber) fills
# Hand-drawn Excalidraw look: Virgil is embedded per-figure (see _font_face);
# 'Segoe Print'/cursive are only fallbacks if the embed ever fails.
FONT = "'Virgil','Segoe Print','Comic Sans MS',cursive"
RULE = 1.5  # pt wide rules

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "fonts", "Virgil.woff2")
_FACE_CACHE = {}


def _font_face(text):
    """Return a <style> block embedding a Virgil subset for `text`.

    The figures are inlined as base64 <img> data URIs, and browsers do not
    fetch external fonts for <img>-loaded SVGs — so the hand-drawn font must
    travel *inside* each SVG. We subset to the glyphs actually used to keep
    each figure tiny (~8-14 KB)."""
    # Subset to exactly the glyphs this figure uses (plus a space) so each
    # embedded font stays as small as possible.
    key = "".join(sorted(set(text) | {" "}))
    if key in _FACE_CACHE:
        return _FACE_CACHE[key]
    try:
        from fontTools import subset as _subset
        opts = _subset.Options()
        opts.flavor = "woff2"
        opts.desubroutinize = True
        opts.ignore_missing_unicodes = True
        font = _subset.load_font(FONT_PATH, opts)
        ss = _subset.Subsetter(options=opts)
        ss.populate(text=key)
        ss.subset(font)
        buf = io.BytesIO()
        font.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        face = ("<style>@font-face{font-family:'Virgil';font-style:normal;"
                "font-weight:400;src:url(data:font/woff2;base64," + b64 +
                ") format('woff2');}</style>")
    except Exception as exc:  # pragma: no cover - fonttools optional
        print("  ! font embed skipped:", exc)
        face = ""
    _FACE_CACHE[key] = face
    return face


# ── Primitive builders ──────────────────────────────────────────────────────
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def defs():
    """Arrowhead markers in each ink colour."""
    marks = []
    for name, col in (("g", GREY), ("p", PURPLE), ("t", TEAL),
                      ("r", RED), ("a", AMBER), ("l", LIGHT)):
        marks.append(
            f'<marker id="ah-{name}" viewBox="0 0 10 10" refX="8.5" refY="5" '
            f'markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">'
            f'<path d="M0 0L10 5L0 10z" fill="{col}"/></marker>')
    return "<defs>" + "".join(marks) + "</defs>"


def rrect(x, y, w, h, fill, rx=9, stroke=None, sw=RULE, dash=None, opacity=None):
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
         f'fill="{fill}"')
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        s += f' stroke-dasharray="{dash}"'
    if opacity is not None:
        s += f' opacity="{opacity}"'
    return s + "/>"


def tspan_lines(x, cy, lines, fill, size, weight, lh):
    """Vertically centred multiline <text>."""
    n = len(lines)
    y0 = cy - (n - 1) * lh / 2.0
    out = [f'<text x="{x}" y="{y0}" fill="{fill}" font-family="{FONT}" '
           f'font-size="{size}" font-weight="{weight}" text-anchor="middle" '
           f'dominant-baseline="central">']
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else lh
        out.append(f'<tspan x="{x}" dy="{dy}">{esc(ln)}</tspan>')
    out.append("</text>")
    return "".join(out)


def box(x, y, w, h, lines, fill=GREY, tcol=WHITE, size=13, weight=600,
        rx=9, lh=16, stroke=None, sw=RULE, dash=None):
    if isinstance(lines, str):
        lines = [lines]
    r = rrect(x, y, w, h, fill, rx=rx, stroke=stroke, sw=sw, dash=dash)
    t = tspan_lines(x + w / 2.0, y + h / 2.0, lines, tcol, size, weight, lh)
    return r + t


def obox(x, y, w, h, lines, stroke=GREY, tcol=GREY, size=13, weight=600,
         rx=9, lh=16, sw=RULE, dash=None, fill="none"):
    """Outlined box (transparent fill) with coloured text."""
    r = rrect(x, y, w, h, fill, rx=rx, stroke=stroke, sw=sw, dash=dash)
    t = tspan_lines(x + w / 2.0, y + h / 2.0, lines if isinstance(lines, list)
                    else [lines], tcol, size, weight, lh)
    return r + t


def text(x, y, s, fill=GREY, size=13, weight=600, anchor="middle",
         italic=False, mono=False):
    fam = ("'SFMono-Regular',ui-monospace,'JetBrains Mono',Consolas,monospace"
           if mono else FONT)
    st = ""  # italics disabled: the hand-drawn font is hard to read slanted
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{fam}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"'
            f'{st} dominant-baseline="central">{esc(s)}</text>')


def line(x1, y1, x2, y2, col=GREY, sw=RULE, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" '
            f'stroke-width="{sw}"{d}/>')


def _mk(col):
    return {GREY: "g", PURPLE: "p", TEAL: "t", RED: "r", AMBER: "a",
            LIGHT: "l"}.get(col, "g")


def arrow(x1, y1, x2, y2, col=GREY, sw=RULE, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" '
            f'stroke-width="{sw}" marker-end="url(#ah-{_mk(col)})"{d}/>')


def path(d, col=GREY, sw=RULE, dash=None, arrow_end=False, fill="none"):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#ah-{_mk(col)})"' if arrow_end else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}"'
            f'{dd}{m}/>')


def cylinder(x, y, w, h, fill=GREY, tcol=WHITE, lines=None, size=12,
             stroke=None, sw=RULE):
    """Database / memory cylinder."""
    ry = min(h * 0.16, 14)
    st = (f' stroke="{stroke}" stroke-width="{sw}"') if stroke else ""
    body = (f'<path d="M{x} {y+ry} A{w/2} {ry} 0 0 0 {x+w} {y+ry} '
            f'L{x+w} {y+h-ry} A{w/2} {ry} 0 0 1 {x} {y+h-ry} Z" '
            f'fill="{fill}"{st}/>')
    top = (f'<ellipse cx="{x+w/2}" cy="{y+ry}" rx="{w/2}" ry="{ry}" '
           f'fill="{fill}"{st}/>')
    lip = (f'<path d="M{x} {y+ry} A{w/2} {ry} 0 0 0 {x+w} {y+ry}" '
           f'fill="none" stroke="{WHITE}" stroke-width="1" opacity="0.35"/>')
    t = ""
    if lines:
        t = tspan_lines(x + w / 2.0, y + h / 2.0 + ry / 2, lines, tcol, size,
                        600, 15)
    return body + top + lip + t


def svg(w, h, body, title=""):
    t = f"<title>{esc(title)}</title>" if title else ""
    used = "".join(re.findall(r'>([^<]*)<', body)) + title
    face = _font_face(used)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{FONT}">{face}{t}{defs()}'
            f'{body}</svg>\n')


def write(rel_path, content):
    full = os.path.join(REPO_ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print("wrote", rel_path, f"({len(content)} bytes)")


# ── Before/after "code card" primitives ─────────────────────────────────────
MONO = ("'SFMono-Regular',ui-monospace,'JetBrains Mono',Menlo,"
        "Consolas,monospace")
CARD_BG = "#232A35"          # self-contained dark code card (theme-independent)
CODE_FG = "#D7DCE6"
CODE_DIM = "#8892A5"
CODE_HI = "#7FC4FF"          # changed / highlighted line
CODE_GOOD = "#83CEA3"        # added
CODE_BAD = "#E98A90"         # removed
LBL_BEFORE = "#9AA0B4"
LBL_AFTER = "#7FC4FF"
PAD = 14
LH = 19
CSIZE = 12.5
CHARW = 7.55
LABEL_AREA = 28
BOTTOM = 12
_STYLE_COL = {"n": CODE_FG, "hi": CODE_HI, "dim": CODE_DIM,
              "good": CODE_GOOD, "bad": CODE_BAD}


def _txt(ln):
    return ln[0] if isinstance(ln, tuple) else ln


def card_size(lines, label, minw=0):
    maxlen = max([len(_txt(l)) for l in lines] + [len(label) + 2])
    w = max(minw, PAD * 2 + int(round(maxlen * CHARW)))
    h = LABEL_AREA + len(lines) * LH + BOTTOM
    return w, h


def code_card(x, y, lines, label, border, labelcol, minw=0):
    w, h = card_size(lines, label, minw)
    out = [rrect(x, y, w, h, CARD_BG, rx=11, stroke=border, sw=1.75)]
    out.append(f'<text x="{x+PAD}" y="{y+15}" fill="{labelcol}" '
               f'font-family="{FONT}" font-size="10.5" font-weight="700" '
               f'letter-spacing="1.2" text-anchor="start" '
               f'dominant-baseline="central">{esc(label)}</text>')
    cy = y + LABEL_AREA + LH / 2
    for ln in lines:
        txt, style = (ln if isinstance(ln, tuple) else (ln, "n"))
        out.append(
            f'<text x="{x+PAD}" y="{cy}" fill="{_STYLE_COL[style]}" '
            f'font-family="{MONO}" font-size="{CSIZE}" text-anchor="start" '
            f'dominant-baseline="central" '
            f'xml:space="preserve">{esc(txt)}</text>')
        cy += LH
    return "".join(out), w, h


def before_after(fname, title, before, after, op="", note_b="", note_a="",
                 blabel="BEFORE", alabel="AFTER", title2="", gap=104):
    wl, hl = card_size(before, blabel)
    wr, hr = card_size(after, alabel)
    top = 46 if not title2 else 62
    y0 = top
    maxh = max(hl, hr)
    xl = 24
    xr = xl + wl + gap
    W = xr + wr + 24
    note_h = 26 if (note_b or note_a) else 0
    H = top + maxh + note_h + 18
    b = [text(W / 2, 24, title, GREY, 15.5, 700)]
    if title2:
        b.append(text(W / 2, 44, title2, LIGHT, 11.5, 500, italic=True))
    cl, _, _ = code_card(xl, y0, before, blabel, GREY_D, LBL_BEFORE)
    cr, _, _ = code_card(xr, y0, after, alabel, PURPLE, LBL_AFTER)
    b.append(cl)
    b.append(cr)
    ay = y0 + maxh / 2
    b.append(arrow(xl + wl + 16, ay, xr - 12, ay, PURPLE, 2.0))
    if op:
        b.append(text((xl + wl + xr) / 2, ay - 13, op, PURPLE, 11, 700))
    if note_b:
        b.append(text(xl + wl / 2, y0 + maxh + 15, note_b, RED, 11, 600))
    if note_a:
        b.append(text(xr + wr / 2, y0 + maxh + 15, note_a, TEAL, 11, 600))
    write(fname, svg(W, H, "".join(b), title))


def rules_fig(fname, title, pairs, note="", lhs_hdr="", rhs_hdr=""):
    """A card of  lhs  →  rhs  rewrite rules (monospace)."""
    lw = max(len(l) for l, _ in pairs)
    rw = max(len(r) for _, r in pairs)
    x0, y0 = 24, 46
    lx = x0 + PAD
    arrow_x1 = lx + int(lw * CHARW) + 12
    arrow_x2 = arrow_x1 + 30
    rx = arrow_x2 + 12
    cardw = (rx + int(rw * CHARW) + PAD) - x0
    rows = len(pairs)
    hdr_h = 20 if (lhs_hdr or rhs_hdr) else 0
    cardh = LABEL_AREA + hdr_h + rows * LH + BOTTOM
    W = x0 + cardw + 24
    H = y0 + cardh + (24 if note else 12)
    b = [text(W / 2, 24, title, GREY, 15.5, 700)]
    b.append(rrect(x0, y0, cardw, cardh, CARD_BG, rx=11, stroke=GREY_D,
                   sw=1.75))
    cy = y0 + LABEL_AREA + hdr_h + LH / 2
    if hdr_h:
        b.append(text(lx, y0 + 16, lhs_hdr, LBL_BEFORE, 10.5, 700,
                      anchor="start"))
        b.append(text(rx, y0 + 16, rhs_hdr, LBL_AFTER, 10.5, 700,
                      anchor="start"))
    for l, r in pairs:
        b.append(f'<text x="{lx}" y="{cy}" fill="{CODE_FG}" '
                 f'font-family="{MONO}" font-size="{CSIZE}" text-anchor="start"'
                 f' dominant-baseline="central" '
                 f'xml:space="preserve">{esc(l)}</text>')
        b.append(arrow(arrow_x1, cy, arrow_x2, cy, PURPLE, 1.8))
        b.append(f'<text x="{rx}" y="{cy}" fill="{CODE_GOOD}" '
                 f'font-family="{MONO}" font-size="{CSIZE}" text-anchor="start"'
                 f' dominant-baseline="central" '
                 f'xml:space="preserve">{esc(r)}</text>')
        cy += LH
    if note:
        b.append(text(W / 2, y0 + cardh + 13, note, LIGHT, 11, 500,
                      italic=True))
    write(fname, svg(W, H, "".join(b), title))




# ── memory-domain helpers ────────────────────────────────────────────────────
def seg(x, y, w, h, label, color, sub=None, tcol=WHITE, size=12.5, rx=3,
        stroke=None):
    lines = [label] if sub is None else [label, sub]
    return box(x, y, w, h, lines, color, tcol=tcol, size=size, rx=rx, lh=15,
               stroke=stroke)


def addr(x, y, s):
    return text(x, y, s, LIGHT, 10.5, 600, anchor="end", mono=True)


def perm(x, y, s, col=TEAL):
    return text(x, y, s, col, 11, 700, anchor="start", mono=True)


# ── UML helpers ──────────────────────────────────────────────────────────────
UML_SIZE = 11
UML_LH = 17


def uml_class(x, y, w, name, attrs=None, methods=None, fill=GREY,
              stereotype=None):
    """A 3-compartment UML class box. Returns (svg, w, h)."""
    attrs = attrs or []
    methods = methods or []
    head_h = 34 if stereotype else 26
    seg_a = len(attrs) * UML_LH + 10 if attrs else 0
    seg_m = len(methods) * UML_LH + 10 if methods else 0
    h = head_h + (seg_a + seg_m or 6)
    p = [rrect(x, y, w, h, fill, rx=6)]
    if stereotype:
        p.append(text(x + w / 2, y + 13, "\u00ab" + stereotype + "\u00bb",
                      WHITE, 9.5, 600))
        p.append(text(x + w / 2, y + 27, name, WHITE, 12.5, 700))
    else:
        p.append(text(x + w / 2, y + 15, name, WHITE, 12.5, 700))
    yy = y + head_h
    for seg, hh in ((attrs, seg_a), (methods, seg_m)):
        if not seg:
            continue
        p.append(line(x, yy, x + w, yy, WHITE, 1))
        cy = yy + 8 + UML_LH / 2 - 3
        for it in seg:
            p.append(text(x + 10, cy, it, WHITE, UML_SIZE, 500,
                          anchor="start", mono=True))
            cy += UML_LH
        yy += hh
    return "".join(p), w, h


def _tri(cx, cy, d, col=GREY, fill="none", s=11):
    if d == "up":
        pts = f"{cx},{cy} {cx-s*0.72},{cy+s} {cx+s*0.72},{cy+s}"
    elif d == "down":
        pts = f"{cx},{cy} {cx-s*0.72},{cy-s} {cx+s*0.72},{cy-s}"
    elif d == "left":
        pts = f"{cx},{cy} {cx+s},{cy-s*0.72} {cx+s},{cy+s*0.72}"
    else:
        pts = f"{cx},{cy} {cx-s},{cy-s*0.72} {cx-s},{cy+s*0.72}"
    return (f'<polygon points="{pts}" fill="{fill}" stroke="{col}" '
            f'stroke-width="1.6" stroke-linejoin="round"/>')


def vrel(cx, y_from, y_to, kind="inherit", col=None, label=None):
    """Vertical relationship; head sits at y_to (the parent/target)."""
    up = y_to < y_from
    d = "up" if up else "down"
    dash = "5 4" if kind in ("realize", "dependency") else None
    if col is None:
        col = PURPLE if kind in ("inherit", "realize") else GREY
    parts = []
    if kind in ("inherit", "realize"):
        parts.append(_tri(cx, y_to, d, col, "none", 11))
        base = y_to + (11 if up else -11)
        parts.append(line(cx, y_from, cx, base, col, 1.6, dash=dash))
    else:
        parts.append(arrow(cx, y_from, cx, y_to, col, 1.7, dash=dash))
    if label:
        parts.append(text(cx + 8, (y_from + y_to) / 2, label, LIGHT, 9.5, 600,
                          anchor="start"))
    return "".join(parts)


def hrel(cy, x_from, x_to, kind="assoc", col=GREY, label=None):
    """Horizontal association / dependency (open arrow at x_to)."""
    dash = "5 4" if kind == "dependency" else None
    parts = [arrow(x_from, cy, x_to, cy, col, 1.7, dash=dash)]
    if label:
        parts.append(text((x_from + x_to) / 2, cy - 9, label, LIGHT, 9.5, 600))
    return "".join(parts)


def hcompose(cy, xw, xp, filled, col=TEAL, label=None):
    """Aggregation/composition diamond at the whole (left), line to part."""
    fillc = col if filled else "none"
    s = 8
    pts = f"{xw},{cy} {xw+s},{cy-s} {xw+2*s},{cy} {xw+s},{cy+s}"
    parts = [f'<polygon points="{pts}" fill="{fillc}" stroke="{col}" '
             f'stroke-width="1.6" stroke-linejoin="round"/>']
    parts.append(line(xw + 2 * s, cy, xp, cy, col, 1.6))
    if label:
        parts.append(text((xw + xp) / 2, cy - 9, label, LIGHT, 9.5, 600))
    return "".join(parts)


def vcompose(cx, y_whole, y_part, filled, col=TEAL, label=None):
    """Aggregation/composition diamond at the whole, line toward the part."""
    fillc = col if filled else "none"
    s = 8
    up = y_part < y_whole
    if up:
        pts = f"{cx},{y_whole} {cx-s},{y_whole-s} {cx},{y_whole-2*s} {cx+s},{y_whole-s}"
        base = y_whole - 2 * s
    else:
        pts = f"{cx},{y_whole} {cx-s},{y_whole+s} {cx},{y_whole+2*s} {cx+s},{y_whole+s}"
        base = y_whole + 2 * s
    parts = [f'<polygon points="{pts}" fill="{fillc}" stroke="{col}" '
             f'stroke-width="1.6" stroke-linejoin="round"/>']
    parts.append(line(cx, base, cx, y_part, col, 1.6))
    if label:
        parts.append(text(cx + 8, (y_whole + y_part) / 2, label, LIGHT, 9.5,
                          600, anchor="start"))
    return "".join(parts)


def tree_conn(parent_cx, parent_by, children, kind="inherit", col=None):
    """Classic UML generalisation tree: one triangle at the parent, a
    horizontal bus, and a vertical drop to each child (cx, y_top)."""
    if col is None:
        col = PURPLE if kind in ("inherit", "realize") else GREY
    dash = "5 4" if kind == "realize" else None
    bus = parent_by + 38
    parts = [_tri(parent_cx, parent_by, "up", col, "none", 11)]
    parts.append(line(parent_cx, parent_by + 11, parent_cx, bus, col, 1.6,
                      dash=dash))
    xs = [c[0] for c in children] + [parent_cx]
    parts.append(line(min(xs), bus, max(xs), bus, col, 1.6, dash=dash))
    for cx, cy in children:
        parts.append(line(cx, bus, cx, cy, col, 1.6, dash=dash))
    return "".join(parts)


def elbow_up(cx_from, y_from, cx_to, y_to, kind="inherit", col=None):
    """L-shaped connector from a child up to a (possibly offset) parent."""
    if col is None:
        col = PURPLE if kind in ("inherit", "realize") else GREY
    dash = "5 4" if kind in ("realize", "dependency") else None
    mid = y_to + 36
    parts = [line(cx_from, y_from, cx_from, mid, col, 1.6, dash=dash),
             line(cx_from, mid, cx_to, mid, col, 1.6, dash=dash)]
    if kind in ("inherit", "realize"):
        parts.append(_tri(cx_to, y_to, "up", col, "none", 11))
        parts.append(line(cx_to, mid, cx_to, y_to + 11, col, 1.6, dash=dash))
    else:
        parts.append(arrow(cx_to, mid, cx_to, y_to, col, 1.7, dash=dash))
    return "".join(parts)


def fig(fname, W, H, title, body, cap=None):
    b = [text(W / 2, 26, title, GREY, 15.5, 700)] + list(body)
    if cap:
        b.append(text(W / 2, H - 14, cap, LIGHT, 10.5, 500))
    write("figures/" + fname, svg(W, H, "".join(b), title))


# ── OOP concepts ─────────────────────────────────────────────────────────────
def fig_oop_pillars():
    W, H = 760, 320
    b = [box(310, 130, 140, 60, ["OOP"], PURPLE, size=15)]
    quad = [("Encapsulation", "bundle data + methods", 40, 70),
            ("Abstraction", "hide the details", 520, 70),
            ("Inheritance", "reuse via IS-A", 40, 216),
            ("Polymorphism", "one interface, many forms", 520, 216)]
    centres = [(140, 97), (620, 97), (140, 243), (620, 243)]
    for (t, s, x, y), (ccx, ccy) in zip(quad, centres):
        b.append(box(x, y, 200, 54, [t, s], GREY, size=12, lh=15))
        b.append(line(ccx if x < 300 else ccx, ccy, 380, 160, GREY, 1.3,
                      dash="4 4"))
    write("figures/oop-pillars.svg",
          svg(W, H, "".join([text(W / 2, 26, "The four pillars of OOP", GREY,
                                  15.5, 700)] + b), "OOP pillars"))


def fig_encapsulation():
    c, w, h = uml_class(280, 60, 220, "BankAccount",
                        ["- balance: double"],
                        ["+ deposit(amt)", "+ withdraw(amt)",
                         "+ getBalance()"], fill=GREY)
    b = [c]
    b.append(text(390, 60 + h + 26, "private data is reachable only through",
                  LIGHT, 10.5, 500))
    b.append(text(390, 60 + h + 42, "public methods that enforce the rules",
                  LIGHT, 10.5, 500))
    fig("encapsulation.svg", 780, 260, "Encapsulation: data + behaviour, "
        "guarded", b)


def fig_inheritance():
    b = []
    p, w, h = uml_class(300, 62, 200, "Animal", [],
                        ["+ eat()", "+ sleep()"], PURPLE)
    b.append(p)
    d, _, _ = uml_class(120, 220, 190, "Dog", [], ["+ bark()"], GREY)
    c, _, _ = uml_class(490, 220, 190, "Cat", [], ["+ meow()"], GREY)
    b.append(d)
    b.append(c)
    b.append(tree_conn(400, 62 + h, [(215, 220), (585, 220)], "inherit"))
    fig("inheritance.svg", 800, 320, "Inheritance: Dog and Cat are-an Animal",
        b, "hollow triangle points to the base class")


def fig_polymorphism():
    b = []
    p, w, h = uml_class(300, 62, 200, "Shape", [], ["+ area(): double"],
                        PURPLE, stereotype="abstract")
    b.append(p)
    c1, _, _ = uml_class(90, 230, 190, "Circle", [], ["+ area(): double"],
                         GREY)
    c2, _, _ = uml_class(320, 230, 190, "Square", [], ["+ area(): double"],
                         GREY)
    c3, _, _ = uml_class(550, 230, 190, "Triangle", [], ["+ area(): double"],
                         GREY)
    b += [c1, c2, c3]
    b.append(tree_conn(400, 62 + h, [(185, 230), (415, 230), (645, 230)],
                       "inherit"))
    fig("polymorphism.svg", 830, 330,
        "Polymorphism: one call, many implementations", b,
        "shape.area() dispatches to the concrete subclass at run time")


def fig_abstraction():
    b = []
    i, w, h = uml_class(300, 62, 220, "Vehicle", [],
                        ["+ start()", "+ stop()"], PURPLE,
                        stereotype="interface")
    b.append(i)
    c1, _, _ = uml_class(120, 232, 200, "Car",
                         ["- engine: Engine"], ["+ start()"], GREY)
    c2, _, _ = uml_class(500, 232, 200, "ElectricCar",
                         ["- battery: Battery"], ["+ start()"], GREY)
    b += [c1, c2]
    b.append(tree_conn(410, 62 + h, [(220, 232), (600, 232)], "realize"))
    fig("abstraction.svg", 820, 365,
        "Abstraction: callers depend on what, not how", b,
        "the interface names the capability; each class supplies the details")


def fig_uml_class():
    W, H = 560, 320
    c, w, h = uml_class(150, 60, 260, "BankAccount",
                        ["- accountNumber: string", "- balance: double"],
                        ["+ deposit(amt: double)", "+ withdraw(amt: double)",
                         "- validate(amt): bool"], GREY)
    b = [c]
    b.append(text(150 + w + 14, 78, "name", LIGHT, 10, 600, anchor="start"))
    b.append(text(150 + w + 14, 128, "attributes", LIGHT, 10, 600,
                  anchor="start"))
    b.append(text(150 + w + 14, 190, "methods", LIGHT, 10, 600,
                  anchor="start"))
    b.append(text(W / 2, H - 30, "+ public    - private    # protected",
                  GREY, 11, 600))
    fig("uml-class.svg", W, H, "Anatomy of a UML class box", b)


def _pair(la, lb, y=80):
    return ([box(60, y, 160, 54, [la], GREY, size=13),
             box(360, y, 160, 54, [lb], GREY, size=13)], y + 27)


def fig_rel_association():
    b, cy = _pair("Teacher", "Student")
    b.append(hrel(cy, 220, 360, "assoc", GREY, "teaches  1 \u2192 *"))
    fig("rel-association.svg", 580, 170, "Association (uses-a)", b,
        "a plain arrow: one class holds a reference to another")


def fig_rel_aggregation():
    b, cy = _pair("Department", "Employee")
    b.append(hcompose(cy, 220, 360, False, TEAL, "has  (shared)"))
    fig("rel-aggregation.svg", 580, 170, "Aggregation (has-a, weak)", b,
        "hollow diamond at the whole; the part outlives the whole")


def fig_rel_composition():
    b, cy = _pair("House", "Room")
    b.append(hcompose(cy, 220, 360, True, TEAL, "owns  (exclusive)"))
    fig("rel-composition.svg", 580, 170, "Composition (has-a, strong)", b,
        "filled diamond at the whole; the part dies with the whole")


def fig_rel_dependency():
    b, cy = _pair("Order", "PaymentService")
    b.append(hrel(cy, 220, 360, "dependency", GREY, "uses"))
    fig("rel-dependency.svg", 620, 170, "Dependency (uses transiently)", b,
        "dashed arrow: a passing use, e.g. a method parameter")


def fig_rel_realization():
    b = []
    i, w, h = uml_class(300, 60, 220, "Drawable", [], ["+ draw()"], PURPLE,
                        stereotype="interface")
    b.append(i)
    c, _, _ = uml_class(300, 210, 220, "Circle", [], ["+ draw()"], GREY)
    b.append(c)
    b.append(vrel(410, 210, 60 + h, "realize"))
    fig("rel-realization.svg", 720, 300, "Realization (implements)", b,
        "dashed line + hollow triangle: a class implements an interface")


def fig_relationships():
    W, H = 860, 300
    b = []
    rows = [("Inheritance", "\u25b3 solid", "is-a", PURPLE),
            ("Realization", "\u25b3 dashed", "implements", PURPLE),
            ("Composition", "\u25c6 filled", "owns (dies with)", TEAL),
            ("Aggregation", "\u25c7 hollow", "has (shared)", TEAL),
            ("Association", "\u2192 solid", "uses / holds", GREY),
            ("Dependency", "\u2192 dashed", "uses transiently", GREY)]
    for i, (name, sym, meaning, col) in enumerate(rows):
        x = 40 + (i % 2) * 420
        y = 64 + (i // 2) * 70
        b.append(box(x, y, 180, 52, [name, sym], col, size=12, lh=15))
        b.append(text(x + 196, y + 26, meaning, LIGHT, 11, 600, anchor="start"))
    fig("relationships.svg", W, H, "The six UML class relationships", b)


def fig_abstract_vs_concrete():
    b = []
    a, w, h = uml_class(90, 64, 220, "Shape", [],
                        ["+ area()  = 0", "+ describe()"], PURPLE,
                        stereotype="abstract")
    b.append(a)
    c, _, ch = uml_class(470, 64, 220, "Rectangle",
                         ["- w: double", "- h: double"], ["+ area()"], GREY)
    b.append(c)
    b.append(text(200, 64 + h + 24, "cannot be instantiated", LIGHT, 10.5, 600))
    b.append(text(580, 64 + ch + 24, "fully implemented \u2014 usable", LIGHT,
                  10.5, 600))
    fig("abstract-vs-concrete.svg", 780, 300,
        "Abstract vs concrete classes", b)


def fig_interface_vs_abstract():
    W, H = 820, 300
    b = [box(60, 70, 320, 150, [""], GREY, rx=8),
         box(440, 70, 320, 150, [""], PURPLE, rx=8)]
    b.append(text(220, 92, "Interface", WHITE, 13, 700))
    for i, t in enumerate(["only pure virtual methods", "no state / fields",
                           "a class can implement many", "the what"]):
        b.append(text(80, 120 + i * 24, "\u2022 " + t, WHITE, 11, 500,
                      anchor="start"))
    b.append(text(600, 92, "Abstract class", WHITE, 13, 700))
    for i, t in enumerate(["may mix concrete + virtual", "can hold state",
                           "single inheritance only", "shared base + the what"]):
        b.append(text(460, 120 + i * 24, "\u2022 " + t, WHITE, 11, 500,
                      anchor="start"))
    fig("interface-vs-abstract.svg", W, H,
        "Interface vs abstract class", b)


# ── SOLID ────────────────────────────────────────────────────────────────────
def fig_solid_overview():
    W, H = 820, 300
    rows = [("S", "Single Responsibility", "one reason to change"),
            ("O", "Open / Closed", "open to extend, closed to modify"),
            ("L", "Liskov Substitution", "subtypes must be swappable"),
            ("I", "Interface Segregation", "many small interfaces"),
            ("D", "Dependency Inversion", "depend on abstractions")]
    b = []
    for i, (k, name, desc) in enumerate(rows):
        y = 60 + i * 44
        b.append(box(60, y, 44, 36, [k], PURPLE, size=16))
        b.append(text(120, y + 12, name, GREY, 12.5, 700, anchor="start"))
        b.append(text(120, y + 28, desc, LIGHT, 10.5, 500, anchor="start"))
    fig("solid-overview.svg", W, H, "SOLID: five principles of OO design", b)


def fig_srp():
    b = []
    bad, w, h = uml_class(60, 66, 250, "Report",
                          [], ["+ generate()", "+ saveToFile()",
                               "+ sendEmail()"], RED)
    b.append(bad)
    b.append(text(60 + 125, 66 + h + 22, "3 reasons to change", RED, 10.5, 600))
    g1, _, h1 = uml_class(430, 60, 200, "Report", [], ["+ generate()"], TEAL)
    g2, _, h2 = uml_class(430, 150, 200, "FileSaver", [], ["+ save()"], TEAL)
    g3, _, h3 = uml_class(430, 232, 200, "Mailer", [], ["+ send()"], TEAL)
    b += [g1, g2, g3]
    b.append(arrow(360, 120, 430, 110, GREY, 1.6))
    b.append(text(650, 150, "one job each", LIGHT, 10.5, 600, anchor="start"))
    fig("srp.svg", 780, 340, "Single Responsibility: split the reasons to "
        "change", b)


def fig_ocp():
    b = []
    i, w, h = uml_class(300, 62, 220, "Shape", [], ["+ area(): double"],
                        PURPLE, stereotype="interface")
    b.append(i)
    kids = []
    for nm, cx in [("Circle", 120), ("Square", 350), ("Hexagon (new)", 580)]:
        col = TEAL if "new" in nm else GREY
        c, _, _ = uml_class(cx, 232, 200, nm, [], ["+ area()"], col)
        b.append(c)
        kids.append((cx + 100, 232))
    b.append(tree_conn(410, 62 + h, kids, "realize"))
    fig("ocp.svg", 830, 330, "Open/Closed: add a class, don't edit existing "
        "ones", b, "new shapes plug in via the interface \u2014 no old code "
        "touched")


def fig_lsp():
    b = []
    p, w, h = uml_class(300, 62, 220, "Bird", [], ["+ move()"], PURPLE)
    b.append(p)
    c1, _, _ = uml_class(120, 222, 200, "Sparrow", [], ["+ move()  // fly"],
                         TEAL)
    c2, _, _ = uml_class(500, 222, 200, "Penguin", [], ["+ move()  // walk"],
                         TEAL)
    b += [c1, c2]
    b.append(tree_conn(410, 62 + h, [(220, 222), (600, 222)], "inherit"))
    fig("lsp.svg", 820, 320, "Liskov Substitution: any subtype must honour the "
        "contract", b, "code written against Bird must work for every subclass")


def fig_isp():
    b = []
    bad, w, h = uml_class(60, 66, 240, "Machine", [],
                          ["+ print()", "+ scan()", "+ fax()"], RED,
                          stereotype="interface")
    b.append(bad)
    b.append(text(60 + 120, 66 + h + 22, "fat interface forces stubs", RED,
                  10.5, 600))
    g1, _, _ = uml_class(430, 66, 180, "Printer", [], ["+ print()"], TEAL,
                         stereotype="interface")
    g2, _, _ = uml_class(430, 176, 180, "Scanner", [], ["+ scan()"], TEAL,
                         stereotype="interface")
    b += [g1, g2]
    b.append(text(640, 130, "small, focused", LIGHT, 10.5, 600,
                  anchor="start"))
    fig("isp.svg", 780, 320, "Interface Segregation: prefer many small "
        "interfaces", b)


def fig_dip():
    b = []
    hi, w, h = uml_class(280, 60, 240, "NotificationService", [],
                         ["+ notify(msg)"], GREY)
    b.append(hi)
    i2, _, h2 = uml_class(280, 168, 240, "MessageSender", [], ["+ send(msg)"],
                          PURPLE, stereotype="interface")
    b.append(i2)
    b.append(vrel(400, 168, 60 + h, "dependency", GREY, "depends on"))
    e1, _, _ = uml_class(80, 280, 190, "EmailSender", [], ["+ send()"], TEAL)
    e2, _, _ = uml_class(520, 280, 190, "SmsSender", [], ["+ send()"], TEAL)
    b += [e1, e2]
    b.append(tree_conn(400, 168 + h2, [(175, 280), (615, 280)], "realize"))
    fig("dip.svg", 780, 400, "Dependency Inversion: both sides depend on an "
        "abstraction", b, "high-level policy and low-level detail meet at the "
        "interface")


# ── Creational patterns ──────────────────────────────────────────────────────
def fig_singleton():
    b = []
    c, w, h = uml_class(270, 70, 240, "Singleton",
                        ["- instance: Singleton", "- Singleton()"],
                        ["+ getInstance(): Singleton", "+ operation()"],
                        PURPLE)
    b.append(c)
    b.append(path(f"M510 95 C575 90 575 150 510 150", TEAL, 1.7,
                  arrow_end=True))
    b.append(text(585, 122, "returns the", LIGHT, 9.5, 600, anchor="start"))
    b.append(text(585, 136, "one instance", LIGHT, 9.5, 600, anchor="start"))
    fig("singleton.svg", 720, 260,
        "Singleton: exactly one instance, globally reachable", b)


def fig_factory_method():
    b = []
    pi, _, ph = uml_class(40, 70, 240, "Product", [], ["+ operation()"],
                          PURPLE, stereotype="interface")
    cr, _, ch = uml_class(430, 70, 250, "Creator", [],
                          ["+ factoryMethod(): Product", "+ someOperation()"],
                          PURPLE, stereotype="abstract")
    cp, _, _ = uml_class(40, 250, 240, "ConcreteProduct", [],
                         ["+ operation()"], GREY)
    cc, _, _ = uml_class(430, 250, 250, "ConcreteCreator", [],
                         ["+ factoryMethod()"], GREY)
    b += [pi, cr, cp, cc]
    b.append(vrel(160, 250, 70 + ph, "realize"))
    b.append(vrel(555, 250, 70 + ch, "inherit"))
    b.append(hrel(96, 430, 280, "dependency", GREY, "creates"))
    fig("factory-method.svg", 720, 360,
        "Factory Method: subclasses choose the product", b)


def fig_abstract_factory():
    b = []
    af, _, afh = uml_class(40, 70, 240, "GUIFactory", [],
                           ["+ createButton()", "+ createCheckbox()"], PURPLE,
                           stereotype="interface")
    b.append(af)
    cf, _, _ = uml_class(40, 250, 240, "WinFactory", [],
                         ["+ createButton()", "+ createCheckbox()"], GREY)
    b.append(cf)
    b.append(vrel(160, 250, 70 + afh, "realize"))
    bi, _, bih = uml_class(440, 70, 240, "Button", [], ["+ paint()"], PURPLE,
                           stereotype="interface")
    b.append(bi)
    cb, _, _ = uml_class(440, 250, 240, "WinButton", [], ["+ paint()"], GREY)
    b.append(cb)
    b.append(vrel(560, 250, 70 + bih, "realize"))
    b.append(hrel(280, 280, 440, "dependency", GREY, "creates"))
    fig("abstract-factory.svg", 720, 360,
        "Abstract Factory: families of related products", b)


def fig_builder():
    b = []
    d, _, dh = uml_class(40, 80, 210, "Director", [],
                         ["+ construct()"], GREY)
    bi, _, bih = uml_class(300, 80, 240, "Builder", [],
                           ["+ buildPartA()", "+ buildPartB()",
                            "+ getResult()"], PURPLE, stereotype="interface")
    cb, _, _ = uml_class(300, 250, 240, "ConcreteBuilder", [],
                         ["+ getResult(): Product"], GREY)
    b += [d, bi, cb]
    b.append(hrel(112, 250, 300, "assoc", GREY, "uses"))
    b.append(vrel(420, 250, 80 + bih, "realize"))
    pr, _, _ = uml_class(600, 250, 90, "Product", [], [], TEAL)
    b.append(pr)
    b.append(hrel(275, 540, 600, "dependency", GREY, "builds"))
    fig("builder.svg", 730, 360,
        "Builder: assemble a complex object step by step", b)


def fig_prototype():
    b = []
    pi, _, ph = uml_class(280, 66, 240, "Prototype", [], ["+ clone(): Prototype"],
                          PURPLE, stereotype="interface")
    b.append(pi)
    c1, _, _ = uml_class(90, 236, 200, "ConcreteA", [], ["+ clone()"], GREY)
    c2, _, _ = uml_class(500, 236, 200, "ConcreteB", [], ["+ clone()"], GREY)
    b += [c1, c2]
    b.append(tree_conn(400, 66 + ph, [(190, 236), (600, 236)], "realize"))
    fig("prototype.svg", 800, 330,
        "Prototype: create new objects by cloning", b,
        "clone() copies an existing instance instead of calling a constructor")


# ── Structural patterns ──────────────────────────────────────────────────────
def fig_adapter():
    b = []
    cl, _, _ = uml_class(40, 96, 170, "Client", [], [], GREY)
    ti, _, th = uml_class(270, 70, 210, "Target", [], ["+ request()"], PURPLE,
                          stereotype="interface")
    ad, _, adh = uml_class(270, 240, 210, "Adapter", [],
                           ["+ request()"], GREY)
    ae, _, _ = uml_class(600, 240, 210, "Adaptee", [],
                         ["+ specificRequest()"], TEAL)
    b += [cl, ti, ad, ae]
    b.append(hrel(120, 210, 270, "assoc", GREY))
    b.append(vrel(375, 240, 70 + th, "realize"))
    b.append(hrel(265, 480, 600, "assoc", GREY, "wraps / calls"))
    fig("adapter.svg", 840, 340,
        "Adapter: make an incompatible interface fit", b)


def fig_decorator():
    b = []
    co, _, ch = uml_class(280, 62, 240, "Component", [], ["+ operation()"],
                          PURPLE, stereotype="interface")
    b.append(co)
    cc, _, _ = uml_class(40, 232, 220, "ConcreteComponent", [],
                         ["+ operation()"], GREY)
    dec, _, dh = uml_class(430, 232, 240, "Decorator", ["- inner: Component"],
                           ["+ operation()"], GREY)
    b += [cc, dec]
    b.append(elbow_up(150, 232, 340, 62 + ch, "realize"))
    b.append(elbow_up(550, 232, 460, 62 + ch, "inherit"))
    b.append(vcompose(550, 232 + dh, 232 + dh + 40, False, TEAL))
    cd, _, _ = uml_class(430, 232 + dh + 40, 240, "ConcreteDecorator", [],
                         ["+ operation()"], GREY)
    b.append(cd)
    b.append(text(690, 232 + dh + 20, "wraps a", LIGHT, 9.5, 600,
                  anchor="start"))
    b.append(text(690, 232 + dh + 34, "Component", LIGHT, 9.5, 600,
                  anchor="start"))
    fig("decorator.svg", 800, 470,
        "Decorator: add behaviour by wrapping", b)


def fig_facade():
    b = []
    cl, _, _ = uml_class(40, 110, 150, "Client", [], [], GREY)
    fa, _, fh = uml_class(250, 100, 200, "Facade", [],
                          ["+ doItAll()"], PURPLE)
    b += [cl, fa]
    b.append(hrel(137, 190, 250, "assoc", GREY))
    for i, nm in enumerate(["SubsystemA", "SubsystemB", "SubsystemC"]):
        sy = 60 + i * 90
        s, _, sh = uml_class(540, sy, 200, nm, [], ["+ op()"], TEAL)
        b.append(s)
        b.append(arrow(450, 126, 540, sy + sh / 2, GREY, 1.7, dash="5 4"))
    fig("facade.svg", 780, 340,
        "Facade: one simple entry to a complex subsystem", b)


def fig_composite():
    b = []
    co, _, ch = uml_class(280, 62, 250, "Component", [],
                          ["+ operation()", "+ add(c)"], PURPLE,
                          stereotype="interface")
    b.append(co)
    lf, _, _ = uml_class(60, 240, 210, "Leaf", [], ["+ operation()"], GREY)
    cm, _, cmh = uml_class(400, 240, 250, "Composite",
                           ["- children: Component[]"],
                           ["+ operation()", "+ add(c)"], GREY)
    b += [lf, cm]
    b.append(tree_conn(405, 62 + ch, [(165, 240), (525, 240)], "realize"))
    b.append(path(f"M650 300 C745 300 745 92 533 92", TEAL, 1.6,
                  arrow_end=True))
    b.append(text(702, 200, "children", LIGHT, 9.5, 600, anchor="start"))
    fig("composite.svg", 800, 360,
        "Composite: treat trees and leaves uniformly", b)


def fig_proxy():
    b = []
    cl, _, _ = uml_class(40, 96, 150, "Client", [], [], GREY)
    si, _, sh = uml_class(250, 70, 210, "Subject", [], ["+ request()"], PURPLE,
                          stereotype="interface")
    px, _, _ = uml_class(250, 240, 210, "Proxy",
                         ["- real: RealSubject"], ["+ request()"], GREY)
    rs, _, _ = uml_class(540, 240, 210, "RealSubject", [], ["+ request()"],
                         TEAL)
    b += [cl, si, px, rs]
    b.append(hrel(120, 190, 250, "assoc", GREY))
    b.append(tree_conn(355, 70 + sh, [(355, 240), (645, 240)], "realize"))
    b.append(hrel(265, 460, 540, "assoc", GREY, "controls"))
    fig("proxy.svg", 780, 340,
        "Proxy: a stand-in that controls access", b)


def fig_bridge():
    b = []
    ab, _, abh = uml_class(40, 70, 240, "Abstraction",
                           ["- impl: Implementor"], ["+ operation()"], PURPLE)
    ra, _, _ = uml_class(40, 250, 240, "RefinedAbstraction", [],
                         ["+ operation()"], GREY)
    im, _, imh = uml_class(440, 70, 240, "Implementor", [],
                           ["+ operationImpl()"], PURPLE,
                           stereotype="interface")
    ci, _, _ = uml_class(440, 250, 240, "ConcreteImpl", [],
                         ["+ operationImpl()"], GREY)
    b += [ab, ra, im, ci]
    b.append(vrel(160, 250, 70 + abh, "inherit"))
    b.append(vrel(560, 250, 70 + imh, "realize"))
    b.append(hcompose(70 + abh / 2, 280, 440, False, TEAL, "bridge"))
    fig("bridge.svg", 720, 360,
        "Bridge: split abstraction from implementation", b)


def fig_flyweight():
    b = []
    ff, _, _ = uml_class(40, 90, 220, "FlyweightFactory",
                         ["- pool: Map"], ["+ get(key): Flyweight"], GREY)
    fw, _, fh = uml_class(330, 70, 240, "Flyweight",
                          ["- intrinsic (shared)"], ["+ op(extrinsic)"],
                          PURPLE, stereotype="interface")
    cf, _, _ = uml_class(330, 240, 240, "ConcreteFlyweight", [],
                         ["+ op(extrinsic)"], TEAL)
    b += [ff, fw, cf]
    b.append(hrel(120, 260, 330, "assoc", GREY, "reuses"))
    b.append(vrel(450, 240, 70 + fh, "realize"))
    fig("flyweight.svg", 640, 340,
        "Flyweight: share intrinsic state across many objects", b,
        "the factory pools shared objects; callers pass the extrinsic state")


# ── Behavioral patterns ──────────────────────────────────────────────────────
def fig_strategy():
    b = []
    ctx, _, cxh = uml_class(40, 90, 230, "Context",
                            ["- strategy: Strategy"], ["+ execute()"], GREY)
    st, _, sh = uml_class(360, 70, 230, "Strategy", [], ["+ algorithm()"],
                          PURPLE, stereotype="interface")
    b += [ctx, st]
    b.append(hcompose(120, 270, 360, False, TEAL, "has-a"))
    c1, _, _ = uml_class(230, 250, 200, "ConcreteA", [], ["+ algorithm()"],
                         GREY)
    c2, _, _ = uml_class(470, 250, 200, "ConcreteB", [], ["+ algorithm()"],
                         GREY)
    b += [c1, c2]
    b.append(tree_conn(475, 70 + sh, [(330, 250), (570, 250)], "realize"))
    fig("strategy.svg", 720, 350,
        "Strategy: swap the algorithm at run time", b)


def fig_observer():
    b = []
    su, _, suh = uml_class(40, 80, 240, "Subject",
                           ["- observers: Observer[]"],
                           ["+ attach(o)", "+ notify()"], GREY)
    ob, _, oh = uml_class(430, 80, 240, "Observer", [], ["+ update()"], PURPLE,
                          stereotype="interface")
    co, _, _ = uml_class(430, 260, 240, "ConcreteObserver", [],
                         ["+ update()"], GREY)
    b += [su, ob, co]
    b.append(hcompose(120, 280, 430, False, TEAL, "notifies  *"))
    b.append(vrel(550, 260, 80 + oh, "realize"))
    fig("observer.svg", 720, 360,
        "Observer: publishers notify their subscribers", b)


def fig_command():
    b = []
    inv, _, _ = uml_class(40, 90, 190, "Invoker",
                          ["- cmd: Command"], ["+ run()"], GREY)
    cm, _, cmh = uml_class(280, 70, 210, "Command", [], ["+ execute()"],
                           PURPLE, stereotype="interface")
    cc, _, _ = uml_class(280, 240, 210, "ConcreteCommand", [],
                         ["+ execute()"], GREY)
    rc, _, _ = uml_class(540, 240, 200, "Receiver", [], ["+ action()"], TEAL)
    b += [inv, cm, cc, rc]
    b.append(hcompose(112, 230, 280, False, TEAL, "holds"))
    b.append(vrel(385, 240, 70 + cmh, "realize"))
    b.append(hrel(265, 490, 540, "assoc", GREY, "calls"))
    fig("command.svg", 780, 340,
        "Command: wrap a request as an object", b)


def fig_state():
    b = []
    ctx, _, cxh = uml_class(40, 90, 210, "Context",
                            ["- state: State"], ["+ request()"], GREY)
    st, _, sh = uml_class(330, 70, 210, "State", [], ["+ handle()"], PURPLE,
                          stereotype="interface")
    b += [ctx, st]
    b.append(hcompose(120, 250, 330, False, TEAL, "current"))
    c1, _, _ = uml_class(230, 250, 190, "StateA", [], ["+ handle()"], GREY)
    c2, _, _ = uml_class(450, 250, 190, "StateB", [], ["+ handle()"], GREY)
    b += [c1, c2]
    b.append(tree_conn(435, 70 + sh, [(325, 250), (545, 250)], "realize"))
    fig("state.svg", 680, 350,
        "State: behaviour changes with internal state", b)


def fig_template_method():
    b = []
    ab, _, abh = uml_class(260, 62, 280, "AbstractClass", [],
                           ["+ templateMethod()", "# step1()  (abstract)",
                            "# step2()  (abstract)"], PURPLE,
                           stereotype="abstract")
    b.append(ab)
    cc, _, _ = uml_class(260, 250, 280, "ConcreteClass", [],
                         ["# step1()", "# step2()"], GREY)
    b.append(cc)
    b.append(vrel(400, 250, 62 + abh, "inherit"))
    b.append(text(560, 110, "templateMethod()", LIGHT, 10, 600, anchor="start"))
    b.append(text(560, 126, "fixes the skeleton;", LIGHT, 10, 600,
                  anchor="start"))
    b.append(text(560, 142, "subclass fills steps", LIGHT, 10, 600,
                  anchor="start"))
    fig("template-method.svg", 800, 360,
        "Template Method: fixed skeleton, overridable steps", b)


def fig_iterator():
    b = []
    ag, _, agh = uml_class(40, 70, 230, "Aggregate", [],
                           ["+ createIterator()"], PURPLE,
                           stereotype="interface")
    it, _, ith = uml_class(430, 70, 230, "Iterator", [],
                           ["+ hasNext()", "+ next()"], PURPLE,
                           stereotype="interface")
    ca, _, _ = uml_class(40, 250, 230, "ConcreteAggregate", [],
                         ["+ createIterator()"], GREY)
    ci, _, _ = uml_class(430, 250, 230, "ConcreteIterator", [],
                         ["+ hasNext()", "+ next()"], GREY)
    b += [ag, it, ca, ci]
    b.append(vrel(155, 250, 70 + agh, "realize"))
    b.append(vrel(545, 250, 70 + ith, "realize"))
    b.append(hrel(300, 270, 430, "dependency", GREY, "creates"))
    fig("iterator.svg", 720, 360,
        "Iterator: traverse a collection without exposing it", b)


def fig_chain_of_responsibility():
    b = []
    h, _, hh = uml_class(280, 62, 250, "Handler",
                         ["- next: Handler"],
                         ["+ setNext(h)", "+ handle(req)"], PURPLE,
                         stereotype="abstract")
    b.append(h)
    b.append(path(f"M530 92 C620 92 620 150 530 150", TEAL, 1.6,
                  arrow_end=True))
    b.append(text(628, 122, "next", LIGHT, 9.5, 600, anchor="start"))
    c1, _, _ = uml_class(120, 250, 220, "ConcreteA", [], ["+ handle(req)"],
                         GREY)
    c2, _, _ = uml_class(430, 250, 220, "ConcreteB", [], ["+ handle(req)"],
                         GREY)
    b += [c1, c2]
    b.append(tree_conn(405, 62 + hh, [(230, 250), (540, 250)], "inherit"))
    fig("chain-of-responsibility.svg", 780, 360,
        "Chain of Responsibility: pass the request down the chain", b,
        "each handler either processes the request or forwards it to next")


ALL = [
    # OOP concepts
    fig_oop_pillars, fig_encapsulation, fig_inheritance, fig_polymorphism,
    fig_abstraction,
    fig_uml_class, fig_relationships,
    fig_rel_association, fig_rel_aggregation, fig_rel_composition,
    fig_rel_dependency, fig_rel_realization,
    fig_abstract_vs_concrete, fig_interface_vs_abstract,
    # SOLID
    fig_solid_overview, fig_srp, fig_ocp, fig_lsp, fig_isp, fig_dip,
    # creational
    fig_singleton, fig_factory_method, fig_abstract_factory, fig_builder,
    fig_prototype,
    # structural
    fig_adapter, fig_decorator, fig_facade, fig_composite, fig_proxy,
    fig_bridge, fig_flyweight,
    # behavioral
    fig_strategy, fig_observer, fig_command, fig_state, fig_template_method,
    fig_iterator, fig_chain_of_responsibility,
]

if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(f"\nDone: {len(ALL)} figures generated.")

