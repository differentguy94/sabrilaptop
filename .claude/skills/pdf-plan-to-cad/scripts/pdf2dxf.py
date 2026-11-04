#!/usr/bin/env python3
"""Vector PDF floor plan (e.g. AutoCAD "Print to PDF") -> DXF at real scale.

Everything that is in the PDF ends up in the DXF, scaled so that 1 drawing unit = 1 metre:
  * stroked paths   -> LINE / ARC / LWPOLYLINE (bezier arcs become true arcs / bulges),
                       exact duplicates removed (AutoCAD plots often draw walls 2-3 times)
  * filled paths    -> solid HATCH (e.g. titles exported as outlines)
  * images          -> solid HATCH rectangles (AutoCAD plots column fills as tiny black JPEGs)
  * real PDF text   -> solid HATCH glyph outlines (looks exactly like the PDF, Arabic included)
                       + editable MTEXT on a separate layer that is OFF by default
  * dimension lines -> layer <prefix>DIMS (lines, ticks and the stroked numbers next to them)
Layers are named <prefix><COLOUR> (BLACK, RED, PINK, GRAY, CYAN, ...); entities keep the exact
RGB colour and a matching lineweight.

Scale: the PDF has no units, so pass --pt-per-m (PDF points per metre). Get it from the
dimension lines: `python3 pdf2dxf.py dims plan.pdf` lists every dimension line with its length
in points; divide by the value written on it (or give several with --dim-values and let the
script do a least-squares fit and print the residuals).

CLI
  python3 pdf2dxf.py dims plan.pdf [--page 1] [--png dims.png]
  python3 pdf2dxf.py convert plan.pdf out.dxf --pt-per-m 19.886 [--rotate 90]
         [--origin-pt X,Y] [--at X,Y] [--prefix GF-] [--dim-values "2606=10.2,203=14"]
As a module: see convert_page(); several PDFs can be placed in one DXF.
"""
from __future__ import annotations

import argparse
import collections
import math
import re
import sys
import unicodedata
try:  # the SVG comes from PyMuPDF, but parse it defensively anyway
    from defusedxml import ElementTree as ET
except ImportError:  # pragma: no cover
    from xml.etree import ElementTree as ET

import ezdxf
import pymupdf
from ezdxf import colors as ezcolors

# ----------------------------------------------------------------------------- colours / weights
NAMED = {
    "BLACK": (0, 0, 0), "WHITE": (255, 255, 255), "RED": (255, 0, 0), "GREEN": (0, 160, 0),
    "BLUE": (0, 0, 255), "YELLOW": (255, 255, 0), "CYAN": (0, 255, 255), "MAGENTA": (255, 0, 255),
    "PINK": (255, 106, 178), "ORANGE": (221, 110, 0), "PURPLE": (191, 0, 255),
    "BROWN": (184, 46, 0), "GRAY": (128, 128, 128), "LIGHTGRAY": (152, 152, 152),
    "DARKGRAY": (118, 118, 118), "STEEL": (92, 161, 184),
}
LINEWEIGHTS = [0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90, 100, 106, 120,
               140, 158, 200, 211]


def rgb255(c):
    return tuple(int(round(v * 255)) for v in c[:3])


def colour_name(rgb):
    best, bd = None, 1e9
    for n, v in NAMED.items():
        d = sum((a - b) ** 2 for a, b in zip(rgb, v))
        if d < bd:
            best, bd = n, d
    return best if bd <= 900 else "RGB%02X%02X%02X" % rgb


def nearest_aci(rgb):
    best, bd = 7, 1e18
    for i in range(1, 256):
        v = ezcolors.int2rgb(ezcolors.DXF_DEFAULT_COLORS[i])
        d = sum((a - b) ** 2 for a, b in zip(rgb, v))
        if d < bd:
            best, bd = i, d
    return best


def lineweight(width_pt):
    if not width_pt:
        return 13
    mm100 = width_pt * 25.4 / 72 * 100
    return min(LINEWEIGHTS[1:], key=lambda w: abs(w - mm100))


