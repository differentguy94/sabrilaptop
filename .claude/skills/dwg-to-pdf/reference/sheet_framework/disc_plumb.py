"""Plumbing - water supply (cold/hot) + drainage (مخطط السباكة) - ground floor + mezzanine.
Positions were read from the gridded base plan (walls: ground back wall y 38.39-38.78, kitchen left wall
x 15.31-15.54, hall wall y 36.41-36.63, men WC block 7.46-9.66, women WC 29.69-31.08 x 36.71-38.39,
tapered wall 23.29-23.69 at the back wall; mezz back wall y 13.44-13.83, 3-compartment sinks y 11.41-12.05
under the stair wall 12.07-12.23, double sink 22.0-23.2 x 12.8-13.38)."""
import math
from sitemodel import G, M, EMPTY_G, EMPTY_M

LAYER = "P-PLUMB"
COLD, HOT, DRAIN, CO, TAG, DIM = 150, 1, 6, 3, 30, 1

# ----------------------------------------------------------------------------- counters
N = {}


def inc(k, n=1):
    N[k] = N.get(k, 0) + n


# ----------------------------------------------------------------------------- symbol helpers
def wp(s, x, y, kind="CH", dx=0.15):
    """water point(s): C left / H right of (x,y); single letter for one kind"""
    if kind == "CH":
        s.water_point(x - dx, y, "C"); s.water_point(x + dx, y, "H")
        inc("C"); inc("H")
    else:
        s.water_point(x, y, kind); inc(kind)


def fd(s, x, y):
    s.floor_drain(x, y, size=0.18); inc("FD")


def plen(pts):
    """polyline length (m) - accumulated per pipe type for the quantity schedule"""
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def drain(s, pts, size=4):
    """drain line: 4"/6" lw 35, 2" lw 25"""
    s.pline(pts, color=DRAIN, lw=35 if size >= 4 else 25)
    inc(f"L_D{size}", plen(pts))


def cold(s, pts):
    s.pline(pts, color=COLD, lw=25, linetype="DASHED")
    inc("L_C", plen(pts))


def hot(s, pts):
    s.pline(pts, color=HOT, lw=25, linetype="DASHED")
    inc("L_H", plen(pts))


def pipe_rows():
    """quantity-schedule rows for the pipe runs drawn on the sheet (lengths in m, +10 % fittings)"""
    lc, lh = N.get("L_C", 0) * 1.1, N.get("L_H", 0) * 1.1
    ld = (N.get("L_D4", 0) + N.get("L_D6", 0)) * 1.1
    l2 = N.get("L_D2", 0) * 1.1
    return [
        ('PPR PN16 قطر 3/4" و 1/2" داخل الجدران', f"{lc:.0f} م", "", "مواسير ماء بارد"),
        ('PPR PN20 قطر 3/4" معزولة حرارياً', f"{lh:.0f} م", "", "مواسير ماء ساخن"),
        ('UPVC قطر 4" (+6" مجمع خارجي) ميل 2% / 2" للفروع', f"{ld:.0f} + {l2:.0f} م", "", "مواسير صرف"),
    ]


def legend_bg(s, x, y, w=10.2):
    """white fill under the legend so the stair-room lines of the base plan do not show through"""
    H = 0.5 + len(LEGEND) * 0.36
    s.hatch([(x, y - H), (x + w, y - H), (x + w, y), (x, y)], color=255, layer="LEGEND")


def gt(s, x, y):
    s.circle(x, y, 0.4, color=DRAIN, lw=35); s.circle(x, y, 0.28, color=DRAIN, lw=13)
    s.text(x, y, "G.T", h=0.13, attach=5, color=DRAIN); inc("GT")


def ic(s, x, y, tag):
    s.hatch([(x - 0.3, y - 0.3), (x + 0.3, y - 0.3), (x + 0.3, y + 0.3), (x - 0.3, y + 0.3)], color=255)
    s.rect(x - 0.3, y - 0.3, x + 0.3, y + 0.3, color=DRAIN, lw=35)
    s.line((x - 0.3, y - 0.3), (x + 0.3, y + 0.3), color=DRAIN, lw=13)
    s.line((x - 0.3, y + 0.3), (x + 0.3, y - 0.3), color=DRAIN, lw=13)
    s.text(x + 0.34, y - 0.14, tag, h=0.11, attach=4, color=DRAIN); inc("IC")


def co(s, x, y, label=True):
    s.circle(x, y, 0.12, color=CO, lw=25); s.dot(x, y, 0.03, color=CO)
    if label:
        s.text(x + 0.14, y + 0.13, "C.O", h=0.09, color=CO)
    inc("CO")


def wh(s, x, y, tag):
    """electric water heater: white box 0.5x0.26 + tag inside"""
    pts = [(x - 0.25, y - 0.13), (x + 0.25, y - 0.13), (x + 0.25, y + 0.13), (x - 0.25, y + 0.13)]
    s.hatch(pts, color=255)
    s.rect(x - 0.25, y - 0.13, x + 0.25, y + 0.13, lw=35)
    s.text(x, y, tag, h=0.08, attach=5); inc("WH")


