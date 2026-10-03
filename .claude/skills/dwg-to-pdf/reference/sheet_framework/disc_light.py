"""Lighting - track lights, pendants, globes, strips, panels; 4000K general / 3000K decorative."""
from sitemodel import G, M, EMPTY_G, EMPTY_M
LAYER = "E-LIGHT"
D = dict(color=1, h=0.12); C = dict(h=0.12, color=7)
TRACKS = [((8.0, 34.8), (15.0, 34.8), 4), ((8.0, 29.6), (15.0, 29.6), 4), ((16.5, 29.6), (31.0, 29.6), 7), ((16.5, 33.8), (31.0, 33.8), 7), ((16.0, 36.9), (24.0, 36.9), 4)]
GLOBES = [(x, 31.45) for x in (24.9, 26.1, 27.3, 28.5, 29.7)] + [(24.45, 28.8), (24.45, 30.4), (21.65, 28.8), (21.65, 30.4), (13.6, 31.45), (15.2, 31.45), (8.4, 29.0), (8.4, 32.3)]
BATTENS = [(16.5, 37.1), (18.5, 37.1), (20.5, 37.1), (22.5, 37.1), (17.5, 36.1), (21.0, 36.1)]
DOWN_G = [(8.2, 39.1), (8.9, 38.5), (8.2, 37.3), (8.9, 37.0), (30.9, 37.9), (30.9, 36.0), (29.3, 36.6), (28.8, 35.5), (27.1, 36.3), (8.4, 41.4), (8.4, 40.0), (31.0, 32.3), (27.0, 38.2), (25.0, 36.3)]

def sym_track(s, x, y): s.pline([(x - 0.4, y), (x + 0.4, y)], width=0.05, color=250); s.spot(x - 0.2, y); s.spot(x + 0.2, y)
def sym_pend(s, x, y): s.pendant(x, y, 0.16)
def sym_globe(s, x, y): s.globe(x, y, 0.12)
def sym_strip(s, x, y): s.strip((x - 0.4, y), (x + 0.4, y))
def sym_batten(s, x, y): s.rect(x - 0.4, y - 0.06, x + 0.4, y + 0.06); s.line((x - 0.4, y), (x + 0.4, y), lw=5)
def sym_down(s, x, y): s.downlight(x, y, 0.12)
def sym_panel(s, x, y): s.led_panel(x, y, 0.4, 0.4)
def sym_sw(s, x, y): s.rect(x - 0.25, y - 0.12, x + 0.25, y + 0.12, lw=35); s.text(x, y, "DIM", h=0.08, attach=5)
LEG_G = [
    (sym_track, "تراك لايت أسود 1 فاز 2 م مع رؤوس سبوت LED 12W قابلة للتوجيه - 4000K شمسي", "black track 2 m + LED spot heads 12W 4000K"),
    (sym_pend, "بندانت معدني أسود قبة 30 سم - لمبة LED فيلامنت 8W 3000K دافئ - ارتفاع 2.2 م", "black dome pendant 30 cm, LED 8W 3000K, h 2.2 m"),
    (sym_globe, "كرة زجاجية 25 سم على إطار البلانتر الحديدي - LED 6W 3000K", "glass globe 25 cm on planter frame, LED 6W 3000K"),
    (sym_strip, "شريط LED 14.4W/م 4000K داخل بروفايل ألمنيوم مع ناشر", "LED strip 14.4 W/m 4000K in aluminium profile"),
    (sym_batten, "إضاءة LED مقاومة للرطوبة Tri-proof 120 سم 36W 4000K - المطبخ", "LED tri-proof batten 120 cm 36W 4000K"),
    (sym_down, "سبوت لايت مدمج LED 7W 4000K - دورات المياه والخدمة", "LED downlight 7W 4000K"),
    (sym_sw, "لوحة تحكم إضاءة مع ديمر 4 دوائر عند الكاشير", "lighting control panel + dimmer 4 circuits"),
]
LEG_M = [
    (sym_panel, "لوحة LED 60×60 سم 36W 4000K شمسي - سقف جبس", "LED panel 60x60 36W 4000K"),
    (sym_batten, "إضاءة LED مقاومة للرطوبة 120 سم 36W 4000K - الغسيل والمستودع", "LED tri-proof batten 120 cm 36W"),
    (sym_down, "سبوت لايت مدمج LED 7W 4000K", "LED downlight 7W 4000K"),
]

