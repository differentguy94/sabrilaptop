"""Append furniture catalogue pages (A2 landscape) with the generated isolated renders + specs + dimensions."""
import pymupdf, arabic_reshaper
from bidi.algorithm import get_display
FONT_AR = "/root/.fonts/arial.ttf"
FONT_AR_B = "/root/.fonts/arialbd.ttf"
FONT_EN = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_EN_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
W, H = 594 / 25.4 * 72, 420 / 25.4 * 72   # A2 landscape in points
reshaper = arabic_reshaper.ArabicReshaper({"delete_harakat": False, "support_ligatures": True})
FONTS = {"ar": pymupdf.Font(fontfile=FONT_AR), "arb": pymupdf.Font(fontfile=FONT_AR_B), "en": pymupdf.Font(fontfile=FONT_EN), "enb": pymupdf.Font(fontfile=FONT_EN_B)}
def tl(text, fontname, fontsize): return FONTS[fontname].text_length(text, fontsize=fontsize)
def register(page):
    for k, f in (("ar", FONT_AR), ("arb", FONT_AR_B), ("en", FONT_EN), ("enb", FONT_EN_B)): page.insert_font(fontname=k, fontfile=f)
def ar(s): return get_display(reshaper.reshape(s))
ITEMS = [  # (image, code, name_ar, name_en, W x D x H cm, material, finish, qty, dims(w,d,h) for annotation)
    ("f00.png", "F1 + F2", "بوث جلد أسود مع طاولة خشب Live-edge", "Booth sofa + live-edge table", "120 × 70 × 110", "جلد صناعي أسود درجة أولى، هيكل خشب زان، إسفنج كثافة 35", "خشب داكن مطفي / جلد أسود", "18 بوث + 12 طاولة", (120, 70, 110)),
    ("f01.png", "F2", "طاولة خشب أكاسيا Live-edge بأرجل حديد", "Live-edge acacia table, steel legs", "120 × 70 × 75", "خشب أكاسيا طبيعي سمك 5 سم بحافة طبيعية، أرجل حديد مربع 5×5 سم", "زيت خشب مطفي / حديد بودرة أسود", "12", (120, 70, 75)),
    ("f02.png", "F4", "طاولة مشتركة Live-edge طويلة مع بنشين", "Communal live-edge table + 2 benches", "480 × 90 × 75", "خشب أكاسيا سمك 6 سم من قطعتين، بنش 200×40 بوسادة جلد أسود", "زيت مطفي / حديد أسود", "1 طاولة + 2 بنش", (480, 90, 75)),
    ("f03.png", "F5", "كرسي طعام حديد أسود بمقعد خشب", "Dining chair, black steel + wood", "45 × 50 × 85", "هيكل حديد أنبوبي 20 مم، مقعد وظهر خشب جوز منحني 12 مم", "بودرة أسود مطفي / خشب جوز", "30", (45, 50, 85)),
    ("f04.png", "F6", "كرسي بار حديد أسود بمقعد خشب دائري", "Bar stool", "Ø38 × 75", "هيكل حديد مربع 25 مم مع مسند قدم، مقعد خشب جوز Ø38 سم", "بودرة أسود مطفي / خشب جوز", "5", (38, 38, 75)),
    ("f05.png", "F7", "بلانتر خشبي بإطار حديد وكرات إضاءة", "Planter partition with globe lights", "100 × 30 × 90 (إطار 180)", "صندوق خشب داكن مع بطانة معدنية ونباتات صناعية، إطار حديد 20 مم، 3 كرات زجاج 25 سم LED 6W 3000K", "خشب داكن / حديد أسود", "13", (100, 30, 180)),
    ("f06.png", "F8", "بنش انتظار خشب وحديد بوسادة جلد", "Waiting bench", "200 × 50 × 45", "قاعدة خشب أكاسيا، إطار حديد أنبوبي أسود، وسادة جلد أسود", "خشب مطفي / حديد أسود", "1", (200, 50, 45)),
    ("f07.png", "F9", "كاونتر الاستقبال", "Front counter", "550 × 65 × 105", "واجهة بلاط سبواي أسود لامع، سطح خشب أكاسيا 5 سم، شبك حديد أسود علوي مع شعار", "بلاط أسود / خشب / حديد", "1", (550, 65, 105)),
    ("f08.png", "F10", "أصيص حجري دائري مع شجرة زيتون", "Stone pot + olive tree", "Ø150 × 300", "أصيص حجر صناعي GRC رمادي، شجرة زيتون صناعية 3 م", "حجر رمادي", "1", (150, 150, 300)),
    ("f09.png", "L2", "بندانت معدني قبة أسود", "Black dome pendant", "Ø30 × 25", "معدن مطلي أسود مطفي، سلك قماش أسود 2 م، لمبة LED فيلامنت 8W 3000K", "أسود مطفي / داخل ذهبي", "27", (30, 30, 25)),
    ("f10.png", "L1", "تراك لايت أسود مع رؤوس سبوت", "Black track light + spot heads", "200 × 4 × 10 (رأس Ø6×12)", "مسار ألمنيوم 1 فاز 2 م، رؤوس LED 12W 4000K زاوية 36°، CRI 90", "أسود مطفي", "13 تراك / 26 رأس", (200, 4, 12)),
    ("f11.png", "F11", "برميل خشبي ديكور", "Decorative oak barrel", "Ø60 × 90", "خشب بلوط معتق مع أطواق حديد أسود", "خشب معتق", "2", (60, 60, 90)),
]
def draw_item(page, x0, y0, cw, ch, it, idx):
    img, code, name_ar, name_en, size, mat, fin, qty, (dw, dd, dh) = it
    pad = 10
    page.draw_rect(pymupdf.Rect(x0, y0, x0 + cw, y0 + ch), color=(0.2, 0.2, 0.2), width=0.8)
    page.draw_rect(pymupdf.Rect(x0, y0, x0 + cw, y0 + 26), color=(0.2, 0.2, 0.2), fill=(0.93, 0.93, 0.93), width=0.8)
    page.insert_text((x0 + 8, y0 + 18), code, fontsize=13, fontname="enb", color=(0.8, 0, 0))
    t = ar(name_ar); tw = tl(t, "arb", 13)
    page.insert_text((x0 + cw - 8 - tw, y0 + 18), t, fontsize=13, fontname="arb")
    # image area
    ir = pymupdf.Rect(x0 + pad + 30, y0 + 34, x0 + cw - pad - 30, y0 + ch * 0.60)
    page.insert_image(ir, filename="furn_img/" + img, keep_proportion=True)
    # dimension annotations around the image (W under, H right)
    rr = ir
    y_d = rr.y1 + 8
    page.draw_line((rr.x0, y_d), (rr.x1, y_d), color=(0.85, 0, 0), width=0.8)
    for xx in (rr.x0, rr.x1): page.draw_line((xx, y_d - 4), (xx, y_d + 4), color=(0.85, 0, 0), width=0.8)
    wl = f"W {dw} cm" if dw != dd or dw not in (38, 60, 150, 30) else f"Ø {dw} cm"
    page.insert_text(((rr.x0 + rr.x1) / 2 - 20, y_d + 11), wl, fontsize=8, fontname="en", color=(0.85, 0, 0))
    x_d = rr.x1 + 10
    page.draw_line((x_d, rr.y0), (x_d, rr.y1), color=(0.85, 0, 0), width=0.8)
    for yy in (rr.y0, rr.y1): page.draw_line((x_d - 4, yy), (x_d + 4, yy), color=(0.85, 0, 0), width=0.8)
    page.insert_text((x_d + 4, (rr.y0 + rr.y1) / 2), f"H {dh}", fontsize=8, fontname="en", color=(0.85, 0, 0), rotate=0)
    page.insert_text((x_d + 4, (rr.y0 + rr.y1) / 2 + 10), f"D {dd}", fontsize=8, fontname="en", color=(0.85, 0, 0))
    # spec rows (Arabic right aligned)
    rows = [("المقاس (سم)", size), ("الخامة", mat), ("التشطيب", fin), ("الكمية", qty), ("الوصف", name_en)]
    yy = y0 + ch * 0.60 + 26
    for lab, val in rows:
        lt = ar(lab + " :"); ltw = tl(lt, "arb", 9)
        page.insert_text((x0 + cw - 8 - ltw, yy), lt, fontsize=9, fontname="arb", color=(0.2, 0.2, 0.2))
        vt = ar(val); maxw = cw - 16 - ltw - 6
        # wrap value
        words = vt.split(" "); lines = []; cur = ""
        for wd in words[::-1] if False else words:
            test = (cur + " " + wd).strip()
            if tl(test, "ar", 9) > maxw and cur:
                lines.append(cur); cur = wd
            else: cur = test
        if cur: lines.append(cur)
        for ln in lines:
            lw = tl(ln, "ar", 9)
            page.insert_text((x0 + cw - 8 - ltw - 6 - lw, yy), ln, fontsize=9, fontname="ar")
            yy += 12
        if not lines: yy += 12
