"""Floor finishes - zones, hatches, areas, quantities."""
from sitemodel import G, M, EMPTY_G, EMPTY_M
LAYER = "A-FLOOR"
D = dict(color=1, h=0.12); C = dict(h=0.12, color=7)

def area(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2
def rect(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

# (code, name_ar, spec, pattern, scale, color)
FIN = {
    "FL1": ("أرضية خرسانية مصقولة (ميكروسمنت رمادي)", "Micro-cement polished concrete grey, 3 mm + sealer", "DOTS", 1.5, 8),
    "FL2": ("بلاط إسمنتي مزخرف أسود/أبيض 20×20 سم", "Patterned cement tiles 20x20 black/white, grey grout", "ANSI37", 0.35, 250),
    "FL3": ("بورسلان مانع للانزلاق R11 رمادي 60×60 سم", "Non-slip porcelain 60x60 grey R11, epoxy grout", "NET", 4.8, 3),
    "FL4": ("بورسلان مانع للانزلاق 60×60 سم - دورات المياه", "Anti-slip porcelain 60x60 light grey", "NET", 4.8, 4),
    "FL5": ("أرضية خرسانية ناعمة مدهونة إيبوكسي", "Smooth concrete + epoxy paint", "DOTS", 2.5, 8),
    "FL6": ("سيراميك 60×60 بيج - غرف السكن والممر", "Ceramic 60x60 beige", "NET", 4.8, 32),
    "FL7": ("أرضية إيبوكسي معزولة - غرفة التجميد", "Insulated epoxy floor (freezer room)", "ANSI31", 0.6, 150),
    "FL8": ("باركيه لامينيت 8 مم - المكتب", "Laminate parquet 8 mm", "ANSI31", 0.4, 30),
}
ZONES_G = [
    ("FL2", rect(9.8, 30.2, 15.6, 32.7)), ("FL2", rect(17.6, 27.2, 21.4, 29.3)), ("FL2", rect(23.4, 31.5, 30.6, 33.2)),
    ("FL2", rect(7.4, 27.3, 9.5, 34.6)), ("FL2", rect(15.0, 33.6, 21.0, 34.9)),
    ("FL3", [(15.3, 35.0), (31.5, 35.0), (31.5, 38.9), (15.3, 38.9)]),
    ("FL4", rect(7.4, 36.5, 9.5, 39.7)), ("FL5", rect(7.4, 39.7, 9.5, 42.4)),
]
ZONES_M = [
    ("FL6", rect(7.4, 6.5, 20.9, 11.5)), ("FL3", rect(7.4, 11.5, 9.5, 13.6)), ("FL4", rect(15.5, 11.5, 20.9, 13.6)),
    ("FL3", rect(21.0, 9.4, 31.5, 13.5)), ("FL7", rect(23.3, 6.5, 26.5, 9.4)), ("FL3", rect(26.7, 6.5, 29.6, 9.4)),
    ("FL8", rect(29.7, 6.5, 31.5, 8.0)), ("FL3", rect(21.0, 6.5, 23.2, 9.4)), ("FL5", rect(7.4, 13.6, 9.5, 17.4)),
]

def bubble(s, x, y, code):
    s.circle(x, y, 0.32, color=7, lw=35); s.text(x, y, code, h=0.13, attach=5, color=7)

def draw_zone(s, code, pts, label_at=None, a_override=None):
    nm, spec, pat, sc, col = FIN[code]
    s.hatch(pts, pattern=pat, scale=sc, color=col)
    s.pline(pts, closed=True, lw=35, color=col)
    a = a_override if a_override is not None else area(pts)
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    if label_at: cx, cy = label_at
    bubble(s, cx, cy + 0.25, code)
    s.text(cx, cy - 0.25, f"المساحة = {a:.1f} م2", h=0.11, attach=5, color=7)
    return a

def schedule(s, x, y, rows, title):
    w, rh = 11.0, 0.42
    cols = [0.9, 1.3, 1.3, 7.5]  # code, area, qty, name
    s.rect(x, y - rh * (len(rows) + 2), x + w, y, color=7, layer="LEGEND")
    s.hatch([(x, y - rh), (x + w, y - rh), (x + w, y), (x, y)], color=254, layer="LEGEND")
    s.text(x + w / 2, y - rh / 2, title, h=0.17, attach=5, color=7, layer="LEGEND")
    xs = [x]
    for c in cols: xs.append(xs[-1] + c)
    for xx in xs[1:-1]: s.line((xx, y - rh), (xx, y - rh * (len(rows) + 2)), color=7, layer="LEGEND")
    hdr = ["الكود", "المساحة م2", "الكمية +10%", "المادة والمواصفات"]
    for i, (code, a, q, name) in enumerate([("", "", "", "")] + rows):
        cy = y - rh * (i + 1) - rh / 2
        if i == 0:
            for k, h in enumerate(hdr): s.text((xs[k] + xs[k + 1]) / 2, cy, h, h=0.11, attach=5, color=7, layer="LEGEND")
            continue
        s.line((x, cy - rh / 2), (x + w, cy - rh / 2), color=8, lw=5, layer="LEGEND")
        s.text((xs[0] + xs[1]) / 2, cy, code, h=0.12, attach=5, color=7, layer="LEGEND")
        s.text((xs[1] + xs[2]) / 2, cy, f"{a:.1f}", h=0.12, attach=5, color=7, layer="LEGEND")
        s.text((xs[2] + xs[3]) / 2, cy, f"{q:.0f} م2", h=0.12, attach=5, color=7, layer="LEGEND")
        s.text(xs[4] - 0.12, cy, name, h=0.11, attach=6, color=7, layer="LEGEND", width=7.3)
    return rh * (len(rows) + 2)

def legend_rows():
    rows = []
    for code, (nm, spec, pat, sc, col) in FIN.items():
        def fn(s, x, y, pat=pat, sc=sc, col=col):
            s.hatch([(x - 0.4, y - 0.17), (x + 0.4, y - 0.17), (x + 0.4, y + 0.17), (x - 0.4, y + 0.17)], pattern=pat, scale=sc * 0.6, color=col)
            s.rect(x - 0.4, y - 0.17, x + 0.4, y + 0.17, color=col)
        rows.append((fn, f"{code} - {nm}", spec))
    return rows

def draw_G(s):
    totals = {}
    hall_a = area(G["hall"]); tile_a = 0
    s.hatch(G["hall"], pattern="DOTS", scale=1.5, color=8)      # FL1 base, islands drawn on top
    for code, pts in ZONES_G:
        a = draw_zone(s, code, pts); totals[code] = totals.get(code, 0) + a
        if code == "FL2": tile_a += a
    totals["FL1"] = hall_a - tile_a
    bubble(s, 19.0, 32.0, "FL1"); s.text(19.0, 31.5, f"المساحة = {totals['FL1']:.1f} م2 (صالة الجلوس)", h=0.12, attach=5, color=7)
    # slope arrows to kitchen drains
    for x, y in [(16.3, 37.2), (19.5, 37.2), (22.5, 37.2)]:
        s.pline([(x - 1.0, y + 0.6), (x, y)], color=1, lw=13); s.pline([(x + 1.0, y + 0.6), (x, y)], color=1, lw=13)
        s.text(x, y - 0.25, "ميل 1% للمصرف", h=0.08, attach=5, color=1)
    # dimensions of islands
    s.dim((9.8, 30.2), (15.6, 30.2), offset=-0.5, **D); s.dim((15.6, 30.2), (15.6, 32.7), offset=0.4, horizontal=False, **D)
    s.dim((17.6, 27.2), (21.4, 27.2), offset=0.0, **D); s.dim((21.4, 27.2), (21.4, 29.3), offset=0.4, horizontal=False, **D)
    s.dim((23.4, 31.5), (30.6, 31.5), offset=-0.7, **D); s.dim((30.6, 31.5), (30.6, 33.2), offset=0.5, horizontal=False, **D)
    s.dim((7.4, 27.3), (9.5, 27.3), offset=-0.5, **D); s.dim((9.5, 27.3), (9.5, 34.6), offset=0.5, horizontal=False, **D)
    s.dim((15.0, 33.6), (21.0, 33.6), offset=-0.5, **D); s.dim((15.3, 35.0), (31.5, 35.0), offset=-0.6, **D); s.dim((15.3, 35.0), (15.3, 38.9), offset=-0.6, horizontal=False, **D)
    s.leader([(12.7, 31.45), (12.0, 29.5)]); s.text(12.0, 29.4, "جزيرة بلاط إسمنتي مزخرف تحت الطاولة المشتركة", attach=3, **C)
    s.leader([(23.0, 37.0), (22.0, 40.2)]); s.text(22.0, 40.3, "بورسلان مانع للانزلاق R11 بميول 1% نحو مصارف الأرضية\\Pوزرة 10 سم مقعرة (cove) على محيط المطبخ", attach=8, **C)
    s.leader([(8.5, 41.0), (10.5, 42.6)]); s.text(10.5, 42.7, "غرفة الدرج: خرسانة ناعمة + إيبوكسي", attach=8, **C)
    s.leader([(19.0, 32.0), (17.5, 33.2)]); s.text(17.5, 33.3, "ميكروسمنت رمادي مصقول 3 مم مع طبقة حماية بولي يوريثان", attach=2, **C)
    x0, y0, x1, y1 = EMPTY_G
    s.legend(x0 + 0.2, y1 - 0.1, "جدول رموز الأرضيات - FLOOR FINISH LEGEND", legend_rows()[:5], w=10.5, rh=0.46)
    rows = [(c, totals[c], totals[c] * 1.1, FIN[c][0]) for c in ("FL1", "FL2", "FL3", "FL4", "FL5") if c in totals]
    schedule(s, 22.4, 45.0, rows, "جدول كميات الأرضيات - الطابق الأرضي")
    s.notes(34.8, 41.8, ["مناسيب: صالة الجلوس ±0.00، المطبخ ودورات المياه -0.02 م مع ميول 1% للمصارف", "تركيب البورسلان بلاصق إسمنتي C2TE ومعجون إيبوكسي للمطبخ",
                         "عزل مائي إسمنتي مرن طبقتين تحت أرضيات المطبخ ودورات المياه مع رفع 30 سم على الجدران", "عتبات ستانلس ستيل عند تغير المادة", "الكميات شاملة 10% هالك"],
            h=0.13, w=12.0, title="ملاحظات الأرضيات")

def draw_M(s):
    totals = {}
    for code, pts in ZONES_M:
        a = draw_zone(s, code, pts); totals[code] = totals.get(code, 0) + a
    s.hatch(M["void"], pattern="ANSI31", scale=1.2, color=8); s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    for x, y in [(26.5, 11.7), (29.6, 11.7)]:
        s.pline([(x - 1.0, y + 0.5), (x, y)], color=1, lw=13); s.pline([(x + 1.0, y + 0.5), (x, y)], color=1, lw=13)
        s.text(x, y - 0.22, "ميل 1%", h=0.08, attach=5, color=1)
    s.dim((7.4, 6.5), (20.9, 6.5), offset=-0.6, **D); s.dim((20.9, 6.5), (20.9, 11.5), offset=0.4, horizontal=False, **D)
    s.dim((21.0, 9.4), (31.5, 9.4), offset=-0.5, **D); s.dim((31.5, 9.4), (31.5, 13.5), offset=0.5, horizontal=False, **D)
    s.dim((23.3, 6.5), (26.5, 6.5), offset=-1.2, **D); s.dim((26.7, 6.5), (29.6, 6.5), offset=-1.2, **D); s.dim((15.5, 11.5), (20.9, 11.5), offset=0.0, **D)
    s.leader([(25.0, 12.5), (24.0, 15.3)]); s.text(24.0, 15.4, "بورسلان مانع للانزلاق R11 مع معجون إيبوكسي\\Pوميول نحو مصارف منطقة الغسيل", attach=2, **C)
    s.leader([(24.9, 8.0), (24.9, 5.3)]); s.text(24.9, 5.2, "غرفة التجميد: أرضية إيبوكسي معزولة فوق ألواح بولي يوريثان", attach=8, **C)
    x0, y0, x1, y1 = EMPTY_M
    s.legend(x0 + 0.2, y1 - 0.1, "جدول رموز الأرضيات - FLOOR FINISH LEGEND", legend_rows()[2:], w=10.5, rh=0.46)
    rows = [(c, totals[c], totals[c] * 1.1, FIN[c][0]) for c in ("FL6", "FL3", "FL4", "FL7", "FL8", "FL5") if c in totals]
    schedule(s, 15.6, 20.0, rows, "جدول كميات الأرضيات - الميزانين")
    s.notes(34.8, 16.5, ["غرف السكن والممر: سيراميك 60×60 بيج مع وزرة 10 سم", "منطقة الغسيل: بورسلان R11 وميول 1% ومصارف أرضية", "الكميات شاملة 10% هالك"], h=0.13, w=8.0, title="ملاحظات")
