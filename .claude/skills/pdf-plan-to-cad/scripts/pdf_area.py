#!/usr/bin/env python3
"""Areas from a vector PDF floor plan (AutoCAD "Print to PDF" and similar).

  python3 pdf_area.py labels plan.pdf                     # areas WRITTEN on the plan ("المساحة 189 متر")
  python3 pdf_area.py render plan.pdf -o crop.png --clip 500,300,800,650 --zoom 4   # gridded crop to read dims
  python3 pdf_area.py area plan.pdf --pt-per-m 19.886 --poly "551.64,252.48 754.44,252.48 754.44,622.32 551.64,622.32"
  python3 pdf_area.py area plan.pdf --pt-per-m 19.886 --rect 551.64,252.48,754.44,622.32
  python3 pdf_area.py area plan.pdf --pt-per-m 19.886 --seed 650,500 [--barrier "603,624 699,624"]

Coordinates are PDF points with y DOWN (PyMuPDF page coordinates), the same numbers `pdf2dxf.py dims`
and `render` print. The scale (--pt-per-m) comes from the dimension lines: see pdf2dxf.py `dims` /
`--dim-values`. --seed does what the web tool's "room click" does: raster flood fill from a point,
holes (furniture/text) filled, half the wall line added back, refused if it leaks to the page border.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
import unicodedata

import pymupdf

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import pdf2dxf  # noqa: E402


def shoelace(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2


def _pts(s):
    return [tuple(float(v) for v in xy.split(",")) for xy in s.split()]


# ----------------------------------------------------------------------------- written areas
AREA_WORDS = re.compile(r"مساح|المس|احة|مسطح|area", re.I)


def labels(page):
    """Area values written as text. Groups spans into lines (visual-order Arabic is fine: we only
    look for the wording and the number). Returns list of (value, line_text_cleaned, bbox)."""
    out = []
    d = page.get_text("dict")
    lines = []
    for b in d["blocks"]:
        for ln in b.get("lines", []):
            for s in ln["spans"]:
                if s["text"].strip():
                    lines.append((ln["dir"], s))
    # merge spans of the same visual line (same direction, overlapping across-line extent, close along-line)
    groups = []
    for dr, s in lines:
        x0, y0, x1, y1 = s["bbox"]
        hit = None
        for g in groups:
            if g["dir"] != dr or abs(g["size"] - s["size"]) > 0.35 * g["size"]:
                continue
            gx0, gy0, gx1, gy1 = g["bbox"]
            if dr[0]:  # horizontal text
                across = min(y1, gy1) - max(y0, gy0) > 0.5 * (y1 - y0)
                gap = max(gx0 - x1, x0 - gx1)
            else:
                across = min(x1, gx1) - max(x0, gx0) > 0.5 * (x1 - x0)
                gap = max(gy0 - y1, y0 - gy1)
            if across and gap < 3 * s["size"]:
                hit = g
                break
        if hit:
            hit["texts"].append(s["text"])
            gx0, gy0, gx1, gy1 = hit["bbox"]
            hit["bbox"] = (min(gx0, x0), min(gy0, y0), max(gx1, x1), max(gy1, y1))
        else:
            groups.append(dict(dir=dr, size=s["size"], texts=[s["text"]], bbox=(x0, y0, x1, y1)))
    for g in groups:
        t = unicodedata.normalize("NFKC", " ".join(g["texts"]))
        t = re.sub("[\u0467\u0640\ufffd]", "", t)
        t = t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹٫", "01234567890123456789."))
        if not (AREA_WORDS.search(t) or re.search(r"(?:^|\s)[مm]\s*2(?:\s|$)", t)):
            continue
        for v in re.findall(r"\d+(?:[.,]\d+)?", re.sub(r"[مm]\s*2", " ", t)):
            val = float(v.replace(",", "."))
            if 1 <= val <= 1e6:
                out.append((val, re.sub(r"\s+", " ", t).strip(), g["bbox"]))
    return out


# ----------------------------------------------------------------------------- room fill (like the web tool)
def room_fill(page, seed, pt_per_m, barriers=(), max_px=6e6):
    """Area (m2) of the closed space around `seed` (PDF pt, y down). Returns (m2, info) or raises."""
    try:
        import numpy as np
        from scipy import ndimage
    except ImportError as e:  # pragma: no cover
        raise SystemExit("room fill needs numpy + scipy: pip install numpy scipy") from e
    W, H = page.rect.width, page.rect.height
    R = min(4.0, math.sqrt(max_px / (W * H)))
    pix = page.get_pixmap(matrix=pymupdf.Matrix(R, R), alpha=False)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(int)
    ink = (a.sum(2) < 690) | ((a.max(2) - a.min(2)) > 60)
    # dimension lines run across rooms: erase them except where another line crosses
    paths = pdf2dxf.page_paths(page)
    orig = ink.copy()
    hw = max(1, round(R * 0.6)) + 1
    probe, end = hw + 2, math.ceil(4 * R)
    h, w = ink.shape
    for d in pdf2dxf.find_dims(paths):
        c, lo, hi = round(d["c"] * R), round(d["lo"] * R) + end, round(d["hi"] * R) - end
        for t in range(max(lo, 0), min(hi, (w if d["ori"] == "H" else h) - 1) + 1):
            if d["ori"] == "H":
                if c - probe < 0 or c + probe >= h or (orig[c - probe, t] and orig[c + probe, t]):
                    continue
                ink[c - hw:c + hw + 1, t] = False
            else:
                if c - probe < 0 or c + probe >= w or (orig[t, c - probe] and orig[t, c + probe]):
                    continue
                ink[t, c - hw:c + hw + 1] = False
    for (x0, y0), (x1, y1) in barriers:
        n = int(math.hypot(x1 - x0, y1 - y0) * R * 2) + 1
        for i in range(n + 1):
            x = round((x0 + (x1 - x0) * i / n) * R)
            y = round((y0 + (y1 - y0) * i / n) * R)
            ink[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = True
    lab, _ = ndimage.label(~ink)  # 4-connected free space
    sx, sy = round(seed[0] * R), round(seed[1] * R)
    k = lab[sy, sx]
    if k == 0:
        raise SystemExit("seed is on a line; move it into the room")
    reg = lab == k
    if reg[0, :].any() or reg[-1, :].any() or reg[:, 0].any() or reg[:, -1].any():
        raise SystemExit("the space is not closed (open door/gap); add --barrier across the opening")
    solid = ndimage.binary_fill_holes(reg)
    edge = ndimage.binary_dilation(solid) & ~solid
    # median drawn line thickness at the boundary -> add half of it all round
    thick = []
    ys, xs = np.nonzero(edge)
    for yy, xx in list(zip(ys, xs))[::8]:
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            if 0 <= yy - dy < h and 0 <= xx - dx < w and solid[yy - dy, xx - dx]:
                t, j, i = 0, yy, xx
                while t < 12 and 0 <= j < h and 0 <= i < w and ink[j, i]:
                    t += 1
                    j += dy
                    i += dx
                thick.append(t)
                break
    T = sorted(thick)[len(thick) // 2] if thick else 1
    px = solid.sum() + edge.sum() * min(T, 8) / 2
    return px / (R * R) / pt_per_m ** 2, dict(R=R, pixels=int(solid.sum()), edge=int(edge.sum()), line_px=T)


# ----------------------------------------------------------------------------- render with grid
def render(page, out, clip=None, zoom=3.0, step=10):
    r = pymupdf.Rect(*clip) if clip else page.rect
    sh = page.new_shape()
    x = math.floor(r.x0 / step) * step
    while x <= r.x1:
        sh.draw_line((x, r.y0), (x, r.y1))
        sh.finish(color=(0, 0.6, 0), width=0.4 if x % (5 * step) == 0 else 0.12)
        x += step
    y = math.floor(r.y0 / step) * step
    while y <= r.y1:
        sh.draw_line((r.x0, y), (r.x1, y))
        sh.finish(color=(0, 0.6, 0), width=0.4 if y % (5 * step) == 0 else 0.12)
        y += step
    sh.commit()
    x = math.ceil(r.x0 / (5 * step)) * 5 * step
    while x <= r.x1:
        y = math.ceil(r.y0 / (5 * step)) * 5 * step
        while y <= r.y1:
            page.insert_text((x + 1, y - 1), f"{int(x)},{int(y)}", fontsize=4, color=(0, 0.5, 0))
            y += 5 * step
        x += 5 * step
    page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=r).save(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("labels", help="area values written on the plan")
    l.add_argument("pdf"); l.add_argument("--page", type=int, default=1)
    r = sub.add_parser("render", help="PNG crop with a 10 pt grid (labels every 50 pt)")
    r.add_argument("pdf"); r.add_argument("-o", "--out", required=True); r.add_argument("--page", type=int, default=1)
    r.add_argument("--clip", help="x0,y0,x1,y1 in PDF pt"); r.add_argument("--zoom", type=float, default=3.0)
    a = sub.add_parser("area", help="area in m2 of a polygon / rectangle / room around a seed point")
    a.add_argument("pdf"); a.add_argument("--page", type=int, default=1)
    a.add_argument("--pt-per-m", type=float, required=True)
    a.add_argument("--poly", help='"x,y x,y x,y ..." PDF pt'); a.add_argument("--rect", help="x0,y0,x1,y1")
    a.add_argument("--seed", help="x,y inside a closed room"); a.add_argument("--barrier", action="append", default=[],
                                                                              help='"x,y x,y" closing line (repeatable)')
    o = ap.parse_args(argv)
    doc = pymupdf.open(o.pdf)
    page = doc[o.page - 1]
    if o.cmd == "labels":
        found = labels(page)
        if not found:
            print("no area written as text on this page")
        for v, t, bb in found:
            print(f"{v:10.2f}  m2   [{t}]  at {tuple(round(c) for c in bb)}")
    elif o.cmd == "render":
        render(page, o.out, tuple(float(v) for v in o.clip.split(",")) if o.clip else None, o.zoom)
        print("wrote", o.out)
    else:
        k = o.pt_per_m
        if o.poly:
            print(f"{shoelace(_pts(o.poly)) / k / k:.2f} m2")
        if o.rect:
            x0, y0, x1, y1 = (float(v) for v in o.rect.split(","))
            print(f"{abs(x1 - x0) * abs(y1 - y0) / k / k:.2f} m2  ({abs(x1 - x0) / k:.3f} x {abs(y1 - y0) / k:.3f} m)")
        if o.seed:
            m2, info = room_fill(page, tuple(float(v) for v in o.seed.split(",")), k, [tuple(_pts(b)) for b in o.barrier])
            print(f"{m2:.2f} m2  (room fill, {info})")


if __name__ == "__main__":
    main()
