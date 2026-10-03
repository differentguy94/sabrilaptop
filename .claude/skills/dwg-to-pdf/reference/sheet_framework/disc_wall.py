"""Wall finishes - codes, strips, quantities (Jazeera Paints concrete effect etc.)."""
from sitemodel import G, M, EMPTY_G, EMPTY_M
LAYER = "A-WALL"
D = dict(color=1, h=0.12); C = dict(h=0.12, color=7)
# code: (name, spec, color, height)
W = {
    "W1": ("دهان خرساني Concrete Effect - دهانات الجزيرة لون رمادي خرساني", "Jazeera Paints Concrete Effect, grey, 2 coats on skim plaster", 8, 6.0),
    "W2": ("بلاط سبواي أسود لامع 7.5×15 سم بروبة سوداء - كامل الارتفاع", "Black gloss subway tile 7.5x15, dark grout, full height 2.8 m", 250, 2.8),
    "W3": ("بلاط سبواي أبيض لامع 7.5×15 سم - دورات المياه والغسيل", "White gloss subway tile 7.5x15, h 2.4 m", 7, 2.4),
    "W4": ("ألواح معدنية مثقبة سوداء (ثقوب Ø8 سم) - جدار مميز", "Perforated black steel panels Ø8 cm holes, feature wall", 5, 3.0),
    "W5": ("تكسية شرائح خشب صنوبر 4×4 سم كل 6 سم على جدار أسود", "Timber slat cladding 4x4 @6 cm on black backing", 32, 3.0),
    "W6": ("دهان جبس بورد دهانات الجزيرة أبيض/رمادي فاتح مطفي", "Jazeera Paints matt emulsion light grey", 9, 2.7),
    "W7": ("حروف 'EINSTEIN' عمودية مضيئة على الجدار الخرساني", "vertical illuminated EINSTEIN lettering", 6, 2.5),
    "W8": ("نيون 'IT IS RUDE TO STARE JUST EAT IT' على جدار الخدمة", "neon sign on BOH wall", 1, 1.2),
    "W9": ("تثبيت شاشة 65 بوصة على الجدار ارتفاع 2.2 م", "65\" TV wall mount, h 2.2 m", 4, 0.9),
    "W10": ("لوحة قائمة مضيئة فوق الكاونتر (3 لوحات 1.2×0.6 م)", "illuminated menu boards above counter", 2, 0.6),
    "W11": ("ألواح ساندويتش بانل 10 سم معزولة - غرفة التجميد", "insulated sandwich panels 10 cm, freezer", 150, 2.4),
}
# strips: (code, [(x,y),...], offset side handled by giving the inner line directly)
STRIPS_G = [
    ("W1", [(7.5, 27.2), (7.5, 36.4)]), ("W1", [(9.6, 36.4), (15.2, 36.4)]), ("W1", [(24.3, 35.1), (31.4, 35.1)]), ("W1", [(31.4, 27.2), (31.4, 30.3)]),
    ("W1", [(7.5, 36.6), (7.5, 42.3)]), ("W1", [(24.4, 35.1), (24.4, 38.8)]),
    ("W2", [(15.4, 38.8), (24.2, 38.8)]), ("W2", [(15.4, 35.1), (15.4, 38.8)]), ("W2", [(15.0, 35.6), (21.0, 35.6)]), ("W2", [(15.1, 34.95), (21.0, 34.95)]),
    ("W3", [(7.5, 36.6), (9.4, 36.6)]), ("W3", [(9.4, 36.6), (9.4, 39.6)]), ("W3", [(30.5, 35.1), (30.5, 38.8)]), ("W3", [(30.5, 38.8), (31.4, 38.8)]), ("W3", [(28.3, 35.1), (28.3, 36.9)]),
    ("W4", [(23.4, 27.4), (23.4, 31.3)]), ("W4", [(24.3, 31.4), (30.5, 31.4)]), ("W4", [(31.4, 31.7), (31.4, 34.9)]),
    ("W5", [(9.7, 27.2), (15.0, 27.2)]), ("W5", [(21.5, 27.2), (23.2, 27.2)]),
]
def strip(s, code, pts):
    s.pline(pts, width=0.09, color=W[code][2])
    mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
    horiz = abs(pts[0][1] - pts[-1][1]) < 0.01
    bx, by = (mx, my + 0.35) if horiz else (mx + 0.4, my)
    s.circle(bx, by, 0.26, color=7, lw=35); s.text(bx, by, code, h=0.11, attach=5, color=7)
def legend_rows(codes):
    rows = []
    for c in codes:
        nm, spec, col, h = W[c]
        def fn(s, x, y, col=col, c=c): s.pline([(x - 0.4, y), (x + 0.4, y)], width=0.09, color=col); s.text(x, y + 0.14, c, h=0.08, attach=5, color=7)
        rows.append((fn, f"{c} - {nm}", f"{spec} / h = {h} m"))
    return rows
