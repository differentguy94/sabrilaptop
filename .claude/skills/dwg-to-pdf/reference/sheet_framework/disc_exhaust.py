"""Kitchen exhaust + general ventilation (مخطط الشفاط والتهوية) - ground floor + mezzanine.
Ground: stainless hood 8.10 x 1.20 m over the cooking line (14 baffle filters + 2 spark-arrestor filters over the
charcoal grill, wet-chemical fire suppression), welded black-steel grease duct 600x400 rising through the back wall
to the roof: ESP/odour unit -> upblast centrifugal fan 6000 CFM; make-up air fan 5000 CFM on the roof with an
insulated 700x400 duct to a 1200x400 wall grille above the hood; small extract fans (WCs, prayer, store, service
room) ducted to exterior louvres; 2 smoke-purge wall fans at the top of the side glass.
Mezzanine: kitchenette hood 0.90x0.60 + riser to a roof fan, prep/wash wall fans, WC fans, corridor fan, store fan,
fresh-air / transfer grilles, and the two risers (grease duct + make-up air) passing through the back wall.
Wall faces used (read from the gridded plan): ground back wall y 38.45-38.80, kitchen left wall x 15.30-15.55,
men WC block x 7.45-9.5, mezz back wall y 13.44-13.83, kitchenette wall x 7.2-7.45."""
from sitemodel import G, M, EMPTY_G, EMPTY_M

LAYER = "M-EXHAUST"
RED, BLK, GRY, FIRE, BLUE = 1, 7, 8, 6, 150
D = dict(color=RED, h=0.12)          # dimensions
C = dict(h=0.12, color=BLK)          # callouts

# ----------------------------------------------------------------------------- symbols
def hood(s, x0, y0, x1, y1, rear="top", cells=14, spark=None, band=0.28, o=0.07):
    """exhaust hood: double outline + diagonals + filter band at the rear (cells) + optional spark-arrestor section"""
    s.rect(x0, y0, x1, y1, lw=35)
    s.rect(x0 + o, y0 + o, x1 - o, y1 - o, lw=13)
    s.line((x0, y0), (x1, y1), lw=9); s.line((x0, y1), (x1, y0), lw=9)
    if rear == "top":
        by0, by1 = y1 - o - band, y1 - o
        s.line((x0 + o, by0), (x1 - o, by0), lw=13)
        xa, xb = x0 + o, (spark if spark else x1 - o)
        step = (xb - xa) / cells
        for i in range(1, cells):
            s.line((xa + i * step, by0), (xa + i * step, by1), lw=9)
        if spark:
            s.line((spark, y0 + o), (spark, y1 - o), lw=25)
            mid = (spark + x1 - o) / 2
            s.line((mid, by0), (mid, by1), lw=9)
            s.hatch([(spark, by0), (x1 - o, by0), (x1 - o, by1), (spark, by1)], pattern="ANSI31", scale=0.25)
    else:                                   # rear = left wall
        bx0, bx1 = x0 + o, x0 + o + band
        s.line((bx1, y0 + o), (bx1, y1 - o), lw=13)
        step = (y1 - y0 - 2 * o) / cells
        for i in range(1, cells):
            s.line((bx0, y0 + o + i * step), (bx1, y0 + o + i * step), lw=9)


def collar(s, x, y, w=0.6, h=0.33):
    """duct collar on the hood plenum (rect + X)"""
    s.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, lw=35)
    s.line((x - w / 2, y - h / 2), (x + w / 2, y + h / 2), lw=13); s.line((x - w / 2, y + h / 2), (x + w / 2, y - h / 2), lw=13)


def esp(s, x, y, w=1.2, h=0.8, txt="ESP\\P+ كربون"):
    s.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, lw=35)
    s.rect(x - w / 2 + 0.08, y - h / 2 + 0.08, x + w / 2 - 0.08, y + h / 2 - 0.08, lw=9)
    s.text(x, y, txt, h=0.1, attach=5)


def sduct(s, pts, label=None, lx=None, ly=None, rot=0.0):
    """small round duct (single dashed line)"""
    s.pline(pts, lw=25, linetype="DASHED")
    if label:
        s.text(lx, ly, label, h=0.08, attach=5, rotation=rot)


def sfan(s, x, y, tag=None, r=0.17, dx=0.2, dy=0.2):
    s.fan(x, y, r)
    if tag:
        s.text(x + dx, y + dy, tag, h=0.09, color=BLK)


def louvre(s, x, y, rot=0.0, w=0.32):
    s.grille(x, y, w=w, h=0.14, rot=rot)


def nozzle(s, x, y):
    s.dot(x, y, 0.04, color=FIRE)
    s.circle(x, y, 0.085, color=FIRE, lw=13)


