import pymupdf, os, shutil
d = pymupdf.open("wechicks_all.pdf")
names = ["مخطط المحل - الأرضي","مخطط المحل - الميزانين","مخطط المحل بالأبعاد - الأرضي","مخطط المحل بالأبعاد - الميزانين"]
for n in ["نقاط أفياش الكهرباء","السباكة","الشفاط والتهوية","الغاز","كاميرات المراقبة","الأسقف","الإنارة","التكييف","الناموسية","معطر الجو","الأرضيات","الجدران","السماعات","النجفة والشاشات"]:
    names += [f"مخطط {n} - الأرضي", f"مخطط {n} - الميزانين"]
d.set_toc([[1, f"{i+1:02d} {t}", i + 1] for i, t in enumerate(names[:d.page_count])])
d.set_metadata({"title": "We Chicks - Working Drawings A2", "author": "ZWORKS - Eng. Mohammad Ramahi"})
dst = "/home/user/sabrilaptop"; full = os.path.join(dst, "WeChicks_Drawings_A2.pdf")
d.save(full, garbage=4, deflate=True); print("full", os.path.getsize(full) // 2**20, "MiB", d.page_count, "pages")
LIM = 29 * 2**20; parts = []; start = 0; n = d.page_count
while start < n:
    end = n
    while True:
        t = pymupdf.open(); t.insert_pdf(d, from_page=start, to_page=end - 1)
        t.set_toc([[l, s, p - start] for l, s, p in d.get_toc() if start < p <= end]); t.set_metadata(d.metadata)
        buf = t.tobytes(garbage=4, deflate=True)
        if len(buf) <= LIM or end - start == 1: break
        end -= 1
    name = os.path.join(dst, f"WeChicks_Drawings_A2_part{len(parts)+1}.pdf"); open(name, "wb").write(buf); parts.append((name, start + 1, end, len(buf) // 2**20)); start = end
for p in parts: print(p)
shutil.copy("oda_out/wechicks_all.dwg", os.path.join(dst, "WeChicks_Drawings.dwg")); shutil.copy("wechicks_oda.dxf", os.path.join(dst, "WeChicks_Drawings.dxf"))
print(os.listdir(dst))