def qty_table(s, x, y, rows, title):
    w, rh = 11.0, 0.4; cols = [0.9, 1.4, 2.0, 6.7]
    s.rect(x, y - rh * (len(rows) + 2), x + w, y, color=7, layer="LEGEND")
    s.hatch([(x, y - rh), (x + w, y - rh), (x + w, y), (x, y)], color=254, layer="LEGEND")
    s.text(x + w / 2, y - rh / 2, title, h=0.17, attach=5, color=7, layer="LEGEND")
    xs = [x]
    for c in cols: xs.append(xs[-1] + c)
    for xx in xs[1:-1]: s.line((xx, y - rh), (xx, y - rh * (len(rows) + 2)), color=7, layer="LEGEND")
    hdr = ["الكود", "المساحة م2", "الكمية +10%", "المادة"]
    for i, r in enumerate([None] + rows):
        cy = y - rh * (i + 1) - rh / 2
        if r is None:
            for k, h in enumerate(hdr): s.text((xs[k] + xs[k + 1]) / 2, cy, h, h=0.11, attach=5, color=7, layer="LEGEND")
            continue
        s.line((x, cy - rh / 2), (x + w, cy - rh / 2), color=8, lw=5, layer="LEGEND")
        code, a, q, name = r
        s.text((xs[0] + xs[1]) / 2, cy, code, h=0.12, attach=5, color=7, layer="LEGEND")
        s.text((xs[1] + xs[2]) / 2, cy, f"{a:.0f}", h=0.12, attach=5, color=7, layer="LEGEND")
        s.text((xs[2] + xs[3]) / 2, cy, q, h=0.11, attach=5, color=7, layer="LEGEND")
        s.text(xs[4] - 0.12, cy, name, h=0.11, attach=6, color=7, layer="LEGEND", width=6.5)
def elev_marker(s, x, y, letter, rot):
    import math
    s.circle(x, y, 0.3, color=7, lw=35); s.text(x, y, letter, h=0.14, attach=5, color=7)
    a = math.radians(rot); s.pline([(x + 0.3 * math.cos(a + 2.3), y + 0.3 * math.sin(a + 2.3)), (x + 0.6 * math.cos(a), y + 0.6 * math.sin(a)), (x + 0.3 * math.cos(a - 2.3), y + 0.3 * math.sin(a - 2.3))], closed=True, color=7)
def draw_G(s):
    for code, pts in STRIPS_G: strip(s, code, pts)
    for x, y, rot in G["tv"]:
        s.rect(x - 0.08, y - 0.7, x + 0.08, y + 0.7, color=4, lw=35) if rot in (90, 270) else s.rect(x - 0.7, y - 0.08, x + 0.7, y + 0.08, color=4, lw=35)
        s.text(x + (0.3 if rot == 90 else -0.3 if rot == 270 else 0), y + (0 if rot in (90, 270) else -0.3), "W9", h=0.1, attach=5, color=7)
    s.rect(15.6, 38.6, 23.3, 38.78, color=2, lw=35); s.text(19.5, 38.4, "W10 - لوحات القائمة المضيئة", h=0.1, attach=5, color=7)
    s.box_label(14.9, 36.3, "W7 EINSTEIN", h=0.09, color=6); s.box_label(7.6, 33.9, "W7", h=0.09, color=6)
    s.box_label(26.0, 34.85, "W8 NEON", h=0.09, color=1)
    for x, y, L, rot in [(19.5, 31.5, "A", 90), (10.0, 32.5, "B", 180), (27.5, 29.5, "C", 90), (19.5, 36.8, "D", 90)]: elev_marker(s, x, y, L, rot)
    # dimensions of finishes
    s.dim((15.4, 38.8), (24.2, 38.8), offset=0.5, **D); s.dim((15.0, 35.6), (21.0, 35.6), offset=-1.0, **D); s.dim((24.3, 31.4), (30.5, 31.4), offset=-0.6, **D)
    s.dim((7.5, 27.2), (7.5, 36.4), offset=-0.5, horizontal=False, **D); s.dim((23.4, 27.4), (23.4, 31.3), offset=-0.6, horizontal=False, **D); s.dim((9.7, 27.2), (15.0, 27.2), offset=-0.5, **D)
    s.dim((9.4, 36.6), (9.4, 39.6), offset=0.5, horizontal=False, **D); s.dim((30.5, 35.1), (30.5, 38.8), offset=-0.5, horizontal=False, **D)
    s.leader([(7.5, 31.0), (6.0, 30.0)]); s.text(6.0, 29.9, "W1 دهان Concrete Effect\\Pدهانات الجزيرة رمادي\\Pكامل الارتفاع 6.0 م", attach=3, **C)
    s.leader([(19.8, 38.8), (19.0, 40.0)]); s.text(19.0, 40.1, "W2 بلاط سبواي أسود لامع كامل ارتفاع المطبخ 2.8 م\\Pعلى ألواح أسمنتية + عزل مائي", attach=8, **C)
    s.leader([(27.4, 31.4), (28.6, 30.2)]); s.text(28.6, 30.1, "W4 ألواح معدنية مثقبة سوداء خلف البوثات\\Pارتفاع 3.0 م مع إضاءة خلفية", attach=1, **C)
    s.leader([(12.3, 27.2), (12.3, 26.5)]); s.text(12.3, 26.45, "W5 تكسية شرائح خشب خلف بوثات الواجهة ارتفاع 1.2 م", attach=2, **C)
    x0, y0, x1, y1 = EMPTY_G
    s.legend(x0 + 0.2, y1 - 0.1, "جدول رموز تشطيب الجدران - WALL FINISH LEGEND", legend_rows(["W1", "W2", "W3", "W4", "W5", "W7", "W8", "W9", "W10"]), w=10.5, rh=0.46)
    rows = [("W1", 230, "25 لتر × 2 طبقة", "دهان Concrete Effect دهانات الجزيرة"), ("W2", 62, "68 م2 بلاط", "سبواي أسود لامع"), ("W3", 48, "53 م2 بلاط", "سبواي أبيض"), ("W4", 32, "35 م2 ألواح", "معدن مثقب أسود"), ("W5", 8, "9 م2", "شرائح خشب"), ("W9", 3, "3 قطعة", "شاشة 65 بوصة"), ("W10", 3, "3 قطعة", "لوحة قائمة مضيئة")]
    qty_table(s, 22.4, 45.0, rows, "جدول كميات تشطيب الجدران - الأرضي")
    s.notes(34.8, 41.4, ["W1: تنعيم الجدران بمعجون، أساس، ثم طبقتان دهانات الجزيرة Concrete Effect رمادي خرساني بالفرشاة الدائرية", "W2/W3: عزل مائي إسمنتي خلف البلاط في المطبخ ودورات المياه، روبة إيبوكسي",
                         "W4: ألواح حديد 2 مم مثقبة Ø8 سم مطلية بودرة أسود مطفي على هيكل خشبي", "جميع الأخشاب معالجة ضد الحريق (Class B)", "الكميات شاملة 10% هالك"], h=0.13, w=12.0, title="ملاحظات تشطيب الجدران")
