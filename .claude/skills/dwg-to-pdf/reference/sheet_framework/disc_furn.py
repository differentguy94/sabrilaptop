"""Furniture plan - codes, dimensions, schedule."""
from sitemodel import G, M, EMPTY_G, EMPTY_M
LAYER = "A-FURN"
D = dict(color=1, h=0.12); C = dict(h=0.12, color=7)
F = {  # code: (name, size, material, qty_G, qty_M)
    "F1": ("كنبة بوث جلد أسود كابيتونيه بإطار خشب", "120×70 سم ارتفاع 110 سم", "جلد صناعي أسود + خشب زان", 18, 0),
    "F2": ("طاولة خشب طبيعي Live-edge بأرجل حديد أسود", "120×70 سم ارتفاع 75 سم", "خشب أكاسيا + حديد مطلي بودرة", 12, 0),
    "F3": ("طاولة خشب Live-edge صغيرة", "70×70 سم ارتفاع 75 سم", "خشب أكاسيا + حديد", 4, 0),
    "F4": ("طاولة مشتركة خشب Live-edge طويلة + بنشين", "480×90 سم ارتفاع 75 سم / بنش 200×40", "خشب أكاسيا سمك 6 سم + حديد", 1, 0),
    "F5": ("كرسي طعام حديد أسود بمقعد خشب", "45×50 سم ارتفاع 85 سم", "حديد مطلي + خشب جوز", 30, 0),
    "F6": ("كرسي بار حديد أسود بمقعد خشب دائري", "Ø38 سم ارتفاع 75 سم", "حديد مطلي + خشب جوز", 5, 0),
    "F7": ("بلانتر خشبي بإطار حديد وكرات إضاءة ونباتات", "100×30 سم ارتفاع 90 سم / إطار 180 سم", "خشب داكن + حديد أسود", 13, 0),
    "F8": ("بنش انتظار خشب وحديد بوسادة جلد", "200×50 سم ارتفاع 45 سم", "خشب + حديد + جلد أسود", 1, 0),
    "F9": ("كاونتر الاستقبال بلاط سبواي أسود وسطح خشب", "550×65 سم ارتفاع 105 سم", "بلاط أسود + خشب أكاسيا + شبك حديد", 1, 0),
    "F10": ("أصيص حجري دائري مع شجرة زيتون", "Ø150 سم ارتفاع 300 سم", "حجر صناعي + شجرة صناعية", 1, 0),
    "F11": ("برميل خشبي ديكور", "Ø60 سم ارتفاع 90 سم", "خشب بلوط + أطواق حديد", 2, 0),
    "F12": ("شاشة تلفزيون 65 بوصة", "145×83 سم", "Smart TV 4K", 3, 1),
    "F13": ("لوحة قائمة مضيئة", "120×60 سم", "صندوق ألمنيوم LED", 3, 0),
    "F14": ("رف تسليم الطلبات عند شباك التوصيل", "135×40 سم", "ستانلس ستيل", 1, 0),
    "F16": ("سرير فردي بمرتبة", "200×100 سم", "حديد + مرتبة 20 سم", 0, 6),
    "F17": ("دولاب ملابس", "100×60 سم ارتفاع 200 سم", "MDF ميلامين", 0, 3),
    "F18": ("مكتب على شكل L + كرسي مكتب", "140×60 سم ارتفاع 75 سم", "MDF + حديد", 0, 1),
    "F19": ("رفوف ستانلس ستيل 4 طبقات", "120×50 سم ارتفاع 180 سم", "ستانلس 304", 0, 6),
    "F21": ("خزائن ملابس للعاملين (Lockers) 6 أبواب", "90×45 سم ارتفاع 180 سم", "صاج مطلي", 0, 2),
}
def bubble(s, x, y, code, col=32):
    s.circle(x, y, 0.28, color=col, lw=35); s.text(x, y, code, h=0.12, attach=5, color=7)