# ----------------------------------------------------------------------------- transform
class Xform:
    """PDF page point (y down) -> DXF point (y up), scaled to metres, rotated CCW, translated."""

    def __init__(self, pt_per_m, rotate_deg=0.0, origin_pt=(0.0, 0.0), at=(0.0, 0.0)):
        self.s = 1.0 / pt_per_m
        t = math.radians(rotate_deg)
        self.c, self.sn = math.cos(t), math.sin(t)
        self.rot = rotate_deg
        self.o = origin_pt
        self.at = at

    def __call__(self, p):
        u = (p[0] - self.o[0]) * self.s
        v = -(p[1] - self.o[1]) * self.s
        return (self.at[0] + u * self.c - v * self.sn, self.at[1] + u * self.sn + v * self.c)

    def angle(self, dx, dy):
        """Direction (dx, dy) on the page -> angle in degrees in the DXF."""
        return (math.degrees(math.atan2(-dy, dx)) + self.rot) % 360


# ----------------------------------------------------------------------------- bezier helpers
def bez(P, t):
    a, b, c, d = P
    mt = 1 - t
    return (mt ** 3 * a[0] + 3 * mt * mt * t * b[0] + 3 * mt * t * t * c[0] + t ** 3 * d[0],
            mt ** 3 * a[1] + 3 * mt * mt * t * b[1] + 3 * mt * t * t * c[1] + t ** 3 * d[1])


def flatten(P, n=None):
    if n is None:
        L = sum(math.dist(P[i], P[i + 1]) for i in range(3))
        n = max(4, min(64, int(L / 0.05) + 1))  # P in metres here -> ~5 cm chords
    return [bez(P, i / n) for i in range(1, n + 1)]


def circumcenter(a, b, c):
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    if abs(d) < 1e-12:
        return None
    ux = ((a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) + (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1])
          + (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])) / d
    uy = ((a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) + (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0])
          + (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])) / d
    return (ux, uy)


def bez_as_arc(P, quant):
    """If cubic P (DXF coords) is a circular arc, return (centre, r, sweep_rad signed CCW+)."""
    p0, p3 = P[0], P[3]
    m = bez(P, 0.5)
    c = circumcenter(p0, m, p3)
    if c is None:
        return None
    r = math.dist(c, p0)
    if r <= 0 or r > 1e4:
        return None
    tol = max(1.5 * quant, 0.01 * r)
    for t in (0.2, 0.35, 0.65, 0.8):
        if abs(math.dist(c, bez(P, t)) - r) > tol:
            return None
    a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
    am = math.atan2(m[1] - c[1], m[0] - c[0])
    a1 = math.atan2(p3[1] - c[1], p3[0] - c[0])
    tau = 2 * math.pi
    if (am - a0) % tau <= (a1 - a0) % tau:
        sweep = (a1 - a0) % tau
    else:
        sweep = -((a0 - a1) % tau)
    if abs(sweep) < 1e-6:
        return None
    return c, r, sweep


# ----------------------------------------------------------------------------- PDF reading
def page_paths(page):
    """List of dicts: pid, kind ('s'|'f'|'fs'), stroke rgb, fill rgb, width, items (page coords)."""
    out = []
    for pid, dr in enumerate(page.get_drawings()):
        items = []
        for it in dr["items"]:
            op = it[0]
            if op == "l":
                items.append(("l", (it[1].x, it[1].y), (it[2].x, it[2].y)))
            elif op == "c":
                items.append(("c", *[(q.x, q.y) for q in it[1:5]]))
            elif op in ("qu", "re"):
                if op == "qu":
                    q = it[1]
                    pts = [(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)]
                else:
                    r = it[1]
                    pts = [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]
                for i in range(4):
                    items.append(("l", pts[i], pts[(i + 1) % 4]))
        out.append(dict(pid=pid, kind=dr.get("type", "s"),
                        stroke=rgb255(dr["color"]) if dr.get("color") else None,
                        fill=rgb255(dr["fill"]) if dr.get("fill") else None,
                        width=dr.get("width") or 0, close=bool(dr.get("closePath")),
                        items=items, rect=tuple(dr["rect"])))
    return out


