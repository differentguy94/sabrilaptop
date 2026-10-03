"""Ceiling plan - exposed slab, timber wave panels, hanging greenery, ring sign, gypsum zones."""
import math
from sitemodel import G, M, EMPTY_G, EMPTY_M
LAYER = "A-CEILING"
D = dict(color=1, h=0.12); C = dict(h=0.12, color=7)
BANDS_Y = [28.6, 30.6, 32.6, 34.6]
def wave(y0, x0, x1, amp=0.25, period=3.0, n=60):
    return [(x0 + (x1 - x0) * i / n, y0 + amp * math.sin(2 * math.pi * (x0 + (x1 - x0) * i / n) / period)) for i in range(n + 1)]
def sym_wave(s, x, y):
    s.pline(wave(y + 0.12, x - 0.45, x + 0.45, 0.05, 0.6, 20), color=32); s.pline(wave(y - 0.12, x - 0.45, x + 0.45, 0.05, 0.6, 20), color=32)
def sym_green(s, x, y): s.line((x - 0.45, y), (x + 0.45, y), color=3, linetype="DASHED", lw=25)
def sym_ring(s, x, y): s.circle(x, y, 0.22, color=7); s.circle(x, y, 0.16, color=7)
def sym_gyp(s, x, y): s.hatch([(x - 0.4, y - 0.17), (x + 0.4, y - 0.17), (x + 0.4, y + 0.17), (x - 0.4, y + 0.17)], pattern="ANSI31", scale=0.3, color=8); s.rect(x - 0.4, y - 0.17, x + 0.4, y + 0.17, color=8)
def sym_tile(s, x, y): s.hatch([(x - 0.4, y - 0.17), (x + 0.4, y - 0.17), (x + 0.4, y + 0.17), (x - 0.4, y + 0.17)], pattern="NET", scale=2.4, color=8); s.rect(x - 0.4, y - 0.17, x + 0.4, y + 0.17, color=8)
def sym_lvl(s, x, y): s.pline([(x - 0.2, y), (x, y + 0.2), (x + 0.2, y)], closed=True, color=7); s.text(x + 0.3, y + 0.05, "+6.00", h=0.1, color=7)
LEG_G = [
    (sym_wave, "C1 - ألواح شرائح خشب متموجة (صنوبر معالج 4×4 سم كل 8 سم) معلقة ارتفاع 4.0-4.6 م", "C1 undulating timber slat panels, suspended +4.0..4.6 m"),
    (sym_green, "C2 - صناديق نباتات صناعية معلقة على حواف الألواح الخشبية", "C2 hanging artificial greenery boxes along panel edges"),
    (sym_ring, "C3 - حلقة إعلانية دائرية Ø2.4 م 'EINSTEIN BURGER' مضيئة - ارتفاع 3.5 م", "C3 circular illuminated ring sign 2.4 m"),
    (sym_gyp, "C4 - سقف جبس بورد مقاوم للرطوبة ارتفاع 2.80 م مدهون أبيض قابل للغسيل", "C4 moisture-resistant gypsum board +2.80 m"),
    (sym_lvl, "C5 - سقف خرساني مكشوف ارتفاع 6.00 م مدهون دهانات الجزيرة مطفي RAL 7016 رمادي غامق", "C5 exposed slab +6.00 m, Jazeera Paints matt RAL 7016"),
]
LEG_M = [
    (sym_tile, "C6 - سقف جبس بلاط 60×60 سم ارتفاع 2.60 م - منطقة التحضير والغسيل", "C6 gypsum tile ceiling 60x60 +2.60 m"),
    (sym_gyp, "C4 - جبس بورد ارتفاع 2.70 م مدهون أبيض - الغرف والممر والمكتب", "C4 gypsum board +2.70 m, white"),
    (sym_lvl, "C7 - ألواح ساندويتش بانل معزولة - غرفة التجميد", "C7 insulated sandwich panels, freezer room"),
]
def level(s, x, y, txt):
    s.pline([(x - 0.2, y), (x, y + 0.2), (x + 0.2, y)], closed=True, color=7); s.hatch([(x - 0.2, y), (x, y + 0.2), (x + 0.2, y)], color=7)
    s.text(x + 0.3, y + 0.08, txt, h=0.12, color=7)
