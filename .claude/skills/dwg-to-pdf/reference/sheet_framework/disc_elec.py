"""Electrical power points (أفياش الكهرباء) - ground floor + mezzanine."""
from sitemodel import G, M, EMPTY_G, EMPTY_M
LAYER = "E-POWER"
R = 0.45

def sym(letter):
    return lambda s, x, y: (s.circle(x, y, 0.2), s.dot(x, y, 0.05), s.text(x - 0.05, y - 0.05, letter, h=0.1))

LEGEND = [
    (sym("P"), "فيش كهربائي جداري 220V ارتفاع 40 سم", "L1+N+G 220V wall socket, h=0.40 m"),
    (sym("U"), "فيش كهربائي جداري مع مدخل USB (طاولات الجلوس)", "wall socket + USB at seating"),
    (sym("F"), "فيش كهربائي أرضي مع USB (بوكس أرضي)", "floor box socket + USB"),
    (sym("K"), "فيش معدات مطبخ 16/32A مقاوم للماء IP44 ارتفاع 120 سم", "kitchen equipment socket IP44, h=1.20 m"),
    (sym("3"), "تغذية 3 فاز (قلايات / ثلاجة تجميد)", "3-phase feed 380V"),
    (sym("C"), "نقطة كاشير: فيش مزدوج + داتا + طابعة", "cashier: double socket + data"),
    (sym("S"), "نقطة شاشة / لوحة إعلانية / نيون ارتفاع 220 سم", "TV / signage / neon point, h=2.20 m"),
    (sym("W"), "نقطة سخان ماء فوري", "instant water heater point"),
    (sym("D"), "لوحة توزيع كهربائية", "distribution board (DB)"),
]

def legend(s, x, y):
    return s.legend(x, y, "جدول رموز الكهرباء - ELECTRICAL LEGEND", LEGEND, w=10.5, rh=0.46)

def pt(s, x, y, L, r=R):
    s.elec_point(x, y, L, r=r)

def db(s, x, y, name):
    s.rect(x - 0.3, y - 0.15, x + 0.3, y + 0.15, lw=35)
    s.hatch([(x - 0.3, y - 0.15), (x + 0.3, y - 0.15), (x + 0.3, y + 0.15), (x - 0.3, y + 0.15)])
    s.text(x, y - 0.2, "D - " + name, h=0.11, attach=2)