def find_dims(paths):
    """Dimension lines = a long horizontal/vertical line with a 45-degree tick at each end.
    Returns list of dict(pid, ori 'H'|'V', c, lo, hi, L) in PDF points (tick centre to tick centre)."""
    dims = []
    for P in paths:
        if P["kind"] == "f":
            continue
        ticks, longs = [], []
        for it in P["items"]:
            if it[0] != "l":
                continue
            (x0, y0), (x1, y1) = it[1], it[2]
            dx, dy = x1 - x0, y1 - y0
            L = math.hypot(dx, dy)
            if 2.5 < L < 12 and abs(abs(dx) - abs(dy)) < 0.2 * L:
                ticks.append(((x0 + x1) / 2, (y0 + y1) / 2))
            elif L >= 8 and (abs(dx) < 0.3 or abs(dy) < 0.3):
                longs.append((x0, y0, x1, y1))
        if len(ticks) < 2 or not longs:
            continue
        found = []
        for i in range(len(ticks)):
            for j in range(i + 1, len(ticks)):
                a, b = ticks[i], ticks[j]
                if abs(a[1] - b[1]) < 0.5:
                    ori, (lo, hi), c = "H", sorted((a[0], b[0])), (a[1] + b[1]) / 2
                elif abs(a[0] - b[0]) < 0.5:
                    ori, (lo, hi), c = "V", sorted((a[1], b[1])), (a[0] + b[0]) / 2
                else:
                    continue
                cov = 0.0
                for x0, y0, x1, y1 in longs:
                    if ori == "H" and abs(y0 - c) < 0.6 and abs(y1 - c) < 0.6:
                        s0, s1 = sorted((x0, x1))
                        cov += max(0.0, min(s1, hi) - max(s0, lo))
                    if ori == "V" and abs(x0 - c) < 0.6 and abs(x1 - c) < 0.6:
                        s0, s1 = sorted((y0, y1))
                        cov += max(0.0, min(s1, hi) - max(s0, lo))
                if cov > 0.4 * (hi - lo):
                    found.append(dict(pid=P["pid"], ori=ori, c=c, lo=lo, hi=hi, L=hi - lo))
        for d in found:  # keep only spans between neighbouring ticks
            if not any(e is not d and e["ori"] == d["ori"] and abs(e["c"] - d["c"]) < 0.6
                       and e["lo"] >= d["lo"] - 0.01 and e["hi"] <= d["hi"] + 0.01 and e["L"] < d["L"]
                       for e in found):
                dims.append(d)
    return dims


def dim_text_pids(paths, dims, dim_pids):
    """Small black stroke paths sitting on/next to a dimension line = the stroked numbers."""
    out = set()
    for P in paths:
        if P["pid"] in dim_pids or P["kind"] == "f" or P["stroke"] != (0, 0, 0):
            continue
        x0, y0, x1, y1 = P["rect"]
        if max(x1 - x0, y1 - y0) > 12:
            continue
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for d in dims:
            if d["ori"] == "H" and d["lo"] < cx < d["hi"] and abs(cy - d["c"]) < 11:
                out.add(P["pid"])
                break
            if d["ori"] == "V" and d["lo"] < cy < d["hi"] and abs(cx - d["c"]) < 11:
                out.add(P["pid"])
                break
    return out


def fit_scale(dims_by_pid, values):
    """values: {pid: metres}. Least squares pt-per-metre + residuals (m)."""
    pairs = []
    for pid, v in values.items():
        cands = dims_by_pid.get(pid, [])
        if not cands:
            raise SystemExit(f"no dimension with id {pid}")
        L = max(cands, key=lambda d: d["L"])["L"] if len(cands) > 1 else cands[0]["L"]
        pairs.append((pid, L, v))
    k = sum(L * v for _, L, v in pairs) / sum(v * v for _, _, v in pairs)
    return k, [(pid, v, L / k - v) for pid, L, v in pairs]


