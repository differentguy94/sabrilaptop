"""CCTV cameras - ground + mezzanine."""
from sitemodel import G, M, EMPTY_G, EMPTY_M
LAYER = "E-CCTV"
D = dict(color=1, h=0.12)
C = dict(h=0.12, color=7)

def sym_dome(s, x, y):   s.camera(x, y, 0, cone=False); s.circle(x, y, 0.3)
def sym_bullet(s, x, y): s.pline([(x-0.3,y-0.1),(x+0.15,y-0.1),(x+0.15,y+0.1),(x-0.3,y+0.1)], closed=True); s.pline([(x+0.15,y-0.06),(x+0.32,y-0.14),(x+0.32,y+0.14),(x+0.15,y+0.06)], closed=True)
def sym_nvr(s, x, y):    s.rect(x-0.3,y-0.12,x+0.3,y+0.12, lw=35); s.text(x,y,"NVR",h=0.09,attach=5)
def sym_cone(s, x, y):   s.arc(x-0.25, y, 0.5, -35, 35, lw=5); s.line((x-0.25,y),(x+0.16,y+0.29),lw=5,linetype="DASHED"); s.line((x-0.25,y),(x+0.16,y-0.29),lw=5,linetype="DASHED")
LEGEND = [
    (sym_dome,   "كاميرا دوم داخلية IP 4MP مع رؤية ليلية - تثبيت سقف ارتفاع 3.0 م", "indoor IP dome camera 4MP IR, ceiling"),
    (sym_bullet, "كاميرا بوليت خارجية IP 4MP مقاومة للعوامل الجوية IP67", "outdoor IP bullet camera 4MP IP67"),
    (sym_cone,   "زاوية تغطية الكاميرا (مجال الرؤية ~ 80 درجة)", "camera field of view"),
    (sym_nvr,    "جهاز تسجيل شبكي NVR 32 قناة + شاشة 24 بوصة + UPS", "NVR 32ch + monitor + UPS"),
]
CAMS_G = [  # (x, y, rot, type, location)
    (19.5, 27.6, 90, "D", "المدخل الرئيسي"), (7.8, 36.2, -40, "D", "صالة الجلوس - الزاوية الشمالية الغربية"),
    (7.8, 27.4, 40, "D", "صالة الجلوس - الزاوية الجنوبية الغربية"), (31.2, 27.4, 140, "D", "صالة الجلوس - الزاوية الجنوبية الشرقية"),
    (31.2, 34.8, 220, "D", "صالة الجلوس - الزاوية الشمالية الشرقية"), (19.8, 35.9, 270, "D", "الكاشير والكاونتر"),
    (22.6, 35.9, 270, "D", "شباك التوصيل"), (15.7, 38.7, -35, "D", "المطبخ - خط الطبخ"), (24.1, 38.7, 215, "D", "المطبخ - منطقة التحضير"),
    (25.0, 35.3, 90, "D", "ممر الخدمة"), (28.4, 37.3, 90, "D", "الدرج"),
    (11.0, 26.6, 270, "B", "الواجهة الخارجية - غرب"), (27.0, 26.6, 270, "B", "الواجهة الخارجية - شرق"),
]
CAMS_M = [
    (9.8, 11.3, 0, "D", "ممر سكن العمال"), (20.6, 11.3, 180, "D", "ممر سكن العمال - شرق"),
    (22.3, 13.3, -30, "D", "منطقة التحضير والغسيل"), (31.3, 13.3, 210, "D", "منطقة التحضير - شرق"),
    (23.0, 9.1, 0, "D", "صالة المستودع والتجميد"), (24.9, 13.3, -60, "D", "الدرج"),
]

def legend(s, x, y): return s.legend(x, y, "جدول رموز الكاميرات - CCTV LEGEND", LEGEND, w=10.5, rh=0.5)

def draw_cams(s, cams, prefix):
    for i, (x, y, rot, t, loc) in enumerate(cams, 1):
        s.camera(x, y, rot, cone=True, r_cone=3.5 if t == "D" else 4.5, span=80)
        s.text(x + 0.35, y + 0.35, f"{prefix}{i}", h=0.13, color=7)
    return len(cams)

def count_table(s, x, y, cams, floor):
    nd = sum(1 for c in cams if c[3] == "D"); nb = sum(1 for c in cams if c[3] == "B")
    rows = [("كاميرا دوم داخلية 4MP", nd), ("كاميرا بوليت خارجية 4MP", nb), ("جهاز NVR 32 قناة", 1 if floor == "G" else 0), ("شاشة مراقبة 24 بوصة", 1), ("الإجمالي - كاميرات", nd + nb)]
    w, rh = 6.5, 0.4
    s.rect(x, y - rh * (len(rows) + 1), x + w, y, color=7, layer="LEGEND")
    s.hatch([(x, y - rh), (x + w, y - rh), (x + w, y), (x, y)], color=254, layer="LEGEND")
    s.text(x + w / 2, y - rh / 2, "جدول الكميات - CCTV SCHEDULE", h=0.16, attach=5, color=7, layer="LEGEND")
    s.line((x + 1.2, y - rh), (x + 1.2, y - rh * (len(rows) + 1)), color=7, layer="LEGEND")
    for i, (name, q) in enumerate(rows, 1):
        cy = y - rh * i - rh / 2
        s.line((x, cy - rh / 2), (x + w, cy - rh / 2), color=8, lw=5, layer="LEGEND")
        s.text(x + w - 0.15, cy, name, h=0.13, attach=6, color=7, layer="LEGEND")
        s.text(x + 0.6, cy, str(q), h=0.14, attach=5, color=7, layer="LEGEND")

