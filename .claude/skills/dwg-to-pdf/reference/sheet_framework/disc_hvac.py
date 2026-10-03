"""HVAC - exposed black ductwork (ground hall + kitchen) and split/cassette units (mezzanine).
مخطط التكييف - الدكت.  Ground: 3 concealed ducted splits above the BOH ceiling feeding two exposed round
supply ducts (A along the back of the hall, B near the facade) + a kitchen supply duct; return grilles in
the BOH wall; fresh-air louvre at the top of the right glass wall; 4 condensing units on the roof.
Mezzanine: wall splits in the staff rooms / corridor / office, 2 ceiling cassettes over the prep walkway,
6 condensing units on the roof, refrigerant trunk + condensate drains to the nearest floor drains."""
from sitemodel import G, M, EMPTY_G, EMPTY_M

LAYER = "M-HVAC"
RED = 1          # dimensions
BLK = 7
CND = 150        # condensate drain lines (blue)

# ----------------------------------------------------------------------------- symbols
def rdiff(s, x, y, r=0.15):
    """round ceiling diffuser (concentric rings as in the renders)"""
    s.circle(x, y, r)
    s.circle(x, y, r * 0.62, lw=9)
    s.circle(x, y, r * 0.3, lw=9)
    s.dot(x, y, r * 0.1)

def tstat(s, x, y):
    s.circle(x, y, 0.16)
    s.text(x, y, "T", h=0.14, attach=5)

def ahu(s, x, y, tag, cap, w=1.1, h=0.55):
    """concealed ducted split unit above the false ceiling: dashed box + tag"""
    s.pline([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)],
            closed=True, lw=35, linetype="DASHED")
    s.text(x, y, tag + ("\\P" + cap if cap else ""), h=0.085, attach=5)

def refr(s, pts):
    """refrigerant pipe pair (dashed)"""
    s.pline(pts, lw=13, linetype="DASHED")

def cond(s, pts):
    """condensate drain PVC (blue, hidden linetype)"""
    s.pline(pts, lw=13, linetype="HIDDEN", color=CND)

def roof_zone(s, x0, y0, x1, y1):
    s.pline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True, lw=9, linetype="DASHED", color=8)

# ----------------------------------------------------------------------------- legend
def L_duct(s, x, y):
    s.duct([(x - 0.42, y), (x + 0.42, y)], w=0.22)
def L_diff(s, x, y):
    rdiff(s, x, y, 0.15)
def L_rag(s, x, y):
    s.grille(x, y, w=0.6, h=0.2)
def L_ahu(s, x, y):
    ahu(s, x, y, "AHU", "", w=0.8, h=0.32)
def L_odu(s, x, y):
    s.rect(x - 0.3, y - 0.12, x + 0.3, y + 0.12); s.circle(x, y, 0.09)
def L_tst(s, x, y):
    tstat(s, x, y)
def L_fa(s, x, y):
    s.grille(x, y, w=0.5, h=0.16); s.line((x, y + 0.08), (x, y + 0.2), lw=9)
def L_refr(s, x, y):
    refr(s, [(x - 0.42, y + 0.06), (x + 0.42, y + 0.06)]); cond(s, [(x - 0.42, y - 0.08), (x + 0.42, y - 0.08)])
def L_split(s, x, y):
    s.split_unit(x, y, w=0.8, h=0.22)
def L_cas(s, x, y):
    s.cassette(x, y, size=0.42)