# ----------------------------------------------------------------------------- SVG glyphs
_NUM = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
_TOK = re.compile(r"[MmLlHhVvCcSsQqTtZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def parse_d(d):
    """SVG path data -> list of subpaths; each = list of segments ('L',p0,p1) / ('C',p0,c1,c2,p1)."""
    toks = _TOK.findall(d)
    i, cmd = 0, None
    cur = start = (0.0, 0.0)
    subs, seg = [], []
    lastc = None

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                if seg:
                    if math.dist(cur, start) > 1e-9:
                        seg.append(("L", cur, start))
                    subs.append(seg)
                    seg = []
                cur = start
                lastc = None
                continue
        rel = cmd.islower()
        C = cmd.upper()
        ox, oy = cur if rel else (0.0, 0.0)
        if C == "M":
            if seg:
                subs.append(seg)
                seg = []
            cur = start = (ox + num(), oy + num())
            cmd = "l" if rel else "L"
            lastc = None
        elif C == "L":
            p = (ox + num(), oy + num())
            seg.append(("L", cur, p))
            cur, lastc = p, None
        elif C == "H":
            p = ((ox if rel else 0.0) + num(), cur[1])
            seg.append(("L", cur, p))
            cur, lastc = p, None
        elif C == "V":
            p = (cur[0], (oy if rel else 0.0) + num())
            seg.append(("L", cur, p))
            cur, lastc = p, None
        elif C == "C":
            c1 = (ox + num(), oy + num())
            c2 = (ox + num(), oy + num())
            p = (ox + num(), oy + num())
            seg.append(("C", cur, c1, c2, p))
            cur, lastc = p, c2
        elif C == "S":
            c1 = (2 * cur[0] - lastc[0], 2 * cur[1] - lastc[1]) if lastc else cur
            c2 = (ox + num(), oy + num())
            p = (ox + num(), oy + num())
            seg.append(("C", cur, c1, c2, p))
            cur, lastc = p, c2
        elif C == "Q":
            q = (ox + num(), oy + num())
            p = (ox + num(), oy + num())
            c1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            c2 = (p[0] + 2 / 3 * (q[0] - p[0]), p[1] + 2 / 3 * (q[1] - p[1]))
            seg.append(("C", cur, c1, c2, p))
            cur, lastc = p, None
        elif C == "T":
            p = (ox + num(), oy + num())
            seg.append(("L", cur, p))
            cur, lastc = p, None
        else:
            raise ValueError("unsupported path command " + cmd)
    if seg:
        subs.append(seg)
    return subs


def _parse_transform(s):
    m = [1, 0, 0, 1, 0, 0]
    if not s:
        return m
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s):
        a = [float(v) for v in _NUM.findall(args)]
        if name == "matrix":
            t = a
        elif name == "translate":
            t = [1, 0, 0, 1, a[0], a[1] if len(a) > 1 else 0]
        elif name == "scale":
            t = [a[0], 0, 0, a[1] if len(a) > 1 else a[0], 0, 0]
        else:
            continue
        m = _mul(m, t)
    return m


def _mul(m, t):  # m then t applied in SVG order: result = m * t
    a, b, c, d, e, f = m
    A, B, C, D, E, F = t
    return [a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D, a * E + c * F + e, b * E + d * F + f]


def _apply(m, p):
    return (m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5])


def _hex(c):
    c = c.strip()
    if c.startswith("#") and len(c) == 7:
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    return (0, 0, 0)


def svg_glyphs(page):
    """Text drawn as outlines: list of (fill_rgb, [subpath segments in PAGE coords])."""
    svg = page.get_svg_image(text_as_path=True)
    root = ET.fromstring(svg)
    XL = "{http://www.w3.org/1999/xlink}href"
    defs = {}
    for el in root.iter():
        if el.tag.endswith("path") and el.get("id", "").startswith("font_"):
            defs[el.get("id")] = parse_d(el.get("d", ""))
    out = []

    def walk(el, m, fill):
        m2 = _mul(m, _parse_transform(el.get("transform")))
        fill = el.get("fill", fill)
        if el.tag.endswith("use"):
            ref = (el.get(XL) or el.get("href") or "").lstrip("#")
            if ref in defs:
                mm = _mul(m2, [1, 0, 0, 1, float(el.get("x", 0)), float(el.get("y", 0))])
                subs = [[(s[0], *[_apply(mm, p) for p in s[1:]]) for s in sub] for sub in defs[ref]]
                out.append((_hex(fill or "#000000"), subs, ref))
            return
        if el.tag.endswith("defs") or el.tag.endswith("clipPath"):
            return
        for ch in el:
            walk(ch, m2, fill)

    walk(root, [1, 0, 0, 1, 0, 0], None)
    return out


# ----------------------------------------------------------------------------- editable text
_KASHIDA = "\u0467\u0640\ufffd"


def _runs(s):
    return re.findall(r"\s+|[0-9.,٠-٩]+|[^\s0-9.,٠-٩]+", s)