def riser(s, x, y, tag, color, tx, ty, attach=4):
    s.hatch([(x, y - 0.12), (x + 0.12, y), (x, y + 0.12), (x - 0.12, y)], color=255)
    s.circle(x, y, 0.12, color=color, lw=35); s.dot(x, y, 0.04, color=color)
    s.text(tx, ty, tag, h=0.09, color=color, attach=attach); inc("RISER")


def valve(s, x, y, rot=0.0, color=COLD):
    s.valve(x, y, 0.17, color=color, rot=rot); inc("VALVE")


def meter(s, x, y):
    s.hatch([(x - 0.18, y - 0.12), (x + 0.18, y - 0.12), (x + 0.18, y + 0.12), (x - 0.18, y + 0.12)], color=255)
    s.rect(x - 0.18, y - 0.12, x + 0.18, y + 0.12, color=COLD, lw=25)
    s.text(x, y, "M", h=0.11, attach=5, color=COLD); inc("METER")


def arrow(s, x, y, ang, size=0.16, color=DRAIN):
    a = math.radians(ang)
    d = (math.cos(a), math.sin(a)); n = (-math.sin(a), math.cos(a))
    tip = (x + d[0] * size, y + d[1] * size)
    b1 = (x - n[0] * size * 0.45, y - n[1] * size * 0.45)
    b2 = (x + n[0] * size * 0.45, y + n[1] * size * 0.45)
    s.hatch([tip, b1, b2], color=color)


def tag(s, x, y, txt, attach=1, h=0.11, color=TAG, width=0):
    return s.text(x, y, txt, h=h, attach=attach, color=color, width=width)


def dim(s, p1, p2, off, horizontal=True):
    s.dim(p1, p2, offset=off, color=DIM, h=0.12, horizontal=horizontal)


def dim_loc(s, p1, p2, off, tx, ty, h=0.12):
    """horizontal dimension like s.dim() but with a user-placed text midpoint (to dodge base-plan labels)"""
    x1, y1 = p1; x2, y2 = p2
    base = (x1, max(y1, y2) + off)
    d = s.msp.add_linear_dim(base=s.P(*base), p1=s.P(x1, y1), p2=s.P(x2, y2), angle=0, location=s.P(tx, ty),
                             dimstyle="A - dim int", dxfattribs={"layer": s.layer, "color": DIM},
                             override={"dimtxt": h, "dimasz": 0.08, "dimclrd": DIM, "dimclre": DIM, "dimclrt": DIM,
                                       "dimexe": 0.05, "dimexo": 0.05, "dimdec": 2, "dimtad": 1, "dimgap": 0.03,
                                       "dimblk": "ARCHTICK", "dimtxsty": "Standard"})
    d.render()
    return d


# ----------------------------------------------------------------------------- legend
def L_line(color, lw, lt=None):
    return lambda s, x, y: s.pline([(x - 0.38, y), (x + 0.38, y)], color=color, lw=lw, linetype=lt)


LEGEND = [
    (lambda s, x, y: s.water_point(x, y, "C"), 'نقطة ماء بارد PPR 1/2"', "cold water point"),
    (lambda s, x, y: s.water_point(x, y, "H"), 'نقطة ماء ساخن PPR 1/2"', "hot water point"),
    (lambda s, x, y: s.floor_drain(x, y, size=0.18), 'مصفى أرضي ستانلس 15×15 سم مع سيفون 2"', "floor drain F/D 2\" with trap"),
    (L_line(DRAIN, 35), 'خط صرف UPVC قطر 4" (رئيسي) / 2" (فرعي) ميل 2%', "drain line UPVC 4\" main / 2\" branch"),
    (L_line(COLD, 25, "DASHED"), 'ماسورة ماء بارد PPR PN16 قطر 3/4" - 1/2"', "cold water pipe PPR PN16"),
    (L_line(HOT, 25, "DASHED"), 'ماسورة ماء ساخن PPR PN20 معزولة 3/4"', "hot water pipe PPR PN20 insulated"),
    (lambda s, x, y: (s.circle(x, y, 0.17, color=DRAIN, lw=35), s.text(x, y, "G.T", h=0.08, attach=5, color=DRAIN)),
     "مصيدة شحوم تحت الأرضية 500 لتر بغطاء محكم", "grease trap 500 L under floor"),
    (lambda s, x, y: (s.rect(x - 0.22, y - 0.12, x + 0.22, y + 0.12, lw=35), s.text(x, y, "WH", h=0.09, attach=5)),
     "سخان ماء كهربائي معلق (السعة حسب المخطط)", "electric water heater, wall hung"),
    (lambda s, x, y: (s.rect(x - 0.15, y - 0.15, x + 0.15, y + 0.15, color=DRAIN, lw=35),
                      s.line((x - 0.15, y - 0.15), (x + 0.15, y + 0.15), color=DRAIN, lw=13),
                      s.line((x - 0.15, y + 0.15), (x + 0.15, y - 0.15), color=DRAIN, lw=13)),
     "غرفة تفتيش I.C قياس 60×60 سم بغطاء حديد زهر", "inspection chamber 60×60 cm"),
    (lambda s, x, y: (s.circle(x, y, 0.11, color=CO, lw=25), s.dot(x, y, 0.03, color=CO)), "فتحة تنظيف C.O مع غطاء نحاس", "cleanout C.O"),
    (lambda s, x, y: s.valve(x, y, 0.2, color=COLD), "محبس إغلاق كروي PPR", "stop valve (ball)"),
    (lambda s, x, y: (s.circle(x, y, 0.12, color=DRAIN, lw=35), s.dot(x, y, 0.04, color=DRAIN)),
     'صاعد / نازل: D.P صرف 4" - W.R ماء 3/4"', "riser: D.P drain / W.R water"),
]