def schedule(s, x, y, rows, title):
    w, rh = 10.5, 0.4; cols = [3.2, 1.0, 1.1, 1.3, 3.9]
    s.rect(x, y - rh * (len(rows) + 2), x + w, y, color=7, layer="LEGEND")
    s.hatch([(x, y - rh), (x + w, y - rh), (x + w, y), (x, y)], color=254, layer="LEGEND")
    s.text(x + w / 2, y - rh / 2, title, h=0.17, attach=5, color=7, layer="LEGEND")
    xs = [x]
    for c in cols: xs.append(xs[-1] + c)
    for xx in xs[1:-1]: s.line((xx, y - rh), (xx, y - rh * (len(rows) + 2)), color=7, layer="LEGEND")
    hdr = ["النوع", "العدد", "الواط", "اللون K", "إجمالي الواط / ملاحظة"]
    for i, r in enumerate([None] + rows):
        cy = y - rh * (i + 1) - rh / 2
        if r is None:
            for k, h in enumerate(hdr): s.text((xs[k] + xs[k + 1]) / 2, cy, h, h=0.11, attach=5, color=7, layer="LEGEND")
            continue
        s.line((x, cy - rh / 2), (x + w, cy - rh / 2), color=8, lw=5, layer="LEGEND")
        vals = [r[0], str(r[1]), str(r[2]), r[3], f"{r[1] * r[2]} W - {r[4]}"]
        for k, v in enumerate(vals):
            s.text((xs[k] + xs[k + 1]) / 2 if k != 0 else xs[1] - 0.1, cy, v, h=0.11, attach=5 if k != 0 else 6, color=7, layer="LEGEND", width=cols[k] - 0.1)

def draw_G(s):
    n_heads = 0
    for (p1, p2, nh) in TRACKS:
        heads = [(p1[0] + (p2[0] - p1[0]) * (i + 0.5) / nh, p1[1]) for i in range(nh)]
        s.track([p1, p2], heads); n_heads += nh
        s.dim(p1, p2, offset=0.35, **D)
    pend = []
    for kind, cx, cy, w, h in G["seating"]:
        if kind in ("booth", "table4", "bench"): pend.append((cx, cy))
    pend += [(10.8, 31.45), (12.4, 31.45), (14.0, 31.45)]
    for x, y in pend: s.pendant(x, y)
    for x, y in GLOBES: s.globe(x, y)
    strips = [((15.0, 34.95), (21.0, 34.95)), ((15.6, 38.85), (23.3, 38.85)), ((7.4, 27.05), (31.5, 27.05)), ((15.3, 34.6), (19.5, 34.6))]
    for p1, p2 in strips: s.strip(p1, p2)
    for x, y in BATTENS: s.rect(x - 0.6, y - 0.08, x + 0.6, y + 0.08); s.line((x - 0.6, y), (x + 0.6, y), lw=5)
    for x, y in DOWN_G: s.downlight(x, y)
    for x in (17.0, 19.5, 22.0): s.rect(x - 0.4, 38.55, x + 0.4, 38.65, color=2)   # under-hood lights
    s.rect(20.6, 35.15, 21.1, 35.4, lw=35); s.text(20.85, 35.05, "DIM", h=0.09, attach=2)
    s.circle(18.5, 31.3, 1.2, lw=5); s.text(18.5, 30.0, "حلقة EINSTEIN BURGER المضيئة Ø2.4 م", h=0.11, attach=5, color=7)
    # neon
    s.box_label(10.6, 36.3, "NEON: I ♥ BURGER", h=0.1, color=7); s.box_label(26.3, 34.85, "NEON: IT IS RUDE TO STARE", h=0.1, color=7)
    # dims & callouts
    s.dim((8.0, 29.6), (8.0, 34.8), offset=-0.5, horizontal=False, **D); s.dim((16.5, 29.6), (16.5, 33.8), offset=-0.6, horizontal=False, **D)
    s.dim((24.9, 31.45), (26.1, 31.45), offset=0.5, **D); s.dim((10.8, 31.45), (12.4, 31.45), offset=-1.3, **D); s.dim((12.4, 31.45), (14.0, 31.45), offset=-1.3, **D)
    s.dim((16.5, 37.1), (18.5, 37.1), offset=0.35, **D); s.dim((18.5, 37.1), (20.5, 37.1), offset=0.35, **D)
    s.leader([(11.5, 29.6), (10.2, 28.9)]); s.text(10.2, 28.8, "تراك أسود 2 م × 3.5 مع 4 رؤوس سبوت 12W\\Pمعلق من السقف المكشوف على ارتفاع 4.2 م", attach=3, **C)
    s.leader([(8.4, 33.7), (6.2, 35.3)]); s.text(6.2, 35.4, "بندانت قبة أسود 30 سم\\Pفوق كل طاولة ارتفاع 2.2 م", attach=2, **C)
    s.leader([(27.3, 31.45), (28.2, 30.3)]); s.text(28.2, 30.2, "كرات زجاجية 25 سم على إطار البلانتر\\P3000K دافئ - ارتفاع 1.8 م", attach=1, **C)
    s.leader([(18.0, 34.95), (18.0, 33.0)]); s.text(18.0, 32.9, "شريط LED تحت سطح الكاونتر وأسفل حافة البار", attach=2, **C)
    s.leader([(19.5, 37.1), (19.0, 39.6)]); s.text(19.0, 39.7, "إضاءة Tri-proof 120 سم 36W 4000K فوق خط الطبخ\\P+ إضاءة مدمجة داخل الهود", attach=8, **C)
    s.leader([(20.85, 35.3), (23.0, 33.4)]); s.text(23.0, 33.3, "لوحة تحكم إضاءة + ديمر عند الكاشير", attach=1, **C)
    n_pend, n_globe, n_bat, n_down = len(pend), len(GLOBES), len(BATTENS), len(DOWN_G)
    rows = [("تراك لايت 2 م أسود", 13, 0, "-", f"{n_heads} رأس سبوت"), ("رأس سبوت LED تراك", n_heads, 12, "4000", "شمسي"), ("بندانت قبة أسود 30 سم", n_pend, 8, "3000", "دافئ"),
            ("كرة زجاجية 25 سم", n_globe, 6, "3000", "دافئ"), ("شريط LED (متر)", 38, 14, "4000", "بروفايل ألمنيوم"), ("Tri-proof 120 سم", n_bat, 36, "4000", "المطبخ"),
            ("سبوت مدمج 7W", n_down, 7, "4000", "دورات المياه/الخدمة"), ("إضاءة داخل الهود", 3, 18, "4000", "مقاومة للحرارة")]
    x0, y0, x1, y1 = EMPTY_G
    s.legend(x0 + 0.2, y1 - 0.1, "جدول رموز الإنارة - LIGHTING LEGEND", LEG_G, w=10.5, rh=0.46)
    schedule(s, 22.4, 45.0, rows, "جدول كميات الإنارة - الطابق الأرضي")
    s.text(12.2, 40.9, f"إجمالي: {n_heads} سبوت تراك + {n_pend} بندانت + {n_globe} كرة + {n_bat} Tri-proof + {n_down} سبوت مدمج", h=0.14, attach=5, color=7)
    s.notes(34.8, 41.2, ["الإضاءة العامة 4000K لون شمسي (تراك، ألواح، Tri-proof)، والإضاءة الديكورية 3000K دافئ (بندانت وكرات) حسب الريندر", "التراكات معلقة بأسلاك من السقف المكشوف ارتفاع 4.2 م ومطلية أسود مطفي",
                         "جميع المصابيح LED عمر 25000 ساعة، معامل إظهار اللون CRI 90", "دوائر الإضاءة على ديمر من لوحة التحكم عند الكاشير (4 دوائر: صالة - بار - ديكور - مطبخ)"], h=0.13, w=12.0, title="ملاحظات الإنارة")

