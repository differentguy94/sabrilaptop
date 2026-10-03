from wcommon import dims_G, dims_M, legend, notes, head
from wmodel import G, M, G_PTS, M_PTS
LAYER = "E-POWER"
CODES = [("P", "فيش كهربائي جداري 220V ارتفاع 40 سم", "wall socket 220V, h=0.40 m"),
         ("U", "فيش جداري + مدخل USB عند الجلسات ارتفاع 40 سم", "socket + USB at seating"),
         ("F", "بوكس أرضي: فيش مزدوج + USB تحت الطاولات", "floor box: double socket + USB"),
         ("K", "فيش معدات مطبخ 16A مقاوم للماء IP44 ارتفاع 120 سم", "kitchen equipment socket IP44, h=1.20 m"),
         ("3", "تغذية 3 فاز 380V (قلايات / ثلاجة تجميد مركزية)", "3-phase feed 380V"),
         ("C", "نقطة كاشير: فيش مزدوج + داتا + طابعة + درج", "cashier: double socket + data + POS"),
         ("S", "نقطة شاشة / نيون / لوحة مضيئة ارتفاع 220 سم", "screen / neon / illuminated sign, h=2.20 m"),
         ("W", "نقطة سخان ماء فوري 220V 16A", "instant water heater point"),
         ("D", "نقطة مكتب: 2 فيش + 2 داتا RJ45", "workstation: 2 sockets + 2 data"),
         ("R", "نقطة سيرفر / راك: فيش مزدوج + UPS", "server rack: double socket + UPS")]
def _legend(s, floor, pts):
    from collections import Counter
    n = Counter(c for _, c in pts)
    rows = [(lambda sh, cx, cy, c=c: sh.elec_point(cx, cy, c, r=0.17), f"{ar}  (العدد {n[c]})", en) for c, ar, en in CODES if n[c]]
    rows.append((lambda sh, cx, cy: sh.box_label(cx, cy, "D.B", h=0.1, w=0.5, color=7), "لوحة توزيع كهربائية رئيسية / فرعية", "distribution board"))
    H = legend(s, floor, "رموز نقاط الكهرباء - LEGEND", rows)
    from wcommon import LEG_G, LEG_M
    x, y, w = LEG_G if floor == "G" else LEG_M
    s.text(x + w, y - H - 0.25, f"إجمالي النقاط: {len(pts)} نقطة", h=0.13, attach=3, color=7, layer="NOTES")
NOTES = ["جميع الأفياش 220V / 13A بريطاني مع تأريض، أفياش المطبخ IP44 على ارتفاع 120 سم من الأرضية النهائية.",
         "كل دائرة أفياش بقاطع 20A، دوائر المطبخ مستقلة بقواطع تفاضلية RCD 30mA.",
         "تغذية 3 فاز للقلايات وغرفة التجميد المركزية بكابل 5x6 مم² وقاطع 32A مستقل لكل جهاز.",
         "نقاط الشاشات والنيون والعلامات المضيئة على دوائر مستقلة يتم التحكم بها من لوحة الكاشير.",
         "الأبعاد الحمراء: مسافات النقاط عن زوايا الجدران وعن بعضها بالمتر (محور النقطة).",
         "تمديد الكابلات داخل مواسير PVC مخفية في الجدران وفوق السقف المستعار، ولا تمر فوق أجهزة الطهي."]
def _draw(s, floor, pts, db):
    for (x, y), c in pts:
        s.elec_point(x, y, c, r=0.22)
    (dims_G if floor == "G" else dims_M)(s, [p for p, _ in pts])
    s.box_label(*db, "D.B", h=0.12, w=0.6, color=7)
    _legend(s, floor, pts)
    notes(s, floor, NOTES, "ملاحظات الكهرباء")
def draw_G(s):
    _draw(s, "G", G_PTS, (17.0, 43.5))
    s.text(17.4, 43.5, "لوحة التوزيع الرئيسية MDB على الجدار الأيمن - تغذية من عداد الشركة", h=0.12, attach=4, color=7, layer="NOTES")
    head(s, "G", "مخطط نقاط أفياش الكهرباء - الدور الأرضي: كل نقطة مرمّزة حسب استخدامها (كاشير، معدات مطبخ، 3 فاز، شاشات ونيون، USB للجلسات) مع أبعادها عن الجدران.")
def draw_M(s):
    _draw(s, "M", M_PTS, (10.9, 18.0))
    s.text(10.9, 17.6, "لوحة توزيع فرعية SDB-M (ميزانين + إدارة) - تغذية من MDB الأرضي", h=0.11, attach=2, color=7, layer="NOTES")
    head(s, "M", "مخطط نقاط أفياش الكهرباء - الميزانين والإدارة: نقاط USB للجلسات والبار، بوكسات أرضية للطاولات، نقاط مكاتب وسيرفر، نيون وشاشات.")