def riser_rect(s, x, y, w, h, tag):
    s.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, lw=35)
    s.hatch([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)],
            pattern="ANSI31", scale=0.2)
    s.text(x, y + h / 2 + 0.04, tag, h=0.09, attach=8)


def riser_circ(s, x, y, tag=None):
    s.circle(x, y, 0.16, lw=35)
    s.dot(x, y, 0.05)
    s.line((x - 0.11, y - 0.11), (x + 0.11, y + 0.11), lw=13); s.line((x - 0.11, y + 0.11), (x + 0.11, y - 0.11), lw=13)
    if tag:
        s.text(x + 0.2, y + 0.18, tag, h=0.09, color=BLK)


def roof_zone(s, x0, y0, x1, y1, label):
    s.pline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True, lw=9, linetype="DASHED", color=GRY)
    s.text((x0 + x1) / 2, y1 - 0.03, label, h=0.1, attach=2, color=GRY)


# ----------------------------------------------------------------------------- legend
def L_hood(s, x, y):
    hood(s, x - 0.42, y - 0.11, x + 0.42, y + 0.11, cells=5, band=0.08, o=0.03)
def L_gduct(s, x, y):
    s.duct([(x - 0.42, y), (x + 0.42, y)], w=0.2)
def L_mduct(s, x, y):
    s.line((x - 0.42, y + 0.1), (x + 0.42, y + 0.1), linetype="DASHED"); s.line((x - 0.42, y - 0.1), (x + 0.42, y - 0.1), linetype="DASHED")
    s.line((x - 0.42, y - 0.1), (x - 0.42, y + 0.1)); s.line((x + 0.42, y - 0.1), (x + 0.42, y + 0.1))
def L_fan(s, x, y):
    s.fan(x, y, 0.13)
def L_esp(s, x, y):
    esp(s, x, y, w=0.6, h=0.24, txt="ESP")
def L_sfan(s, x, y):
    s.fan(x - 0.15, y, 0.1); sduct(s, [(x - 0.05, y), (x + 0.4, y)])
def L_grille(s, x, y):
    s.grille(x, y, w=0.5, h=0.14)
def L_nozzle(s, x, y):
    nozzle(s, x - 0.2, y); s.pline([(x - 0.2, y + 0.085), (x - 0.2, y + 0.11), (x + 0.3, y + 0.11)], color=FIRE, lw=13, linetype="DASHED")
    s.rect(x + 0.3, y - 0.07, x + 0.42, y + 0.11, color=FIRE, lw=13)
def L_riser(s, x, y):
    riser_rect(s, x - 0.18, y, 0.3, 0.2, ""); riser_circ(s, x + 0.25, y)
def L_spark(s, x, y):
    s.rect(x - 0.3, y - 0.1, x + 0.3, y + 0.1, lw=25)
    s.hatch([(x - 0.3, y - 0.1), (x + 0.3, y - 0.1), (x + 0.3, y + 0.1), (x - 0.3, y + 0.1)], pattern="ANSI31", scale=0.25)

LEGEND_G = [
    (L_hood, "هود شفط ستانلس مع فلاتر دهون Baffle ونظام إطفاء", "SS exhaust hood + baffle filters + fire suppression"),
    (L_spark, "قسم فلتر مانع للشرر فوق شواية الفحم", "spark-arrestor filter section (charcoal grill)"),
    (L_gduct, "دكت شفط دهون 600×400 صاج أسود 1.2 مم ملحوم", "welded 1.2 mm black steel grease duct 600×400"),
    (L_mduct, "دكت هواء تعويضي 700×400 صاج مجلفن معزول", "insulated GI make-up air duct 700×400"),
    (L_fan, "مروحة شفط طاردة مركزية / مروحة هواء تعويضي على السطح", "roof upblast exhaust fan / make-up air fan"),
    (L_esp, "وحدة ترسيب كهروستاتيكي ESP + فلتر كربون للروائح", "electrostatic precipitator + carbon odour filter"),
    (L_sfan, "مروحة شفط صغيرة Ø150 / Ø400 مع دكت دائري ولوفر خارجي", "small extract fan + round duct + ext. louvre"),
    (L_grille, "شبكة هواء / لوفر ألمنيوم في الجدار", "wall grille / aluminium louvre"),
    (L_nozzle, "فوهة إطفاء كيميائي رطب + أنبوب العامل + أسطوانة", "wet-chemical nozzle + agent pipe + cylinder"),
]
LEGEND_M = [
    (L_hood, "هود مطبخ صغير ستانلس 0.90×0.60 م مع فلتر دهون", "small kitchenette hood + grease filter"),
    (L_sfan, "مروحة شفط جدارية/سقفية Ø150 - Ø250 مع دكت دائري", "wall / ceiling extract fan + round duct"),
    (L_grille, "شبكة هواء نقي / شبكة نقل هواء / لوفر", "fresh-air grille / transfer grille / louvre"),
    (L_riser, "صاعد دكت مستطيل / دائري إلى السطح", "rectangular / round duct riser to the roof"),
    (L_gduct, "دكت شفط دهون 600×400 (صاعد من الطابق الأرضي)", "grease duct riser 600×400 from ground floor"),
    (L_mduct, "دكت هواء تعويضي 700×400 معزول (صاعد)", "insulated make-up air duct riser 700×400"),
]