def draw_G(s):
    # seating: U at every booth, F floor boxes at communal table and facade booths
    for kind, cx, cy, w, h in G["seating"]:
        if kind == "booth":
            if cx < 9:      pt(s, 7.65, cy, "U")                    # left wall booths
            elif cy < 29 and cx < 15:  pt(s, cx, 27.35, "F")        # facade booths -> floor box
            elif cx > 22 and cx < 23: pt(s, 23.3, cy, "U")          # right-front booths (column/partition side)
            elif cy > 32:   pt(s, cx, 31.8, "U")                    # right row booths (planter back)
        elif kind == "table4":
            pt(s, cx, 36.35, "U")
        elif kind == "bench":
            pt(s, 15.7, cy, "U")
    for x in (11.3, 13.5):
        pt(s, x, 31.45, "F")                                       # communal table floor boxes
    for x in (16.0, 18.4):
        pt(s, x, 34.85, "U")                                       # bar counter front
    # kitchen equipment
    for name, x0, x1, y0, y1, needs in G["equipment"]:
        if "P" not in needs:
            continue
        cx = (x0 + x1) / 2
        if y0 > 37:                                                # cooking line - sockets on back wall
            L = "3" if "قلاية" in name else "K"
            pt(s, cx, 38.75, L, r=0.3)
        elif "كاشير" in name:
            pt(s, cx, 34.7, "C")
        elif "تسليم" in name:
            pt(s, 22.0, 35.6, "P", r=0.3)
        else:
            pt(s, cx, (y0 + y1) / 2, "K", r=0.3)
    for x in (24.5, 25.1):
        pt(s, x, 38.75, "W", r=0.3)                               # hand sinks water heaters
    pt(s, 21.0, 37.4, "K", r=0.3); pt(s, 23.6, 37.4, "K", r=0.3)   # prep area spare sockets
    pt(s, 24.6, 36.6, "P", r=0.3)                                 # stairs / corridor
    # screens, signage, neon
    for x, y, rot in G["tv"]:
        pt(s, x, y, "S")
    pt(s, 18.5, 38.75, "S", r=0.3); pt(s, 21.5, 38.75, "S", r=0.3)   # illuminated menu boards
    pt(s, 27.5, 34.8, "S"); pt(s, 19.5, 27.3, "S"); pt(s, 15.4, 26.6, "S")   # neon wall sign / entrance sign / fascia sign
    # services rooms
    pt(s, 9.3, 38.6, "P"); pt(s, 9.3, 37.3, "P")                  # men WC hand dryers
    pt(s, 31.3, 36.4, "P"); pt(s, 29.3, 36.8, "P"); pt(s, 26.3, 37.2, "P"); pt(s, 9.3, 41.0, "P")
    pt(s, 31.1, 32.9, "P")
    db(s, 31.0, 32.2, "لوحة التوزيع الرئيسية MDB")
    db(s, 24.15, 36.2, "لوحة المطبخ DB-K")
    # dimensions (red) + callouts
    D = dict(color=1, h=0.12)
    s.dim((11.3, 31.45), (13.5, 31.45), offset=-1.3, **D)                    # communal floor boxes
    s.dim((11.15, 27.35), (13.45, 27.35), offset=0.9, **D)                   # facade floor boxes
    s.dim((7.65, 28.0), (7.65, 29.4), offset=0.5, horizontal=False, **D)
    s.dim((7.65, 29.4), (7.65, 30.9), offset=0.5, horizontal=False, **D)
    s.dim((7.65, 30.9), (7.65, 33.7), offset=0.5, horizontal=False, **D)
    s.dim((10.3, 36.35), (12.35, 36.35), offset=0.55, **D); s.dim((12.35, 36.35), (14.4, 36.35), offset=0.55, **D)
    s.dim((24.6, 31.8), (26.7, 31.8), offset=-0.9, **D); s.dim((26.7, 31.8), (28.8, 31.8), offset=-0.9, **D)
    s.dim((16.0, 34.85), (18.4, 34.85), offset=-0.9, **D)
    s.dim((15.8, 38.75), (18.15, 38.75), offset=0.45, **D); s.dim((18.15, 38.75), (21.2, 38.75), offset=0.45, **D)
    s.dim((21.2, 38.75), (24.5, 38.75), offset=0.45, **D); s.dim((24.5, 38.75), (25.1, 38.75), offset=0.45, **D)
    s.dim((15.3, 38.75), (15.8, 38.75), offset=0.45, **D)
    s.dim((7.4, 32.0), (7.45, 32.0), offset=0.0, **D) if False else None
    C = dict(h=0.12, color=7)
    s.leader([(7.65, 33.7), (6.3, 34.9)]); s.text(6.3, 35.0, "فيش جداري USB\Pارتفاع 40 سم", attach=2, **C)
    s.leader([(11.15, 27.35), (10.2, 26.55)]); s.text(10.2, 26.5, "بوكس أرضي مقاوم للماء مع USB", attach=3, **C)
    s.leader([(18.15, 38.75), (18.15, 39.7)]); s.text(18.15, 39.75, "أفياش المطبخ IP44 ارتفاع 120 سم\Pعلى الجدار الخلفي خلف المعدات", attach=8, **C)
    s.leader([(7.45, 32.0), (6.0, 31.2)]); s.text(6.0, 31.1, "نقطة شاشة 65 بوصة\Pارتفاع 220 سم", attach=3, **C)
    s.leader([(31.0, 32.2), (33.2, 31.4)]); s.text(33.2, 31.3, "لوحة التوزيع الرئيسية MDB\P3 فاز - غرفة الخدمة", attach=1, **C)
    s.leader([(24.15, 36.2), (24.15, 39.6)]); s.text(24.15, 39.65, "لوحة المطبخ الفرعية DB-K\Pتغذية 3 فاز للقلايات", attach=8, **C)
    s.leader([(19.5, 27.3), (20.6, 26.4)]); s.text(20.7, 26.45, "نقطة نيون المدخل I ♥ BURGER", attach=1, **C)
    s.leader([(15.4, 26.6), (13.8, 25.9)]); s.text(13.7, 25.9, "تغذية لوحة الواجهة المضيئة", attach=3, **C)
    s.text(12.5, 29.6, "العدد الإجمالي للنقاط: جداري 32 - أرضي 4 - مطبخ 14 - شاشات 7 - 3 فاز 4", h=0.14, attach=5, color=7)
    # legend + notes
    x0, y0, x1, y1 = EMPTY_G
    legend(s, x0 + 0.2, y1 - 0.1)
    s.notes(34.8, 45.0, [
        "ارتفاع الأفياش الجدارية 40 سم من الأرض ما لم يذكر غير ذلك",
        "أفياش المطبخ IP44 بارتفاع 120 سم فوق الطاولات مع قاطع تسرب أرضي 30mA",
        "القلايات وثلاجة التجميد على خطوط 3 فاز مستقلة من لوحة المطبخ",
        "نقاط الشاشات واللوحات ارتفاع 220 سم مع تمديد HDMI/داتا",
        "البوكسات الأرضية من النوع المغلق المقاوم للماء",
        "جميع التمديدات داخل الجدران والأسقف بمواسير PVC وفق كود البناء السعودي",
    ], h=0.14, w=9.0, title="ملاحظات الكهرباء")

