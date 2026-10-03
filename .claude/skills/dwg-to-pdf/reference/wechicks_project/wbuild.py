"""We Chicks: fill the user's 28 frames + 2 new columns, save DXF, plot to A2 PDF"""
import sys, argparse, importlib, subprocess
from fixdoc import load_fixed
from wlib import Ctx, Sheet, sheet_box, FRAME
ap = argparse.ArgumentParser(); ap.add_argument("--only"); ap.add_argument("--out", default="wechicks_all"); ap.add_argument("--preview", action="store_true"); ap.add_argument("--noplot", action="store_true")
a = ap.parse_args()
# col, module, in_place, clear_layers, titleG, titleM
SHEETS = [(2, "elec", True, ("E-POWER", "LEGEND"), None, None), (3, "plumb", True, (), None, None), (4, "exhaust", True, (), None, None),
          (5, "gas", True, (), None, None), (6, "cctv", True, (), None, None), (7, "ceil", True, (), None, None), (8, "light", True, (), None, None),
          (9, "hvac", True, (), None, None), (10, "insect", True, (), None, None), (11, "fresh", True, (), None, None), (12, "floor", True, (), None, None),
          (13, "wall", True, (), None, None), (14, "speak", False, (), "مخطط السماعات", "مخطط السماعات - الميزانين"),
          (15, "chand", False, (), "مخطط النجفة والشاشات", "مخطط النجفة والشاشات - الميزانين")]
only = set(a.only.split(",")) if a.only else None
doc = load_fixed("wechicks.dxf"); ctx = Ctx(doc)
# fix the forgotten title of the mezzanine base plan (frame 15)
for e in ctx.box_entities("M", 0):
    if e.dxftype() == "MTEXT" and e.dxf.char_height > 0.4 and "المحل" in e.plain_text():
        import re; m = re.match(r"(\\pi[^;]*;)", e.text); e.text = (m.group(1) if m else "") + "مخطط المحل - الميزانين"
boxes = []
if not only:
    boxes += [sheet_box("G", 0), sheet_box("M", 0), sheet_box("G", 1), sheet_box("M", 1)]
for col, name, inplace, clear, tG, tM in SHEETS:
    if only and name not in only: continue
    mod = importlib.import_module("disc_" + name)
    layer = getattr(mod, "LAYER", "NOTES")
    for floor, title, fn in (("G", tG, mod.draw_G), ("M", tM, mod.draw_M)):
        s = Sheet(ctx, floor, col, title, layer, in_place=inplace, clear_layers=clear)
        fn(s); boxes.append(sheet_box(floor, col)); print("sheet", name, floor)
doc.saveas(a.out + ".dxf"); print("saved", a.out + ".dxf")
frames = ";".join(",".join(f"{v:.3f}" for v in b) for b in boxes)
cmd = ["/usr/bin/python3", "/home/user/sabrilaptop/.claude/skills/dwg-to-pdf/scripts/dwg2pdf_frames.py", a.out + ".dxf", "-o", a.out + ".pdf",
       "--frames=" + frames, "--keep-order", "--flip-file", "flip.txt"]
if a.preview: cmd += ["--preview", ",".join(str(i + 1) for i in range(len(boxes))), "--preview-dpi", "70"]
if a.noplot: sys.exit(0)
r = subprocess.run(cmd, capture_output=True, text=True); print("\n".join(l for l in (r.stdout + r.stderr).splitlines() if "Required" not in l)[-1500:])