def legend(s, x, y):
    return s.legend(x, y, "جدول رموز السباكة - PLUMBING LEGEND", LEGEND, w=10.2, rh=0.36, h=0.12)


# ----------------------------------------------------------------------------- schedule table
def table(s, x, y, title, header, rows, widths, rh=0.27, h=0.105):
    w = sum(widths); th = 0.36; hh = 0.3
    H = th + hh + rh * len(rows)
    s.hatch([(x, y - H), (x + w, y - H), (x + w, y), (x, y)], color=255, layer="LEGEND")
    s.rect(x, y - H, x + w, y, color=7, layer="LEGEND")
    s.hatch([(x, y - th), (x + w, y - th), (x + w, y), (x, y)], color=254, layer="LEGEND")
    s.text(x + w / 2, y - th / 2, title, h=0.17, attach=5, color=7, layer="LEGEND")
    yy = y - th
    s.line((x, yy - hh), (x + w, yy - hh), color=7, layer="LEGEND")
    cx = x
    for i, wd in enumerate(widths):
        if i:
            s.line((cx, yy), (cx, y - H), color=7, lw=5, layer="LEGEND")
        s.text(cx + wd / 2, yy - hh / 2, header[i], h=h, attach=5, color=7, layer="LEGEND")
        cx += wd
    yy -= hh
    last = len(widths) - 1
    for r in rows:
        cx = x
        for i, wd in enumerate(widths):
            if i == last or i == 0:
                s.text(cx + wd - 0.08, yy - rh / 2, str(r[i]), h=h, attach=6, color=7, layer="LEGEND", width=wd - 0.12)
            else:
                s.text(cx + wd / 2, yy - rh / 2, str(r[i]), h=h, attach=5, color=7, layer="LEGEND")
            cx += wd
        s.line((x, yy - rh), (x + w, yy - rh), color=7, lw=5, layer="LEGEND")
        yy -= rh
    return H


HEAD = ["المواصفات", "العدد", "الرمز", "البند"]
WID = [3.5, 0.8, 1.1, 4.1]