LEGEND_G = [
    (L_duct, "دكت تغذية دائري مكشوف أسود مطفي Ø450 / Ø300", "exposed round supply duct, matt black GI"),
    (L_diff, "ناشر هواء سقفي دائري Ø300 (مطبخ Ø250)", "round ceiling diffuser"),
    (L_rag, "شبكة رجوع هواء 600×600 في الجدار فوق الأبواب", "return air grille 600×600 in wall"),
    (L_ahu, "وحدة تكييف مخفية فوق السقف المستعار (ducted)", "concealed ducted split indoor unit"),
    (L_odu, "وحدة خارجية (مكثف) على السطح", "outdoor condensing unit on roof"),
    (L_tst, "ثرموستات جداري ارتفاع 150 سم", "wall thermostat h=1.50 m"),
    (L_fa, "مأخذ هواء نقي Ø250 مع دامبر يدوي", "fresh-air louvre + volume damper"),
    (L_refr, "مواسير فريون نحاس معزولة / تصريف مكثفات PVC (أزرق)", "refrigerant pipes (dashed) / condensate (blue)"),
]
LEGEND_M = [
    (L_split, "وحدة سبليت جدارية ارتفاع 220 سم", "wall-mounted split unit h=2.20 m"),
    (L_cas, "كاسيت سقفي 4 اتجاهات 60×60", "4-way ceiling cassette"),
    (L_odu, "وحدة خارجية (مكثف) على السطح", "outdoor condensing unit on roof"),
    (L_refr, "مواسير فريون نحاس معزولة / تصريف مكثفات PVC (أزرق)", "refrigerant pipes (dashed) / condensate (blue)"),
    (L_duct, "صاعد مواسير داخل تري معدني", "pipe riser in steel tray"),
]

def legend(s, x, y, rows, w=10.0):
    return s.legend(x, y, "جدول رموز التكييف - HVAC LEGEND", rows, w=w, rh=0.40)

# ----------------------------------------------------------------------------- schedule table
def schedule(s, x, y, title, rows, cols, rh=0.3):
    """simple table: cols = [(header, width)], rows = list of cell lists (same order). Drawn down from (x,y)."""
    W = sum(c[1] for c in cols)
    th, hh = 0.42, 0.32
    H = th + hh + rh * len(rows)
    s.rect(x, y - H, x + W, y, color=BLK, layer="LEGEND")
    s.hatch([(x, y - th), (x + W, y - th), (x + W, y), (x, y)], color=254, layer="LEGEND")
    s.text(x + W / 2, y - th / 2, title, h=0.18, attach=5, color=BLK, layer="LEGEND")
    s.hatch([(x, y - th - hh), (x + W, y - th - hh), (x + W, y - th), (x, y - th)], color=253, layer="LEGEND")
    s.line((x, y - th), (x + W, y - th), color=BLK, layer="LEGEND")
    s.line((x, y - th - hh), (x + W, y - th - hh), color=BLK, layer="LEGEND")
    # columns run right-to-left (Arabic table): first column at the right edge
    cx = x + W
    xs = []
    for hdr, cw in cols:
        xs.append((cx - cw, cx))
        s.text(cx - cw / 2, y - th - hh / 2, hdr, h=0.12, attach=5, color=BLK, layer="LEGEND")
        cx -= cw
        if cx > x + 0.01:
            s.line((cx, y - th), (cx, y - H), color=BLK, lw=5, layer="LEGEND")
    for i, row in enumerate(rows):
        cy = y - th - hh - rh * (i + 0.5)
        s.line((x, cy - rh / 2), (x + W, cy - rh / 2), color=BLK, lw=5, layer="LEGEND")
        for (x0, x1), cell in zip(xs, row):
            s.text((x0 + x1) / 2, cy, cell, h=0.11, attach=5, color=BLK, layer="LEGEND")
    return H

COLS = [("الرمز", 1.4), ("النوع", 3.3), ("السعة BTU/hr", 1.7), ("الموقع", 3.1), ("العدد", 0.9)]