def draw_M(s):
    r = M["rooms"]
    for key in ("r1", "r2", "r3"):
        x0, y0, x1, y1 = r[key]
        pt(s, x0 + 0.3, (y0 + y1) / 2, "U"); pt(s, x1 - 0.3, (y0 + y1) / 2, "U"); pt(s, (x0 + x1) / 2, y0 + 0.25, "P")
    pt(s, 14.0, 11.25, "P"); pt(s, 18.5, 11.25, "P")              # corridor
    for name, x0, x1, y0, y1, needs in M["equipment"]:
        if "P" not in needs:
            continue
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if x1 < 8.5:        pt(s, 8.3, cy, "K", r=0.3)              # kitchenette column
        elif x1 < 22:       pt(s, 22.3, cy, "K", r=0.3)             # freezer / fridges column
        elif "تجميد" in name: pt(s, 24.9, 9.1, "3")
        elif "مكتب" in name: pt(s, 30.5, 6.75, "C")
        else:               pt(s, cx, 13.3, "K", r=0.3)
    for x in (24.3, 26.4, 29.7):
        pt(s, x, 13.3, "W", r=0.3)                                # water heaters for sinks
    for x in (23.0, 31.3):
        pt(s, x, 12.0, "P", r=0.3)
    pt(s, 26.2, 10.3, "P", r=0.3); pt(s, 28.5, 10.3, "P", r=0.3)   # steel table line
    pt(s, 15.8, 13.4, "P"); pt(s, 20.7, 13.4, "P"); pt(s, 28.0, 9.1, "P"); pt(s, 9.3, 16.9, "P")
    db(s, 21.6, 11.7, "لوحة الميزانين DB-M")
    D = dict(color=1, h=0.12)
    for key in ("r1", "r2", "r3"):
        x0, y0, x1, y1 = r[key]
        s.dim((x0 + 0.3, (y0 + y1) / 2), (x1 - 0.3, (y0 + y1) / 2), offset=-1.0, **D)
    s.dim((22.3, 10.8), (22.3, 9.3), offset=0.6, horizontal=False, **D); s.dim((22.3, 9.3), (22.3, 7.8), offset=0.6, horizontal=False, **D)
    s.dim((24.3, 13.3), (26.4, 13.3), offset=0.4, **D); s.dim((26.4, 13.3), (29.7, 13.3), offset=0.4, **D)
    s.dim((8.3, 12.7), (8.3, 11.85), offset=0.5, horizontal=False, **D); s.dim((8.3, 11.85), (8.3, 10.7), offset=0.5, horizontal=False, **D)
    C = dict(h=0.12, color=7)
    s.leader([(21.6, 11.7), (21.6, 14.6)]); s.text(21.6, 14.65, "لوحة الميزانين DB-M\Pتغذية من اللوحة الرئيسية بكابل 4×16 مم", attach=8, **C)
    s.leader([(24.9, 9.1), (25.0, 5.6)]); s.text(25.0, 5.5, "ثلاجة التجميد المركزية: خط 3 فاز مستقل 32A", attach=8, **C)
    s.leader([(8.3, 11.85), (9.6, 14.2)]); s.text(9.7, 14.25, "أفياش المطبخ الصغير IP44\Pارتفاع 120 سم", attach=1, **C)
    s.text(14.0, 5.2, "العدد الإجمالي للنقاط: جداري 14 - USB 6 - مطبخ 10 - 3 فاز 1", h=0.14, attach=5, color=7)
    x0, y0, x1, y1 = EMPTY_M
    legend(s, x0 + 0.2, y1 - 0.1)
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    s.notes(34.8, 20.0, ["الغرف: فيش USB بجانب كل سرير + فيش عام", "أفياش منطقة الغسيل IP44 ارتفاع 120 سم",
                         "ثلاجة التجميد المركزية خط 3 فاز مستقل"], h=0.14, w=9.0, title="ملاحظات")