# ============================================================================= GROUND FLOOR
def draw_G(s):
    N.clear()
    BW0, BW1 = 38.46, 38.87           # back wall band (inner / outer face, measured on the plot)
    YC, YH = 38.72, 38.60             # cold / hot mains inside the band
    YCOL = 39.75                      # external sewer collector line
    YFD = 37.08                       # kitchen floor-drain / trunk line

    # ------------------------------------------------------------- main water inlet (from the street)
    cold(s, [(22.2, 41.0), (22.2, 38.74)])
    arrow(s, 22.2, 40.9, -90, color=COLD)
    meter(s, 22.2, 40.5)
    valve(s, 22.2, 40.1, rot=90)
    s.text(21.9, 40.85, "نقطة تغذية الماء الرئيسية", h=0.3, color=32, attach=3)
    tag(s, 21.9, 40.42, 'عداد مياه 1" + محبس رئيسي + صمام عدم رجوع', attach=3)
    tag(s, 22.45, 41.15, 'من شبكة المياه العامة - ماسورة 1" PPR', attach=1)

    # cold main inside the back wall band, west and east of the inlet
    cold(s, [(15.37, YC), (24.3, YC)])
    cold(s, [(24.8, YC), (30.62, YC)])
    valve(s, 16.0, YC); valve(s, 26.6, YC)
    wh(s, 24.55, 38.56, "WH-1 80L")                    # kitchen heater above the hand sinks
    valve(s, 24.1, YC)
    hot(s, [(24.8, YH), (30.24, YH)])                 # hot main east to women WC / ablution
    valve(s, 26.6, YH, color=HOT)
    tag(s, 15.45, 38.9, 'ماء بارد PPR 3/4" داخل الجدار الخلفي', attach=7, h=0.1)
    tag(s, 27.3, 38.9, 'ماء ساخن 3/4" معزول من WH-1', attach=7, h=0.1)
    # cold-main run lengths: chain between the base-plan 7.90/6.30 dims (y 39.09) and the 16.15 dim (y 39.43)
    for a, b in ((15.37, 21.75), (21.75, 22.2), (22.2, 29.62), (29.62, 30.62)):
        dim(s, (a, YC), (b, YC), 0.48)

    # water riser to the mezzanine
    riser(s, 21.75, 38.58, "W.R", COLD, 21.9, 38.5, attach=4)
    s.leader([(21.75, 38.7), (21.6, 38.9)], color=COLD)
    tag(s, 21.6, 38.9, 'صاعد ماء W.R 3/4" للميزانين', attach=9, h=0.1)

    # ------------------------------------------------------------- hand sinks (corridor, under the stair landing)
    for sx in (24.2, 24.85):
        wp(s, sx, 38.3)
    hot(s, [(25.0, YH), (25.0, 38.4)])
    drain(s, [(24.2, 38.2), (24.2, 38.14), (24.85, 38.14), (24.85, 38.2)], 2)
    drain(s, [(24.55, 38.14), (24.55, YFD)], 2)
    co(s, 24.55, 37.45)
    dim(s, (24.2, 38.3), (24.85, 38.3), -0.62)

    # ------------------------------------------------------------- kitchen floor drains + trunk to the grease trap
    for x in (16.3, 19.5, 22.5):
        fd(s, x, YFD)
    fd(s, 24.55, 36.35)
    drain(s, [(16.3, YFD), (24.55, YFD), (24.55, 36.35), (24.72, 36.33)])
    arrow(s, 21.0, YFD, 0)
    tag(s, 19.75, 37.19, 'صرف رئيسي 4" ميل 2% - إلى مصيدة الشحوم', attach=7, h=0.1)
    fd(s, 18.0, 35.8)                                  # counter back strip
    fd(s, 19.5, 36.25)                                 # salad fridge condensate
    drain(s, [(18.0, 35.8), (19.5, 35.8), (19.5, YFD)], 2)
    # mezzanine wash-area stack drops inside the thick tapered wall and joins the trunk
    riser(s, 23.45, 38.25, "D.P-1", DRAIN, 23.45, 38.42, attach=8)
    drain(s, [(23.45, 38.13), (23.45, YFD)])
    co(s, 23.45, 37.88)
    # dimensions of the drains along the cooking line (chain under the FD line)
    for a, b in ((15.54, 16.3), (19.5, 22.5), (22.5, 23.45), (23.45, 24.55)):
        dim(s, (a, YFD), (b, YFD), 0.26)
    dim_loc(s, (16.3, YFD), (19.5, YFD), 0.26, 17.0, 37.43)      # text moved left of the base-plan fryer labels
    dim(s, (22.3, YFD), (22.3, BW0), 0.0, horizontal=False)
    dim(s, (19.19, 36.25), (19.5, 36.25), -0.3)

    # ------------------------------------------------------------- grease trap + inspection chamber + sewer
    gt(s, 25.1, 36.3)
    drain(s, [(25.2, 36.7), (25.2, 39.45)])            # G.T outlet to I.C-1
    arrow(s, 25.2, 38.95, 90)
    ic(s, 25.2, YCOL, "I.C-1")
    drain(s, [(25.2, 40.05), (25.2, 41.0)], 6)
    arrow(s, 25.2, 41.0, 90)
    tag(s, 25.4, 41.15, 'إلى شبكة الصرف الصحي العامة UPVC 6"', attach=1)
    s.leader([(25.38, 36.02), (26.3, 34.5)], color=DRAIN)
    tag(s, 26.4, 34.55, "مصيدة شحوم G.T سعة 500 لتر - تحت الأرضية\\Pمدخل / مخرج 4\" مع تهوية 2\" - تنظيف شهري", attach=1, h=0.1, color=DRAIN)
    dim(s, (25.1, 36.3), (25.76, 36.3), 0.5)
    dim(s, (25.2, 36.3), (25.2, YCOL), 0.4, horizontal=False)
    dim(s, (15.37, BW1), (15.37, YCOL), -0.6, horizontal=False)
    dim(s, (22.2, YCOL), (25.2, YCOL), 0.55)

    # ------------------------------------------------------------- women WC + prayer room (ablution)
    cold(s, [(29.62, YC), (29.62, 36.4)])              # cold riser in the WC/prayer wall
    valve(s, 29.62, 38.3, rot=90)
    hot(s, [(30.24, YH), (30.24, 36.4)])
    wp(s, 30.62, 38.32, "C")                            # toilet flush
    cold(s, [(30.62, YC), (30.62, 38.42)])
    wp(s, 30.03, 37.3, dx=0.21)                        # women basin (wall hung at x 29.95)
    cold(s, [(29.62, 37.3), (29.82, 37.3)])
    fd(s, 30.6, 37.3)
    wp(s, 30.03, 36.4, dx=0.21)                        # ablution tap (prayer room)
    cold(s, [(29.62, 36.4), (29.82, 36.4)])
    fd(s, 30.45, 35.7)
    drain(s, [(29.95, 37.45), (29.95, 37.15), (30.45, 37.15)], 2)
    drain(s, [(30.6, 37.3), (30.45, 37.3)], 2)
    drain(s, [(29.95, 35.85), (29.95, 35.7), (30.45, 35.7)], 2)
    drain(s, [(30.45, 35.7), (30.45, 39.45)])
    co(s, 30.45, 35.45)
    arrow(s, 30.45, 38.9, 90)
    ic(s, 30.45, YCOL, "I.C-4")
    s.leader([(30.45, 35.7), (29.9, 34.6)], color=TAG)
    tag(s, 29.3, 34.55, 'نقطة وضوء C+H + مصفى أرضي 2" في المصلى', attach=1, h=0.1)
    dim(s, (29.69, 38.9), (30.45, 38.9), 0.0)
    dim(s, (29.69, 35.7), (30.45, 35.7), -0.3)
    dim(s, (29.82, 36.4), (29.82, 37.3), -0.55, horizontal=False)

    # external sewer collector along the back wall
    drain(s, [(15.15, YCOL), (24.9, YCOL)], 6)
    drain(s, [(25.5, YCOL), (30.15, YCOL)], 6)
    arrow(s, 20.0, YCOL, 0); arrow(s, 28.0, YCOL, 180)
    tag(s, 16.5, 39.95, 'مجمع صرف خارجي UPVC 6" ميل 1% - غرفة تفتيش عند كل تغيير اتجاه', attach=1, h=0.1)
    dim(s, (14.85, YCOL), (25.2, YCOL), -0.28)
    dim(s, (25.2, YCOL), (30.45, YCOL), -0.28)

    # ------------------------------------------------------------- men WC block (left) + stair-room heater
    cold(s, [(15.37, YC), (15.37, 36.52), (9.77, 36.52), (9.77, 39.22), (9.55, 39.22)])   # in the walls
    valve(s, 9.77, 36.95, rot=90)
    tag(s, 11.6, 36.76, 'ماء بارد PPR 3/4" داخل جدار الصالة - طول 10.7 م', attach=1, h=0.1)
    wh(s, 9.3, 39.22, "WH-2 30L")
    hot(s, [(9.1, 39.09), (9.1, 37.42)])
    wp(s, 8.98, 38.98, "C"); cold(s, [(9.77, 38.98), (9.08, 38.98)])          # toilet
    wp(s, 7.8, 38.38, "C"); cold(s, [(9.77, 38.38), (7.9, 38.38)])            # basin 1 (cubicle)
    wp(s, 8.1, 38.24, "H"); hot(s, [(9.1, 38.24), (8.2, 38.24)])
    wp(s, 7.8, 37.55, "C"); cold(s, [(9.77, 37.55), (7.9, 37.55)])            # basin 2 (anteroom)
    wp(s, 8.1, 37.42, "H"); hot(s, [(9.1, 37.42), (8.2, 37.42)])
    fd(s, 8.2, 38.05); fd(s, 8.3, 36.8)
    drain(s, [(8.62, 38.9), (8.62, 36.8), (10.15, 36.8)])                      # toilet 4" trunk -> I.C-2
    drain(s, [(7.91, 38.5), (7.91, 38.05), (8.62, 38.05)], 2)
    drain(s, [(7.91, 36.92), (7.91, 36.8), (8.62, 36.8)], 2)
    riser(s, 8.62, 37.5, "D.P-2", DRAIN, 8.78, 37.68, attach=4)
    ic(s, 10.45, 36.95, "I.C-2")
    drain(s, [(10.75, 36.95), (14.85, 36.95), (14.85, 39.45)])
    arrow(s, 12.8, 36.95, 0)
    ic(s, 14.85, YCOL, "I.C-3")
    tag(s, 11.0, 37.3, 'صرف دورة مياه الرجال UPVC 4" ميل 2%', attach=1, h=0.1)
    # staff-WC stack from the mezzanine lands in the back wall band and runs in the kitchen side wall
    riser(s, 17.5, 38.52, "D.P-3", DRAIN, 17.65, 38.52, attach=4)
    drain(s, [(17.38, 38.52), (15.49, 38.52), (15.49, 37.55), (14.85, 37.55)])
    co(s, 15.12, 37.55, label=False)
    dim(s, (7.46, 38.94), (8.63, 38.94), 0.9)
    dim(s, (7.91, 37.13), (7.91, 38.73), -0.91, horizontal=False)
    dim(s, (10.45, 36.95), (14.85, 36.95), 0.45)

    # ------------------------------------------------------------- legend / schedule / notes
    x0, y0, x1, y1 = EMPTY_G
    legend_bg(s, x0 + 0.2, y1 - 0.1)
    legend(s, x0 + 0.2, y1 - 0.1)
    rows = [
        ('خلاط / صنبور ماء بارد 1/2" PPR', N.get("C", 0), "C", "نقطة ماء بارد"),
        ('ماء ساخن 1/2" من السخان', N.get("H", 0), "H", "نقطة ماء ساخن"),
        ('ستانلس 15×15 سم مع سيفون 2"', N.get("FD", 0), "F/D", "مصفى أرضي"),
        ("500 لتر بولي إيثيلين تحت الأرضية", N.get("GT", 0), "G.T", "مصيدة شحوم"),
        ("60×60 سم بغطاء حديد زهر", N.get("IC", 0), "I.C", "غرفة تفتيش"),
        ("WH-1 80 لتر مطبخ / WH-2 30 لتر W.C", N.get("WH", 0), "WH", "سخان ماء كهربائي"),
        ('كروي PPR 3/4" - 1/2"', N.get("VALVE", 0), "", "محبس إغلاق"),
        ("مع غطاء نحاس بمستوى الأرضية", N.get("CO", 0), "C.O", "فتحة تنظيف"),
        ('1" مع صمام عدم رجوع', N.get("METER", 0), "M", "عداد مياه رئيسي"),
        ('D.P-1/2/3 صرف 4" + W.R ماء 3/4"', N.get("RISER", 0), "D.P/W.R", "صاعد / نازل للميزانين"),
    ] + pipe_rows()
    table(s, 15.3, 45.05, "جدول كميات السباكة - الأرضي", HEAD, rows, WID, rh=0.23, h=0.1)
    s.text(13.2, 29.6, "إجمالي الأرضي: بارد %d / ساخن %d / مصافي %d / سخانات %d / غرف تفتيش %d / مصيدة شحوم %d"
           % (N.get("C", 0), N.get("H", 0), N.get("FD", 0), N.get("WH", 0), N.get("IC", 0), N.get("GT", 0)), h=0.14, attach=5, color=7)
    s.notes(34.8, 45.0, [   # keep every line < 80 characters: the notes block does not wrap
        "مواسير التغذية PPR PN16 (بارد) و PN20 (ساخن) داخل الجدران، الساخن معزول حرارياً",
        'مواسير الصرف UPVC: 4" للمراحيض والخطوط الرئيسية، 2" للمغاسل والمصافي',
        'ميل خطوط الصرف الداخلية 2% والمجمع الخارجي 6" بميل 1%',
        "مصيدة شحوم إلزامية لكامل صرف المطبخ ومنطقة غسيل الميزانين - تنظيف شهري",
        "صرف دورات المياه لا يمر عبر مصيدة الشحوم بل مباشرة إلى غرف التفتيش",
        "اختبار ضغط التغذية 10 بار لمدة 24 ساعة قبل التغطية واختبار الصرف بالملء",
        "WH-1 سعة 80 لتر فوق مغاسل المطبخ ويغذي أيضاً مغسلة النساء والوضوء",
        "WH-2 سعة 30 لتر لدورة الرجال - تعليق السخانات على ارتفاع +2.00 م",
        "غرف التفتيش 60×60 سم بغطاء حديد زهر، وفتحة تنظيف C.O عند قاعدة كل نازل",
        "محبس إغلاق عند كل جهاز صحي وكل فرع + محبس رئيسي وعداد وصمام عدم رجوع",
        "مصافي الأرضية ستانلس ستيل بسيفون مانع للروائح، ميل أرضية المطبخ 1% نحوها",
        "خزان علوي 2 م3 على السطح مع مضخة تقوية (انظر مخطط الميزانين)",
        "التنفيذ وفق كود البناء السعودي SBC 701 ومتطلبات شركة المياه الوطنية",
    ], h=0.14, w=9.0, title="ملاحظات السباكة")


