#!/usr/bin/env python3
"""Coffee shop unit 12: two plotted PDFs (ground + upper floor) -> one DXF in metres.

    python3 build_coffee12.py ground.pdf upper.pdf Coffee12_Plans.dxf

Scales were fitted on every dimension line of each PDF (max residual 4 mm, see SCALE_* below).
Ground floor: origin (0,0) = inner corner of the cafe at its front glass, left wall.
Upper floor : plotted rotated in the PDF; rotated back 90 deg CCW so its titles read horizontally,
              and aligned to the same front (Y=0) / back (Y=18.6) lines as the ground floor.
              It sits 25 m to the right: MOVE it (-25,0) to stack it over the ground floor.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".claude", "skills", "pdf-plan-to-cad", "scripts"))
import pdf2dxf  # noqa: E402
import pymupdf  # noqa: E402
from ezdxf import colors as ezc  # noqa: E402

# dimension id (from `pdf2dxf.py dims`) = value written on the plan (m)
GROUND_DIMS = {2705: 7, 2792: 3.3, 2771: 2.95, 2723: 3.45, 2832: 3.2, 2812: 3.3, 2656: 1.3, 2945: 2.7,
               3078: 14.68, 2885: 4.74, 2606: 10.2, 3121: 12.87, 2929: 3.5, 2861: 3.53, 3063: 9.8,
               3103: 18.6, 2747: 3.53, 203: 14, 2497: 7.2, 2907: 4.45, 2690: 4.8, 2621: 4.8}
UPPER_DIMS = {83: 20.1, 677: 1.5, 97: 6.45, 717: 12.15, 120: 10.2, 693: 26.02, 188: 26.02}
UPPER_AT_X = 25.0

PURPLE, MAGENTA, RED, BLACK, BROWN = (191, 0, 255), (255, 0, 255), (255, 0, 0), (0, 0, 0), (184, 46, 0)
H, V = (1, 0), (0, 1)
# exact label texts (the PDF text layer is in visual order with kashida fillers); bbox = glyph extents
GROUND_TEXT = [
    ("خدمات خارجية", (406.8, 190.8, 554.3, 215.1), 28.2, H, PURPLE),
    ("مصعد\\Pطلبات", (675.3, 228.5, 694.4, 241.5), 7.08, H, PURPLE),
    ("المساحة 121 متر", (508.3, 229.9, 638.2, 245.1), 18.72, H, BLACK),
    ("غاز", (278.1, 283.1, 294.3, 294.8), 14.04, H, PURPLE),
    ("مصعد", (592.1, 288.0, 608.0, 290.9), 7.08, H, PURPLE),
    ("ارتفاع 5 متر", (616.5, 396.6, 723.7, 415.1), 19.44, H, MAGENTA),
    ("المساحة 189 متر", (608.7, 444.2, 737.5, 459.6), 18.72, H, BLACK),
    ("جلسات خارجية", (365.9, 516.3, 493.2, 535.3), 21.84, H, PURPLE),
    ("كافيه", (625.7, 517.7, 707.9, 544.2), 32.76, H, RED),
    ("12", (639.2, 570.5, 661.6, 587.4), 23.52, H, PURPLE),
    ("جلسات خارجية", (440.7, 690.9, 568.0, 709.9), 21.84, H, PURPLE),
    ("ممشى تابع للمجمع", (454.5, 855.3, 704.3, 887.6), 32.76, H, PURPLE),
    ("معماري الدور الأرضي", (230.3, 1081.6, 722.4, 1148.5), 61.44, H, BROWN),
]
UPPER_TEXT = [
    ("سلالم", (609.6, 310.3, 629.7, 358.5), 20.4, V, BLACK),
    ("جلسات على الواجهه الأمامية", (178.9, 430.7, 208.0, 740.9), 29.4, V, MAGENTA),
    ("مطاعم وكافيهات علوية", (361.9, 589.8, 391.5, 850.3), 29.4, V, MAGENTA),
    ("ارتفاع 4 متر", (325.0, 591.0, 353.0, 745.3), 29.4, V, MAGENTA),
    ("المساحة 483 متر", (409.9, 595.4, 433.1, 790.3), 28.32, V, BLACK),
    ("حمامات", (572.8, 608.1, 582.4, 647.9), 16.08, V, RED),
    ("حمامات", (593.5, 721.2, 603.1, 760.9), 16.08, V, RED),
    ("12", (365.6, 530.3, 398.9, 574.4), 46.0, V, MAGENTA),
    ("معماري الدور الأول علوي", (707.0, 368.2, 756.7, 790.0), 45.6, V, BROWN),
]


def labels(rows):
    return [dict(text=t, bbox=b, size=s, dir=d, rgb=c) for t, b, s, d, c in rows]


def fitted(pdf, values):
    import collections
    paths = pdf2dxf.page_paths(pymupdf.open(pdf)[0])
    byp = collections.defaultdict(list)
    for d in pdf2dxf.find_dims(paths):
        byp[d["pid"]].append(d)
    return pdf2dxf.fit_scale(byp, values)


def shoelace(P):
    return abs(sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))) / 2


def add_area(doc, msp, xf, page_poly, name, layer, rgb):
    pts = [xf(p) for p in page_poly]
    a = shoelace(pts)
    if layer not in doc.layers:
        doc.layers.add(layer, color=pdf2dxf.nearest_aci(rgb)).off()
    attrs = {"layer": layer, "true_color": ezc.rgb2int(rgb), "lineweight": 50}
    msp.add_lwpolyline(pts, close=True, dxfattribs=attrs)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    msp.add_mtext(f"{name}\\P{a:.2f} م²", dxfattribs={**attrs, "style": "ARABIC", "char_height": 0.45,
                                                     "attachment_point": 5, "insert": (cx, cy)})
    return a


def main(ground_pdf, upper_pdf, out):
    kg, rg = fitted(ground_pdf, GROUND_DIMS)
    ku, ru = fitted(upper_pdf, UPPER_DIMS)
    print(f"ground {kg:.4f} pt/m, max residual {max(abs(r[2]) for r in rg) * 1000:.1f} mm")
    print(f"upper  {ku:.4f} pt/m, max residual {max(abs(r[2]) for r in ru) * 1000:.1f} mm")

    doc = pdf2dxf.new_doc()
    msp = doc.modelspace()
    g = pdf2dxf.convert_page(doc, ground_pdf, kg, origin_pt=(551.64, 622.32), at=(0, 0), prefix="GF-",
                             text_override=labels(GROUND_TEXT))
    u = pdf2dxf.convert_page(doc, upper_pdf, ku, rotate=90, origin_pt=(88.15, 206.8), at=(UPPER_AT_X, 0),
                             prefix="UF-", text_override=labels(UPPER_TEXT))
    print("ground:", dict(g["stats"]))
    print("upper :", dict(u["stats"]))

    # ---- area outlines (layers AREA-*, OFF by default)
    xg, xu = g["xform"], u["xform"]
    xin = lambda y: 267.72 + 0.09737 * (y - 375.72)  # inner face of the slanted west wall (page pt)
    A = {}
    A["ground_indoor"] = add_area(doc, msp, xg, [(551.64, 252.48), (754.44, 252.48), (754.44, 622.32), (551.64, 622.32)],
                                  "الدور الأرضي - داخلي", "AREA-INDOOR", (0, 160, 0))
    A["outdoor_side"] = add_area(doc, msp, xg, [(311.4, 252.48), (547.68, 252.48), (547.68, 622.32), (xin(622.32), 622.32),
                                                (xin(324.0), 324.0), (311.4, 324.0)],
                                 "جلسات خارجية جانبية", "AREA-OUTDOOR", (0, 120, 255))
    A["outdoor_front"] = add_area(doc, msp, xg, [(xin(626.28), 626.28), (754.44, 626.28), (754.44, 769.44), (xin(769.44), 769.44)],
                                  "جلسات خارجية أمامية", "AREA-OUTDOOR", (0, 120, 255))
    A["upper_indoor"] = add_area(doc, msp, xu, [(282.3, 206.8), (648.0, 206.8), (648.0, 989.9), (282.3, 989.9)],
                                 "الميزانين - داخلي", "AREA-INDOOR", (0, 160, 0))
    A["upper_terrace"] = add_area(doc, msp, xu, [(43.0, 206.8), (282.3, 206.8), (282.3, 989.9), (88.2, 989.9), (88.2, 513.7), (43.0, 513.7)],
                                  "التراس", "AREA-TERRACE", (255, 140, 0))
    for k, v in A.items():
        print(f"  {k:14s} {v:8.2f} m2")
    doc.saveas(out)
    print("wrote", out, f"{os.path.getsize(out) / 1e6:.1f} MB")
    return A


if __name__ == "__main__":
    main(*sys.argv[1:4])
