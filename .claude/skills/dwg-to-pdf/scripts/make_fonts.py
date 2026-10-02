#!/usr/bin/env python3
"""Build substitute TTFs for Windows fonts that AutoCAD drawings reference (arial.ttf,
georgia.ttf, tahoma.ttf, times.ttf, ...) by merging a Latin font with Noto Naskh Arabic.
Output goes to ~/.fonts and the ezdxf font cache is rebuilt.

Why: the cloud container has no Arial; ezdxf then falls back to a font without Arabic
presentation forms and Arabic text renders as boxes. Family names are rewritten so that
MTEXT inline codes like \\fArial|b0|i0|c178|p34; resolve to the merged font.
Usage: make_fonts.py [extra_name.ttf ...]   (extra names get the sans substitute)
"""
import os, sys, glob, shutil
from fontTools import merge
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem

OUT = os.path.expanduser("~/.fonts")
os.makedirs(OUT, exist_ok=True)

def first(*globs):
    for g in globs:
        hits = sorted(glob.glob(g))
        if hits: return hits[0]
    return None

SANS_R = first("/usr/share/fonts/truetype/liberation*/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
SANS_B = first("/usr/share/fonts/truetype/liberation*/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
SERIF_R = first("/usr/share/fonts/truetype/liberation*/LiberationSerif-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
ARAB_R = first("/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf", "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf")
ARAB_B = first("/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf", "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf")

def rename(path, family):
    f = TTFont(path)
    for rec in f["name"].names:
        if rec.nameID in (1, 4, 16): rec.string = family
        elif rec.nameID == 6: rec.string = family.replace(" ", "")
        elif rec.nameID == 3: rec.string = f"{family};merged-arabic"
    f.save(path)

def build(latin, arabic, out, family):
    if os.path.exists(out): return out
    if latin is None:
        raise SystemExit("no Latin base font found (install fonts-liberation or fonts-dejavu)")
    if arabic is None:
        # DejaVu Sans already carries Arabic presentation forms: just rename a copy
        shutil.copy(latin if "DejaVu" in latin else first("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), out)
        rename(out, family); return out
    a = TTFont(arabic); b = TTFont(latin)
    tmp = out + ".ar.tmp"
    scale_upem(a, b["head"].unitsPerEm); a.save(tmp)        # merge needs equal unitsPerEm
    merged = merge.Merger().merge([latin, tmp]); merged.save(out); os.remove(tmp)
    rename(out, family)
    cm = TTFont(out).getBestCmap()
    pf = sum(1 for cp in range(0xFE70, 0xFF00) if cp in cm)
    assert pf > 100, f"{out}: Arabic presentation forms missing ({pf})"
    return out

TARGETS = {  # windows font file name -> (latin, arabic, family)
    "arial.ttf": (SANS_R, ARAB_R, "Arial"), "arialbd.ttf": (SANS_B, ARAB_B, "Arial"),
    "tahoma.ttf": (SANS_R, ARAB_R, "Tahoma"), "tahomabd.ttf": (SANS_B, ARAB_B, "Tahoma"),
    "calibri.ttf": (SANS_R, ARAB_R, "Calibri"), "verdana.ttf": (SANS_R, ARAB_R, "Verdana"),
    "segoeui.ttf": (SANS_R, ARAB_R, "Segoe UI"),
    "georgia.ttf": (SERIF_R, ARAB_R, "Georgia"), "times.ttf": (SERIF_R, ARAB_R, "Times New Roman"),
    "simplex.ttf": (SANS_R, ARAB_R, "Simplex"),
}
for extra in sys.argv[1:]:
    name = os.path.basename(extra).lower()
    if not name.endswith(".ttf"): name += ".ttf"
    TARGETS.setdefault(name, (SANS_R, ARAB_R, os.path.splitext(name)[0].title()))

for fname, (lat, ar, fam) in TARGETS.items():
    try:
        build(lat, ar, os.path.join(OUT, fname), fam); print("font ok:", fname)
    except Exception as ex:
        print("font FAILED:", fname, ex)

from ezdxf.fonts import fonts
fonts.build_system_font_cache(); fonts.load()
print("ezdxf cache: arial.ttf found =", fonts.font_manager.has_font("arial.ttf"))