def draw_M(s):
    r = M["rooms"]
    for key in ("r1", "r2", "r3", "corridor", "office"):
        x0, y0, x1, y1 = r[key]; strip(s, "W6", [(x0 + 0.1, y0 + 0.1), (x1 - 0.1, y0 + 0.1)]); strip(s, "W6", [(x0 + 0.1, y1 - 0.1), (x1 - 0.1, y1 - 0.1)])
    for key in ("prep", "wc_a", "wc_b", "store", "lobby"):
        x0, y0, x1, y1 = r[key]; strip(s, "W3", [(x0 + 0.1, y1 - 0.1), (x1 - 0.1, y1 - 0.1)]); strip(s, "W3", [(x0 + 0.1, y0 + 0.1), (x0 + 0.1, y1 - 0.1)])
    x0, y0, x1, y1 = r["freezer_room"]; strip(s, "W11", [(x0 + 0.1, y0 + 0.1), (x1 - 0.1, y0 + 0.1), (x1 - 0.1, y1 - 0.1), (x0 + 0.1, y1 - 0.1), (x0 + 0.1, y0 + 0.1)])
    strip(s, "W3", [(8.1, 10.2), (8.1, 13.1)])
    s.dim((22.0, 13.4), (31.5, 13.4), offset=0.5, **D); s.dim((7.4, 6.5), (20.9, 6.5), offset=-0.6, **D); s.dim((23.3, 6.5), (26.5, 6.5), offset=-1.2, **D)
    s.leader([(26.0, 13.4), (25.5, 15.3)]); s.text(25.5, 15.4, "W3 بلاط سبواي أبيض لامع ارتفاع 2.4 م على كامل منطقة التحضير والغسيل", attach=2, **C)
    s.leader([(14.0, 6.6), (14.0, 5.3)]); s.text(14.0, 5.2, "W6 جبس/بلاستر مدهون دهانات الجزيرة مطفي رمادي فاتح", attach=8, **C)
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    x0, y0, x1, y1 = EMPTY_M
    s.legend(x0 + 0.2, y1 - 0.1, "جدول رموز تشطيب الجدران - WALL FINISH LEGEND", legend_rows(["W3", "W6", "W11"]), w=10.5, rh=0.46)
    rows = [("W3", 95, "105 م2 بلاط", "سبواي أبيض لامع"), ("W6", 150, "17 لتر × 2 طبقة", "دهانات الجزيرة مطفي"), ("W11", 40, "44 م2 ألواح", "ساندويتش بانل 10 سم")]
    qty_table(s, 15.6, 20.0, rows, "جدول كميات تشطيب الجدران - الميزانين")
    s.notes(34.8, 17.0, ["وزرة 10 سم سيراميك في الغرف والممر", "زوايا ألمنيوم حماية على أركان الممرات"], h=0.13, w=8.0, title="ملاحظات")