def schedule(s, x, y, codes, floor, title):
    w, rh = 12.6, 0.33; cols = [0.8, 0.8, 4.4, 3.4, 3.2]
    rows = [(c,) + F[c][:3] + ((F[c][3] if floor == "G" else F[c][4]),) for c in codes]
    s.rect(x, y - rh * (len(rows) + 2), x + w, y, color=7, layer="LEGEND")
    s.hatch([(x, y - rh), (x + w, y - rh), (x + w, y), (x, y)], color=254, layer="LEGEND")
    s.text(x + w / 2, y - rh / 2, title, h=0.17, attach=5, color=7, layer="LEGEND")
    xs = [x]
    for c in cols: xs.append(xs[-1] + c)
    for xx in xs[1:-1]: s.line((xx, y - rh), (xx, y - rh * (len(rows) + 2)), color=7, layer="LEGEND")
    hdr = ["الكود", "العدد", "الوصف", "المقاس", "الخامة والتشطيب"]
    for i, r in enumerate([None] + rows):
        cy = y - rh * (i + 1) - rh / 2
        if r is None:
            for k, h in enumerate(hdr): s.text((xs[k] + xs[k + 1]) / 2, cy, h, h=0.11, attach=5, color=7, layer="LEGEND")
            continue
        s.line((x, cy - rh / 2), (x + w, cy - rh / 2), color=8, lw=5, layer="LEGEND")
        code, name, size, mat, q = r
        s.text((xs[0] + xs[1]) / 2, cy, code, h=0.11, attach=5, color=7, layer="LEGEND"); s.text((xs[1] + xs[2]) / 2, cy, str(q), h=0.12, attach=5, color=7, layer="LEGEND")
        s.text(xs[3] - 0.1, cy, name, h=0.1, attach=6, color=7, layer="LEGEND", width=4.2); s.text(xs[4] - 0.1, cy, size, h=0.1, attach=6, color=7, layer="LEGEND", width=3.2); s.text(xs[5] - 0.1, cy, mat, h=0.1, attach=6, color=7, layer="LEGEND", width=3.0)