def bubble(s, x, y, code):
    s.circle(x, y, 0.3, color=7, lw=35); s.text(x, y, code, h=0.13, attach=5, color=7)
def draw_G(s):
    # exposed slab zone (light hatch) over the hall
    s.hatch(G["hall"], pattern="DOTS", scale=2.0, color=254)
    # timber wave bands
    for y in BANDS_Y:
        top = wave(y + 0.5, 8.0, 31.0); bot = wave(y - 0.5, 8.0, 31.0)
        poly = top + bot[::-1]
        s.hatch(poly, pattern="ANSI31", scale=0.3, color=32)
        s.pline(top, color=32, lw=25); s.pline(bot, color=32, lw=25)
        s.line((8.0, y + 0.5), (8.0, y - 0.5), color=32, lw=25); s.line((31.0, y + 0.5), (31.0, y - 0.5), color=32, lw=25)
        s.pline(wave(y + 0.8, 8.0, 31.0), color=3, linetype="DASHED", lw=13); s.pline(wave(y - 0.8, 8.0, 31.0), color=3, linetype="DASHED", lw=13)
        bubble(s, 9.0, y, "C1")
    # ring sign
    s.circle(18.5, 31.3, 1.2, color=7, lw=35); s.circle(18.5, 31.3, 1.0, color=7, lw=35)
    s.text(18.5, 31.3, "EINSTEIN BURGER\\PRING SIGN", h=0.14, attach=5, color=7); bubble(s, 18.5, 32.8, "C3")
    # gypsum zones
    for pts, code, lvl in [([(15.3, 35.0), (31.5, 35.0), (31.5, 38.9), (15.3, 38.9)], "C4", "+2.80"), ([(7.4, 36.5), (9.5, 36.5), (9.5, 39.7), (7.4, 39.7)], "C4", "+2.60"), ([(7.4, 39.7), (9.5, 39.7), (9.5, 42.4), (7.4, 42.4)], "C4", "+2.80")]:
        s.hatch(pts, pattern="ANSI31", scale=0.5, color=8); s.pline(pts, closed=True, color=8, lw=25)
        cx = sum(p[0] for p in pts) / 4; cy = sum(p[1] for p in pts) / 4
        bubble(s, cx, cy + 0.3, code); level(s, cx, cy - 0.5, lvl)
    # counter bulkhead
    s.rect(15.0, 34.9, 21.0, 35.7, color=250, lw=35); s.text(18.0, 35.3, "بلكونة شرائح خشب سوداء فوق الكاونتر +2.60 مع لوحة القائمة", h=0.1, attach=5, color=7)
    level(s, 12.5, 33.6, "+6.00 سقف مكشوف"); level(s, 26.0, 28.5, "+4.00 أسفل الألواح الخشبية"); bubble(s, 12.5, 34.2, "C5")
    s.text(19.0, 36.2, "C2 - نباتات معلقة على حواف الألواح (خط أخضر متقطع)", h=0.11, attach=5, color=3)
    # dims
    for i in range(len(BANDS_Y) - 1): s.dim((7.4, BANDS_Y[i]), (7.4, BANDS_Y[i + 1]), offset=-0.45, horizontal=False, **D)
    s.dim((8.0, 34.6), (31.0, 34.6), offset=0.9, **D); s.dim((8.0, 28.1), (8.0, 29.1), offset=-1.2, horizontal=False, **D)
    s.dim((17.3, 31.3), (19.7, 31.3), offset=-1.6, **D); s.dim((15.3, 35.0), (31.5, 35.0), offset=-0.9, **D)
    s.leader([(12.0, 30.6), (10.5, 29.5)]); s.text(10.5, 29.4, "ألواح شرائح خشب صنوبر 4×4 سم بتموج ±25 سم\\Pمعلقة بكابلات ستانلس من السقف المكشوف", attach=3, **C)
    s.leader([(23.0, 32.6), (24.0, 33.6)]); s.text(24.0, 33.7, "السقف المكشوف: دكتات سوداء ومواسير مكشوفة\\P(انظر مخطط التكييف والكهرباء)", attach=1, **C)
    x0, y0, x1, y1 = EMPTY_G
    s.legend(x0 + 0.2, y1 - 0.1, "جدول رموز الأسقف - CEILING LEGEND", LEG_G, w=10.5, rh=0.5)
    s.notes(34.8, 45.0, ["السقف المكشوف: تنظيف وترميم الخرسانة ثم دهان دهانات الجزيرة مطفي RAL 7016 - الكمية ≈ 215 م2 (45 لتر)", "ألواح الخشب: 4 أمواج × 23 م × 1.0 م = 92 م2 صنوبر معالج ضد الحريق (Fire retardant)",
                         "جبس بورد مقاوم للرطوبة 12.5 مم للمطبخ والخدمات ≈ 75 م2 مع فتحات صيانة 60×60", "فوق خط الطبخ: ألواح أسمنتية مقاومة للحريق بدلاً من الجبس", "حلقة الإعلان: إطار حديد Ø2.4 م مع أحرف أكريليك مضيئة 20 سم",
                         "الكميات شاملة 10% هالك"], h=0.13, w=12.0, title="ملاحظات الأسقف")