def draw_G(s):
    n = draw_cams(s, CAMS_G, "C")
    s.rect(30.7, 32.05, 31.3, 32.35, lw=35); s.hatch([(30.7, 32.05), (31.3, 32.05), (31.3, 32.35), (30.7, 32.35)])
    s.text(31.0, 31.95, "NVR 32CH + UPS", h=0.11, attach=2)
    s.leader([(31.0, 32.2), (33.2, 30.8)]); s.text(33.2, 30.7, "جهاز التسجيل NVR 32 قناة\\Pفي غرفة الخدمة مع UPS ساعة", attach=1, **C)
    s.leader([(19.8, 35.9), (18.6, 33.6)]); s.text(18.6, 33.5, "شاشة مراقبة 24 بوصة عند الكاشير", attach=3, **C)
    s.leader([(11.0, 26.6), (9.6, 25.9)]); s.text(9.5, 25.9, "كاميرا خارجية تحت الكرنيش ارتفاع 3.5 م", attach=3, **C)
    s.leader([(7.8, 36.2), (6.2, 37.0)]); s.text(6.2, 37.1, "كاميرا دوم زاوية\\Pارتفاع 3.0 م", attach=2, **C)
    for (x1, y1), (x2, y2), off, hz in [((7.8, 27.4), (7.8, 36.2), 0.6, False), ((7.8, 27.4), (19.5, 27.6), 0.6, True), ((19.5, 27.6), (31.2, 27.4), 0.6, True),
                                         ((15.7, 38.7), (24.1, 38.7), 0.5, True), ((11.0, 26.6), (27.0, 26.6), -0.5, True), ((19.8, 35.9), (22.6, 35.9), -0.6, True), ((25.0, 35.3), (28.4, 37.3), 0.5, False)]:
        s.dim((x1, y1), (x2, y2), offset=off, horizontal=hz, **D)
    x0, y0, x1, y1 = EMPTY_G
    legend(s, x0 + 0.2, y1 - 0.1)
    count_table(s, 4.2, 42.3, CAMS_G, "G")
    s.text(12.5, 29.6, f"عدد الكاميرات في الطابق الأرضي = {n} (11 داخلية + 2 خارجية)", h=0.14, attach=5, color=7)
    s.notes(34.8, 45.0, ["كاميرات IP بدقة 4 ميجابكسل مع رؤية ليلية 30 م وتغذية PoE", "كابل Cat6 من كل كاميرا إلى جهاز NVR في غرفة الخدمة",
                         "سعة تخزين 8 تيرابايت لتسجيل 30 يوماً متواصلة", "تطبيق مراقبة عن بعد للجوال + شاشة عند الكاشير", "لا كاميرات داخل دورات المياه والمصلى وغرف السكن"],
            h=0.14, w=9.0, title="ملاحظات الكاميرات")

def draw_M(s):
    n = draw_cams(s, CAMS_M, "CM")
    s.rect(30.4, 7.4, 31.0, 7.7, lw=35); s.text(30.7, 7.3, "MONITOR", h=0.1, attach=2)
    s.leader([(30.7, 7.55), (33.2, 6.2)]); s.text(33.2, 6.1, "شاشة متابعة في المكتب\\Pمتصلة بجهاز NVR الأرضي", attach=1, **C)
    s.leader([(22.3, 13.3), (22.0, 15.2)]); s.text(22.0, 15.3, "كاميرا دوم تغطي أحواض الغسيل والتحضير", attach=2, **C)
    for (x1, y1), (x2, y2), off, hz in [((9.8, 11.3), (20.6, 11.3), 0.5, True), ((22.3, 13.3), (31.3, 13.3), 0.5, True), ((23.0, 9.1), (24.9, 13.3), 0.6, False)]:
        s.dim((x1, y1), (x2, y2), offset=off, horizontal=hz, **D)
    x0, y0, x1, y1 = EMPTY_M
    legend(s, x0 + 0.2, y1 - 0.1)
    count_table(s, 4.2, 17.3, CAMS_M, "M")
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    s.text(14.0, 5.2, f"عدد الكاميرات في الميزانين = {n} داخلية", h=0.14, attach=5, color=7)
    s.notes(34.8, 20.0, ["كاميرات الميزانين موصولة بنفس جهاز NVR في الطابق الأرضي", "لا كاميرات داخل غرف السكن ودورات المياه"], h=0.14, w=9.0, title="ملاحظات")