# ============================================================================= GROUND
def draw_G(s):
    DA, DB, HY, RX, DW = 33.8, 29.4, 34.5, 31.0, 0.45     # duct A, duct B, header y, riser x, duct width
    XD = [9.0 + 2.5 * i for i in range(9)]                 # diffuser stations (9 per duct)
    # ---- indoor units (concealed above BOH ceilings)
    ahu(s, 26.6, 36.1, "AHU-1", "5 TR - 2000 CFM", w=1.2)
    ahu(s, 28.7, 37.0, "AHU-2", "5 TR - 2000 CFM", w=1.2)
    ahu(s, 23.75, 37.25, "AHU-3", "3 TR - 1200 CFM", w=1.0, h=0.5)
    # ---- supply: AHU-1 drop + header + riser + duct B (one run), AHU-2 drop, duct A branch
    s.duct([(26.6, 35.825), (26.6, HY), (RX, HY), (RX, DB), (8.0, DB)], w=DW)
    s.duct([(28.9, 36.725), (28.9, HY + DW / 2)], w=DW)
    s.duct([(RX - DW / 2, DA), (8.0, DA)], w=DW)
    for x in XD:
        rdiff(s, x, DA); rdiff(s, x, DB)
    # ---- kitchen supply Ø300
    s.duct([(23.25, 37.25), (18.0, 37.25)], w=0.3)
    for x in (18.3, 20.3, 22.3):
        rdiff(s, x, 37.25, 0.125)
    # duct size / flow tags inside the ducts
    for x in (12.75, 22.75):
        s.text(x, DA, "Ø450 - 2000 CFM", h=0.1, attach=5)
        s.text(x, DB, "Ø450 - 2000 CFM", h=0.1, attach=5)
    s.text(28.0, HY, "450×450 - 4000 CFM", h=0.1, attach=5)
    s.text(RX, 31.6, "Ø450", h=0.1, attach=5, rotation=90)
    s.text(19.3, 37.25, "Ø300 - 1200 CFM", h=0.09, attach=5)
    # ---- return air grilles in the BOH wall (above the doors)
    for x in (26.0, 27.9, 29.8):
        s.grille(x, 35.02, w=0.6, h=0.22)
    # ---- fresh-air louvre at the top of the right glass + duct to the return plenum
    s.grille(31.62, 34.1, w=0.5, h=0.12, rot=90)
    s.duct([(31.55, 34.1), (31.4, 34.1), (31.4, 35.5)], w=0.2)
    s.valve(31.4, 35.25, size=0.18, rot=90)
    # ---- thermostats
    for x, y in ((11.4, 36.32), (24.6, 34.8), (24.05, 36.3)):
        tstat(s, x, y)
    # ---- outdoor units on the roof above the BOH
    roof_zone(s, 25.7, 39.65, 31.4, 40.55)
    XO = (26.6, 27.9, 29.2, 30.5)
    for i, x in enumerate(XO, 1):
        s.outdoor_unit(x, 40.05, w=0.9, h=0.35, label=f"ODU-{i}")
    s.text(28.55, 41.0, "وحدات خارجية على السطح (4 عدد) - قواعد مطاطية", h=0.14, attach=5)
    # refrigerant pipes ODU -> AHU
    refr(s, [(26.6, 39.875), (26.6, 36.375)])
    refr(s, [(27.9, 39.875), (27.9, 38.78), (28.7, 38.78), (28.7, 37.275)])
    refr(s, [(29.2, 39.875), (29.2, 38.62), (24.1, 38.62), (24.1, 37.5)])
    s.text(30.35, 39.3, "مواسير فريون نحاس معزولة", h=0.1, attach=5)
    s.text(30.5, 39.55, "احتياطي", h=0.09, attach=5)
    # condensate drains (to the kitchen floor drain / hand-sink drain)
    cond(s, [(27.1, 35.9), (27.1, 35.2), (24.7, 35.2), (24.7, 36.4)])
    cond(s, [(29.2, 36.8), (29.4, 36.8), (29.4, 35.2), (27.1, 35.2)])
    cond(s, [(23.35, 37.0), (24.6, 37.0), (24.6, 36.4)])
    s.text(24.95, 36.4, "F/D", h=0.09, attach=4, color=CND)
    # ---- dimensions (red)
    xs = [7.4] + XD + [31.5]
    for a, b in zip(xs[1:-1], xs[2:]):
        s.dim((a, DA), (b, DA), offset=-0.85, color=RED)                # duct A diffuser chain (base y 32.95)
    s.dim((7.4, DA), (8.0, DA), offset=0.5, color=RED)                  # duct A end to the left wall
    for a, b in zip(xs[:7], xs[1:7]):
        s.dim((a, DB), (b, DB), offset=0.5, color=RED)                  # duct B diffuser chain (base y 29.9)
    s.dim((12.0, 27.0), (12.0, DB), offset=0.3, color=RED, horizontal=False)        # duct B from facade
    s.dim((20.0, DB), (20.0, DA), offset=0.35, color=RED, horizontal=False)         # A-B spacing
    s.dim((RX, DB), (RX, DA), offset=0.35, color=RED, horizontal=False)             # riser
    s.dim((24.3, DA), (24.3, 35.0), offset=0.3, color=RED, horizontal=False)        # duct A to BOH wall
    s.dim((26.0, 35.02), (27.9, 35.02), offset=0.55, color=RED)                     # grille spacing
    s.dim((27.9, 35.02), (29.8, 35.02), offset=0.55, color=RED)
    s.dim((26.0, 36.375), (27.2, 36.375), offset=0.25, color=RED)                   # AHU-1 width
    s.dim((18.3, 37.25), (20.3, 37.25), offset=-0.55, color=RED)                    # kitchen diffusers
    s.dim((20.3, 37.25), (22.3, 37.25), offset=-0.55, color=RED)
    s.dim((22.3, 37.25), (23.25, 37.25), offset=-0.55, color=RED)
    for a, b in zip(XO[:-1], XO[1:]):
        s.dim((a, 40.05), (b, 40.05), offset=0.55, color=RED)                       # ODU spacing
    s.dim((31.5, 38.9), (31.5, 40.05), offset=0.3, color=RED, horizontal=False)     # ODU from back wall
    # ---- callouts (Arabic, with leaders)
    s.text(11.5, 34.45, "دكت تغذية A Ø450 مكشوف أسود - 2000 CFM\\Pأسفل الدكت +3.60 م - ناشر كل 2.50 م", h=0.12, attach=5)
    s.leader([(11.5, 34.26), (11.5, DA + DW / 2)])
    s.text(28.5, 28.55, "دكت تغذية B Ø450 مكشوف أسود - 2000 CFM\\Pأسفل الدكت +3.60 م - ناشر كل 2.50 م", h=0.12, attach=5)
    s.leader([(28.5, 28.75), (28.5, DB - DW / 2)])
    s.text(27.9, 30.35, "ناشر هواء دائري Ø300 - 220 CFM (18 عدد)", h=0.12, attach=5)
    s.leader([(26.9, 30.25), (26.5, DB + 0.15)])
    s.text(20.0, 39.75, "دكت تغذية المطبخ Ø300 - 1200 CFM (3 ناشرات Ø250) - أسفل الدكت +2.80 م", h=0.12, attach=5)
    s.leader([(22.4, 39.68), (22.4, 37.4)])
    s.text(24.0, 40.1, "شبكات رجوع هواء 600×600 عدد 3\\Pفي جدار الخدمات فوق الأبواب +2.40 م", h=0.12, attach=5)
    s.leader([(25.3, 39.92), (26.0, 35.15)])
    s.text(33.9, 34.75, "مأخذ هواء نقي Ø250\\Pأعلى الزجاج +3.20 م\\Pدامبر يدوي - إلى بلينوم الرجوع", h=0.12, attach=5)
    s.leader([(32.95, 34.6), (31.7, 34.15)])
    s.text(12.0, 36.95, "ثرموستات جداري +1.50 م (3 عدد)", h=0.12, attach=5)
    s.leader([(12.0, 36.85), (11.4, 36.48)])
    s.text(21.9, 34.3, "AHU-3: وحدة مخفية 3 TR فوق سقف التحضير +2.80 م", h=0.11, attach=5)
    s.leader([(23.9, 34.37), (24.2, 35.0), (24.2, 37.0)])
    s.text(33.6, 30.2, "صاعد Ø450 أسود مكشوف", h=0.11, attach=5)
    s.leader([(32.9, 30.2), (RX + DW / 2, 30.2)])
    # ---- legend, schedule, notes
    x0, y0, x1, y1 = EMPTY_G
    legend(s, x0 + 0.2, y1, LEGEND_G, w=10.0)
    schedule(s, 14.7, y1, "جدول وحدات التكييف - HVAC EQUIPMENT SCHEDULE", [
        ["AHU-1", "وحدة مخفية ducted split", "60,000 (5 TR)", "فوق سقف ردهة الدرج - صالة", "1"],
        ["AHU-2", "وحدة مخفية ducted split", "60,000 (5 TR)", "فوق سقف المستودع - صالة", "1"],
        ["AHU-3", "وحدة مخفية ducted - مطبخ", "36,000 (3 TR)", "فوق سقف منطقة التحضير", "1"],
        ["ODU-1,2", "وحدة خارجية 5 TR", "60,000", "السطح فوق الخدمات", "2"],
        ["ODU-3", "وحدة خارجية 3 TR", "36,000", "السطح فوق الخدمات", "1"],
        ["ODU-4", "وحدة خارجية احتياطية", "60,000", "السطح فوق الخدمات", "1"],
        ["SD", "ناشر دائري Ø300", "220 CFM", "صالة - دكت A و B", "18"],
        ["SD-K", "ناشر دائري Ø250", "400 CFM", "المطبخ", "3"],
        ["RAG", "شبكة رجوع 600×600", "1,350 CFM", "جدار الخدمات", "3"],
        ["FA", "مأخذ هواء نقي Ø250", "400 CFM", "أعلى الزجاج الجانبي", "1"],
        ["T", "ثرموستات جداري", "-", "صالة ×2 / مطبخ ×1", "3"],
    ], COLS, rh=0.3)
    s.notes(34.8, 45.0, [
        "الدكتات صاج مجلفن GI 24 g مطلية أسود مطفي، مكشوفة تحت البلاطة",
        "عزل الدكتات 25 مم صوف زجاجي بغطاء أسود فوق الأسقف المستعارة",
        "وصلات مرنة Flexible connectors عند مخارج جميع الوحدات",
        "دامبر حريق Fire damper عند اختراق جدار المطبخ والخدمات",
        "موازنة الهواء: ضغط سالب 50 Pa في المطبخ نسبة إلى الصالة",
        "أسفل الدكت المكشوف +3.60 م في الصالة و +2.80 م في المطبخ",
        "الوحدات الداخلية مخفية فوق السقف المستعار مع باب معاينة 60×60",
        "الوحدات الخارجية على السطح مع قواعد مطاطية ومسافة 1 م بينها",
        "تصريف المكثفات PVC Ø25 بميل 1% إلى أقرب مصرف أرضي",
        "العدد: AHU = 3 ، ODU = 4 ، ناشر = 21 ، شبكة رجوع = 3 ، ثرموستات = 3",
    ], h=0.14, w=9.0, title="ملاحظات التكييف")

