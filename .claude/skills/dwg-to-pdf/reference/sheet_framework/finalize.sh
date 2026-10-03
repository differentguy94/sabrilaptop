#!/usr/bin/env bash
# Full build -> PDF (+ furniture catalogue pages) -> DWG (ODA) -> deliverables in the project folder
set -euo pipefail
cd /tmp/claude-0/-home-user-sabrilaptop/6a4f6234-9858-5cf3-989b-6ce57a9ed0bd/scratchpad/einstein
python3 build.py --out einstein_all 2>&1 | grep -v "Required" | grep -E "^sheet|^saved|^purged|Error|Trace" 
python3 furn_catalog.py
python3 - <<'PY'
import pymupdf
d = pymupdf.open("einstein_all.pdf"); c = pymupdf.open("furn_catalog.pdf")
toc = d.get_toc(); n = d.page_count
d.insert_pdf(c)
toc += [[1, f"{n+1+i:02d} ملحق مواصفات الأثاث بالصور ({i+1})", n + 1 + i] for i in range(c.page_count)]
d.set_toc(toc); d.set_metadata({"title": "Einstein Burger - Working Drawings A2", "author": "ZWORKS - Eng. Mohammad Ramahi"})
d.save("einstein_final.pdf", garbage=3, deflate=True); print("final pdf pages:", d.page_count)
PY
rm -rf oda_in oda_out && mkdir oda_in oda_out && cp einstein_all.dxf oda_in/
xvfb-run -a timeout 900 /usr/bin/ODAFileConverter "$PWD/oda_in" "$PWD/oda_out" ACAD2018 DWG 0 1 "*.dxf" 2>&1 | grep -v -i "locale" | tail -2 || true
ls -la oda_out/
DST=/home/user/sabrilaptop
cp einstein_final.pdf "$DST/Einstein_Burger_Drawings_A2.pdf"
cp oda_out/einstein_all.dwg "$DST/Einstein_Burger_Drawings.dwg"
cp einstein_all.dxf "$DST/Einstein_Burger_Drawings.dxf"
ls -la "$DST" | grep -i einstein
