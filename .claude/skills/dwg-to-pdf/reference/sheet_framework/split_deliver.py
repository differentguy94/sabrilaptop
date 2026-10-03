import pymupdf, sys, os
src = sys.argv[1]; dst = "/home/user/sabrilaptop"
d = pymupdf.open(src)
# shrink catalogue images (PNG -> JPEG, <=150 dpi on an A2 page is still crisp)
d.rewrite_images(dpi_threshold=160, dpi_target=150, quality=82, lossy=True, lossless=True, set_to_gray=False)
full = os.path.join(dst, "Einstein_Burger_Drawings_A2.pdf")
d.save(full, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
print("full", os.path.getsize(full)//2**20, "MiB")
n = d.page_count
LIM = 29 * 2**20
# split into parts each <= LIM
parts = []; start = 0
while start < n:
    end = n
    while True:
        t = pymupdf.open(); t.insert_pdf(d, from_page=start, to_page=end-1)
        toc = [[l, s, p - start] for l, s, p in d.get_toc() if start < p <= end]
        t.set_toc(toc); t.set_metadata(d.metadata)
        buf = t.tobytes(garbage=4, deflate=True)
        if len(buf) <= LIM or end - start == 1: break
        end -= 1
    name = os.path.join(dst, f"Einstein_Burger_Drawings_A2_part{len(parts)+1}.pdf")
    open(name, "wb").write(buf); parts.append((name, start+1, end, len(buf)//2**20)); start = end
for p in parts: print(p)
