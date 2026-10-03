"""LPG gas system (مخطط الغاز) - ground floor + mezzanine.
Ground: 4 x 45 kg cylinder bank in a ventilated steel cage outside behind the back wall (25.0-27.4 x 39.6-40.6),
manifold -> two-stage regulator -> G4 meter -> main ball valve -> NC solenoid -> sleeve through the back wall at
x=24.0 -> 3/4" copper main exposed on the back wall (+1.80 m) feeding 6 drops (3 fryers, flat grill, gas
char-broiler, 2-burner stove) each with a 1/2" ball valve (+1.20 m) and a 1.0 m stainless flexible hose.
A 1/2" branch leaves the kitchen through the west wall, runs OUTSIDE along the exterior walls (the strip
x 9.9-15.4 behind the hall wall is an open light-well) to the riser GR-1 at the WC-block corner (10.05, 38.8).
Mezzanine: GR-1 arrives at (10.05, 13.85) outside the kitchenette wall (x 9.68-9.87), enters through a sleeve,
isolation valve + solenoid, crosses to the gas oven on the west wall (valve + hose + gas point).
Wall data read from the gridded plan: back wall y 38.39-38.78, kitchen west wall x 15.38-15.60, hall north
wall y 36.44-36.69, WC-block east wall x 9.68-9.90; mezz kitchenette east wall x 9.68-9.87, units x 7.68-8.35
(sink y 12.63-13.32, oven 11.34-12.32, fridge 9.9-11.05)."""
import math
from sitemodel import G, M, EMPTY_G, EMPTY_M

LAYER = "G-GAS"
DIM, BLK, GRY, WHITE = 1, 7, 8, 255
WIRE = 8              # control / alarm cable (grey dashed)
W34, W12 = 0.05, 0.03  # polyline widths for 3/4" and 1/2" pipes

# ----------------------------------------------------------------------------- counters / lengths
N = {}
LEN = {}


def inc(k, n=1):
    N[k] = N.get(k, 0) + n


def plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


# ----------------------------------------------------------------------------- symbol helpers
def pipe(s, pts, size="34", add=True):
    """gas pipe: 3/4" thick / 1/2" thin orange polyline (layer colour)"""
    w = W34 if size == "34" else W12
    s.pline(pts, width=w)
    if add:
        LEN[size] = LEN.get(size, 0.0) + plen(pts)


def white_circle(s, x, y, r):
    h = s.msp.add_hatch(color=WHITE, dxfattribs={"layer": s.layer})
    h.paths.add_edge_path().add_arc(s.P(x, y), r, 0, 360)