def draw_M(s):
    r = M["rooms"]
    for key, code, lvl, pat, sc in [("prep", "C6", "+2.60", "NET", 4.8), ("corridor", "C4", "+2.70", "ANSI31", 0.5), ("r1", "C4", "+2.70", "ANSI31", 0.5), ("r2", "C4", "+2.70", "ANSI31", 0.5), ("r3", "C4", "+2.70", "ANSI31", 0.5),
                                      ("wc_a", "C4", "+2.50", "ANSI31", 0.5), ("wc_b", "C4", "+2.50", "ANSI31", 0.5), ("store", "C6", "+2.60", "NET", 4.8), ("office", "C4", "+2.70", "ANSI31", 0.5), ("lobby", "C6", "+2.60", "NET", 4.8), ("freezer_room", "C7", "+2.40", "ANSI37", 0.5)]:
        x0, y0, x1, y1 = r[key]; pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        s.hatch(pts, pattern=pat, scale=sc, color=8); s.pline(pts, closed=True, color=8, lw=25)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        bubble(s, cx, cy + 0.35, code); level(s, cx - 0.3, cy - 0.5, lvl)
    s.hatch(M["void"], pattern="ANSI31", scale=1.2, color=8); s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    s.dim((22.0, 11.4), (31.5, 11.4), offset=-0.5, **D); s.dim((7.4, 9.7), (20.9, 9.7), offset=-0.4, **D); s.dim((23.3, 9.4), (26.5, 9.4), offset=-0.5, **D)
    s.leader([(26.5, 12.5), (26.0, 15.3)]); s.text(26.0, 15.4, "سقف جبس بلاط 60×60 مقاوم للرطوبة مع ألواح LED مدمجة\\Pارتفاع 2.60 م وفتحات صيانة", attach=2, **C)
    s.leader([(24.9, 8.0), (24.9, 5.3)]); s.text(24.9, 5.2, "غرفة التجميد: سقف ساندويتش بانل 10 سم معزول", attach=8, **C)
    x0, y0, x1, y1 = EMPTY_M
    s.legend(x0 + 0.2, y1 - 0.1, "جدول رموز الأسقف - CEILING LEGEND", LEG_M, w=10.5, rh=0.5)
    s.notes(34.8, 20.0, ["جبس بورد 12.5 مم على هيكل معدني، دهان دهانات الجزيرة أبيض مطفي ≈ 95 م2", "سقف بلاط جبس 60×60 ≈ 60 م2 (منطقة التحضير والغسيل والمستودع)", "فتحات صيانة 60×60 عند وحدات التكييف", "الكميات شاملة 10% هالك"], h=0.13, w=9.0, title="ملاحظات")