# ============================================================================= MEZZANINE
def draw_M(s):
    r = M["rooms"]
    SY = 6.75                                    # wall splits on the front wall of the rooms
    SX = {"r3": 9.5, "r2": 14.1, "r1": 18.75}
    for i, key in enumerate(("r3", "r2", "r1"), 1):
        x = SX[key]
        s.split_unit(x, SY, w=0.9, h=0.25)
        s.text(x + 0.55, SY, f"WS-{i}", h=0.1, attach=4)
    s.split_unit(14.0, 11.35, w=0.9, h=0.25)                  # corridor
    s.text(14.55, 11.35, "WS-4", h=0.1, attach=4)
    s.split_unit(31.3, 7.3, w=0.9, h=0.25, rot=90)            # office
    CX = (24.2, 29.3)
    for i, x in enumerate(CX, 1):
        s.cassette(x, 10.9, size=0.75)
        s.text(x + 0.45, 11.2, f"CU-{i}", h=0.1, attach=4)
    # ---- outdoor units on the roof
    roof_zone(s, 10.6, 14.65, 22.6, 15.75)
    XO = [11.5 + 2.0 * i for i in range(6)]
    for i, x in enumerate(XO, 1):
        s.outdoor_unit(x, 15.3, w=0.9, h=0.35, label=f"ODU-M{i}")
        refr(s, [(x, 15.125), (x, 14.4)])
    s.text(16.6, 16.25, "وحدات خارجية على السطح فوق الميزانين (6 عدد) - قواعد مطاطية", h=0.14, attach=5)
    # refrigerant trunk on the roof -> two risers (corridor side / prep side)
    refr(s, [(11.0, 14.4), (22.4, 14.4)])
    refr(s, [(11.0, 14.4), (11.0, 11.1), (8.2, 11.1), (8.2, 6.9), (9.05, 6.9)])
    refr(s, [(11.0, 11.1), (16.75, 11.1)])
    refr(s, [(11.95, 11.1), (11.95, 6.9), (13.65, 6.9)])
    refr(s, [(16.75, 11.1), (16.75, 6.9), (18.3, 6.9)])
    refr(s, [(14.0, 11.1), (14.0, 11.225)])
    refr(s, [(22.4, 14.4), (22.4, 11.05), (30.95, 11.05), (30.95, 7.3), (31.175, 7.3)])
    s.text(10.7, 12.6, "صاعد فريون", h=0.1, attach=5, rotation=90)
    s.text(22.65, 11.7, "صاعد فريون", h=0.1, attach=5, rotation=90)
    # condensate drains to the nearest floor drains
    cond(s, [(9.05, 6.58), (21.1, 6.58), (21.1, 11.42), (24.3, 11.42), (24.3, 12.7)])
    cond(s, [(24.2, 11.275), (24.3, 11.42)])
    cond(s, [(29.3, 11.275), (29.6, 11.7)])
    cond(s, [(14.45, 11.42), (15.45, 11.42), (15.45, 12.3), (16.2, 12.3)])
    cond(s, [(31.3, 7.75), (31.07, 7.75), (31.07, 11.7), (29.6, 11.7)])
    for x, y in ((24.3, 12.7), (29.6, 11.7), (16.2, 12.3)):
        s.text(x + 0.12, y + 0.05, "F/D", h=0.09, attach=7, color=CND)
    # ---- dimensions
    chain = [7.4, 9.5, 14.1, 18.75, 20.9]
    for a, b in zip(chain[:-1], chain[1:]):
        s.dim((a, SY), (b, SY), offset=0.35, color=RED)                       # splits along the front wall
    for a, b in zip(XO[:-1], XO[1:]):
        s.dim((a, 15.3), (b, 15.3), offset=0.65, color=RED)                   # ODU spacing
    s.dim((31.3, 7.3), (31.3, 8.0), offset=-0.5, color=RED, horizontal=False)   # office split from wall
    s.dim((22.0, 10.9), (24.2, 10.9), offset=-0.5, color=RED)                 # cassette 1 from the lobby edge
    s.dim((29.3, 10.9), (31.5, 10.9), offset=-0.5, color=RED)                 # cassette 2 from the right wall
    s.dim((9.5, 11.35), (14.0, 11.35), offset=-0.45, color=RED)               # corridor split from kitchenette wall
    s.dim((11.0, 11.5), (11.0, 14.4), offset=0.3, color=RED, horizontal=False)  # riser length
    s.dim((10.6, 15.3), (11.5, 15.3), offset=0.65, color=RED)                 # first ODU from the zone edge
    # ---- callouts
    s.text(8.6, 7.4, "سبليت جداري 18000 BTU +2.20 م", h=0.11, attach=5)
    s.text(12.9, 7.4, "سبليت جداري 18000 BTU", h=0.11, attach=5)
    s.text(17.5, 7.4, "سبليت جداري 18000 BTU", h=0.11, attach=5)
    s.text(12.6, 11.85, "WS-4 سبليت 12000 BTU للممر +2.20 م", h=0.11, attach=5)
    s.leader([(13.3, 11.78), (14.0, 11.48)])
    s.text(29.85, 8.25, "WS-5 سبليت 12000 BTU للمكتب", h=0.1, attach=5)
    s.leader([(30.7, 8.2), (31.25, 7.8)])
    s.text(26.1, 10.75, "كاسيت سقفي 24000 BTU (2 عدد) - سقف +2.60 م", h=0.11, attach=5)
    s.leader([(24.85, 10.78), (24.6, 10.9)])
    s.text(13.2, 12.6, "مواسير فريون نحاس معزولة داخل تري معدني\\Pتصريف مكثفات PVC Ø25 (أزرق)", h=0.11, attach=5)
    s.leader([(11.95, 12.6), (11.05, 12.6)])
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    s.text(19.5, 3.4, "يُخدم من دكتات الطابق الأرضي - انظر مخطط التكييف الأرضي", h=0.14, attach=5, color=8)
    # ---- legend, schedule, notes
    x0, y0, x1, y1 = EMPTY_M
    legend(s, x0 + 0.2, y1, LEGEND_M, w=9.0)
    schedule(s, 13.6, y1, "جدول وحدات التكييف - الميزانين", [
        ["WS-1..3", "سبليت جداري Wall split", "18,000", "غرف السكن 1 - 2 - 3", "3"],
        ["WS-4", "سبليت جداري", "12,000", "ممر السكن", "1"],
        ["WS-5", "سبليت جداري", "12,000", "المكتب", "1"],
        ["CU-1,2", "كاسيت سقفي 4 اتجاهات", "24,000", "منطقة التحضير والغسيل", "2"],
        ["ODU-M1..M3", "وحدة خارجية", "18,000", "السطح فوق الميزانين", "3"],
        ["ODU-M4", "وحدة خارجية ملتي 1:2", "24,000", "السطح (الممر + المكتب)", "1"],
        ["ODU-M5,M6", "وحدة خارجية", "24,000", "السطح (الكاسيتات)", "2"],
        ["CD", "تصريف مكثفات PVC Ø25", "-", "إلى أقرب مصرف أرضي", "5"],
    ], COLS, rh=0.3)
    s.notes(34.8, 20.0, [
        "سبليت جداري 18000 BTU في كل غرفة سكن على ارتفاع +2.20 م",
        "كاسيت سقفي 24000 BTU عدد 2 في منطقة التحضير بسقف +2.60 م",
        "سبليت 12000 BTU للممر وآخر للمكتب على وحدة خارجية ملتي 1:2",
        "الوحدات الخارجية 6 عدد على السطح فوق الميزانين مع قواعد مطاطية",
        "مواسير فريون نحاس معزولة داخل تري معدني تحت سقف الممر",
        "تصريف المكثفات PVC Ø25 بميل 1% إلى أقرب مصرف أرضي",
        "الفراغ المزدوج فوق الصالة يُخدم من دكتات الطابق الأرضي",
        "العدد: سبليت = 5 ، كاسيت = 2 ، وحدة خارجية = 6",
    ], h=0.14, w=9.0, title="ملاحظات التكييف - الميزانين")
