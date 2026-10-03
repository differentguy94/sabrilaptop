"""Contact sheets of the final PDF for visual QA (6 pages per image)."""
import pymupdf, sys
from PIL import Image, ImageDraw
pdf = sys.argv[1] if len(sys.argv) > 1 else "einstein_final.pdf"
d = pymupdf.open(pdf); cols, rows, w = 2, 3, 1000
for s in range(0, d.page_count, cols * rows):
    ims = []
    for i in range(s, min(s + cols * rows, d.page_count)):
        pg = d[i]; z = w / pg.rect.width; pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z))
        ims.append((i, Image.frombytes("RGB", (pix.width, pix.height), pix.samples)))
    h = max(im.height for _, im in ims); sheet = Image.new("RGB", (cols * w, rows * h), "white"); dr = ImageDraw.Draw(sheet)
    for k, (i, im) in enumerate(ims):
        x, y = (k % cols) * w, (k // cols) * h; sheet.paste(im, (x, y)); dr.rectangle([x, y, x + 70, y + 24], fill="yellow"); dr.text((x + 6, y + 5), f"p{i+1}", fill="black")
    sheet.save(f"qa_{s // (cols*rows) + 1}.png"); print("qa sheet", s // (cols * rows) + 1, "pages", s + 1, "-", min(s + cols * rows, d.page_count))