def text_lines(page):
    """Best-effort logical-order Arabic strings from AutoCAD-plotted PDF text.
    Returns list of dict(text, bbox, size, dir, rgb)."""
    d = page.get_text("dict")
    out = []
    for b in d["blocks"]:
        for ln in b.get("lines", []):
            spans = [s for s in ln["spans"] if s["text"].strip()]
            if not spans:
                continue
            dx, dy = ln["dir"]
            spans.sort(key=lambda s: -(((s["bbox"][0] + s["bbox"][2]) / 2) * dx + ((s["bbox"][1] + s["bbox"][3]) / 2) * dy))
            parts = []
            for s in spans:
                parts.extend(reversed(_runs(s["text"])))
            txt = "".join(parts)
            txt = re.sub(r"([0-9٠-٩])([^\s0-9.,٠-٩])", r"\1 \2", txt)
            txt = re.sub(r"([^\s0-9.,٠-٩])([0-9٠-٩])", r"\1 \2", txt)
            txt = unicodedata.normalize("NFKC", "".join(ch for ch in txt if ch not in _KASHIDA))
            txt = re.sub(r"\s+", " ", txt).strip()
            x0 = min(s["bbox"][0] for s in spans); y0 = min(s["bbox"][1] for s in spans)
            x1 = max(s["bbox"][2] for s in spans); y1 = max(s["bbox"][3] for s in spans)
            col = spans[0]["color"]
            out.append(dict(text=txt, bbox=(x0, y0, x1, y1), size=max(s["size"] for s in spans), dir=(dx, dy),
                            rgb=((col >> 16) & 255, (col >> 8) & 255, col & 255)))
    return out


# ----------------------------------------------------------------------------- DXF writing
class Writer:
    def __init__(self, doc):
        self.doc = doc
        self.msp = doc.modelspace()
        if "ARABIC" not in doc.styles:
            doc.styles.add("ARABIC", font="arial.ttf")

    def layer(self, name, rgb, off=False):
        if name not in self.doc.layers:
            lay = self.doc.layers.add(name, color=nearest_aci(rgb))
            if off:
                lay.off()
        return name

    def attrs(self, layer, rgb, lw=None):
        a = {"layer": layer, "true_color": ezcolors.rgb2int(rgb)}
        if lw is not None:
            a["lineweight"] = lw
        return a


def _chains(prims, eps):
    """Group consecutive primitives whose end meets the next start."""
    chains, cur = [], []
    for p in prims:
        if cur and math.dist(cur[-1]["b"], p["a"]) <= eps:
            cur.append(p)
        else:
            if cur:
                chains.append(cur)
            cur = [p]
    if cur:
        chains.append(cur)
    return chains