def legend(s, x, y, rows, w=10.4, rh=0.3):
    return s.legend(x, y, "جدول رموز الشفط والتهوية - EXHAUST & VENTILATION LEGEND", rows, w=w, rh=rh)


# ----------------------------------------------------------------------------- quantity schedule
def schedule(s, x, y, title, rows, cols, rh=0.26):
    """RTL table: cols = [(header, width)] from the right edge; rows = list of cell lists. Drawn down from (x,y)."""
    W = sum(c[1] for c in cols)
    th, hh = 0.42, 0.32
    H = th + hh + rh * len(rows)
    s.rect(x, y - H, x + W, y, color=BLK, layer="LEGEND")
    s.hatch([(x, y - th), (x + W, y - th), (x + W, y), (x, y)], color=254, layer="LEGEND")
    s.text(x + W / 2, y - th / 2, title, h=0.18, attach=5, color=BLK, layer="LEGEND")
    s.hatch([(x, y - th - hh), (x + W, y - th - hh), (x + W, y - th), (x, y - th)], color=253, layer="LEGEND")
    s.line((x, y - th), (x + W, y - th), color=BLK, layer="LEGEND")
    s.line((x, y - th - hh), (x + W, y - th - hh), color=BLK, layer="LEGEND")
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
            s.text((x0 + x1) / 2, cy, cell, h=0.1, attach=5, color=BLK, layer="LEGEND", width=x1 - x0 - 0.05)
    return H

COLS = [("الرمز", 1.2), ("البند", 2.5), ("المواصفات", 5.3), ("الكمية", 0.85), ("الوحدة", 0.75)]

SCHED_G = [
    ["H-1", "هود شفط المطبخ", "ستانلس 304 سماكة 1.2 مم - 8.10 × 1.20 × 0.50 م مع إضاءة LED", "1", "عدد"],
    ["BF", "فلتر دهون Baffle", "ستانلس 500 × 500 × 50 مم قابل للغسيل", "14", "عدد"],
    ["SA", "فلتر مانع للشرر", "ستانلس 500 × 500 مم فوق شواية الفحم (قسم 1.10 م)", "2", "عدد"],
    ["FS", "نظام إطفاء الهود", "كيميائي رطب ANSUL R-102 - أسطوانة 3 جالون - 10 فوهات - سحب يدوي", "1", "نظام"],
    ["ED", "دكت شفط دهون", "600 × 400 مم صاج أسود 1.2 مم ملحوم + غلاف مقاوم للحريق + بابا تنظيف 300×300", "4.5", "م.ط"],
    ["EF-1", "مروحة شفط طاردة مركزية Upblast", "6000 CFM - ضغط ستاتيكي 750 Pa - 3 HP - 380V - على السطح", "1", "عدد"],
    ["ESP", "وحدة ترسيب كهروستاتيكي + كربون", "6000 CFM - 1.20 × 0.80 م - كفاءة 95% - باب صيانة", "1", "عدد"],
    ["MUA-1", "مروحة هواء تعويضي", "5000 CFM - 300 Pa - 2 HP - فلتر G4 - على السطح", "1", "عدد"],
    ["MD", "دكت هواء تعويضي", "700 × 400 مم صاج مجلفن معزول 25 مم", "2.5", "م.ط"],
    ["MG", "شبكة هواء تعويضي", "1200 × 400 مم ألمنيوم مزدوجة الانحراف مع دامبر", "1", "عدد"],
    ["EF-2..7", "مروحة شفط صغيرة", "Ø150 - 150 CFM - 35 dB - دورات المياه/المصلى/المستودع/الخدمة + 5 لوفر خارجي", "6", "عدد"],
    ["EF-8,9", "مروحة تفريغ دخان جدارية", "Ø400 - 1500 CFM - أعلى الزجاج الجانبي +3.40 م", "2", "عدد"],
]
SCHED_M = [
    ["H-2", "هود المطبخ الصغير", "ستانلس 304 - 0.90 × 0.60 × 0.40 م مع فلتر دهون", "1", "عدد"],
    ["ED-2", "دكت شفط الهود الصغير", "Ø150 صاج مجلفن 0.8 مم إلى السطح", "4.0", "م.ط"],
    ["EF-M1", "مروحة شفط الهود الصغير", "Ø150 - 300 CFM - على السطح", "1", "عدد"],
    ["EF-M2,3", "مروحة شفط جدارية", "Ø250 - 600 CFM مع مصراع جاذبية - منطقة التحضير والغسيل", "2", "عدد"],
    ["EF-M4,5", "مروحة شفط دورات المياه", "Ø150 - 150 CFM إلى لوفر في الجدار الخلفي", "2", "عدد"],
    ["EF-M6", "مروحة شفط الممر", "Ø200 - 300 CFM جدارية +2.30 م", "1", "عدد"],
    ["EF-M7", "مروحة شفط المستودع", "Ø150 - 150 CFM سقفية إلى السطح", "1", "عدد"],
    ["FG", "شبكة هواء نقي", "400 × 200 مم ألمنيوم مع فلتر - الغرف 3 + المكتب", "4", "عدد"],
    ["TG", "شبكة نقل هواء في الأبواب", "400 × 200 مم - الغرف 3 + غرفة التجميد + المستودع", "5", "عدد"],
    ["VG", "شبكة تهوية مكثف الثلاجة", "400 × 400 مم إلى الردهة", "1", "عدد"],
    ["R", "صاعد دكت", "شفط 600×400 + هواء تعويضي 700×400 (غلاف مقاوم للحريق) + Ø150", "3", "عدد"],
]


