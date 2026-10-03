"""render a region of the model with a 1 m grid overlay -> PNG tiles for coordinate reading"""
import sys, ezdxf
from ezdxf import recover
from ezdxf.addons.drawing import Frontend, RenderContext, layout, config
from ezdxf.addons.drawing.pymupdf import PyMuPdfBackend
from ezdxf.math import BoundingBox2d
doc, _ = recover.readfile("wechicks.dxf")
msp = doc.modelspace()
regions = {"G": (8.0, 34.5, 16.0, 55.0), "M": (-4.0, 9.5, 24.0, 29.5)}
name = sys.argv[1]; x0, y0, x1, y1 = regions[name]; ppu = float(sys.argv[2]) if len(sys.argv) > 2 else 60
tiles = int(sys.argv[3]) if len(sys.argv) > 3 else 1
# delete everything outside the region (speed)
for e in list(msp):
    try:
        from ezdxf.bbox import extents
        bb = extents([e], fast=True)
        if not bb.has_data or bb.extmax.x < x0 - 1 or bb.extmin.x > x1 + 1 or bb.extmax.y < y0 - 1 or bb.extmin.y > y1 + 1:
            e.destroy()
    except Exception:
        pass
if "GRID" not in doc.layers: doc.layers.add("GRID", color=1)
import math
for gx in range(math.ceil(x0), math.floor(x1) + 1):
    msp.add_line((gx, y0), (gx, y1), dxfattribs={"layer": "GRID", "color": 1 if gx % 5 else 6, "lineweight": 5})
    for gy in range(math.ceil(y0), math.floor(y1) + 1, 2):
        msp.add_text(f"{gx}", dxfattribs={"layer": "GRID", "color": 1, "height": 0.12}).set_placement((gx + 0.03, gy + 0.05))
for gy in range(math.ceil(y0), math.floor(y1) + 1):
    msp.add_line((x0, gy), (x1, gy), dxfattribs={"layer": "GRID", "color": 1 if gy % 5 else 6, "lineweight": 5})
    for gx in range(math.ceil(x0), math.floor(x1) + 1, 2):
        msp.add_text(f"{gy}", dxfattribs={"layer": "GRID", "color": 3, "height": 0.12}).set_placement((gx + 0.3, gy + 0.05))
ctx = RenderContext(doc)
cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE, color_policy=config.ColorPolicy.COLOR, min_lineweight=0.1)
H = (y1 - y0) / tiles
for t in range(tiles):
    ty0 = y0 + t * H; ty1 = ty0 + H
    backend = PyMuPdfBackend()
    Frontend(ctx, backend, config=cfg).draw_layout(msp)
    box = BoundingBox2d([(x0, ty0), (x1, ty1)])
    w_mm = (x1 - x0) * 10; h_mm = H * 10
    page = layout.Page(w_mm, h_mm, layout.Units.mm, margins=layout.Margins.all(0))
    png = backend.get_pixmap_bytes(page, fmt="png", render_box=box, dpi=int(ppu * 2.54))
    open(f"grid_{name}_{t+1}.png", "wb").write(png); print("wrote", f"grid_{name}_{t+1}.png")