def draw_M(s):
    r = M["rooms"]; panels = []
    for key in ("r1", "r2", "r3"):
        x0, y0, x1, y1 = r[key]; panels += [(x0 + (x1 - x0) * 0.3, (y0 + y1) / 2), (x0 + (x1 - x0) * 0.7, (y0 + y1) / 2)]
    panels += [(10.5, 10.6), (14.0, 10.6), (17.5, 10.6), (23.5, 12.5), (26.5, 12.5), (29.5, 12.5), (24.5, 10.6), (28.0, 10.6), (30.6, 7.2), (22.1, 8.0)]
    for x, y in panels: s.led_panel(x, y)
    battens = [(24.9, 8.0), (28.1, 8.0), (8.0, 15.5)]
    for x, y in battens: s.rect(x - 0.6, y - 0.08, x + 0.6, y + 0.08); s.line((x - 0.6, y), (x + 0.6, y), lw=5)
    downs = [(16.2, 12.6), (18.0, 12.6), (19.9, 12.6), (19.9, 11.0), (8.0, 13.0), (8.4, 16.5)]
    for x, y in downs: s.downlight(x, y)
    s.dim((panels[0][0], panels[0][1]), (panels[1][0], panels[1][1]), offset=-1.0, **D); s.dim((10.5, 10.6), (14.0, 10.6), offset=0.4, **D); s.dim((23.5, 12.5), (26.5, 12.5), offset=0.5, **D); s.dim((26.5, 12.5), (29.5, 12.5), offset=0.5, **D)
    s.leader([(23.5, 12.5), (23.0, 15.3)]); s.text(23.0, 15.4, "ألواح LED 60×60 سم 36W 4000K شمسي في سقف الجبس ارتفاع 2.6 م", attach=2, **C)
    s.leader([(24.9, 8.0), (24.9, 5.3)]); s.text(24.9, 5.2, "إضاءة Tri-proof مقاومة للرطوبة داخل غرفة التجميد والمستودع", attach=8, **C)
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    rows = [("لوحة LED 60×60", len(panels), 36, "4000", "شمسي"), ("Tri-proof 120 سم", len(battens), 36, "4000", "رطوبة"), ("سبوت مدمج 7W", len(downs), 7, "4000", "دورات المياه")]
    x0, y0, x1, y1 = EMPTY_M
    s.legend(x0 + 0.2, y1 - 0.1, "جدول رموز الإنارة - LIGHTING LEGEND", LEG_M, w=10.5, rh=0.46)
    schedule(s, 15.6, 20.0, rows, "جدول كميات الإنارة - الميزانين")
    s.text(14.0, 5.2, f"إجمالي الميزانين: {len(panels)} لوحة + {len(battens)} Tri-proof + {len(downs)} سبوت", h=0.14, attach=5, color=7)
    s.notes(34.8, 17.5, ["مفاتيح الإضاءة بجانب أبواب الغرف ارتفاع 120 سم", "إضاءة طوارئ LED عند مخارج الممر والدرج"], h=0.13, w=8.0, title="ملاحظات")
