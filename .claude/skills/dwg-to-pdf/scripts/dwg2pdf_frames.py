#!/usr/bin/env python3
"""
dwg2pdf_frames.py - plot every sheet frame of a DWG/DXF to one multi-page vector PDF.

  python3 dwg2pdf_frames.py drawing.dwg -o out.pdf                 # auto: frames, A2, Arabic
  python3 dwg2pdf_frames.py drawing.dwg --dump-arabic              # list unique Arabic lines
  python3 dwg2pdf_frames.py drawing.dwg -o out.pdf --flip-file flip.txt --preview 1,4

What it does (all learned the hard way - see SKILL.md):
  * DWG -> DXF with libredwg `dwg2dxf` (found on PATH or in ~/.dwg2pdf-tools/mmenv/bin)
  * frame detection: closed axis-aligned rectangles sharing the same size (the sheet borders),
    sorted top-to-bottom then left-to-right; override with --frame-size / --frames / --layer
  * Arabic: reshape (contextual forms) + bidi (visual order) BEFORE handing text to ezdxf,
    because ezdxf draws glyphs left-to-right as given; optional word-order flip list for
    labels stored in visual order (--flip-file, one line each, matched after whitespace
    normalisation). Modelspace text is processed exactly once (never via doc.blocks!).
  * MTEXT \\pi/\\pl/\\pr paragraph indents: AutoCAD files store them in DRAWING UNITS,
    ezdxf multiplies by char_height -> rescale (auto-detected, --indent-units to force);
    single-paragraph first-line indents become insert-point shifts (exact, no wrap issues).
  * ezdxf PyMuPdfBackend mutates its recording on every replay -> subclass copies it per page.
  * white background, true colours (or --mono), absolute lineweights with a 0.1 mm floor,
    smooth curves, page size A0..A4 or WxH mm, orientation auto-matched to the frame.
"""
import argparse, collections, math, os, re, shutil, subprocess, sys, time
from pathlib import Path

import ezdxf
from ezdxf import recover
from ezdxf.fonts import fonts
from ezdxf.math import BoundingBox2d, Vec3
from ezdxf.addons.drawing import Frontend, RenderContext, layout, config
from ezdxf.addons.drawing import pymupdf as pdfbackend
import pymupdf
import arabic_reshaper
from bidi.algorithm import get_display

PAGES_MM = {"A0": (1189, 841), "A1": (841, 594), "A2": (594, 420), "A3": (420, 297), "A4": (297, 210)}
AR = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
CTRL = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")
# MTEXT inline codes; odd split indexes are codes, even are text
CODE_RE = re.compile(r"(\\[fF][^;]*;|\\p[^;]*;|\\[HWQCcTAS][^;]*;|\\U\+[0-9A-Fa-f]{4}|\\[PLlOoKkNX~\\{}]|[{}]|%%[a-zA-Z0-9]{1,3})")
PCODE = re.compile(r"\\p([^;]*);")
NUM = re.compile(r"-?\d+(?:\.\d+)?")
norm = lambda s: " ".join(CTRL.sub("", s).split())
stats = collections.Counter()


# ----------------------------------------------------------------------------- input
def find_dwg2dxf():
    for cand in [shutil.which("dwg2dxf"), os.environ.get("DWG2DXF"),
                 os.path.expanduser("~/.dwg2pdf-tools/mmenv/bin/dwg2dxf")]:
        if cand and os.access(cand, os.X_OK):
            return cand
    sys.exit("dwg2dxf not found - run scripts/setup.sh first")


def load_doc(path: Path, workdir: Path):
    if path.suffix.lower() == ".dwg":
        dxf = workdir / (path.stem + ".dxf")
        if not dxf.exists() or dxf.stat().st_mtime < path.stat().st_mtime:
            exe = find_dwg2dxf()
            print(f"converting with {exe} ...", flush=True)
            r = subprocess.run([exe, "-y", "-o", str(dxf), str(path)], capture_output=True, text=True)
            if not dxf.exists():
                sys.exit(f"dwg2dxf failed:\n{r.stderr[-2000:]}")
        path = dxf
    doc, auditor = recover.readfile(str(path))
    print(f"loaded {path.name}: DXF {doc.dxfversion}, {len(auditor.errors)} errors, {len(auditor.fixes)} fixes")
    return doc