# ============================================================================= GROUND
def draw_G(s):
    HX0, HY0, HX1, HY1 = 15.4, 37.25, 23.5, 38.45        # hood: back edge on the kitchen back wall face
    SPX = 22.4                                             # spark-arrestor section from x=22.4 to the end
    WY0, WY1 = 38.45, 38.8                                 # back wall faces
    RX, RY = 19.5, 40.2                                    # riser x / roof duct y
    EX, FX = 21.8, 23.4                                    # ESP centre / exhaust fan centre
    MX = 16.3                                              # make-up air riser x
    # ---- hood + filters + collar
    hood(s, HX0, HY0, HX1, HY1, cells=14, spark=SPX)
    collar(s, RX, HY1 - 0.165)
    s.text(22.95, 37.6, "مانع شرر", h=0.09, attach=5)
    # ---- wet-chemical fire suppression: nozzles over each appliance, plenum and duct, agent pipe, cylinder, pull
    NZ = [15.8, 16.3, 16.8, 18.15, 19.2, 20.1, 22.9]
    for x in NZ:
        nozzle(s, x, 38.0)
    nozzle(s, 17.3, 38.24); nozzle(s, 21.6, 38.24); nozzle(s, RX, 38.3)
    s.pline([(24.5, 36.9), (24.5, 37.1), (24.1, 37.1), (24.1, 38.0), (15.8, 38.0)], color=FIRE, lw=13, linetype="DASHED")
    for x in (17.3, 21.6):
        s.line((x, 38.0), (x, 38.24), color=FIRE, lw=13, linetype="DASHED")
    s.line((RX, 38.0), (RX, 38.3), color=FIRE, lw=13, linetype="DASHED")
    s.rect(24.35, 36.6, 24.65, 36.9, color=FIRE, lw=35)
    s.text(24.5, 36.55, "أسطوانة الإطفاء 3 جالون", h=0.09, attach=2, color=FIRE)
    s.rect(24.22, 36.05, 24.38, 36.21, color=FIRE, lw=35)
    s.text(24.43, 36.13, "سحب يدوي", h=0.09, attach=4, color=FIRE)
    # ---- grease duct riser through the back wall -> roof: ESP -> upblast fan
    s.duct([(RX, HY1), (RX, RY), (EX - 0.6, RY)], w=0.6)
    esp(s, EX, RY + 0.0, w=1.2, h=0.8)
    s.duct([(EX + 0.6, RY), (FX - 0.35, RY)], w=0.6)
    s.fan(FX, RY, 0.35, label="EF-1")
    s.text(RX, 39.65, "600×400", h=0.09, attach=5, rotation=90)
    # ---- make-up air: roof fan -> insulated duct down through the wall -> grille above the hood
    s.fan(MX, 40.5, 0.33, label="MUA-1")
    s.pline([(MX - 0.35, 40.17), (MX - 0.35, 38.7)], linetype="DASHED"); s.pline([(MX + 0.35, 40.17), (MX + 0.35, 38.7)], linetype="DASHED")
    s.line((MX - 0.35, 40.17), (MX + 0.35, 40.17))
    s.text(MX, 39.4, "700×400", h=0.09, attach=5, rotation=90)
    s.grille(MX, 38.62, w=1.2, h=0.16)
    s.text(15.58, 38.62, "MG 1200×400", h=0.08, attach=6)
    roof_zone(s, 14.9, 39.85, 24.1, 41.3, "منطقة السطح فوق المطبخ - معدات الشفط والهواء التعويضي على قواعد خرسانية 20 سم")
    # ---- small extract fans + round ducts + exterior louvres
    sfan(s, 9.1, 39.35, "EF-2"); sfan(s, 9.1, 37.7, "EF-3")
    sduct(s, [(8.93, 39.35), (7.6, 39.35)], "Ø150", 8.3, 39.45); sduct(s, [(8.93, 37.7), (7.6, 37.7)], "Ø150", 8.3, 37.8)
    louvre(s, 7.33, 39.35, rot=90); louvre(s, 7.33, 37.7, rot=90)
    sfan(s, 30.62, 38.2, "EF-4", dx=-0.55, dy=-0.3)                               # women WC
    sduct(s, [(30.62, 38.37), (30.62, 38.5)]); louvre(s, 30.62, 38.62)
    sfan(s, 29.3, 36.6, "EF-5", dx=0.2, dy=-0.3)                                   # prayer room
    sfan(s, 27.2, 36.85, "EF-6")                                                   # store
    sduct(s, [(27.2, 37.02), (27.2, 37.15), (29.3, 37.15), (29.3, 38.5)], "Ø200", 29.45, 37.9, rot=90)
    sduct(s, [(29.3, 36.77), (29.3, 37.15)]); louvre(s, 29.3, 38.62)
    sfan(s, 31.0, 32.65, "EF-7", dx=-0.45, dy=0.1)                                 # service room
    sduct(s, [(31.17, 32.65), (31.4, 32.65)]); louvre(s, 31.5, 32.65, rot=90)
    s.fan(31.3, 34.0, 0.25, label="EF-8"); s.fan(31.3, 29.3, 0.25, label="EF-9")   # smoke purge wall fans
    # ---- dimensions (red)
    s.dim((HX0, HY1), (HX1, HY1), offset=0.55, **D)                                # hood total 8.10 (base y 39.0)
    s.dim((HX0, HY0), (RX, HY0), offset=-0.2, **D)                                 # hood start -> collar 4.10
    s.dim((RX, HY0), (SPX, HY0), offset=-0.2, **D)                                 # collar -> spark section 2.90
    s.dim((SPX, HY0), (HX1, HY0), offset=-0.2, **D)                                # spark section 1.10
    s.dim((HX1, HY0), (HX1, HY1), offset=0.3, horizontal=False, **D)               # hood depth 1.20
    s.dim((15.3, WY1), (MX, WY1), offset=0.75, **D)                                # kitchen wall -> MUA riser 1.00
    s.dim((MX, WY1), (RX, WY1), offset=0.75, **D)                                  # MUA riser -> exhaust riser 3.20
    s.dim((RX, HY1), (RX, RY), offset=-0.55, horizontal=False, **D)                # riser length 1.65
    s.dim((MX, WY1), (MX, 40.17), offset=-1.15, horizontal=False, **D)             # MUA duct length 1.37
    s.dim((RX, RY), (EX, RY), offset=0.65, **D)                                    # riser -> ESP 2.30
    s.dim((EX, RY), (FX, RY), offset=0.65, **D)                                    # ESP -> fan 1.60
    s.dim((EX - 0.6, RY - 0.4), (EX + 0.6, RY - 0.4), offset=-0.22, **D)           # ESP length 1.20 (base y 39.58)
    s.dim((7.33, 39.35), (9.1, 39.35), offset=0.15, **D)                           # men WC fan from the wall
    s.dim((9.1, 37.7), (9.1, 39.35), offset=0.25, horizontal=False, **D)           # men WC fans spacing
    s.dim((29.3, WY1), (30.62, WY1), offset=0.2, **D)                              # louvres spacing on the back wall
    s.dim((27.2, 36.85), (29.3, 36.85), offset=-0.45, **D)                         # store -> prayer fans
    s.dim((31.3, 29.3), (31.3, 34.0), offset=0.7, horizontal=False, **D)           # smoke purge fans spacing
    s.dim((31.3, 34.0), (31.3, 35.0), offset=0.7, horizontal=False, **D)           # to the BOH wall
    s.dim((30.5, 32.65), (31.0, 32.65), offset=-0.4, **D)                          # service fan from the wall
    # ---- callouts (Arabic, black, leaders)
    s.text(14.95, 41.05, "مروحة هواء تعويضي MUA-1 على السطح - 5000 CFM\\P300 Pa - 2 HP - فلتر G4 - دكت 700×400 معزول", attach=3, **C)
    s.leader([(14.95, 40.9), (15.95, 40.5)])
    s.text(14.95, 40.3, "شبكة هواء تعويضي 1200×400 ألمنيوم\\Pفي الجدار الخلفي فوق الهود +2.40 م", attach=3, **C)
    s.leader([(14.95, 40.15), (15.7, 38.7)])
    s.text(14.95, 39.6, "هود شفط ستانلس ستيل 304 - 8.10 × 1.20 × 0.50 م\\Pأسفل الهود +2.00 م - بروز 15 سم عن المعدات\\P"
                        "فلاتر دهون Baffle 500×500 مم (14 عدد) + إضاءة LED\\Pنظام إطفاء كيميائي رطب 10 فوهات (ANSUL R-102)\\P"
                        "صاعد دكت الشفط 600×400 داخل غلاف مقاوم للحريق ساعتين", attach=3, **C)
    s.leader([(14.95, 39.3), (15.45, 38.35)])
    s.text(14.95, 38.4, "مروحة شفط Ø150 - 150 CFM لكل مقصورة (2 عدد)\\Pدكت PVC Ø150 إلى لوفر في الجدار الجانبي", attach=3, **C)
    s.leader([(10.4, 38.2), (9.3, 39.2)])
    s.text(24.3, 41.3, "مروحة شفط طاردة مركزية Upblast على السطح EF-1\\P6000 CFM - ضغط ستاتيكي 750 Pa - 3 HP - 380V - مخرج رأسي 3 م", attach=1, **C)
    s.leader([(24.3, 41.15), (23.65, 40.45)])
    s.text(24.3, 40.75, "وحدة ترسيب كهروستاتيكي ESP + فلتر كربون للروائح\\P6000 CFM - 1.20 × 0.80 م - كفاءة 95% - باب صيانة", attach=1, **C)
    s.leader([(24.3, 40.6), (22.4, 40.58)])
    s.text(24.3, 40.15, "قسم فلتر مانع للشرر 1.10 م فوق شواية الفحم\\Pفلاتر Spark arrestor ستانلس (2 عدد)", attach=1, **C)
    s.leader([(24.3, 40.0), (23.45, 38.4)])
    s.text(30.0, 41.3, "مراوح شفط Ø150 - 150 CFM (6 عدد): دورات المياه\\Pوالمصلى والمستودع وغرفة الخدمة - تعمل مع الإضاءة", attach=1, **C)
    s.leader([(30.0, 41.15), (30.62, 38.72)])
    s.text(30.0, 40.75, "لوفر خارجي Ø150 / Ø200 مع شبك ضد الطيور\\Pوصمام عدم رجوع - في الجدار الخلفي", attach=1, **C)
    s.leader([(30.0, 40.6), (29.3, 38.72)])
    s.text(32.75, 31.05, "مروحة تفريغ دخان Ø400\\P1500 CFM - أعلى الزجاج\\P+3.40 م (2 عدد)", attach=1, h=0.11, color=BLK)
    s.leader([(32.75, 30.95), (31.55, 33.85)]); s.leader([(32.75, 30.95), (31.55, 29.45)])
    s.text(18.3, 30.35, "إجمالي أعمال الشفط والتهوية - الطابق الأرضي: هود 1 - فلاتر 16 - فوهات إطفاء 10\\P"
                        "مروحة شفط 1 - ESP 1 - مروحة هواء تعويضي 1 - مراوح شفط صغيرة 6 - مراوح دخان 2 - لوفر 5", h=0.13, attach=5, color=BLK)
    # ---- legend, schedule, notes
    x0, y0, x1, y1 = EMPTY_G
    legend(s, x0 + 0.2, 45.25, LEGEND_G, w=10.4, rh=0.3)
    schedule(s, 14.8, 45.25, "جدول كميات الشفط والتهوية - EXHAUST QUANTITY SCHEDULE", SCHED_G, COLS, rh=0.25)
    s.notes(34.8, 45.0, [
        "هود شفط ستانلس 304 سماكة 1.2 مم مع فلاتر Baffle وإضاءة LED مقاومة للحرارة",
        "دكت شفط الدهون صاج أسود 1.2 مم ملحوم مانع للتسرب بميل 2% نحو الهود - NFPA 96",
        "أبواب تنظيف 300×300 كل 3 م وعند كل كوع - غلاف مقاوم للحريق ساعتين حول الدكت",
        "بروز الهود 15 سم على الأقل عن حافة المعدات وأسفل الهود على ارتفاع +2.00 م",
        "معدل الشفط 500 CFM/م للمعدات و 700 CFM/م لقسم الفحم = 6000 CFM إجمالي",
        "هواء تعويضي 80% من الشفط = 5000 CFM مع فلتر G4 وضغط سالب 50 Pa في المطبخ",
        "نظام إطفاء كيميائي رطب مع فوهات فوق كل جهاز وقطع تلقائي للغاز والكهرباء",
        "مراوح دورات المياه Ø150 تعمل مع الإضاءة مع مؤقت إيقاف 10 دقائق وصمام عدم رجوع",
        "مخرج مروحة الشفط رأسي 3 م فوق السطح وبعيد 3 م عن أي مأخذ هواء أو فتحة",
        "تهوية الصالة العامة عبر رجوع هواء وحدات التكييف - انظر مخطط التكييف",
        "العدد: هود 1 - مروحة شفط 1 - ESP 1 - هواء تعويضي 1 - مراوح صغيرة 8 - فوهات 10",
    ], h=0.14, w=9.0, title="ملاحظات الشفط والتهوية")


