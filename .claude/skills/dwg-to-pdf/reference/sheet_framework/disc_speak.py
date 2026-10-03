"""Ceiling speakers (100 V line)."""
from sitemodel import G, M, EMPTY_G, EMPTY_M
LAYER = "E-SPEAKER"
D = dict(color=1, h=0.12); C = dict(h=0.12, color=7)
SP_G = [(9.5, 29.0), (9.5, 33.5), (13.5, 29.0), (13.5, 33.5), (18.0, 29.5), (18.0, 33.5), (22.5, 29.5), (22.5, 33.5), (27.0, 29.5), (27.0, 33.5), (30.5, 31.5)]
SP_G_OTHER = [(19.5, 36.5, "المطبخ"), (8.5, 38.6, "دورة مياه الرجال"), (31.0, 37.5, "دورة مياه النساء"), (19.5, 28.0, "المدخل")]
SP_M = [(26.5, 12.5, "منطقة التحضير"), (14.0, 10.6, "ممر السكن"), (30.6, 7.0, "المكتب")]
def sym_sp(s, x, y): s.dot(x, y, 0.1); s.circle(x, y, 0.22)
def sym_cov(s, x, y): s.circle(x, y, 0.3, lw=5)
def sym_amp(s, x, y): s.rect(x-0.3, y-0.12, x+0.3, y+0.12, lw=35); s.text(x, y, "AMP", h=0.09, attach=5)
def sym_vol(s, x, y): s.rect(x-0.12, y-0.12, x+0.12, y+0.12); s.text(x, y, "V", h=0.1, attach=5)
LEGEND = [
    (sym_sp, "سماعة سقف 6 بوصة 6W نظام 100V لون أسود - معلقة من السقف المكشوف", "ceiling speaker 6\" 6W 100V black, pendant mount"),
    (sym_cov, "دائرة تغطية الصوت (نصف قطر 2.4 م)", "sound coverage radius 2.4 m"),
    (sym_amp, "مضخم صوت 120W + مكسر + مشغل بلوتوث/USB", "amplifier 120W + mixer + BT/USB player"),
    (sym_vol, "مفتاح تحكم بمستوى الصوت لكل منطقة", "zone volume control"),
]
def legend(s, x, y): return s.legend(x, y, "جدول رموز السماعات - SPEAKER LEGEND", LEGEND, w=10.5, rh=0.5)
def draw_G(s):
    for x, y in SP_G: s.speaker(x, y)
    for x, y, _ in SP_G_OTHER: s.speaker(x, y, cover=1.8)
    s.rect(19.6, 35.2, 20.4, 35.45, lw=35); s.hatch([(19.6, 35.2), (20.4, 35.2), (20.4, 35.45), (19.6, 35.45)])
    s.text(20.0, 35.1, "AMP 120W", h=0.1, attach=2)
    for x, y in [(20.9, 35.3), (24.0, 36.0), (9.0, 36.3)]:
        s.rect(x-0.12, y-0.12, x+0.12, y+0.12); s.text(x, y, "V", h=0.1, attach=5)
    s.leader([(20.0, 35.3), (21.5, 33.3)]); s.text(21.5, 33.2, "مضخم صوت 120W + مشغل بلوتوث عند الكاشير\\P3 مناطق: الصالة - المطبخ - دورات المياه", attach=1, **C)
    s.leader([(9.5, 33.5), (6.4, 34.6)]); s.text(6.4, 34.7, "سماعة سقف 6 بوصة\\Pمعلقة ارتفاع 4.0 م", attach=2, **C)
    s.dim((9.5, 29.0), (13.5, 29.0), offset=-0.7, **D); s.dim((13.5, 29.0), (18.0, 29.5), offset=-0.9, **D); s.dim((18.0, 29.5), (22.5, 29.5), offset=-0.7, **D)
    s.dim((22.5, 29.5), (27.0, 29.5), offset=-0.7, **D); s.dim((27.0, 29.5), (30.5, 31.5), offset=-0.7, **D)
    s.dim((9.5, 29.0), (9.5, 33.5), offset=-1.4, horizontal=False, **D); s.dim((18.0, 29.5), (18.0, 33.5), offset=0.6, horizontal=False, **D)
    s.dim((7.4, 29.0), (9.5, 29.0), offset=-0.7, **D)
    n = len(SP_G) + len(SP_G_OTHER)
    s.text(12.5, 29.6, f"عدد السماعات في الطابق الأرضي = {n} (الصالة 11 + المطبخ 1 + دورات المياه 2 + المدخل 1)", h=0.14, attach=5, color=7)
    x0, y0, x1, y1 = EMPTY_G
    legend(s, x0 + 0.2, y1 - 0.1)
    s.notes(34.8, 45.0, ["سماعات سقف 6 بوصة 6W نظام 100V لون أسود، تعليق بسلك من السقف المكشوف ارتفاع 4.0 م", "تباعد السماعات 4.0 - 4.5 م لتغطية متجانسة بمستوى 70 dB",
                         "كابل سماعات 2×1.5 مم داخل مواسير PVC سوداء مكشوفة", "مضخم 120W مع 3 مناطق تحكم مستقلة ومدخل بلوتوث/USB", "العدد الإجمالي = 15 سماعة + مضخم 1"],
            h=0.14, w=9.0, title="ملاحظات السماعات")
def draw_M(s):
    for x, y, _ in SP_M: s.speaker(x, y, cover=1.8)
    for x, y in [(22.2, 12.0)]:
        s.rect(x-0.12, y-0.12, x+0.12, y+0.12); s.text(x, y, "V", h=0.1, attach=5)
    s.leader([(26.5, 12.5), (26.5, 15.0)]); s.text(26.5, 15.1, "سماعة سقف 6 بوصة - سقف جبس ارتفاع 2.6 م", attach=8, **C)
    s.dim((14.0, 10.6), (26.5, 12.5), offset=-5.0, **D); s.dim((26.5, 12.5), (30.6, 7.0), offset=0.5, horizontal=False, **D)
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    s.text(14.0, 5.2, f"عدد السماعات في الميزانين = {len(SP_M)}", h=0.14, attach=5, color=7)
    x0, y0, x1, y1 = EMPTY_M
    legend(s, x0 + 0.2, y1 - 0.1)
    s.notes(34.8, 20.0, ["سماعات الميزانين على منطقة رابعة من نفس المضخم", "سماعات سقف جبس مدمجة 6 بوصة لون أبيض"], h=0.14, w=9.0, title="ملاحظات")
