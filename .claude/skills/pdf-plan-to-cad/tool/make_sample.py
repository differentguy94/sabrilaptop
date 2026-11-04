#!/usr/bin/env python3
"""Builds sample_plan.pdf: a small 12 x 8 m cafe at 1:100 on A4 landscape, used as the example
the web tool opens with. Dimensions carry real text so the tool can auto-calibrate from them.

    pip install pymupdf pymupdf-fonts && python3 make_sample.py sample_plan.pdf
Expected by room click: hall 79.12 m2 (79.60 - door swing 0.64 + entrance 0.16), kitchen 16.33 m2
(15.60 + doorway 0.09 + door swing 0.64); gross 96 m2.
"""
import math
import sys

import pymupdf

M = 72 / 25.4 * 10  # 1:100 -> 1 m = 10 mm on paper = 28.3465 pt
OX, OY = 150, 105   # paper position of the inner top-left corner


def P(x, y):
    return (OX + x * M, OY + y * M)


def main(out):
    doc = pymupdf.open()
    page = doc.new_page(width=842, height=595)
    sh = page.new_shape()

    def line(a, b, w=0.7, col=(0, 0, 0)):
        sh.draw_line(P(*a), P(*b))
        sh.finish(color=col, width=w, closePath=False)

    def poly(pts, w=0.7, col=(0, 0, 0), close=True):  # finish() closes paths unless told not to
        sh.draw_polyline([P(*p) for p in pts] + ([P(*pts[0])] if close else []))
        sh.finish(color=col, width=w, closePath=close)

    # outer walls 0.2 m with an entrance (double glass door) at x 5.2..6.8 on the front (y = 8)
    poly([(-0.2, -0.2), (12.2, -0.2), (12.2, 8.2), (6.8, 8.2), (6.8, 8), (12, 8), (12, 0), (0, 0), (0, 8),
          (5.2, 8), (5.2, 8.2), (-0.2, 8.2)], w=1.1)
    line((5.2, 8.1), (6.8, 8.1), w=0.5, col=(0.2, 0.6, 0.8))          # glass door
    # kitchen partitions 0.1 m: x 7.95..8.05 (y 0..4.05) and y 3.95..4.05 (x 7.95..12)
    poly([(7.95, 0), (7.95, 2.6), (8.05, 2.6), (8.05, 0)], close=False)
    poly([(7.95, 3.5), (7.95, 4.05), (12, 4.05)], close=False)
    poly([(8.05, 3.5), (8.05, 3.95), (12, 3.95)], close=False)
    # kitchen door: leaf (hinge at y 3.5, opening into the hall) + swing arc to the other jamb
    line((7.95, 3.5), (7.05, 3.5), col=(0.85, 0, 0))
    pts = [(7.95 - 0.9 * math.cos(t), 3.5 - 0.9 * math.sin(t)) for t in [i * (math.pi / 2) / 16 for i in range(17)]]
    poly(pts, col=(0.85, 0, 0), close=False)
    line((7.95, 2.6), (8.05, 2.6))
    line((7.95, 3.5), (8.05, 3.5))  # jamb: closes the partition cavity at the door
    # hall furniture: round tables with four chairs
    for cx, cy in [(1.6, 1.8), (4.0, 1.8), (1.6, 5.2), (4.0, 5.2), (6.4, 5.2), (9.6, 6.2)]:
        sh.draw_circle(P(cx, cy), 0.45 * M)
        sh.finish(color=(1, 0.42, 0.7), width=0.6)
        for dx, dy in [(0.75, 0), (-0.75, 0), (0, 0.75), (0, -0.75)]:
            x, y = cx + dx, cy + dy
            sh.draw_rect(pymupdf.Rect(P(x - 0.2, y - 0.2), P(x + 0.2, y + 0.2)))
            sh.finish(color=(1, 0.42, 0.7), width=0.6)
    # counter in the kitchen
    poly([(8.6, 0.5), (11.5, 0.5), (11.5, 1.1), (8.6, 1.1)], col=(0.3, 0.3, 0.3))

    sh.commit()

    # dimensions: line + 45 degree ticks + extension lines + real text
    def dim(a, b, off, text):
        (x0, y0), (x1, y1) = a, b
        d = page.new_shape()
        e = 0.15 if off > 0 else -0.15
        if abs(y1 - y0) < 1e-9:  # horizontal
            yd = y0 + off
            ends = [P(x0, yd), P(x1, yd)]
            d.draw_line(P(x0, y0 + e), P(x0, yd + e)); d.draw_line(P(x1, y1 + e), P(x1, yd + e))
        else:
            xd = x0 + off
            ends = [P(xd, y0), P(xd, y1)]
            d.draw_line(P(x0 + e, y0), P(xd + e, y0)); d.draw_line(P(x1 + e, y1), P(xd + e, y1))
        d.draw_line(*ends)
        for q in ends:
            q = pymupdf.Point(q)
            d.draw_line(q + (-2.1, 2.1), q + (2.1, -2.1))
        d.finish(color=(0, 0, 0), width=0.5, closePath=False)
        d.commit()
        (ax, ay), (bx, by) = ends
        if abs(by - ay) < 1e-9:
            page.insert_text(((ax + bx) / 2 - len(text) * 2.35, ay - 2.5), text, fontsize=8.5, fontname="helv")
        else:
            page.insert_text((ax - 2.5, (ay + by) / 2 + len(text) * 2.35), text, fontsize=8.5, fontname="helv", rotate=90)

    dim((0, -0.2), (12, -0.2), -1.0, "12.00")
    dim((0, -0.2), (7.95, -0.2), -0.55, "7.95")
    dim((7.95, -0.2), (12, -0.2), -0.55, "4.05")
    dim((-0.2, 0), (-0.2, 8), -1.0, "8.00")
    dim((12.2, 0), (12.2, 3.95), 0.8, "3.95")
    dim((12.2, 4.05), (12.2, 8), 0.8, "3.95")

    # Arabic labels (shaped by MuPDF/HarfBuzz) with FiraGO
    arch = pymupdf.Archive()
    css = pymupdf.css_for_pymupdf_font("figo", archive=arch, name="figo")
    css += "* {font-family: figo;} p {margin:0; text-align:center;}"

    def label(cx, cy, html, w=5.0, h=1.0):
        x, y = P(cx, cy)
        r = pymupdf.Rect(x - w * M / 2, y - h * M / 2, x + w * M / 2, y + h * M / 2)
        page.insert_htmlbox(r, f'<div dir="rtl">{html}</div>', css=css, archive=arch)

    label(4.0, 3.45, '<p style="font-size:15px;color:#7a1fa2">صالة الجلوس</p>'
                     '<p style="font-size:11px">المساحة 96 م²</p>', h=1.4)
    label(10.0, 2.4, '<p style="font-size:13px;color:#7a1fa2">مطبخ</p>', w=3)
    label(6.0, 9.7, '<p style="font-size:17px;color:#b02e00">مثال: مقهى صغير — الدور الأرضي</p>', w=9, h=1.2)
    doc.subset_fonts()
    doc.save(out, garbage=4, deflate=True)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sample_plan.pdf")