# ----------------------------------------------------------------------------- frames
def rect_of(e):
    """(x0,y0,x1,y1) if entity is a closed axis-aligned rectangle, else None."""
    t = e.dxftype()
    if t == "LWPOLYLINE":
        pts = [(p[0], p[1]) for p in e.get_points("xy")]
        closed = e.closed
    elif t == "POLYLINE" and e.is_2d_polyline:
        pts = [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices]
        closed = e.is_closed
    else:
        return None
    if len(pts) == 5 and abs(pts[0][0] - pts[4][0]) < 1e-6 and abs(pts[0][1] - pts[4][1]) < 1e-6:
        pts = pts[:4]; closed = True
    if len(pts) != 4 or not closed:
        return None
    xs = sorted(p[0] for p in pts); ys = sorted(p[1] for p in pts)
    w, h = xs[-1] - xs[0], ys[-1] - ys[0]
    if w <= 0 or h <= 0:
        return None
    tol = 1e-3 * max(w, h)
    # axis aligned: every corner on the bbox edge
    for x, y in pts:
        if min(abs(x - xs[0]), abs(x - xs[-1])) > tol or min(abs(y - ys[0]), abs(y - ys[-1])) > tol:
            return None
    return (xs[0], ys[0], xs[-1], ys[-1])


def detect_frames(msp, args):
    if args.frames:
        boxes = [tuple(float(v) for v in f.split(",")) for f in args.frames.split(";")]
        return boxes if args.keep_order else sort_frames(boxes)
    ext = BoundingBox2d()
    rects = []
    for e in msp:
        if args.layer and e.dxf.layer != args.layer:
            continue
        r = rect_of(e)
        if r:
            rects.append(r)
    if not rects:
        sys.exit("no closed rectangles found - pass --frames 'x0,y0,x1,y1;...'")
    if args.frame_size:
        fw, fh = (float(v) for v in args.frame_size.lower().split("x"))
        tol = 0.02 * max(fw, fh)
        boxes = [r for r in rects if abs(r[2] - r[0] - fw) < tol and abs(r[3] - r[1] - fh) < tol]
    else:
        # group by rounded size; candidates = groups whose size is "sheet like" (big)
        maxw = max(r[2] - r[0] for r in rects); maxh = max(r[3] - r[1] for r in rects)
        groups = collections.defaultdict(list)
        for r in rects:
            w, h = r[2] - r[0], r[3] - r[1]
            if w < 0.25 * maxw and h < 0.25 * maxh:
                continue
            groups[(round(w / maxw, 2), round(h / maxh, 2))].append(r)
        # prefer the most frequent large size; ties -> larger area
        key = max(groups, key=lambda k: (len(groups[k]), k[0] * k[1]))
        boxes = groups[key]
        if len(boxes) == 1 and len(groups) > 1:
            print("note: only one rectangle of the dominant size; if sheets are nested borders use --frame-size")
    print(f"frames: {len(boxes)}  size ~{boxes[0][2]-boxes[0][0]:.3f} x {boxes[0][3]-boxes[0][1]:.3f} units")
    # drop rectangles fully inside another selected rectangle (inner border lines)
    boxes = [b for b in boxes if not any(o is not b and o[0] <= b[0] and o[1] <= b[1] and o[2] >= b[2] and o[3] >= b[3]
                                        and (o[2]-o[0])*(o[3]-o[1]) > 1.001*(b[2]-b[0])*(b[3]-b[1]) for o in boxes)]
    return sort_frames(boxes)


def sort_frames(boxes):
    # rows: top to bottom (y descending), within a row left to right
    h = max(b[3] - b[1] for b in boxes)
    boxes = sorted(boxes, key=lambda b: -b[1])
    rows, cur = [], [boxes[0]]
    for b in boxes[1:]:
        if abs(b[1] - cur[0][1]) < 0.5 * h:
            cur.append(b)
        else:
            rows.append(cur); cur = [b]
    rows.append(cur)
    out = []
    for row in rows:
        out.extend(sorted(row, key=lambda b: b[0]))
    return out