def build(out_pdf, title_ar="ملحق مواصفات الأثاث والإضاءة بالصور - FURNITURE & LIGHTING SPECIFICATION"):
    doc = pymupdf.open()
    per = 6; cols, rows = 3, 2
    m = 30; top = 70; bottom = 60
    cw = (W - 2 * m - (cols - 1) * 14) / cols; ch = (H - top - bottom - (rows - 1) * 14) / rows
    for p in range(0, len(ITEMS), per):
        page = doc.new_page(width=W, height=H); register(page)
        page.draw_rect(pymupdf.Rect(12, 12, W - 12, H - 12), color=(0, 0, 0), width=1.2)
        t = ar(title_ar); tw = tl(t, "arb", 20)
        page.insert_text(((W - tw) / 2, 48), t, fontsize=20, fontname="arb")
        sub = ar(f"Einstein Burger - مطعم اينشتاين بورجر | ZWORKS - م. محمد الرماحي | صفحة {p // per + 1} من {(len(ITEMS) + per - 1) // per}")
        sw = tl(sub, "ar", 10)
        page.insert_text(((W - sw) / 2, H - 30), sub, fontsize=10, fontname="ar", color=(0.3, 0.3, 0.3))
        for k, it in enumerate(ITEMS[p:p + per]):
            c, r = k % cols, k // cols
            draw_item(page, m + c * (cw + 14), top + r * (ch + 14), cw, ch, it, p + k)
    doc.save(out_pdf); print("catalog pages:", doc.page_count)
if __name__ == "__main__":
    build("furn_catalog.pdf")