def white_rect(s, x0, y0, x1, y1):
    s.hatch([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color=WHITE)


def bvalve(s, x, y, rot=0.0, size=0.15, count=True):
    """isolation ball valve: bow-tie + small circle (ball)"""
    s.valve(x, y, size, rot=rot)
    s.circle(x, y, size * 0.2, lw=9)
    if count:
        inc("VALVE")


def solenoid(s, x, y, rot=0.0, size=0.16):
    """NC solenoid valve: bow-tie + coil box beside it with S"""
    s.valve(x, y, size, rot=rot)
    c = math.cos(math.radians(rot + 90)); n = math.sin(math.radians(rot + 90))
    bx, by = x + 0.16 * c, y + 0.16 * n
    white_rect(s, bx - 0.07, by - 0.06, bx + 0.07, by + 0.06)
    s.rect(bx - 0.07, by - 0.06, bx + 0.07, by + 0.06, lw=13)
    s.line((x, y), (bx, by), lw=9)
    s.text(bx, by, "S", h=0.07, attach=5)
    inc("SOL")


def regulator(s, x, y):
    white_rect(s, x - 0.14, y - 0.11, x + 0.14, y + 0.11)
    s.rect(x - 0.14, y - 0.11, x + 0.14, y + 0.11, lw=25)
    s.text(x, y, "REG", h=0.07, attach=5)
    inc("REG")


def meter(s, x, y):
    white_rect(s, x - 0.15, y - 0.11, x + 0.15, y + 0.11)
    s.rect(x - 0.15, y - 0.11, x + 0.15, y + 0.11, lw=25)
    s.circle(x, y, 0.07, lw=9)
    s.text(x, y, "M", h=0.08, attach=5)
    inc("METER")


def detector(s, x, y, r=0.14):
    white_circle(s, x, y, r)
    s.circle(x, y, r, lw=25)
    s.text(x, y, "GD", h=0.07, attach=5)
    inc("GD")


def esb(s, x, y, size=0.2):
    h = size / 2
    white_rect(s, x - h, y - h, x + h, y + h)
    s.rect(x - h, y - h, x + h, y + h, lw=25)
    s.dot(x, y, 0.055, color=1)
    inc("ESB")


def gcp(s, x, y):
    white_rect(s, x - 0.18, y - 0.11, x + 0.18, y + 0.11)
    s.rect(x - 0.18, y - 0.11, x + 0.18, y + 0.11, lw=35)
    s.text(x, y, "GCP", h=0.08, attach=5)
    inc("GCP")


def hose(s, p1, p2, n=7, amp=0.035):
    """flexible stainless hose: zig-zag polyline"""
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    pts = [p1]
    for i in range(1, n):
        t = i / n
        sgn = amp if i % 2 else -amp
        pts.append((x1 + dx * t + nx * sgn, y1 + dy * t + ny * sgn))
    pts.append(p2)
    s.pline(pts, lw=13)
    inc("HOSE")


def gas_point(s, x, y):
    white_circle(s, x, y, 0.11)
    s.gas_point(x, y)
    inc("GP")


def cylinder(s, x, y, r=0.2):
    white_circle(s, x, y, r)
    s.cylinder(x, y, r)
    inc("CYL")


def riser(s, x, y, tag):
    pts = [(x, y - 0.16), (x + 0.16, y), (x, y + 0.16), (x - 0.16, y)]
    s.hatch(pts, color=WHITE)
    s.pline(pts, closed=True, lw=25)
    s.circle(x, y, 0.09, lw=13)
    s.dot(x, y, 0.035)
    s.text(x, y + 0.2, tag, h=0.1, attach=8)
    inc("RISER")


def sleeve(s, x, y):
    """pipe sleeve through the wall"""
    s.circle(x, y, 0.07, color=BLK, lw=13)


def wire(s, pts):
    s.pline(pts, lw=5, linetype="DASHED", color=WIRE)


def drop(s, x, y_main, y_valve, y_hose0, y_hose1, y_gp):
    """vertical drop from the main: 1/2" line, ball valve, flexible hose, gas point"""
    s.line((x, y_main), (x, y_hose0), lw=25)
    LEN["12"] = LEN.get("12", 0.0) + 0.6     # vertical from +1.80 m to the +1.20 m valve
    bvalve(s, x, y_valve, rot=90, size=0.14)
    hose(s, (x, y_hose0), (x, y_hose1))
    gas_point(s, x, y_gp)


def dim(s, p1, p2, off, horizontal=True):
    s.dim(p1, p2, offset=off, color=DIM, h=0.12, horizontal=horizontal)


def tag(s, x, y, txt, attach=1, h=0.12, width=0):
    return s.text(x, y, txt, h=h, attach=attach, color=BLK, width=width)


# ----------------------------------------------------------------------------- legend
def L_main(s, x, y): s.pline([(x - 0.38, y), (x + 0.38, y)], width=W34)
def L_br(s, x, y): s.pline([(x - 0.38, y), (x + 0.38, y)], width=W12)
def L_bv(s, x, y): s.pline([(x - 0.3, y), (x + 0.3, y)], width=W12); bvalve(s, x, y, 0, 0.16, count=False)
def L_hose(s, x, y): N_ = N.get("HOSE", 0); hose(s, (x - 0.3, y), (x + 0.3, y)); N["HOSE"] = N_
def L_gp(s, x, y): s.gas_point(x, y)
def L_sol(s, x, y): N_ = N.get("SOL", 0); s.pline([(x - 0.3, y), (x + 0.3, y)], width=W12); solenoid(s, x, y, 0, 0.16); N["SOL"] = N_
def L_reg(s, x, y): N_ = N.get("REG", 0); regulator(s, x, y); N["REG"] = N_
def L_met(s, x, y): N_ = N.get("METER", 0); meter(s, x, y); N["METER"] = N_
def L_gd(s, x, y): N_ = N.get("GD", 0); detector(s, x, y); N["GD"] = N_
def L_esb(s, x, y): N_ = N.get("ESB", 0); esb(s, x, y); N["ESB"] = N_
def L_gcp(s, x, y): N_ = N.get("GCP", 0); gcp(s, x, y); N["GCP"] = N_
def L_cyl(s, x, y): N_ = N.get("CYL", 0); cylinder(s, x, y, 0.15); N["CYL"] = N_
def L_ris(s, x, y): N_ = N.get("RISER", 0); riser(s, x - 0.1, y - 0.05, ""); N["RISER"] = N_
def L_wire(s, x, y): wire(s, [(x - 0.38, y), (x + 0.38, y)])

LEGEND_G = [
    (L_main, 'خط غاز رئيسي نحاس 3/4" مكشوف على الجدار +1.80 م - مطلي أصفر', 'LPG main, copper 3/4", exposed, painted yellow'),
    (L_br, 'فرع / نزلة غاز نحاس 1/2"', 'branch / drop, copper 1/2"'),
    (L_bv, 'محبس عزل كروي (بول فالف) معتمد للغاز +1.20 م', 'isolation ball valve, gas rated, h=1.20 m'),
    (L_hose, "خرطوم مرن ستانلس ستيل معتمد 1.0 م مع وصلة سريعة", "stainless flexible gas hose 1.0 m + quick coupler"),
    (L_gp, "نقطة غاز (وصلة جهاز)", "gas point / appliance connection"),
    (L_sol, 'صمام كهرومغناطيسي NC (سولينويد) 3/4" 220V', 'NC solenoid valve 3/4" 220V'),
    (L_reg, "منظم ضغط مرحلتين 37 mbar سعة 12 كجم/س", "two-stage regulator 37 mbar, 12 kg/h"),
    (L_met, "عداد غاز G4 مع صمام عدم رجوع", "gas meter G4 + non-return valve"),
    (L_gd, "كاشف تسرب غاز LPG جداري +0.30 م", "LPG leak detector, wall, h=0.30 m"),
    (L_esb, "زر إيقاف طوارئ +1.40 م (يغلق السولينويد)", "emergency shut-off push button h=1.40 m"),
    (L_gcp, "لوحة تحكم وإنذار الغاز GCP خارجية IP65", "gas control / alarm panel IP65"),
    (L_cyl, "أسطوانة غاز LPG سعة 45 كجم", "LPG cylinder 45 kg"),
    (L_ris, 'صاعد غاز GR-1 نحاس 1/2" إلى الميزانين', 'gas riser GR-1 copper 1/2" to mezzanine'),
    (L_wire, "كابل تحكم / إنذار 2×1.5 مم2 داخل ماسورة PVC", "control / alarm cable in PVC conduit"),
]
LEGEND_M = [
    (L_ris, 'صاعد غاز GR-1 نحاس 1/2" قادم من الأرضي (خارجي)', 'gas riser GR-1 copper 1/2" from ground floor'),
    (L_br, 'ماسورة غاز نحاس 1/2" مكشوفة +2.20 م - مطلية أصفر', 'copper gas pipe 1/2", exposed, painted yellow'),
    (L_bv, "محبس عزل كروي (بول فالف) معتمد للغاز", "isolation ball valve, gas rated"),
    (L_sol, 'صمام كهرومغناطيسي NC (سولينويد) 1/2"', 'NC solenoid valve 1/2"'),
    (L_hose, "خرطوم مرن ستانلس ستيل معتمد 1.0 م", "stainless flexible gas hose 1.0 m"),
    (L_gp, "نقطة غاز (وصلة جهاز) +1.20 م", "gas point / appliance connection"),
    (L_gd, "كاشف تسرب غاز LPG جداري +0.30 م", "LPG leak detector h=0.30 m"),
    (L_esb, "زر إيقاف طوارئ +1.40 م", "emergency shut-off push button"),
    (L_wire, "كابل تحكم / إنذار إلى لوحة GCP الأرضية", "control / alarm cable to ground GCP"),
]


def legend(s, x, y, rows, rh, w=10.5):
    n = len(rows)
    H = 0.5 + n * rh
    s.hatch([(x, y - H), (x + w, y - H), (x + w, y), (x, y)], color=WHITE, layer="LEGEND")   # mask the stair room
    return s.legend(x, y, "جدول رموز الغاز - LPG GAS LEGEND", rows, w=w, rh=rh, h=0.115)


# ----------------------------------------------------------------------------- schedule table
def table(s, x, y, title, header, rows, widths, rh=0.23, h=0.105):
    w = sum(widths); th = 0.36; hh = 0.3
    H = th + hh + rh * len(rows)
    s.hatch([(x, y - H), (x + w, y - H), (x + w, y), (x, y)], color=WHITE, layer="LEGEND")
    s.rect(x, y - H, x + w, y, color=BLK, layer="LEGEND")
    s.hatch([(x, y - th), (x + w, y - th), (x + w, y), (x, y)], color=254, layer="LEGEND")
    s.text(x + w / 2, y - th / 2, title, h=0.17, attach=5, color=BLK, layer="LEGEND")
    yy = y - th
    s.line((x, yy - hh), (x + w, yy - hh), color=BLK, layer="LEGEND")
    cx = x
    for i, wd in enumerate(widths):
        if i:
            s.line((cx, yy), (cx, y - H), color=BLK, lw=5, layer="LEGEND")
        s.text(cx + wd / 2, yy - hh / 2, header[i], h=h, attach=5, color=BLK, layer="LEGEND")
        cx += wd
    yy -= hh
    last = len(widths) - 1
    for r in rows:
        cx = x
        for i, wd in enumerate(widths):
            if i == last or i == 0:
                s.text(cx + wd - 0.08, yy - rh / 2, str(r[i]), h=h, attach=6, color=BLK, layer="LEGEND", width=wd - 0.12)
            else:
                s.text(cx + wd / 2, yy - rh / 2, str(r[i]), h=h, attach=5, color=BLK, layer="LEGEND")
            cx += wd
        s.line((x, yy - rh), (x + w, yy - rh), color=BLK, lw=5, layer="LEGEND")
        yy -= rh
    return H


HEAD = ["المواصفات", "الكمية", "الوحدة", "البند"]
WID = [4.6, 0.8, 0.8, 3.6]


# ============================================================================= GROUND FLOOR
def draw_G(s):
    N.clear(); LEN.clear()
    YM = 38.62                      # main line on the back wall (wall band 38.39-38.78)
    XE = 24.0                       # entry / sleeve x
    YO = 39.75                      # outside horizontal run
    DROPS = [15.8, 16.3, 16.8, 18.15, 19.2, 20.1]    # fryers x3, flat grill, gas char-broiler, 2-burner stove
    GDX = [17.35, 21.2]             # gas detectors on the back wall
    XB, YB, XR, YR = 15.0, 36.95, 10.05, 38.8        # exterior branch: vertical x, horizontal y, riser x/y
    # ---------------------------------------------------------------- cylinder cage (outside, behind the back wall)
    cx0, cy0, cx1, cy1 = 25.0, 39.6, 27.4, 40.6
    s.hatch([(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)], pattern="ANSI37", scale=0.3, color=GRY)
    s.rect(cx0, cy0, cx1, cy1, lw=35)
    for px, py in ((cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)):
        s.dot(px, py, 0.04)
    s.text((cx0 + cx1) / 2, cy1 - 0.04, "LPG CAGE 2.40 x 1.00 m", h=0.08, attach=2)
    CYL = [25.3, 25.9, 26.5, 27.1]
    for x in CYL:
        cylinder(s, x, 40.2, 0.2)
        s.line((x, 40.0), (x, YO), lw=13)                     # pig-tail
    pipe(s, [(CYL[0], YO), (CYL[-1], YO)], "34")             # manifold
    inc("MANIFOLD")
    # outside run: manifold -> regulator -> meter -> elbow -> main valve -> solenoid -> sleeve
    pipe(s, [(CYL[0], YO), (XE, YO), (XE, 38.78)], "34")
    regulator(s, 24.72, YO)
    meter(s, 24.3, YO)
    bvalve(s, XE, 39.45, rot=90, size=0.16, count=False); inc("MAINV")
    solenoid(s, XE, 39.08, rot=-90, size=0.16)       # coil box on the right (x 24.16)
    sleeve(s, XE, 38.78)
    # ---------------------------------------------------------------- main line inside on the back wall
    pipe(s, [(XE, 38.78), (XE, YM), (15.55, YM)], "34")
    s.line((15.55, YM - 0.08), (15.55, YM + 0.08), lw=25)     # reducer 3/4" -> 1/2"
    for x in DROPS:
        drop(s, x, YM, 38.5, 38.3, 38.05, 37.92)
    for x in GDX:
        detector(s, x, YM)
    # ---------------------------------------------------------------- 1/2" branch to the mezzanine (exterior)
    pipe(s, [(15.55, YM), (XB, YM), (XB, YB), (XR, YB), (XR, YR)], "12")
    sleeve(s, 15.38, YM)
    bvalve(s, XB, 38.25, rot=90, size=0.14)
    riser(s, XR, YR, "GR-1")
    LEN["12"] += 4.0                                          # vertical riser ground -> mezzanine
    # ---------------------------------------------------------------- control: GCP + ESB outside, ESB inside, cables
    gcp(s, 29.1, 39.15)
    esb(s, 28.6, 39.2)                                        # outside beside the cage
    esb(s, 25.62, 35.65)                                      # inside: kitchen exit to the BOH corridor (store wall)
    wire(s, [(GDX[0], 38.72), (24.1, 38.72), (24.1, 38.84), (28.9, 38.84), (28.9, 39.04)])
    wire(s, [(24.16, 38.84), (24.16, 39.02)])
    wire(s, [(28.6, 39.1), (28.6, 38.84)])
    # ---------------------------------------------------------------- dimensions (red)
    chain = [15.55] + sorted(DROPS + GDX) + [XE]
    for a, b in zip(chain, chain[1:]):
        dim(s, (a, YM), (b, YM), 40.35 - YM)
    dim(s, (15.55, YM), (XE, YM), 40.8 - YM)
    dim(s, (XE, 38.78), (XE, YO), -0.9, horizontal=False)
    dim(s, (XE, YO), (cx0, YO), 40.1 - YO)
    for a, b in zip(CYL, CYL[1:]):
        dim(s, (a, 40.2), (b, 40.2), 0.75)
    dim(s, (cx0, cy1), (cx1, cy1), 0.7)
    dim(s, (cx1, cy0), (cx1, cy1), 0.5, horizontal=False)
    dim(s, (cx1, 38.78), (cx1, cy0), 0.5, horizontal=False)
    dim(s, (XB, YM), (XB, YB), -0.6, horizontal=False)
    dim(s, (XR, YB), (XB, YB), 0.5)
    dim(s, (XR, YB), (XR, YR), 0.5, horizontal=False)
    # ---------------------------------------------------------------- callouts (black, leaders)
    s.leader([(16.3, 38.5), (16.5, 39.45)])
    tag(s, 16.5, 39.45, 'نزلة 1/2" لكل جهاز\\Pمحبس كروي +1.20 م\\P+ خرطوم ستانلس 1.0 م', attach=8, h=0.11)
    s.leader([(19.75, YM + 0.03), (19.75, 39.45)])
    tag(s, 19.4, 39.45, 'خط رئيسي نحاس 3/4"\\Pمكشوف على الجدار +1.80 م\\Pمطلي أصفر - كلبسات كل 1.5 م', attach=8, h=0.11)
    s.leader([(21.2, YM + 0.14), (22.0, 39.45)])
    tag(s, 22.0, 39.45, "كاشف غاز LPG +0.30 م\\Pموصول بلوحة GCP\\Pيغلق السولينويد + إنذار", attach=8, h=0.11)
    s.leader([(24.6, 39.86), (23.4, 41.0)]); s.leader([(23.92, 39.08), (23.3, 41.0)])
    tag(s, 23.3, 40.95,
        "منظم ضغط مرحلتين 37 mbar + عداد غاز G4 بصمام عدم رجوع\\P"
        'محبس إغلاق رئيسي كروي 3/4" + صمام سولينويد NC 3/4" 220V\\P'
        "كم حماية PVC عبر الجدار مع مانع تسرب - لحام فضة لكل الوصلات", attach=9, h=0.11)
    s.leader([(cx1, cy1), (28.4, 40.75)])
    tag(s, 28.4, 41.3,
        "قفص أسطوانات LPG 2.40×1.00×1.80 م شبك معدني مجلفن بقفل\\P"
        "4 أسطوانات 45 كجم (2 عمل + 2 احتياط) مع منفولد تبديل تلقائي\\P"
        "على بعد ≥ 1.0 م من أي فتحة - أرضية خرسانية - لوحة تحذير", attach=1, h=0.11, width=6.3)
    tag(s, 28.35, 39.55, "لوحة تحكم الغاز GCP خارجية IP65 + زر طوارئ\\Pبجانب القفص +1.40 م", attach=7, h=0.11)
    s.leader([(25.62, 35.55), (26.0, 34.6)])
    tag(s, 26.0, 34.55, "زر إيقاف طوارئ ESB-1 عند مخرج المطبخ +1.40 م\\Pيغلق السولينويد (كابل داخل الجدار إلى GCP)", attach=1, h=0.11)
    s.leader([(XR + 0.16, YR), (10.6, 39.2)])
    tag(s, 10.6, 39.2, 'صاعد غاز GR-1 نحاس 1/2" خارجي على الجدار\\Pإلى فرن الميزانين (+4.00 م) - محبس عزل عند الخروج', attach=7, h=0.11)
    s.leader([(12.5, YB), (12.5, 37.95)])
    tag(s, 12.5, 38.0, 'فرع 1/2" خارجي مثبت على الجدار بكلبسات كل 1.5 م\\Pمطلي أصفر - بعيد 15 سم عن الجدار', attach=8, h=0.11, width=3.4)
    s.leader([(XB + 0.08, 38.25), (14.75, 37.2)])
    tag(s, 14.75, 37.2, 'محبس عزل فرع الميزانين 1/2"', attach=9, h=0.1)
    tag(s, 18.3, 30.3,
        f"الإجمالي الأرضي: {N['CYL']} أسطوانات 45 كجم - {N['GP']} نقاط غاز - {N['VALVE'] + N['MAINV']} محابس\\P"
        f"{N['HOSE']} خراطيم مرنة - {N['GD']} كواشف غاز - {N['ESB']} أزرار طوارئ - صاعد GR-1", attach=5, h=0.14)
    # ---------------------------------------------------------------- legend / schedule / notes
    x0, y0, x1, y1 = EMPTY_G
    legend(s, x0 + 0.2, y1 - 0.1, LEGEND_G, rh=0.33)
    L34 = math.ceil(LEN["34"] + 1.0); L12 = math.ceil(LEN["12"] + 1.0)
    rows = [
        ('نحاس Type L لحام فضة، مكشوف +1.80 م، مطلي أصفر RAL 1021', L34, "م.ط", 'ماسورة نحاس 3/4"'),
        ("نزلات الأجهزة + فرع الميزانين الخارجي + الصاعد 4 م", L12, "م.ط", 'ماسورة نحاس 1/2"'),
        ('6 نزلات 1/2" + فرع الميزانين 1/2" + رئيسي 3/4" خارجي', N["VALVE"] + N["MAINV"], "عدد", "محبس عزل كروي للغاز"),
        ("ستانلس ستيل معتمد 1/2 بوصة × 1.0 م مع وصلة سريعة", N["HOSE"], "عدد", "خرطوم مرن + نقطة غاز"),
        ("مرحلتين 0.7 بار / 37 mbar سعة 12 كجم/س", N["REG"], "عدد", "منظم ضغط"),
        ("G4 مع صمام عدم رجوع - قراءة شهرية", N["METER"], "عدد", "عداد غاز"),
        ('NC 3/4" 220V يغلق بالإنذار / الطوارئ / انقطاع الكهرباء', N["SOL"], "عدد", "صمام سولينويد"),
        ("جداري +0.30 م، حساسية 20% LEL، مخرج ريليه", N["GD"], "عدد", "كاشف تسرب غاز LPG"),
        ("فطر أحمر بغطاء واقٍ +1.40 م (مخرج المطبخ + القفص)", N["ESB"], "عدد", "زر إيقاف طوارئ"),
        ("خارجية IP65 - منطقتان - صفارة + ضوء - بطارية احتياط", N["GCP"], "عدد", "لوحة تحكم الغاز GCP"),
        ("45 كجم (2 عمل + 2 احتياط) مع صمام وخرطوم ضغط عالٍ لكل أسطوانة", N["CYL"], "عدد", "أسطوانة غاز LPG"),
        ("2.40×1.00×1.80 م شبك مجلفن بقفل + منفولد 4 مداخل تبديل تلقائي", N["MANIFOLD"], "عدد", "قفص أسطوانات + منفولد"),
    ]
    table(s, 15.3, 45.05, "جدول كميات الغاز - الأرضي - LPG SCHEDULE", HEAD, rows, WID)
    s.notes(34.8, 45.0, [
        "النظام غاز بترولي مسال LPG من بنك 4 أسطوانات 45 كجم في قفص خارجي مهوّى بشبك معدني وقفل",
        "القفص على بعد لا يقل عن 1.0 م من أي فتحة أو مصدر اشتعال و3.0 م من مخارج الطوارئ مع لوحة تحذير",
        "منظم مرحلتين: 0.7 بار عند القفص و37 mbar عند المدخل - عداد G4 - محبس رئيسي كروي خارج المبنى",
        'المواسير نحاس Type L بلحام فضة: 3/4" للخط الرئيسي و1/2" للنزلات والفرع - مكشوفة على الجدار +1.80 م',
        "المواسير مطلية أصفر RAL 1021 مع ملصق GAS كل 3 م وكلبسات كل 1.5 م",
        "يمنع مرور مواسير الغاز داخل الأرضية أو الأسقف المغلقة أو عبر دورات المياه",
        "نزلة لكل جهاز: محبس كروي +1.20 م + خرطوم مرن ستانلس معتمد 1.0 م مع وصلة سريعة",
        "كاشفا غاز بارتفاع 30 سم من الأرض (الغاز أثقل من الهواء) موصولان بلوحة GCP تغلق السولينويد",
        "زر طوارئ عند مخرج المطبخ وآخر بجانب القفص - السولينويد يغلق أيضاً مع إطفاء الهود وانقطاع الكهرباء",
        "اختبار الضغط بالنيتروجين 1.5× ضغط التشغيل لمدة 24 ساعة بدون هبوط + اختبار التسرب بمحلول الصابون",
        "التنفيذ وفق متطلبات الدفاع المدني السعودي ومواصفات SASO و NFPA 58 / 54 بواسطة مقاول معتمد",
        'الصاعد GR-1 خارجي 1/2" إلى فرن الميزانين مع محبس عزل عند الخروج - انظر مخطط الميزانين',
    ], h=0.14, w=9.0, title="ملاحظات الغاز")


# ============================================================================= MEZZANINE
def draw_M(s):
    N.clear(); LEN.clear()
    XR, YR = 10.05, 13.85            # riser arriving outside the kitchenette east wall (x 9.68-9.87)
    XI = 9.5                          # interior run on the inner face of the east wall
    YC = 12.47                        # crossing between the sink (12.63) and the oven (12.32)
    XW = 7.58                         # west wall face (wall 7.27-7.49, units 7.68-8.35)
    GPX, GPY = 8.0, 11.83             # gas oven connection
    riser(s, XR, YR, "GR-1")
    pipe(s, [(XR, YR), (XI, YR), (XI, YC), (XW, YC), (XW, 12.05)], "12")
    LEN["12"] += 4.0                                          # vertical riser
    sleeve(s, 9.78, YR)
    bvalve(s, XI, 13.55, rot=90, size=0.14)
    solenoid(s, XI, 13.2, rot=-90, size=0.15)        # coil box on the wall side (x 9.66)
    bvalve(s, XW, 12.27, rot=90, size=0.14)
    hose(s, (XW, 12.05), (GPX - 0.12, GPY))
    gas_point(s, GPX, GPY)
    detector(s, 9.54, 11.75)
    esb(s, XW, 11.2)
    wire(s, [(9.68, 11.75), (9.78, 11.75), (9.78, 13.2), (9.73, 13.2)])
    wire(s, [(XW, 11.3), (7.44, 11.3), (7.44, 13.7), (9.78, 13.7), (9.78, 13.26)])
    # ---------------------------------------------------------------- dimensions
    dim(s, (7.49, YR), (XR, YR), 0.45)
    dim(s, (XR, YR), (15.38, YR), 0.45)
    dim(s, (XR, 11.65), (XR, YR), 0.75, horizontal=False)
    dim(s, (XI, YC), (XI, YR), -0.8, horizontal=False)
    dim(s, (XW, YC), (XI, YC), 0.45)
    dim(s, (8.55, 9.72), (8.55, GPY), 0.25, horizontal=False)
    dim(s, (XW, 11.2), (XW, 12.27), -0.4, horizontal=False)
    dim(s, (XI, 13.2), (XI, 13.55), 0.5, horizontal=False)
    # ---------------------------------------------------------------- callouts
    s.leader([(XR + 0.16, YR), (11.3, 14.75)])
    tag(s, 11.3, 14.75, 'صاعد غاز GR-1 نحاس 1/2" قادم من الأرضي\\Pخارجي على الجدار - كم حماية عبر الجدار', attach=7, h=0.11)
    s.leader([(XI + 0.1, 13.4), (11.6, 13.4)])
    tag(s, 11.65, 13.45, 'محبس عزل كروي 1/2" + صمام سولينويد NC 1/2"\\Pعند دخول الفرع - ارتفاع +2.20 م', attach=4, h=0.11)
    s.leader([(9.68, 11.75), (10.0, 11.4)])
    tag(s, 10.0, 11.4, "كاشف غاز LPG +0.30 م موصول بلوحة GCP الأرضية عبر كابل داخل الصاعد", attach=1, h=0.11, width=2.6)
    s.leader([(GPX - 0.11, GPY), (7.2, 12.72)])
    tag(s, 7.15, 12.75, 'فرن غاز عينين: نقطة غاز + محبس كروي +1.20 م\\P+ خرطوم مرن ستانلس 1.0 م', attach=6, h=0.1)
    s.leader([(XW - 0.1, 11.2), (6.9, 10.6)])
    tag(s, 6.9, 10.55, "زر إيقاف طوارئ\\P+1.40 م", attach=3, h=0.1)
    tag(s, 14.0, 5.2,
        f"الإجمالي الميزانين: {N['GP']} نقطة غاز (فرن) - {N['VALVE']} محبس عزل - {N['SOL']} سولينويد - {N['GD']} كاشف - "
        f"{N['ESB']} زر طوارئ - صاعد GR-1", attach=5, h=0.14)
    # ---------------------------------------------------------------- void text, legend, schedule, notes
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    x0, y0, x1, y1 = EMPTY_M
    legend(s, x0 + 0.2, y1 - 0.1, LEGEND_M, rh=0.36, w=10.0)
    L12 = math.ceil(LEN["12"] + 0.5)
    rows = [
        ("صاعد 4.0 م + تمديد داخلي مكشوف +2.20 م - نحاس مطلي أصفر", L12, "م.ط", 'ماسورة نحاس 1/2"'),
        ('1/2" عند دخول الفرع + عند الفرن (+1.20 م)', N["VALVE"], "عدد", "محبس عزل كروي"),
        ('NC 1/2" 220V يغلق بإشارة الكاشف / الطوارئ', N["SOL"], "عدد", "صمام سولينويد"),
        ("ستانلس ستيل معتمد 1/2 بوصة × 1.0 م", N["HOSE"], "عدد", "خرطوم مرن"),
        ("وصلة فرن غاز عينين 2×3.5 kW", N["GP"], "عدد", "نقطة غاز"),
        ("جداري +0.30 م - حساسية 20% LEL", N["GD"], "عدد", "كاشف تسرب غاز LPG"),
        ("فطر أحمر بغطاء واقٍ +1.40 م", N["ESB"], "عدد", "زر إيقاف طوارئ"),
        ('كم حماية + كلبسات - نحاس 1/2" خارجي', N["RISER"], "عدد", "صاعد GR-1 (مشترك)"),
    ]
    table(s, 15.3, 20.05, "جدول كميات الغاز - الميزانين", HEAD, rows, WID)
    s.notes(34.8, 20.0, [
        'الفرع 1/2" يصعد خارجياً على جدار دورة المياه (GR-1) ويدخل المطبخ الصغير عبر كم حماية',
        "محبس عزل كروي + صمام سولينويد عند الدخول، ومحبس + خرطوم مرن ستانلس 1.0 م عند الفرن",
        "التمديد الداخلي مكشوف بارتفاع +2.20 م مطلي أصفر مع كلبسات كل 1.5 م",
        "كاشف غاز +0.30 م وزر طوارئ موصولان بلوحة GCP الأرضية - الإنذار يغلق سولينويد الطابقين",
        "تهوية دائمة للمطبخ الصغير: فتحة سفلية 150 سم2 على الجدار الخارجي (الغاز أثقل من الهواء)",
        "اختبار الضغط 1.5× لمدة 24 ساعة + اختبار الصابون - التنفيذ وفق الدفاع المدني و SASO",
    ], h=0.14, w=9.0, title="ملاحظات الغاز - الميزانين")