# ----------------------------------------------------------------------------- text
class TextFixer:
    def __init__(self, doc, flip_set, indent_units, shape=True):
        self.doc = doc
        self.flip = flip_set
        self.shape = shape
        self.indent_units = indent_units
        self.reshaper = arabic_reshaper.ArabicReshaper({"delete_harakat": False, "support_ligatures": True})
        self.pi_samples = []

    # -- Arabic -----------------------------------------------------------------
    def shape_piece(self, s, flip):
        s = CTRL.sub("", s)
        if flip:
            lead = s[:len(s) - len(s.lstrip())]; trail = s[len(s.rstrip()):]
            s = lead + " ".join(reversed(s.split())) + trail
            stats["flipped"] += 1
        stats["shaped"] += 1
        return get_display(self.reshaper.reshape(s))

    def paragraph(self, p):
        parts = CODE_RE.split(p)
        plain = norm("".join(parts[0::2]))
        flip = plain in self.flip
        for i in range(0, len(parts), 2):
            if AR.search(parts[i]):
                parts[i] = self.shape_piece(parts[i], flip)
        return "".join(parts)

    def mtext(self, raw):
        raw = raw.replace("^J", "\\P").replace("^M", "")
        if not self.shape or not AR.search(raw):
            return raw
        return "\\P".join(self.paragraph(p) for p in raw.split("\\P"))

    def plain(self, s):
        if not self.shape or not AR.search(s):
            return s
        return self.shape_piece(s, norm(s) in self.flip)

    # -- indents ----------------------------------------------------------------
    def collect_pi(self, e):
        for m in PCODE.finditer(e.text):
            mi = re.search(r"i(-?\d+(?:\.\d+)?)", m.group(1))
            if mi and e.dxf.width > 0:
                self.pi_samples.append((abs(float(mi.group(1))), e.dxf.width, e.dxf.char_height))

    def decide_indent_units(self):
        if self.indent_units != "auto":
            return self.indent_units
        if not self.pi_samples:
            return "height"
        over = sum(1 for v, w, h in self.pi_samples if v > 1.05 * w)        # impossible in drawing units
        ratio = sorted(v / w for v, w, h in self.pi_samples)[len(self.pi_samples) // 2]
        units = "height" if over > 0.1 * len(self.pi_samples) or ratio < 0.15 else "drawing"
        print(f"indent units: {units} (samples={len(self.pi_samples)}, median indent/width={ratio:.2f}, over-width={over})")
        return units

    def fix_indents(self, e, units):
        if units != "drawing" or "\\p" not in e.text:
            return
        h = e.dxf.char_height or 1.0
        m1 = re.fullmatch(r"\\pi(-?\d+(?:\.\d+)?);(.*)", e.text, flags=re.S)
        if m1 and "\\P" not in m1.group(2) and "\\p" not in m1.group(2):
            # single paragraph, first-line indent only -> shift the insert point instead
            d = float(m1.group(1))
            tdir = e.dxf.text_direction if e.dxf.hasattr("text_direction") else None
            if tdir is None or tdir.magnitude < 1e-9:
                r = math.radians(e.dxf.get("rotation", 0.0)); tdir = Vec3(math.cos(r), math.sin(r), 0)
            e.dxf.insert = e.dxf.insert + tdir.normalize() * d
            e.text = m1.group(2)
            stats["indent->shift"] += 1
            return
        max_indent = 0.0
        def repl(m):
            nonlocal max_indent
            body = m.group(1)
            mi = re.match(r"i(-?\d+(?:\.\d+)?)", body)
            if mi:
                max_indent = max(max_indent, float(mi.group(1)))
            return "\\p" + NUM.sub(lambda n: f"{float(n.group()) / h:g}", body) + ";"
        e.text = PCODE.sub(repl, e.text)
        if max_indent > 0 and e.dxf.attachment_point == 1 and e.dxf.width > 0:
            e.dxf.width += max_indent          # keep the indented first line from wrapping
            stats["widened"] += 1

    # -- driver -----------------------------------------------------------------
    def run(self):
        spaces = [self.doc.modelspace()] + [b for b in self.doc.blocks
                                            if not b.name.lower().startswith(("*model_space", "*paper_space"))]
        for sp in spaces:
            for e in sp:
                if e.dxftype() == "MTEXT":
                    self.collect_pi(e)
        units = self.decide_indent_units()
        for sp in spaces:
            for e in sp:
                t = e.dxftype()
                if t == "MTEXT":
                    self.fix_indents(e, units)
                    e.text = self.mtext(e.text); stats["mtext"] += 1
                elif t in ("TEXT", "ATTRIB", "ATTDEF"):
                    e.dxf.text = self.plain(e.dxf.text); stats["text"] += 1
                elif t == "INSERT":
                    for a in e.attribs:
                        a.dxf.text = self.plain(a.dxf.text)


def dump_arabic(doc):
    seen = collections.OrderedDict()
    for sp in [doc.modelspace()] + [b for b in doc.blocks if not b.name.lower().startswith(("*model_space", "*paper_space"))]:
        for e in sp:
            t = e.text if e.dxftype() == "MTEXT" else (e.dxf.text if e.dxftype() in ("TEXT", "ATTRIB", "ATTDEF") else "")
            if not t or not AR.search(t):
                continue
            for p in t.replace("^J", "\\P").split("\\P"):
                plain = norm("".join(CODE_RE.split(p)[0::2]))
                if plain and AR.search(plain):
                    seen[plain] = seen.get(plain, 0) + 1
    print(f"# {len(seen)} unique Arabic lines (stored order). Copy the ones whose WORD ORDER reads")
    print("# backwards into flip.txt (one per line); titles usually read fine, short labels often not.")
    for s, n in seen.items():
        print(f"{s}")
    return seen


# ----------------------------------------------------------------------------- fonts
def ensure_fonts(doc):
    fonts.load()
    fm = fonts.font_manager
    wanted = set()
    for st in doc.styles:
        f = (st.dxf.font or "").strip().lower()
        if f.endswith(".ttf"):
            wanted.add(f)
    for sp in [doc.modelspace()] + list(doc.blocks):
        for e in sp:
            if e.dxftype() == "MTEXT":
                for m in re.finditer(r"\\f([^|;]+)[|;]", e.text):
                    wanted.add(m.group(1).strip().lower().replace(" ", "") + ".ttf")
    missing = [f for f in wanted if not fm.has_font(f)]
    if missing:
        here = Path(__file__).resolve().parent
        print("building substitutes for missing fonts:", missing)
        subprocess.run([sys.executable, str(here / "make_fonts.py"), *missing], check=False)
        fonts.build_system_font_cache(); fonts.load()
    print("fonts ok; fallback =", fonts.font_manager.fallback_font_name())


# ----------------------------------------------------------------------------- render
class MultiPageBackend(pdfbackend.PyMuPdfBackend):
    """PyMuPdfBackend transforms/crops its recording in place on replay -> copy per page."""
    def player(self):
        return super().player().copy()

    def get_replay(self, page, *, settings=layout.Settings(), render_box=None):
        self._init_flip_y = True
        return super().get_replay(page, settings=settings, render_box=render_box)


def frame_title(msp, box):
    x0, y0, x1, y1 = box
    best = None
    for e in msp.query("MTEXT TEXT"):
        p = e.dxf.insert
        if x0 <= p.x <= x1 and y0 <= p.y <= y1:
            h = e.dxf.char_height if e.dxftype() == "MTEXT" else e.dxf.height
            if best is None or h > best[0]:
                raw = e.text if e.dxftype() == "MTEXT" else e.dxf.text
                plain = norm("".join(CODE_RE.split(raw.split("\\P")[0])[0::2]))
                best = (h, plain)
    return best[1] if best else ""


def render(doc, frames, args, titles):
    msp = doc.modelspace()
    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.WHITE,
        color_policy=config.ColorPolicy.MONOCHROME if args.mono else config.ColorPolicy.COLOR,
        lineweight_policy=config.LineweightPolicy.ABSOLUTE,
        min_lineweight=args.min_lw * 300 / 25.4,      # mm -> 1/300 inch
        lineweight_scaling=args.lw_scale,
        max_flattening_distance=0.002 * max(f[2] - f[0] for f in frames) / 30,
        circle_approximation_count=256,
        hatching_timeout=90.0,
    )
    backend = MultiPageBackend()
    Frontend(RenderContext(doc), backend, config=cfg).draw_layout(msp, finalize=True)

    out = pymupdf.open()
    toc = []
    previews = {int(v) for v in args.preview.split(",")} if args.preview else set()
    for i, box in enumerate(frames, 1):
        fw, fh = box[2] - box[0], box[3] - box[1]
        pw, ph = args.page_mm
        if args.orientation == "auto":
            if (fw >= fh) != (pw >= ph):
                pw, ph = ph, pw
        elif args.orientation == "landscape" and pw < ph or args.orientation == "portrait" and pw > ph:
            pw, ph = ph, pw
        page = layout.Page(pw, ph, layout.Units.mm, margins=layout.Margins.all(args.margin))
        settings = layout.Settings(fit_page=True, crop_at_margins=True,
                                   page_alignment=layout.PageAlignment.MIDDLE_CENTER)
        bb = BoundingBox2d([(box[0], box[1]), (box[2], box[3])])
        pdf = backend.get_pdf_bytes(page, settings=settings, render_box=bb)
        out.insert_pdf(pymupdf.open("pdf", pdf))
        toc.append([1, f"{i:02d} {titles[i-1]}".strip(), i])
        if i in previews:
            png = Path(args.output).with_suffix(f".p{i:02d}.png")
            png.write_bytes(backend.get_pixmap_bytes(page, fmt="png", settings=settings, render_box=bb, dpi=args.preview_dpi))
        print(f"  page {i}/{len(frames)} {titles[i-1]!r} ({len(pdf)//1024} KB)", flush=True)
    out.set_toc(toc)
    out.set_metadata({"title": Path(args.output).stem, "producer": "dwg2pdf_frames (ezdxf + PyMuPDF)"})
    out.save(args.output, garbage=3, deflate=True)
    return out.page_count


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="DWG or DXF")
    ap.add_argument("-o", "--output", help="output PDF (default: <input>_<page>.pdf)")
    ap.add_argument("--page", default="A2", help="A0..A4 or WxH in mm (default A2)")
    ap.add_argument("--orientation", default="auto", choices=["auto", "landscape", "portrait"])
    ap.add_argument("--margin", type=float, default=4.0, help="page margin in mm (default 4)")
    ap.add_argument("--mono", action="store_true", help="monochrome plot (like monochrome.ctb)")
    ap.add_argument("--min-lw", type=float, default=0.10, help="minimum line width in mm (default 0.10)")
    ap.add_argument("--lw-scale", type=float, default=1.0, help="lineweight scale factor")
    ap.add_argument("--frames", help="explicit frames 'x0,y0,x1,y1;x0,y0,x1,y1;...' (skips detection)")
    ap.add_argument("--keep-order", action="store_true", help="with --frames: keep the given order as page order")
    ap.add_argument("--frame-size", help="WxH of the frame rectangles in drawing units, e.g. 29.22x20.6")
    ap.add_argument("--layer", help="only consider rectangles on this layer for frame detection")
    ap.add_argument("--flip-file", help="text file: Arabic lines whose word order must be reversed")
    ap.add_argument("--no-shape", action="store_true", help="disable Arabic shaping/bidi (rarely wanted)")
    ap.add_argument("--indent-units", default="auto", choices=["auto", "drawing", "height"])
    ap.add_argument("--dump-arabic", action="store_true", help="print unique Arabic lines and exit")
    ap.add_argument("--list-frames", action="store_true", help="print detected frames and exit")
    ap.add_argument("--preview", help="comma separated page numbers to also write as PNG")
    ap.add_argument("--preview-dpi", type=int, default=60)
    ap.add_argument("--workdir", help="where the converted DXF goes (default: next to the input)")
    args = ap.parse_args()

    t0 = time.time()
    inp = Path(args.input).resolve()
    workdir = Path(args.workdir).resolve() if args.workdir else inp.parent
    workdir.mkdir(parents=True, exist_ok=True)
    if args.page.upper() in PAGES_MM:
        args.page_mm = PAGES_MM[args.page.upper()]
    else:
        args.page_mm = tuple(float(v) for v in args.page.lower().split("x"))
    args.output = args.output or str(inp.with_name(f"{inp.stem}_{args.page.upper()}.pdf"))

    doc = load_doc(inp, workdir)
    msp = doc.modelspace()
    if args.dump_arabic:
        dump_arabic(doc); return
    frames = detect_frames(msp, args)
    titles = [frame_title(msp, b) for b in frames]
    if args.list_frames:
        for i, (b, t) in enumerate(zip(frames, titles), 1):
            print(f"{i:02d}: x={b[0]:.3f}..{b[2]:.3f} y={b[1]:.3f}..{b[3]:.3f}  {t!r}")
        return
    flip = set()
    if args.flip_file:
        flip = {norm(l) for l in Path(args.flip_file).read_text(encoding="utf-8").splitlines() if norm(l) and not l.startswith("#")}
    ensure_fonts(doc)
    TextFixer(doc, flip, args.indent_units, shape=not args.no_shape).run()
    print("text:", dict(stats))
    n = render(doc, frames, args, titles)
    print(f"saved {args.output}: {n} pages, {os.path.getsize(args.output)//1024} KB, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
