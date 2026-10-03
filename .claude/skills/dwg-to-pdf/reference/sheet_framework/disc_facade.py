"""Front facade elevation."""
import math
from sitemodel import FACADE
LAYER = "A-FACADE"
D = dict(color=1, h=0.12); C = dict(h=0.12, color=7)
Y0 = 30.0   # ground line in the sheet
def draw_G(s):
    s.erase_plan()
    f = FACADE; x0, x1 = f["x0"], f["x1"]; hg = f["h_glass"]; hf0, hf1 = f["h_fascia"]; ht = f["h_total"]
    gy = lambda h: Y0 + h
    s.text(19.5, 44.2, "الواجهة الرئيسية - FRONT ELEVATION  مقياس 1:50", h=0.4, attach=5, color=7)
    # ground line & parapet
    s.line((x0 - 1.0, Y0), (x1 + 1.0, Y0), color=7, lw=50); s.hatch([(x0 - 1.0, Y0 - 0.25), (x1 + 1.0, Y0 - 0.25), (x1 + 1.0, Y0), (x0 - 1.0, Y0)], pattern="ANSI31", scale=0.4, color=8)
    s.rect(x0, Y0, x1, gy(ht), color=7, lw=35)
    # columns (concrete)
    for cx0, cx1 in f["columns"]:
        s.rect(cx0, Y0, cx1, gy(ht), color=7, lw=35); s.hatch([(cx0, Y0), (cx1, Y0), (cx1, gy(ht)), (cx0, gy(ht))], pattern="AR-CONC", scale=0.02, color=8)
    # right solid concrete wall with mural
    sx0, sx1 = f["solid"]
    s.hatch([(sx0, Y0), (sx1, Y0), (sx1, gy(ht)), (sx0, gy(ht))], pattern="AR-CONC", scale=0.02, color=8)
    s.rect(sx0 + 1.0, gy(0.6), sx1 - 0.6, gy(4.3), color=8, lw=13); s.hatch([(sx0 + 1.0, gy(0.6)), (sx1 - 0.6, gy(0.6)), (sx1 - 0.6, gy(4.3)), (sx0 + 1.0, gy(4.3))], pattern="DOTS", scale=1.0, color=250)
    s.text((sx0 + sx1) / 2 + 0.2, gy(2.6), "جدارية رسم اينشتاين\\Pطباعة/رسم يدوي على الخرسانة\\P6.5 × 3.7 م", h=0.2, attach=5, color=7)
    s.text((sx0 + sx1) / 2 + 0.2, gy(1.2), "I ♥ BURGER", h=0.35, attach=5, color=250)
    # glass curtain wall between columns
    for gx0, gx1 in f["glass"]:
        s.rect(gx0, Y0, gx1, gy(hg), color=7, lw=35)
        s.hatch([(gx0, Y0), (gx1, Y0), (gx1, gy(hg)), (gx0, gy(hg))], pattern="ANSI31", scale=1.2, color=150)
        n = max(1, round((gx1 - gx0) / 2.1)); mw = (gx1 - gx0) / n
        for i in range(1, n): s.line((gx0 + i * mw, Y0), (gx0 + i * mw, gy(hg)), color=250, lw=50)
        s.line((gx0, gy(2.4)), (gx1, gy(2.4)), color=250, lw=35)   # transom
        s.dim((gx0, gy(hg)), (gx0 + mw, gy(hg)), offset=0.25, **D)
    # door
    dx0, dx1 = f["door"]
    s.rect(dx0, Y0, dx1, gy(2.4), color=250, lw=50); s.line(((dx0 + dx1) / 2, Y0), ((dx0 + dx1) / 2, gy(2.4)), color=250, lw=50)
    for hx in ((dx0 + dx1) / 2 - 0.12, (dx0 + dx1) / 2 + 0.12): s.line((hx, gy(0.9)), (hx, gy(1.5)), color=7, lw=50)
    s.text((dx0 + dx1) / 2, gy(-0.45), "باب زجاجي مزدوج 2.10 م", h=0.12, attach=5, color=7)
    # fascia band
    fx0, fx1 = x0, f["solid"][0]
    s.hatch([(fx0, gy(hf0)), (fx1, gy(hf0)), (fx1, gy(hf1)), (fx0, gy(hf1))], color=250); s.rect(fx0, gy(hf0), fx1, gy(hf1), color=7, lw=35)
    lc = f["logo_center"]; ly = (hf0 + hf1) / 2
    s.text(lc, gy(ly - 0.12), "EINSTEIN BURGER", h=0.42, attach=5, color=255)
    s.circle(lc - 0.35, gy(ly + 0.42), 0.12, color=255, lw=35); s.circle(lc + 0.35, gy(ly + 0.42), 0.12, color=255, lw=35); s.line((lc - 0.23, gy(ly + 0.42)), (lc + 0.23, gy(ly + 0.42)), color=255, lw=35)
    s.arc(lc - 0.25, gy(ly + 0.12), 0.25, 180, 360, color=255, lw=50); s.arc(lc + 0.25, gy(ly + 0.12), 0.25, 180, 360, color=255, lw=50)
    for i in range(6):
        sx = fx0 + (fx1 - fx0) * (i + 0.5) / 6
        s.pline([(sx - 0.12, gy(hf1)), (sx + 0.12, gy(hf1)), (sx, gy(hf1) + 0.3)], closed=True, color=2); s.pline([(sx - 0.5, gy(hf1) - 0.05), (sx, gy(hf1) + 0.3), (sx + 0.5, gy(hf1) - 0.05)], color=2, lw=5, linetype="DASHED")
    s.text(fx0 + 0.3, gy(ht) + 0.35, "6 × كشاف غسيل جداري LED 20W 4000K على الكرنيش", h=0.12, color=7)
    # dims
    s.dim((x0, Y0), (x1, Y0), offset=-1.3, **D)
    for (cx0, cx1) in f["columns"]: s.dim((cx0, Y0), (cx1, Y0), offset=-0.7, **D)
    s.dim((f["glass"][0][0], Y0), (f["glass"][0][1], Y0), offset=-0.7, **D); s.dim((f["glass"][1][0], Y0), (f["glass"][1][1], Y0), offset=-0.7, **D); s.dim((sx0, Y0), (sx1, Y0), offset=-0.7, **D)
    s.dim((x1, Y0), (x1, gy(hg)), offset=0.5, horizontal=False, **D); s.dim((x1, gy(hg)), (x1, gy(hf1)), offset=0.5, horizontal=False, **D); s.dim((x1, gy(hf1)), (x1, gy(ht)), offset=0.5, horizontal=False, **D); s.dim((x1, Y0), (x1, gy(ht)), offset=1.4, horizontal=False, **D)
    s.dim((dx0, Y0), (dx1, Y0), offset=-0.3, **D); s.dim((x0 - 0.5, Y0), (x0 - 0.5, gy(2.4)), offset=-0.3, horizontal=False, **D)
    # material callouts
    s.leader([(10.0, gy(3.9)), (9.0, gy(5.6))]); s.text(9.0, gy(5.7), "F1 كرنيش ألمنيوم مركب ACP أسود مطفي ارتفاع 1.20 م\\Pمع أحرف أكريليك مضيئة 3D ارتفاع 45 سم", attach=8, **C)
    s.leader([(11.0, gy(1.5)), (11.0, gy(-1.9))]); s.text(11.0, gy(-2.0), "F2 واجهة زجاج مقسى 12 مم شفاف بإطار ألمنيوم أسود\\Pمقاسم كل 2.10 م وعتب أفقي على 2.40 م", attach=8, **C)
    s.leader([(15.3, gy(1.0)), (15.3, gy(-1.9))]); s.text(15.3, gy(-2.0), "F3 أعمدة خرسانية مكشوفة 45 سم\\Pدهان Concrete Effect دهانات الجزيرة", attach=8, **C)
    s.leader([(27.0, gy(2.6)), (27.0, gy(-1.9))]); s.text(27.0, gy(-2.0), "F5 جدار خرساني مع جدارية اينشتاين\\Pطباعة UV مباشرة أو رسم يدوي + طبقة حماية", attach=8, **C)
    # plan key strip
    ky = 27.6
    s.text(x0, ky + 0.55, "مفتاح المسقط - PLAN KEY (خط الواجهة)", h=0.14, color=7)
    s.line((x0, ky), (x1, ky), color=150, lw=35)
    for cx0, cx1 in f["columns"]: s.rect(cx0, ky - 0.2, cx1, ky + 0.2, color=7, lw=35); s.hatch([(cx0, ky - 0.2), (cx1, ky - 0.2), (cx1, ky + 0.2), (cx0, ky + 0.2)], color=8)
    s.rect(sx0, ky - 0.15, sx1, ky + 0.15, color=7, lw=35); s.hatch([(sx0, ky - 0.15), (sx1, ky - 0.15), (sx1, ky + 0.15), (sx0, ky + 0.15)], pattern="ANSI31", scale=0.4, color=8)
    s.arc(dx0, ky, 1.05, 0, 90, color=7, lw=13); s.arc(dx1, ky, 1.05, 90, 180, color=7, lw=13)
    s.pline([(19.5, ky - 1.2), (19.5, ky - 0.5)], width=0.08, color=4); s.text(19.5, ky - 1.45, "المدخل", h=0.12, attach=5, color=7)
    # legend
    rows = [
        (lambda s, x, y: (s.hatch([(x - 0.4, y - 0.15), (x + 0.4, y - 0.15), (x + 0.4, y + 0.15), (x - 0.4, y + 0.15)], color=250)), "F1 - كرنيش ألمنيوم مركب ACP أسود مطفي 4 مم على هيكل حديد - 1.20 م × 16.75 م ≈ 20 م2", "F1 black ACP fascia 4 mm on steel frame"),
        (lambda s, x, y: (s.hatch([(x - 0.4, y - 0.15), (x + 0.4, y - 0.15), (x + 0.4, y + 0.15), (x - 0.4, y + 0.15)], pattern="ANSI31", scale=0.6, color=150), s.rect(x - 0.4, y - 0.15, x + 0.4, y + 0.15, color=250)), "F2 - زجاج مقسى 12 مم شفاف + إطار ألمنيوم أسود بودرة ≈ 51 م2 (8 ألواح 2.10 × 3.30)", "F2 12 mm tempered glass, black aluminium frame"),
        (lambda s, x, y: (s.hatch([(x - 0.4, y - 0.15), (x + 0.4, y - 0.15), (x + 0.4, y + 0.15), (x - 0.4, y + 0.15)], pattern="AR-CONC", scale=0.01, color=8), s.rect(x - 0.4, y - 0.15, x + 0.4, y + 0.15, color=7)), "F3 - خرسانة مكشوفة بدهان Concrete Effect دهانات الجزيرة ≈ 48 م2", "F3 exposed concrete finish"),
        (lambda s, x, y: s.text(x, y, "ABC", h=0.16, attach=5, color=7), "F4 - أحرف أكريليك مضيئة 3D ارتفاع 45 سم LED 4000K داخلية + شعار الشارب", "F4 3D illuminated acrylic letters 45 cm"),
        (lambda s, x, y: (s.hatch([(x - 0.4, y - 0.15), (x + 0.4, y - 0.15), (x + 0.4, y + 0.15), (x - 0.4, y + 0.15)], pattern="DOTS", scale=0.6, color=250)), "F5 - جدارية اينشتاين طباعة UV على الخرسانة 6.5 × 3.7 م ≈ 24 م2", "F5 Einstein mural UV print"),
        (lambda s, x, y: s.pline([(x - 0.12, y - 0.1), (x + 0.12, y - 0.1), (x, y + 0.15)], closed=True, color=2), "F6 - كشاف غسيل جداري LED 20W 4000K IP65 - 6 قطع", "F6 LED wall washer 20W 4000K IP65 x6"),
    ]
    s.legend(4.2, 43.2, "جدول مواد الواجهة - FACADE MATERIALS", rows, w=14.5, rh=0.5)
    s.notes(34.8, 43.2, ["الارتفاع الكلي للواجهة 5.00 م، الزجاج 3.30 م، الكرنيش من 3.30 إلى 4.50 م", "باب مدخل زجاجي مزدوج 2.10 × 2.40 م مع مقابض ستانلس 60 سم وقفل أرضي",
                         "الشعار أحرف أكريليك مضيئة من الداخل مثبتة على الكرنيش، والشارب والنظارة أيقونة 60 سم", "ستارة هوائية فوق الباب من الداخل (انظر مخطط الناموسية)", "الكميات شاملة 10% هالك"],
            h=0.13, w=10.0, title="ملاحظات الواجهة")
def draw_M(s): pass