def draw_G(s):
    nb = 0
    for kind, cx, cy, w, h in G["seating"]:
        if kind == "booth":
            bubble(s, cx, cy, "F2" if h > 1.0 else "F3"); nb += 1
            sx = cx - 0.75 if cx < 9 else (cx if cy > 32 or cy < 29 else cx + 0.75)
            sy = cy if (cx < 9 or (29 <= cy <= 32)) else (cy + 0.75 if cy > 32 else cy - 0.6)
            bubble(s, sx, sy, "F1")
        elif kind == "table4": bubble(s, cx, cy, "F2"); bubble(s, cx - 0.75, cy, "F5"); bubble(s, cx + 0.75, cy, "F5")
        elif kind == "communal": bubble(s, cx, cy, "F4"); bubble(s, cx - 1.5, cy + 0.9, "F5"); bubble(s, cx + 1.5, cy - 0.9, "F5")
        elif kind == "bench": bubble(s, cx, cy, "F8")
        elif kind == "bar": pass
    bubble(s, 17.4, 34.25, "F6"); s.text(17.4, 33.85, "×5", h=0.1, attach=5, color=7)
    for x0, y0, x1, y1 in G["planters"]: bubble(s, (x0 + x1) / 2, (y0 + y1) / 2, "F7")
    bubble(s, 18.0, 35.33, "F9"); bubble(s, G["tree"][0], G["tree"][1] - 0.6, "F10")
    for x, y in [(9.7, 30.2), (16.3, 32.6)]: s.circle(x, y, 0.3, color=32); bubble(s, x, y - 0.6, "F11")
    for x, y, rot in G["tv"]: bubble(s, x + (0.6 if rot == 90 else -0.6 if rot == 270 else 0), y + (0 if rot in (90, 270) else -0.6), "F12")
    bubble(s, 19.5, 38.4, "F13"); bubble(s, 22.5, 35.7, "F14")
    # dims (user style) of key items
    s.dim((10.0, 31.0), (14.8, 31.0), offset=-0.7, **D); s.dim((14.8, 31.0), (14.8, 31.9), offset=0.9, horizontal=False, **D)
    s.dim((15.0, 35.0), (21.0, 35.0), offset=-1.2, **D); s.dim((8.05, 27.4), (8.05, 29.0), offset=-0.4, horizontal=False, **D)
    s.dim((23.5, 32.3), (25.5, 32.3), offset=1.0, **D); s.dim((25.5, 32.3), (27.6, 32.3), offset=1.0, **D); s.dim((9.3, 27.4), (23.4, 27.4), offset=-0.6, **D)
    s.dim((9.5, 35.0), (15.3, 35.0), offset=0.0, **D); s.dim((15.6, 34.25), (19.2, 34.25), offset=-0.6, **D); s.dim((24.3, 27.9), (24.3, 31.3), offset=-0.5, horizontal=False, **D)
    s.text(12.4, 30.0, "ممر رئيسي عرض 1.6 م", h=0.11, attach=5, color=7); s.text(20.5, 33.0, "ممر خدمة عرض 1.95 م", h=0.11, attach=5, color=7)
    s.leader([(8.4, 33.7), (6.2, 35.2)]); s.text(6.2, 35.3, "F1 بوث جلد أسود 120×70\\Pارتفاع ظهر 110 سم", attach=2, **C)
    s.leader([(12.4, 31.45), (11.0, 29.0)]); s.text(11.0, 28.9, "F4 طاولة مشتركة خشب Live-edge 480×90 سم\\Pسمك 6 سم على أرجل حديد مع بنشين", attach=3, **C)
    s.leader([(18.0, 35.33), (17.0, 39.7)]); s.text(17.0, 39.8, "F9 كاونتر 5.50 م: واجهة بلاط سبواي أسود، سطح خشب أكاسيا 5 سم\\Pشبك حديد علوي ولوحات قائمة مضيئة", attach=8, **C)
    s.leader([(27.4, 31.45), (28.6, 30.3)]); s.text(28.6, 30.2, "F7 بلانتر خشب 100×30 بإطار حديد أسود\\Pوكرات إضاءة ونباتات صناعية", attach=1, **C)
    x0, y0, x1, y1 = EMPTY_G
    s.text(14.9, 43.1, "الأرقام داخل الدوائر = كود الأثاث حسب الجدول\\Pانظر صفحات مواصفات الأثاث بالصور آخر الملف", h=0.13, attach=3, color=7)
    schedule(s, 22.3, 45.0, ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14"], "G", "جدول الأثاث - الطابق الأرضي - FURNITURE SCHEDULE")
    s.notes(14.9, 45.0, ["إجمالي المقاعد: 18 بوث + 30 كرسي + 5 بار + بنش = 55 مقعداً", "جميع الأخشاب أكاسيا/جوز طبيعي بتشطيب زيت مطفي، الحديد مطلي بودرة أسود مطفي",
                         "جلد البوثات صناعي درجة أولى مقاوم للبقع، إسفنج كثافة 35", "صور ومواصفات كل قطعة في ملحق الأثاث آخر الملف"], h=0.12, w=10.3, title="ملاحظات الأثاث")
def draw_M(s):
    for x0, y0, x1, y1 in M["beds"]:
        s.rect(x0, y0, x1, y1, color=32); s.line((x0 + 0.3, y0), (x0 + 0.3, y1), color=32, lw=5); bubble(s, (x0 + x1) / 2, (y0 + y1) / 2, "F16")
    for x, y in [(10.9, 6.9), (15.7, 6.9), (20.2, 6.9)]: s.rect(x - 0.5, y - 0.3, x + 0.5, y + 0.3, color=32); bubble(s, x, y + 0.75, "F17")
    bubble(s, 30.5, 7.2, "F18")
    for x, y in [(27.2, 7.0), (28.5, 7.0), (27.2, 8.8), (28.5, 8.8)]: s.rect(x - 0.6, y - 0.25, x + 0.6, y + 0.25, color=32); bubble(s, x, y + 0.5, "F19")
    for y in (9.0, 12.5): s.rect(31.1, y - 0.6, 31.5, y + 0.6, color=32); bubble(s, 30.7, y, "F19")
    for x in (9.0, 10.2): s.rect(x - 0.45, 10.0, x + 0.45, 10.45, color=32); bubble(s, x, 10.9, "F21")
    bubble(s, 30.6, 8.4, "F12")
    s.dim((8.0, 7.0), (10.0, 7.0), offset=-0.3, **D); s.dim((10.0, 7.0), (10.0, 8.0), offset=0.3, horizontal=False, **D); s.dim((26.6, 7.0), (27.8, 7.0), offset=-0.4, **D); s.dim((29.8, 6.6), (31.2, 6.6), offset=-0.3, **D)
    s.leader([(9.0, 7.5), (9.0, 5.3)]); s.text(9.0, 5.2, "F16 سرير فردي حديد 200×100 مع مرتبة 20 سم - 2 لكل غرفة", attach=8, **C)
    s.leader([(27.2, 8.8), (26.5, 15.2)]); s.text(26.5, 15.3, "F19 رفوف ستانلس 4 طبقات 120×50×180 للمستودع والتخزين", attach=2, **C)
    s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)
    x0, y0, x1, y1 = EMPTY_M
    schedule(s, 4.2, 20.0, ["F16", "F17", "F18", "F19", "F21", "F12"], "M", "جدول الأثاث - الميزانين - FURNITURE SCHEDULE")
    s.notes(34.8, 20.0, ["أثاث السكن اقتصادي متين سهل التنظيف", "رفوف المستودع ستانلس 304 حمولة 150 كجم/رف"], h=0.13, w=9.0, title="ملاحظات")