def convert_page(doc, pdf_path, pt_per_m, page_no=1, rotate=0.0, origin_pt=(0.0, 0.0), at=(0.0, 0.0),
                 prefix="", glyph_text=True, editable_text=True, text_override=None, dedupe=True):
    """Draw one PDF page into doc's modelspace. Returns dict with xform, dims, counts, bbox."""
    pdf = pymupdf.open(pdf_path)
    page = pdf[page_no - 1]
    xf = Xform(pt_per_m, rotate, origin_pt, at)
    W = Writer(doc)
    msp = W.msp
    quant = 0.12 / pt_per_m  # "Print to PDF" coordinates are 600 dpi = 0.12 pt steps
    paths = page_paths(page)
    dims = find_dims(paths)
    dim_pids = {d["pid"] for d in dims}
    dim_txt = dim_text_pids(paths, dims, dim_pids)
    stats = collections.Counter()

    # ---- primitives (page coords) with z-order index, for dedupe (keep the last = visible one)
    prims = []
    for P in paths:
        if P["kind"] == "f" or not P["stroke"]:
            continue
        for it in P["items"]:
            if it[0] == "l":
                a, b = it[1], it[2]
                if math.dist(a, b) < 1e-6:
                    continue
                key = ("l",) + tuple(sorted([(round(a[0], 2), round(a[1], 2)), (round(b[0], 2), round(b[1], 2))]))
                prims.append(dict(pid=P["pid"], t="l", pts=(a, b), key=key))
            else:
                a, c1, c2, b = it[1:]
                m = bez((a, c1, c2, b), 0.5)
                key = ("c",) + tuple(sorted([(round(a[0], 2), round(a[1], 2)), (round(b[0], 2), round(b[1], 2))])) + \
                      ((round(m[0], 2), round(m[1], 2)),)
                prims.append(dict(pid=P["pid"], t="c", pts=(a, c1, c2, b), key=key))
    last = {}
    for i, p in enumerate(prims):
        last[p["key"]] = i
    keep = [p for i, p in enumerate(prims) if not dedupe or last[p["key"]] == i]
    stats["primitives"] = len(prims)
    stats["duplicates_removed"] = len(prims) - len(keep)
    by_pid = collections.defaultdict(list)
    for p in keep:
        by_pid[p["pid"]].append(p)

    # ---- strokes
    for P in paths:
        if P["pid"] not in by_pid:
            continue
        rgb = P["stroke"]
        if P["pid"] in dim_pids or P["pid"] in dim_txt:
            lay = W.layer(prefix + "DIMS", rgb)
        else:
            lay = W.layer(prefix + colour_name(rgb), rgb)
        at_ = W.attrs(lay, rgb, lineweight(P["width"]))
        segs = []
        for p in by_pid[P["pid"]]:
            q = [xf(v) for v in p["pts"]]
            segs.append(dict(t=p["t"], q=q, a=q[0], b=q[-1]))
        for ch in _chains(segs, 2 * quant):
            closed = len(ch) > 1 and math.dist(ch[-1]["b"], ch[0]["a"]) <= 2 * quant
            verts = []  # (x, y, bulge)
            only_arcs = True
            for s in ch:
                if s["t"] == "l":
                    verts.append((s["a"][0], s["a"][1], 0.0))
                    only_arcs = False
                    continue
                arc = bez_as_arc(s["q"], quant)
                if arc:
                    verts.append((s["a"][0], s["a"][1], math.tan(arc[2] / 4)))
                else:
                    only_arcs = False
                    verts.append((s["a"][0], s["a"][1], 0.0))
                    for pt in flatten(s["q"])[:-1]:
                        verts.append((pt[0], pt[1], 0.0))
            end = ch[-1]["b"]
            if len(verts) == 1 and not closed:
                s = ch[0]
                if s["t"] == "l":
                    msp.add_line(s["a"], s["b"], dxfattribs=at_)
                    stats["LINE"] += 1
                    continue
                arc = bez_as_arc(s["q"], quant)
                if arc:
                    c, r, sw = arc
                    a0 = math.degrees(math.atan2(s["a"][1] - c[1], s["a"][0] - c[0]))
                    a1 = math.degrees(math.atan2(s["b"][1] - c[1], s["b"][0] - c[0]))
                    if sw < 0:
                        a0, a1 = a1, a0
                    msp.add_arc(c, r, a0, a1, dxfattribs=at_)
                    stats["ARC"] += 1
                    continue
            if closed and only_arcs:
                arcs = [bez_as_arc(s["q"], quant) for s in ch]
                c0, r0 = arcs[0][0], arcs[0][1]
                if all(math.dist(a[0], c0) < max(2 * quant, 0.01 * r0) and abs(a[1] - r0) < max(2 * quant, 0.01 * r0) for a in arcs) \
                        and abs(abs(sum(a[2] for a in arcs)) - 2 * math.pi) < 0.05:
                    msp.add_circle(c0, r0, dxfattribs=at_)
                    stats["CIRCLE"] += 1
                    continue
            if not closed:
                verts.append((end[0], end[1], 0.0))
            msp.add_lwpolyline(verts, format="xyb", close=closed, dxfattribs=at_)
            stats["LWPOLYLINE"] += 1

    # ---- filled paths -> solid hatch
    for P in paths:
        if P["kind"] not in ("f", "fs") or not P["fill"]:
            continue
        rgb = P["fill"]
        lay = W.layer(prefix + "FILL-" + colour_name(rgb), rgb)
        subs, cur = [], []
        for it in P["items"]:
            a = it[1]
            if cur and math.dist(cur[-1][-1], a) > 1e-3:
                subs.append(cur)
                cur = []
            if it[0] == "l":
                cur.append((it[1], it[2]))
            else:
                cur.append(tuple(it[1:5]))
        if cur:
            subs.append(cur)
        _hatch(msp, W, lay, rgb, [[(("L" if len(s) == 2 else "C"), *s) for s in sub] for sub in subs], xf)
        stats["HATCH(fill)"] += 1

    # ---- images -> solid black (or average colour) rectangles
    seen = set()
    for info in page.get_image_info(xrefs=True):
        x0, y0, x1, y1 = info["bbox"]
        k = tuple(round(v, 1) for v in info["bbox"])
        if k in seen:
            continue
        seen.add(k)
        rgb = (0, 0, 0)
        try:
            pix = pymupdf.Pixmap(pdf, info["xref"])
            if pix.n >= 3:
                s = pix.samples
                n = pix.n
                cnt = collections.Counter(tuple(s[i:i + 3]) for i in range(0, len(s), n * 5))
                rgb = cnt.most_common(1)[0][0]
        except Exception:
            pass
        lay = W.layer(prefix + "SOLID-" + colour_name(rgb), rgb)
        h = msp.add_hatch(dxfattribs={"layer": lay})
        h.set_solid_fill(color=nearest_aci(rgb), rgb=rgb)
        h.paths.add_polyline_path([xf(p) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))], is_closed=True)
        stats["HATCH(image)"] += 1

    # ---- text: exact outlines + editable MTEXT (layer off)
    if glyph_text:
        for rgb, subs, ref in svg_glyphs(page):
            lay = W.layer(prefix + "TEXT-PDF", rgb)
            _hatch(msp, W, lay, rgb, subs, xf)
            stats["HATCH(glyph)"] += 1
    labels = text_override if text_override is not None else (text_lines(page) if editable_text else [])
    for t in labels:
        x0, y0, x1, y1 = t["bbox"]
        dx, dy = t.get("dir", (1, 0))
        rgb = tuple(t.get("rgb", (0, 0, 0)))
        lay = W.layer(prefix + "TEXT-EDIT", rgb, off=True)
        h = t["size"] * 0.62 / pt_per_m
        mt = msp.add_mtext(t["text"], dxfattribs={
            "layer": lay, "style": "ARABIC", "char_height": h, "attachment_point": 5,
            "insert": xf(((x0 + x1) / 2, (y0 + y1) / 2)), "rotation": xf.angle(dx, dy),
            "true_color": ezcolors.rgb2int(rgb)})
        mt.dxf.width = max(x1 - x0, y1 - y0) / pt_per_m * 1.15
        stats["MTEXT"] += 1

    corners = [xf(p) for p in ((page.rect.x0, page.rect.y0), (page.rect.x1, page.rect.y0),
                                (page.rect.x1, page.rect.y1), (page.rect.x0, page.rect.y1))]
    return dict(xform=xf, dims=dims, stats=stats, paths=paths,
                page_bbox=(min(c[0] for c in corners), min(c[1] for c in corners),
                           max(c[0] for c in corners), max(c[1] for c in corners)))


