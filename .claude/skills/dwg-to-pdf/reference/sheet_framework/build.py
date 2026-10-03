#!/usr/bin/env python3
"""Assemble all discipline sheets into one DXF and plot to PDF.
usage: build.py [--only key,key] [--no-pdf]"""
import sys, importlib, argparse, subprocess, os, time
import fixdoc, lib
from lib import Ctx, Sheet, sheet_box

SHEETS = [  # key, module, title G, title M (None = no mezzanine sheet)
    ("elec",    "disc_elec",    "مخطط نقاط أفياش الكهرباء",        "مخطط نقاط أفياش الكهرباء - الميزانين"),
    ("plumb",   "disc_plumb",   "مخطط السباكة",                    "مخطط السباكة - الميزانين"),
    ("hvac",    "disc_hvac",    "مخطط التكييف - الدكت",             "مخطط التكييف - الميزانين"),
    ("gas",     "disc_gas",     "مخطط الغاز",                      "مخطط الغاز - الميزانين"),
    ("exhaust", "disc_exhaust", "مخطط الشفاط والتهوية",            "مخطط الشفاط والتهوية - الميزانين"),
    ("cctv",    "disc_cctv",    "مخطط كاميرات المراقبة",           "مخطط كاميرات المراقبة - الميزانين"),
    ("speak",   "disc_speak",   "مخطط السماعات",                   "مخطط السماعات - الميزانين"),
    ("insect",  "disc_insect",  "مخطط الناموسية",                  "مخطط الناموسية - الميزانين"),
    ("fresh",   "disc_fresh",   "مخطط معطر الجو",                  "مخطط معطر الجو - الميزانين"),
    ("floor",   "disc_floor",   "مخطط الأرضية",                    "مخطط الأرضية - الميزانين"),
    ("light",   "disc_light",   "مخطط الانارة - التراك لايت",       "مخطط الانارة - الميزانين"),
    ("ceil",    "disc_ceil",    "مخطط السقف",                      "مخطط السقف - الميزانين"),
    ("wall",    "disc_wall",    "مخطط الجدران والتشطيبات",         "مخطط الجدران - الميزانين"),
    ("furn",    "disc_furn",    "مخطط الأثاث",                     "مخطط الأثاث - الميزانين"),
    ("facade",  "disc_facade",  "مخطط الواجهة",                    None),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma separated sheet keys")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--out", default="einstein_all")
    a = ap.parse_args()
    keys = a.only.split(",") if a.only else [s[0] for s in SHEETS]
    t0 = time.time()
    doc = fixdoc.load_fixed()
    ctx = Ctx(doc)
    boxes = []
    # index / cover sheet (column 16, far right so it never collides)
    import disc_index
    rows = [(2, "مخطط المحل - المخطط العام", "الأرضي"), (3, "مخطط المحل - المخطط العام", "الميزانين")]
    page = 4
    for key, modname, tg, tm in SHEETS:
        if key not in keys: continue
        rows.append((page, tg, "الأرضي")); page += 1
        if tm: rows.append((page, tm, "الميزانين")); page += 1
    disc_index.ROWS = rows
    if not a.only:
        si = Sheet(ctx, "G", 16, "فهرس المخططات", "LEGEND")
        disc_index.draw_G(si); boxes.append(sheet_box("G", 16))
    boxes += [sheet_box("G", 0), sheet_box("M", 0)]
    col = 0
    for key, modname, tg, tm in SHEETS:
        if key not in keys:
            continue
        col += 1
        mod = importlib.import_module(modname)
        sg = Sheet(ctx, "G", col, tg, mod.LAYER)
        mod.draw_G(sg); boxes.append(sheet_box("G", col))
        if tm:
            sm = Sheet(ctx, "M", col, tm, mod.LAYER)
            mod.draw_M(sm); boxes.append(sheet_box("M", col))
        print(f"sheet {key} done ({time.time()-t0:.0f}s)", flush=True)
    dxf = a.out + ".dxf"
    doc.saveas(dxf)
    print("saved", dxf, f"{os.path.getsize(dxf)//1024} KB")
    if not a.no_pdf:
        S = "/home/user/sabrilaptop/.claude/skills/dwg-to-pdf/scripts/dwg2pdf_frames.py"
        frames = ";".join(",".join(f"{v:.4f}" for v in b) for b in boxes)
        prev = ",".join(str(i) for i in range(1, len(boxes) + 1))
        cmd = [sys.executable, S, dxf, "-o", a.out + ".pdf", "--flip-file", "flip.txt", "--frames", frames, "--keep-order", "--preview", prev, "--preview-dpi", "60"]
        subprocess.run(cmd, check=False)
    print(f"total {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