# ============================================================================= MEZZANINE
def draw_M(s):
    N.clear()
    BW0, BW1 = 13.44, 13.83           # back wall band
    YC, YH = 13.76, 13.65             # cold / hot mains in the band
    YCS, YHS = 12.3, 12.16            # cold / hot lines serving the 3-compartment sinks (stair wall)
    YT = 11.18                        # prep drain trunk (between the base ".70" and "3.05" dim texts)

    # ------------------------------------------------------------- water riser + mains in the band
    riser(s, 21.7, 13.62, "W.R", COLD, 21.85, 13.52, attach=4)
    s.leader([(21.7, 13.74), (21.45, 14.15)], color=COLD)
    tag(s, 20.95, 14.22, 'صاعد ماء بارد W.R 3/4" من الأرضي', attach=3, h=0.1)
    tag(s, 20.95, 14.47, "تغذية من الخزان العلوي 2 م3 عبر مضخة تقوية", attach=3, h=0.1)
    cold(s, [(21.7, YC), (30.55, YC)]); cold(s, [(21.7, YC), (15.44, YC)])
    valve(s, 22.05, YC); valve(s, 21.35, YC)
    wh(s, 22.6, 13.62, "WH-1 50L")
    wh(s, 30.3, 13.62, "WH-2 50L")
    dim(s, (15.44, 13.62), (21.11, 13.62), 0.3)             # cold-main run lengths in the back wall
    dim(s, (21.11, 13.62), (21.7, 13.62), 0.3)
    dim(s, (21.7, 13.62), (23.45, 13.62), 0.3)
    dim(s, (23.45, 13.62), (30.55, 13.62), 0.3)
    dim(s, (30.55, 13.62), (31.05, 13.62), 0.3)

    # ------------------------------------------------------------- double sink + its floor drain
    wp(s, 22.28, 13.42, "C"); cold(s, [(22.28, YC), (22.28, 13.5)])
    wp(s, 22.9, 13.42, "H"); hot(s, [(22.85, YH), (22.9, YH), (22.9, 13.5)])
    fd(s, 22.6, 12.55)
    drain(s, [(22.6, 12.79), (22.6, 12.55)], 2)
    dim(s, (22.0, 12.55), (22.6, 12.55), -0.3)

    # ------------------------------------------------------------- 3-compartment sinks (each basin C+H)
    cold(s, [(23.74, YC), (23.74, YCS), (29.33, YCS)])
    hot(s, [(22.85, YH), (23.86, YH), (23.86, YHS), (26.46, YHS)])            # WH-1 -> sink 1
    hot(s, [(30.3, 13.49), (30.3, YHS), (28.3, YHS)])                         # WH-2 -> sink 2
    valve(s, 23.74, 13.1, rot=90); valve(s, 23.86, 12.7, rot=90, color=HOT)
    for bx in (24.98, 25.64, 26.31, 28.15, 28.82, 29.48):
        s.water_point(bx - 0.15, YCS, "C"); s.water_point(bx + 0.15, YHS, "H"); inc("C"); inc("H")
        drain(s, [(bx + 0.22, 11.41), (bx + 0.22, YT)], 2)
    tag(s, 25.1, 10.98, 'خلاط C+H + صرف 2" بسيفون لكل حوض', attach=1, h=0.1)

    # ------------------------------------------------------------- prep/wash drain trunk -> D.P-1 (in the tapered wall)
    fd(s, 27.3, YT); fd(s, 30.5, YT)
    co(s, 30.92, YT)
    drain(s, [(30.92, YT), (22.6, YT), (22.6, 12.55), (23.45, 12.55), (23.45, 13.18)])
    arrow(s, 26.0, YT, 180); arrow(s, 23.45, 12.9, 90)
    riser(s, 23.45, 13.3, "D.P-1", DRAIN, 23.45, 13.46, attach=8)
    tag(s, 23.75, 10.45, 'صرف رئيسي 4" ميل 2% تحت بلاطة الميزانين', attach=1, h=0.1)
    tag(s, 31.1, 14.78, 'نازل صرف D.P-1 قطر 4" إلى مصيدة الشحوم بالأرضي', attach=3, h=0.1)
    s.leader([(23.57, 13.3), (23.95, 14.55), (27.3, 14.72)], color=DRAIN)
    dim(s, (24.98, YT), (27.3, YT), -0.55)
    dim(s, (27.3, YT), (30.5, YT), -0.55)
    dim(s, (30.5, YT), (31.05, YT), -0.55)

    # ------------------------------------------------------------- staff WC-A / WC-B
    hot(s, [(22.35, YH), (15.9, YH)])                                         # WH-1 -> WC basins
    cold(s, [(15.44, YC), (15.44, 13.15), (15.56, 13.15)])
    wp(s, 15.66, 13.15, "C"); wp(s, 15.9, 13.15, "H"); hot(s, [(15.9, YH), (15.9, 13.25)])     # basin A
    wp(s, 16.68, 13.46, "C"); cold(s, [(16.68, YC), (16.68, 13.56)])                            # toilet A
    wp(s, 19.08, 13.5, "C"); cold(s, [(19.08, YC), (19.08, 13.6)])                              # basin B
    wp(s, 19.34, 13.5, "H"); hot(s, [(19.34, YH), (19.34, 13.6)])
    cold(s, [(20.87, YC), (20.87, 11.42), (9.77, 11.42), (9.77, 13.45), (8.0, 13.45)])         # toilet B + kitchenette
    valve(s, 20.87, 13.2, rot=90)
    wp(s, 20.87, 11.42, "C")
    fd(s, 16.2, 12.2); fd(s, 20.0, 12.2)
    drain(s, [(20.65, 12.45), (20.65, 10.95)])
    co(s, 20.65, 12.45)
    drain(s, [(15.78, 12.2), (20.65, 12.2)])
    drain(s, [(17.5, 12.2), (17.5, 13.38)])
    drain(s, [(16.68, 13.0), (16.68, 12.2)])
    drain(s, [(15.78, 12.6), (15.78, 12.2)], 2)
    drain(s, [(19.21, 12.95), (19.21, 12.2)], 2)
    arrow(s, 18.0, 12.2, 180); arrow(s, 16.5, 12.2, 0)
    riser(s, 17.5, 13.5, "D.P-3", DRAIN, 17.65, 13.5, attach=4)
    tag(s, 16.3, 11.78, 'صرف دورات المياه 4" ميل 2% إلى النازل D.P-3', attach=1, h=0.1)
    dim(s, (15.54, 12.2), (16.2, 12.2), 0.3)
    dim(s, (16.2, 12.2), (20.0, 12.2), 0.3)
    dim(s, (20.0, 12.2), (20.98, 12.2), 0.3)
    dim(s, (15.54, 13.06), (16.68, 13.06), 0.38)
    dim(s, (18.8, 10.95), (20.51, 10.95), -0.45)

    # ------------------------------------------------------------- kitchenette (staff housing)
    wp(s, 7.9, 13.45, "C")
    wh(s, 8.75, 13.15, "WH-3 10L")
    cold(s, [(8.75, 13.45), (8.75, 13.28)])
    hot(s, [(8.5, 13.28), (8.5, 13.58), (8.15, 13.58)])
    wp(s, 8.15, 13.58, "H")
    drain(s, [(8.0, 12.63), (8.0, 12.5), (8.5, 12.5)], 2)
    riser(s, 8.62, 12.5, "D.P-2", DRAIN, 8.78, 12.42, attach=4)
    tag(s, 7.72, 14.05, "مطبخ صغير: مغسلة C+H + سخان 10 لتر", attach=1, h=0.1)
    dim(s, (9.0, 13.15), (9.65, 13.15), 0.35)
    dim(s, (8.42, 11.61), (8.42, 12.63), 0.0, horizontal=False)

    # ------------------------------------------------------------- void text, legend, schedule, notes
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    x0, y0, x1, y1 = EMPTY_M
    legend_bg(s, x0 + 0.2, y1 - 0.1)
    legend(s, x0 + 0.2, y1 - 0.1)
    rows = [
        ('خلاط / صنبور 1/2" PPR', N.get("C", 0), "C", "نقطة ماء بارد"),
        ('ماء ساخن 1/2" من السخانات', N.get("H", 0), "H", "نقطة ماء ساخن"),
        ('ستانلس 15×15 سم مع سيفون 2"', N.get("FD", 0), "F/D", "مصفى أرضي"),
        ("WH-1/2 سعة 50 لتر + WH-3 سعة 10 لتر", N.get("WH", 0), "WH", "سخان ماء كهربائي"),
        ('كروي PPR 3/4"', N.get("VALVE", 0), "", "محبس إغلاق"),
        ("عند بداية كل خط صرف", N.get("CO", 0), "C.O", "فتحة تنظيف"),
        ('D.P-1/2/3 صرف 4" + W.R ماء 3/4"', N.get("RISER", 0), "D.P/W.R", "نازل / صاعد"),
        ("2 م3 GRP على السطح + مضخة 0.75 حصان", 1, "", "خزان علوي + مضخة"),
    ] + pipe_rows()
    table(s, 15.3, 20.05, "جدول كميات السباكة - الميزانين", HEAD, rows, WID)
    s.text(14.0, 5.2, "إجمالي نقاط السباكة - الميزانين: ماء بارد %d / ماء ساخن %d / مصافي أرضية %d / سخانات %d / نوازل وصواعد %d"
           % (N.get("C", 0), N.get("H", 0), N.get("FD", 0), N.get("WH", 0), N.get("RISER", 0)), h=0.14, attach=5, color=7)
    s.notes(34.8, 20.0, [   # keep every line < 80 characters: the notes block does not wrap
        'صرف الميزانين عبر ثلاثة نوازل 4": D.P-1 منطقة الغسيل، D.P-2 المطبخ الصغير',
        "D.P-3 دورات المياه - جميع النوازل تصل إلى شبكة صرف الطابق الأرضي",
        "مواسير الصرف تحت بلاطة الميزانين داخل السقف المستعار للمطبخ (+2.80) بميل 2%",
        "عزل صوتي لمواسير الصرف داخل السقف المستعار وفتحة تنظيف عند بداية كل خط",
        'تهوية الصرف: ماسورة تهوية 2" من نهاية كل خط ترتفع 0.60 م فوق السطح',
        "خزان علوي 2 م3 GRP على السطح مع مضخة تقوية 0.75 حصان وضغط لا يقل عن 1.5 بار",
        "سخانات 50 لتر WH-1 / WH-2 فوق المغاسل + سخان 10 لتر تحت مغسلة المطبخ الصغير",
        'المغاسل ستانلس ستيل: خلاط بارد/ساخن لكل حوض وصرف 2" بسيفون',
        "اختبار ضغط 10 بار لمدة 24 ساعة - PPR PN16/PN20 للتغذية و UPVC للصرف - SBC 701",
    ], h=0.14, w=9.0, title="ملاحظات السباكة - الميزانين")