def _signed_area(r):
    return sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r))) / 2


def _inside(pt, r):
    x, y = pt
    ins = False
    j = len(r) - 1
    for i in range(len(r)):
        xi, yi = r[i]
        xj, yj = r[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins


def _hatch(msp, W, lay, rgb, subs, xf):
    """Solid fill with PDF 'nonzero' semantics: contours wound like the outer outline are filled
    even where they overlap (e.g. kashida strokes); opposite-wound contours are holes of the
    outline that contains them. DXF hatches are odd-even, so overlapping outers get own hatches."""
    rings = []
    for sub in subs:
        pts = []
        for s in sub:
            if s[0] == "L":
                if not pts:
                    pts.append(xf(s[1]))
                pts.append(xf(s[2]))
            else:
                q = [xf(v) for v in s[1:]]
                if not pts:
                    pts.append(q[0])
                L = sum(math.dist(q[i], q[i + 1]) for i in range(3))
                n = max(3, min(24, int(L / 0.01) + 1))  # ~1 cm chords on glyphs
                pts.extend(flatten(q, n))
        if len(pts) > 3 and math.dist(pts[0], pts[-1]) < 1e-9:
            pts = pts[:-1]
        if len(pts) >= 3 and abs(_signed_area(pts)) > 1e-12:
            rings.append(pts)
    if not rings:
        return None
    areas = [_signed_area(r) for r in rings]
    top = [i for i, r in enumerate(rings)
           if not any(j != i and abs(areas[j]) > abs(areas[i]) and _inside(r[0], rings[j]) for j in range(len(rings)))]
    pos = sum(abs(areas[i]) for i in top if areas[i] > 0)
    neg = sum(abs(areas[i]) for i in top if areas[i] < 0)
    outer_sign = 1 if pos >= neg else -1
    outers = [i for i in range(len(rings)) if areas[i] * outer_sign > 0]
    groups = {i: [i] for i in outers}
    for i in range(len(rings)):
        if i in groups:
            continue
        host = [o for o in outers if abs(areas[o]) > abs(areas[i]) and _inside(rings[i][0], rings[o])]
        if host:
            groups[min(host, key=lambda o: abs(areas[o]))].append(i)
        else:
            groups[i] = [i]
    for members in groups.values():
        h = msp.add_hatch(dxfattribs={"layer": lay})
        h.set_solid_fill(color=nearest_aci(rgb), rgb=rgb, style=0)
        for i in members:
            h.paths.add_polyline_path(rings[i], is_closed=True)
    return True


def new_doc():
    doc = ezdxf.new("R2010", setup=True)  # opens in AutoCAD 2010 and newer
    doc.header["$INSUNITS"] = 6      # metres
    doc.header["$MEASUREMENT"] = 1   # metric
    doc.header["$LUNITS"] = 2        # decimal
    doc.header["$LUPREC"] = 3
    doc.header["$LWDISPLAY"] = 1
    return doc


# ----------------------------------------------------------------------------- CLI
def _cmd_dims(a):
    pdf = pymupdf.open(a.pdf)
    page = pdf[a.page - 1]
    dims = find_dims(page_paths(page))
    dims.sort(key=lambda d: (d["ori"], d["c"], d["lo"]))
    print("id      ori  position (pt)                      length_pt")
    for d in dims:
        pos = (f"x {d['lo']:7.1f}-{d['hi']:7.1f} @y {d['c']:7.1f}" if d["ori"] == "H"
               else f"y {d['lo']:7.1f}-{d['hi']:7.1f} @x {d['c']:7.1f}")
        print(f"{d['pid']:<7d} {d['ori']}    {pos}   {d['L']:9.2f}")
    if a.png:
        sh = page.new_shape()
        for d in dims:
            if d["ori"] == "H":
                sh.draw_line((d["lo"], d["c"]), (d["hi"], d["c"]))
            else:
                sh.draw_line((d["c"], d["lo"]), (d["c"], d["hi"]))
        sh.finish(color=(0, 0.7, 0), width=1.5)
        sh.commit()
        for d in dims:
            mx = (d["lo"] + d["hi"]) / 2
            pt = (mx, d["c"] + 9) if d["ori"] == "H" else (d["c"] + 3, mx)
            page.insert_text(pt, str(d["pid"]), fontsize=7, color=(0, 0.55, 0))
        page.get_pixmap(dpi=a.dpi).save(a.png)
        print("wrote", a.png)


def _parse_vals(s):
    out = {}
    for kv in s.split(","):
        if kv.strip():
            k, v = kv.split("=")
            out[int(k)] = float(v)
    return out


def _cmd_convert(a):
    k = a.pt_per_m
    if a.dim_values:
        pdf = pymupdf.open(a.pdf)
        dims = find_dims(page_paths(pdf[a.page - 1]))
        byp = collections.defaultdict(list)
        for d in dims:
            byp[d["pid"]].append(d)
        k, res = fit_scale(byp, _parse_vals(a.dim_values))
        print(f"fitted scale: {k:.4f} pt/m; residuals (m): " + ", ".join(f"{p}:{v}->{r:+.3f}" for p, v, r in res))
    if not k:
        raise SystemExit("give --pt-per-m or --dim-values (see `dims`)")
    doc = new_doc()
    o = tuple(float(v) for v in a.origin_pt.split(",")) if a.origin_pt else (0.0, 0.0)
    at = tuple(float(v) for v in a.at.split(",")) if a.at else (0.0, 0.0)
    r = convert_page(doc, a.pdf, k, a.page, a.rotate, o, at, a.prefix,
                     glyph_text=not a.no_glyphs, editable_text=not a.no_mtext)
    doc.saveas(a.out)
    print("wrote", a.out, dict(r["stats"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dims", help="list dimension lines (id, length in PDF points)")
    d.add_argument("pdf"); d.add_argument("--page", type=int, default=1)
    d.add_argument("--png", help="write a PNG with the dimension ids drawn on the plan")
    d.add_argument("--dpi", type=int, default=150)
    c = sub.add_parser("convert", help="PDF page -> DXF in metres")
    c.add_argument("pdf"); c.add_argument("out")
    c.add_argument("--page", type=int, default=1)
    c.add_argument("--pt-per-m", type=float, help="PDF points per metre")
    c.add_argument("--dim-values", help='fit the scale: "dimId=metres,dimId=metres,..." (ids from `dims`)')
    c.add_argument("--rotate", type=float, default=0.0, help="rotate the plan CCW (degrees)")
    c.add_argument("--origin-pt", help="page point (PDF pt, y down) that goes to --at")
    c.add_argument("--at", help="DXF point for --origin-pt (metres)")
    c.add_argument("--prefix", default="", help="layer name prefix, e.g. GF-")
    c.add_argument("--no-glyphs", action="store_true", help="skip text outlines")
    c.add_argument("--no-mtext", action="store_true", help="skip editable MTEXT copies")
    a = ap.parse_args(argv)
    {"dims": _cmd_dims, "convert": _cmd_convert}[a.cmd](a)


if __name__ == "__main__":
    main()