# ============================================================================= MEZZANINE
def draw_M(s):
    WY0, WY1, WC = 13.44, 13.83, 13.63          # back wall faces / centre
    RX, MX = 19.5, 16.3                          # grease duct riser / make-up air riser (same x as ground)
    # ---- risers through the back wall
    riser_rect(s, RX, WC, 0.6, 0.4, "R-E 600×400")
    riser_rect(s, MX, WC, 0.7, 0.4, "R-M 700×400")
    # ---- kitchenette hood + Ø150 duct along the left wall -> riser in the stair room
    hood(s, 7.5, 11.4, 8.1, 12.3, rear="left", cells=2, band=0.16)
    sduct(s, [(7.8, 12.3), (7.8, 13.9)], "Ø150", 8.0, 13.2, rot=90)
    riser_circ(s, 7.8, 14.08, "R-K")
    # ---- extract fans
    s.fan(25.0, WC, 0.25, label=None); s.text(25.3, WC + 0.3, "EF-M2", h=0.09, color=BLK)
    s.fan(29.0, WC, 0.25, label=None); s.text(29.3, WC + 0.3, "EF-M3", h=0.09, color=BLK)
    sfan(s, 18.3, 13.2, "EF-M4", dx=-0.7, dy=-0.35); sduct(s, [(18.3, 13.37), (18.3, 13.5)]); louvre(s, 18.3, WC)
    sfan(s, 20.4, 13.1, "EF-M5", dx=0.2, dy=-0.35); sduct(s, [(20.4, 13.27), (20.4, 13.5)]); louvre(s, 20.4, WC)
    s.fan(14.0, 11.6, 0.2); s.text(14.3, 11.75, "EF-M6", h=0.09, color=BLK)                  # corridor wall fan
    sfan(s, 27.3, 7.0, "EF-M7", dx=0.2, dy=-0.35)                                           # store ceiling fan -> roof
    s.text(27.3, 6.78, "إلى السطح", h=0.08, attach=2)
    # ---- fresh-air grilles (front wall of the rooms + office) and door transfer grilles
    FG = [(9.5, 6.5), (14.1, 6.5), (18.75, 6.5), (30.6, 6.5)]
    for x, y in FG:
        s.grille(x, y, w=0.4, h=0.14); s.text(x + 0.25, y - 0.12, "FG", h=0.08, color=BLK)
    TG = [(11.0, 9.7), (12.3, 9.7), (17.2, 9.7), (23.9, 9.4), (29.0, 9.4)]
    for x, y in TG:
        s.grille(x, y, w=0.4, h=0.12); s.text(x + 0.25, y + 0.08, "TG", h=0.08, color=BLK)
    s.grille(23.3, 8.5, w=0.4, h=0.14, rot=90); s.text(23.45, 8.75, "VG", h=0.08, color=BLK)
    # ---- dimensions (red)
    chain = [MX, 18.3, RX, 20.4, 25.0, 29.0, 31.5]
    for a, b in zip(chain[:-1], chain[1:]):
        s.dim((a, WC), (b, WC), offset=0.82, **D)                                   # back-wall chain (base y 14.45)
    s.dim((15.5, WC), (MX, WC), offset=0.82, **D)                                   # from the WC-A wall
    s.dim((7.5, 11.4), (7.5, 12.3), offset=-0.5, horizontal=False, **D)             # kitchenette hood 0.90
    s.dim((7.8, 12.3), (7.8, 13.9), offset=-0.9, horizontal=False, **D)             # Ø150 duct run 1.60
    s.dim((9.5, 11.6), (14.0, 11.6), offset=0.35, **D)                              # corridor fan from the wall
    s.dim((14.0, 11.6), (15.5, 11.6), offset=0.35, **D)
    for a, b in zip([7.4, 9.5, 14.1, 18.75], [9.5, 14.1, 18.75, 20.9]):
        s.dim((a, 6.5), (b, 6.5), offset=-0.4, **D)                                 # fresh-air grilles chain
    s.dim((26.7, 7.0), (27.3, 7.0), offset=0.3, **D)                                # store fan from the wall
    s.dim((23.3, 8.5), (23.3, 9.4), offset=0.25, horizontal=False, **D)             # condenser grille from the door wall
    # ---- callouts
    s.text(7.05, 12.75, "هود مطبخ صغير ستانلس 0.90×0.60 م\\Pفلتر دهون + دكت Ø150 إلى مروحة\\P300 CFM على السطح", attach=3, **C)
    s.leader([(7.05, 12.6), (7.5, 12.1)])
    s.text(9.8, 14.3, "صاعد دكت Ø150 إلى مروحة الهود الصغير على السطح EF-M1", attach=4, h=0.11, color=BLK)
    s.leader([(9.8, 14.3), (8.0, 14.15)])
    s.text(17.9, 15.25, "صواعد: دكت شفط الهود 600×400 + دكت هواء تعويضي 700×400\\Pمن الطابق الأرضي إلى السطح داخل غلاف مقاوم للحريق ساعتين", attach=5, **C)
    s.leader([(16.9, 14.87), (MX, 13.85)]); s.leader([(18.9, 14.87), (RX, 13.85)])
    s.text(21.3, 15.25, "مروحة شفط Ø150 - 150 CFM لكل دورة مياه (2 عدد)\\Pدكت Ø150 إلى لوفر في الجدار الخلفي", attach=1, **C)
    s.leader([(21.3, 15.1), (20.4, 13.85)])
    s.text(27.0, 15.25, "مروحة شفط جدارية Ø250 - 600 CFM (2 عدد)\\Pمنطقة التحضير والغسيل +2.20 م مع مصراع", attach=5, **C)
    s.leader([(26.0, 14.87), (25.2, 13.85)])
    s.text(13.6, 12.2, "مروحة شفط الممر Ø200 - 300 CFM جدارية +2.30 م", h=0.11, attach=5, color=BLK)
    s.leader([(14.0, 12.1), (14.0, 11.8)])
    s.text(14.1, 5.75, "شبكة هواء نقي 400×200 مع فلتر في الجدار الأمامي لكل غرفة سكن (3 عدد) + المكتب", h=0.11, attach=5, color=BLK)
    s.leader([(14.1, 5.85), (14.1, 6.42)])
    s.text(22.7, 11.1, "شبكة نقل هواء 400×200\\Pأسفل كل باب TG (5 عدد)", h=0.1, attach=5, color=BLK)
    s.leader([(23.3, 10.95), (23.9, 9.5)])
    s.text(22.4, 7.6, "شبكة تهوية\\Pمكثف 400×400", h=0.1, attach=5, color=BLK)
    s.leader([(22.9, 7.75), (23.22, 8.4)])
    s.text(27.0, 5.85, "مروحة شفط المستودع Ø150 - 150 CFM سقفية إلى السطح", h=0.1, attach=5, color=BLK)
    s.leader([(27.2, 5.95), (27.3, 6.83)])
    s.text(31.0, 5.45, "شبكة هواء نقي 300×300 للمكتب", h=0.1, attach=5, color=BLK)
    s.leader([(30.7, 5.55), (30.6, 6.42)])
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    s.text(19.5, 3.3, "إجمالي الميزانين: هود 1 - مراوح شفط 7 - شبكات هواء نقي 4 - شبكات نقل 5 - شبكة مكثف 1 - صواعد 3", h=0.14, attach=5, color=BLK)
    # ---- legend, schedule, notes
    x0, y0, x1, y1 = EMPTY_M
    legend(s, x0 + 0.2, 20.25, LEGEND_M, w=10.4, rh=0.32)
    schedule(s, 14.8, 20.25, "جدول كميات الشفط والتهوية - الميزانين", SCHED_M, COLS, rh=0.26)
    s.notes(34.8, 20.0, [
        "هود المطبخ الصغير ستانلس 0.90×0.60 م مع فلتر دهون ودكت Ø150 إلى مروحة على السطح",
        "مراوح التحضير والغسيل جدارية Ø250 - 600 CFM مع مصراع جاذبية على ارتفاع +2.20 م",
        "مراوح دورات المياه Ø150 - 150 CFM تعمل مع الإضاءة مع مؤقت إيقاف 10 دقائق",
        "شبكات هواء نقي 400×200 مع فلتر في الجدار الأمامي لكل غرفة وشبكة نقل أسفل كل باب",
        "صاعد دكت شفط الهود 600×400 وصاعد الهواء التعويضي 700×400 داخل غلاف مقاوم للحريق ساعتين",
        "باب تنظيف 300×300 على صاعد دكت الدهون عند مستوى الميزانين",
        "تهوية غرفة التجميد: شبكة 400×400 لمكثف الثلاجة + مروحة شفط المستودع Ø150 إلى السطح",
        "العدد: هود 1 - مراوح 7 - شبكات هواء نقي 4 - شبكات نقل 5 - شبكة مكثف 1 - صواعد 3",
    ], h=0.14, w=9.0, title="ملاحظات الشفط والتهوية - الميزانين")
