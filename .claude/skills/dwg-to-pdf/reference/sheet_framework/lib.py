"""Drawing helpers for the Einstein Burger discipline sheets (ezdxf).
Coordinates are the ORIGINAL frame coordinates of each floor (as in the gridded PNGs):
 ground floor frame  x 3.45..35.13, y 23.05..45.39 ; mezzanine frame y -1.90..20.44.
Sheet.* methods add the column offset automatically."""
import math, re, datetime
import ezdxf
from ezdxf.math import Vec3, BoundingBox2d
from ezdxf.bbox import extents

FRAME = {"G": (3.446, 23.050, 35.131, 45.392), "M": (3.446, -1.903, 35.131, 20.439)}
COL_STEP = 35.0
LW = 20
TODAY = datetime.date.today().strftime("%d / %m / %Y")
CODES = re.compile(r"\\[A-Za-z][^;]*;|[{}]")

LAYERS = {  # name: color
    "E-POWER": 5, "P-PLUMB": 40, "M-HVAC": 6, "G-GAS": 30, "M-EXHAUST": 1, "E-CCTV": 4, "E-SPEAKER": 4,
    "E-INSECT": 146, "E-FRESH": 4, "A-FLOOR": 3, "E-LIGHT": 6, "A-CEILING": 6, "A-WALL": 3, "A-FURN": 32,
    "A-FACADE": 7, "LEGEND": 7, "NOTES": 7, "F-FIRE": 244,
}


class Ctx:
    def __init__(self, doc):
        self.doc = doc
        self.msp = doc.modelspace()
        for n, c in LAYERS.items():
            if n not in doc.layers:
                doc.layers.add(n, color=c)
        self._purge_strays()
        self._drop_mtext_columns()
        self.src = {f: self._collect(f) for f in ("G", "M")}

    def _drop_mtext_columns(self):
        """AutoCAD dynamic-column MTEXT (title texts) flows into a 2nd column in ezdxf when the
        defined height is smaller than the text -> make them plain single-column texts."""
        n = 0
        for e in self.msp.query("MTEXT"):
            if e.has_columns:
                e._columns = None
                e.dxf.defined_height = 0.0
                if e.has_xdata("ACAD"):
                    e.discard_xdata("ACAD")
                n += 1
        print(f"dropped column data from {n} MTEXT entities")

    @staticmethod
    def anchor(e):
        """representative point: MTEXT insert (+ first-line indent, which AutoCAD stores in drawing
        units in these files), TEXT insert, DIMENSION text point, otherwise the fast bbox centre."""
        t = e.dxftype()
        try:
            if t == "MTEXT":
                p = e.dxf.insert
                m = re.match(r"\\pi(-?\d+(?:\.\d+)?);", e.text)
                if m:
                    d = e.dxf.text_direction if e.dxf.hasattr("text_direction") else Vec3(1, 0, 0)
                    if d.magnitude < 1e-9:
                        d = Vec3(1, 0, 0)
                    p = p + d.normalize() * float(m.group(1))
                return p
            if t in ("TEXT", "ATTRIB"):
                return e.dxf.insert
            if t == "DIMENSION":
                return e.dxf.get("text_midpoint", None) or e.dxf.defpoint
        except Exception:
            pass
        bb = extents([e], fast=True)
        return bb.center if bb.has_data else None

    @staticmethod
    def inside(p, floor, margin=0.2):
        x0, y0, x1, y1 = FRAME[floor]
        return x0 - margin <= p.x <= x1 + margin and y0 - margin <= p.y <= y1 + margin

    def _purge_strays(self):
        """delete leftover entities lying outside both frames (old template garbage)"""
        n = 0
        for e in list(self.msp):
            p = self.anchor(e)
            if p is None:
                continue
            if not (self.inside(p, "G") or self.inside(p, "M")):
                e.destroy(); n += 1
        print(f"purged {n} stray entities outside the frames")

    def _collect(self, floor):
        out = []
        for e in list(self.msp):
            p = self.anchor(e)
            if p is not None and self.inside(p, floor):
                out.append(e)
        return out


class Sheet:
    """One A2 frame: a translated copy of the floor's base plan + discipline content."""

    def __init__(self, ctx, floor, col, title, layer, color=None, date=TODAY, copy_base=True):
        self.ctx, self.msp, self.floor, self.col = ctx, ctx.msp, floor, col
        self.dx = col * COL_STEP
        self.layer, self.color = layer, (LAYERS[layer] if color is None else color)
        self.frame = FRAME[floor]
        self.title = title
        self.copy_mode = copy_base
        if copy_base:
            self._copy_base(title, date)

    # ------------------------------------------------------------ base plan copy
    def _copy_base(self, title, date):
        fx0, fy0, fx1, fy1 = self.frame
        self.copied = []
        for e in self.ctx.src[self.floor]:
            if self.copy_mode == "frame":      # title block strip + frame rectangle only
                bb = extents([e], fast=True)
                big = bb.has_data and (bb.size.x > 30 and bb.size.y > 20)
                if not big and bb.has_data and bb.extmax.y > fy0 + 3.6:
                    continue
            try:
                c = e.copy()
            except Exception:
                continue
            self.msp.add_entity(c)
            self.copied.append(c)
            try:
                c.translate(self.dx, 0, 0)
            except Exception:
                pass
            if c.dxftype() == "MTEXT":
                plain = CODES.sub("", c.text)
                m = re.match(r"(\\pi[^;]*;)", c.text)
                prefix = m.group(1) if m else ""
                if "مخطط المحل" in plain and c.dxf.char_height > 0.4:
                    c.text = prefix + title
                    c.dxf.defined_height = 0.0      # a defined height < text height makes ezdxf flow into a 2nd column
                    c._columns = None               # drop AutoCAD dynamic-column data (renders the text in column 2)
                    if c.has_xdata("ACAD"):
                        c.discard_xdata("ACAD")
                elif plain.startswith("DATE"):
                    c.text = prefix + f"DATE : {date}"

    def erase_plan(self):
        """remove the copied plan content, keep the frame rectangle and the title block strip"""
        fx0, fy0, fx1, fy1 = self.frame
        keep = []
        for c in getattr(self, "copied", []):
            bb = extents([c], fast=True)
            big = bb.has_data and (bb.size.x > 30 and bb.size.y > 20)
            if bb.has_data and bb.extmax.y > fy0 + 3.6 and not big:
                c.destroy()
            else:
                keep.append(c)
        self.copied = keep

    # ------------------------------------------------------------ primitives
    def P(self, x, y):
        return (x + self.dx, y)

    def attribs(self, color=None, layer=None, lw=LW, **kw):
        d = {"layer": layer or self.layer, "color": self.color if color is None else color, "lineweight": lw}
        d.update(kw)
        return d

    def line(self, p1, p2, color=None, lw=LW, linetype=None, layer=None):
        a = self.attribs(color, layer, lw)
        if linetype: a["linetype"] = linetype
        return self.msp.add_line(self.P(*p1), self.P(*p2), dxfattribs=a)

    def pline(self, pts, closed=False, color=None, lw=LW, width=0.0, linetype=None, layer=None):
        a = self.attribs(color, layer, lw)
        if linetype: a["linetype"] = linetype
        pl = self.msp.add_lwpolyline([self.P(*p) for p in pts], format="xy", close=closed, dxfattribs=a)
        if width:
            pl.dxf.const_width = width
        return pl

    def rect(self, x0, y0, x1, y1, color=None, lw=LW, width=0.0, layer=None):
        return self.pline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True, color=color, lw=lw, width=width, layer=layer)

    def circle(self, x, y, r, color=None, lw=LW, layer=None):
        return self.msp.add_circle(self.P(x, y), r, dxfattribs=self.attribs(color, layer, lw))

    def arc(self, x, y, r, a0, a1, color=None, lw=LW, layer=None):
        return self.msp.add_arc(self.P(x, y), r, a0, a1, dxfattribs=self.attribs(color, layer, lw))

    def dot(self, x, y, r, color=None, layer=None):
        """solid filled circle (circle + SOLID hatch)"""
        self.circle(x, y, r, color, layer=layer)
        h = self.msp.add_hatch(color=self.color if color is None else color, dxfattribs={"layer": layer or self.layer})
        h.paths.add_edge_path().add_arc(self.P(x, y), r, 0, 360)
        return h

    def hatch(self, pts, pattern="SOLID", scale=1.0, color=None, angle=0.0, layer=None, transparency=None):
        h = self.msp.add_hatch(color=self.color if color is None else color, dxfattribs={"layer": layer or self.layer})
        if pattern == "SOLID":
            h.set_solid_fill(color=self.color if color is None else color)
        else:
            h.set_pattern_fill(pattern, color=self.color if color is None else color, scale=scale, angle=angle)
        h.paths.add_polyline_path([self.P(*p) for p in pts], is_closed=True)
        if transparency is not None:
            h.transparency = transparency
        return h

    def text(self, x, y, s, h=0.15, color=None, attach=1, width=0, rotation=0.0, layer=None, bold=False):
        a = {"layer": layer or self.layer, "color": self.color if color is None else color, "char_height": h,
             "attachment_point": attach, "rotation": rotation}
        if width: a["width"] = width
        m = self.msp.add_mtext(s, dxfattribs=a)
        m.set_location(self.P(x, y), attachment_point=attach)
        return m

    def label(self, x, y, s, h=0.12, color=None, rotation=0.0, layer=None):
        """centered label"""
        return self.text(x, y, s, h, color, attach=5, rotation=rotation, layer=layer)

    def dim(self, p1, p2, offset=0.6, color=3, h=0.12, horizontal=True):
        """linear dimension between p1 and p2 (frame coords)."""
        x1, y1 = p1; x2, y2 = p2
        if horizontal:
            base = (x1, max(y1, y2) + offset)
            angle = 0
        else:
            base = (max(x1, x2) + offset, y1)
            angle = 90
        d = self.msp.add_linear_dim(base=self.P(*base), p1=self.P(x1, y1), p2=self.P(x2, y2), angle=angle,
                                    dimstyle="A - dim int", dxfattribs={"layer": self.layer, "color": color},
                                    override={"dimtxt": h, "dimasz": 0.08, "dimclrd": color, "dimclre": color,
                                              "dimclrt": color, "dimexe": 0.05, "dimexo": 0.05, "dimdec": 2,
                                              "dimtad": 1, "dimgap": 0.03, "dimblk": "ARCHTICK", "dimtxsty": "Standard"})
        d.render()
        return d

    def leader(self, pts, color=None):
        return self.pline(pts, color=color, lw=13)

    # ------------------------------------------------------------ compound symbols
    def elec_point(self, x, y, letter="P", r=0.54, note=None):
        """power point in the user's style: big circle + solid dot + letter"""
        self.circle(x, y, r)
        self.dot(x, y, 0.112)
        self.text(x - 0.06, y - 0.16, letter, h=0.194)
        if note:
            self.text(x + r * 0.7, y + r * 0.7, note, h=0.09)

    def floor_drain(self, x, y, size=0.22):
        s = size / 2
        self.rect(x - s, y - s, x + s, y + s, lw=13)
        self.line((x - s, y - s), (x + s, y + s), lw=13); self.line((x - s, y + s), (x + s, y - s), lw=13)
        self.text(x + s + 0.03, y + s, "F/D", h=0.10)

    def water_point(self, x, y, kind="C"):
        """C cold, H hot, CH both"""
        col = {"C": 150, "H": 1, "CH": 40}[kind]
        self.circle(x, y, 0.10, color=col, lw=13)
        self.dot(x, y, 0.04, color=col)
        self.text(x + 0.12, y + 0.12, kind, h=0.09, color=col)

    def valve(self, x, y, size=0.16, color=None, rot=0.0):
        s = size / 2; c = math.cos(math.radians(rot)); n = math.sin(math.radians(rot))
        def R(px, py): return (x + px * c - py * n, y + px * n + py * c)
        self.pline([R(-s, -s * 0.7), R(s, s * 0.7), R(s, -s * 0.7), R(-s, s * 0.7)], closed=True, color=color, lw=13)

    def camera(self, x, y, rot=0.0, cone=True, r_cone=3.0, span=70):
        """CCTV camera: body + lens + dashed coverage cone"""
        c = math.cos(math.radians(rot)); n = math.sin(math.radians(rot))
        def R(px, py): return (x + px * c - py * n, y + px * n + py * c)
        self.pline([R(-0.25, -0.15), R(0.15, -0.15), R(0.15, 0.15), R(-0.25, 0.15)], closed=True)
        self.pline([R(0.15, -0.10), R(0.35, -0.18), R(0.35, 0.18), R(0.15, 0.10)], closed=True)
        self.dot(x, y, 0.05)
        if cone:
            a0, a1 = rot - span / 2, rot + span / 2
            self.arc(x, y, r_cone, a0, a1, lw=5)
            for a in (a0, a1):
                self.line((x, y), (x + r_cone * math.cos(math.radians(a)), y + r_cone * math.sin(math.radians(a))), lw=5, linetype="DASHED")

    def speaker(self, x, y, r=0.35, cover=2.4):
        self.dot(x, y, r * 0.45)
        self.circle(x, y, r)
        if cover:
            self.circle(x, y, cover, lw=5)

    def device_dot(self, x, y, r=0.35, cover=0.0, letter=None):
        """generic device: solid dot + ring (+ coverage ring)"""
        self.dot(x, y, r * 0.5)
        self.circle(x, y, r)
        if cover:
            self.circle(x, y, cover, lw=5)
        if letter:
            self.text(x + r + 0.05, y + r, letter, h=0.12)

    def spot(self, x, y, s=0.09):
        """spot/track head (user's style): square + two circles + tick"""
        self.rect(x - s, y - s, x + s, y + s)
        self.circle(x, y, 0.083); self.circle(x, y, 0.039)
        self.line((x, y + 0.04), (x, y - 0.04))

    def track(self, pts, heads=None, width=0.05):
        """lighting track (thick polyline) with spot heads at given points"""
        self.pline(pts, width=width, color=250)
        for hx, hy in (heads or []):
            self.spot(hx, hy)

    def pendant(self, x, y, r=0.18):
        self.circle(x, y, r); self.circle(x, y, r * 0.35)
        self.line((x - r, y), (x + r, y), lw=9); self.line((x, y - r), (x, y + r), lw=9)

    def globe(self, x, y, r=0.12):
        self.circle(x, y, r); self.dot(x, y, r * 0.5, color=2)

    def led_panel(self, x, y, w=0.6, h=0.6):
        self.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        self.line((x - w / 2, y - h / 2), (x + w / 2, y + h / 2), lw=9); self.line((x - w / 2, y + h / 2), (x + w / 2, y - h / 2), lw=9)

    def downlight(self, x, y, r=0.10):
        self.circle(x, y, r); self.dot(x, y, r * 0.4)

    def strip(self, p1, p2, width=0.06, color=2):
        self.pline([p1, p2], width=width, color=color)

    def cassette(self, x, y, size=1.0):
        """4-way cassette AC (user's style)"""
        s = size / 2; t = size * 0.09
        self.rect(x - s, y - s, x + s, y + s)
        self.rect(x - s + t * 0.4, y - s + t * 1.2, x - s + t * 1.4, y + s - t * 1.2)
        self.rect(x + s - t * 1.4, y - s + t * 1.2, x + s - t * 0.4, y + s - t * 1.2)
        self.rect(x - s + t * 1.6, y + s - t * 1.4, x + s - t * 1.6, y + s - t * 0.4)
        self.rect(x - s + t * 1.6, y - s + t * 0.4, x + s - t * 1.6, y - s + t * 1.4)
        self.text(x, y, "AC", h=0.12, attach=5)

    def split_unit(self, x, y, w=0.9, h=0.25, rot=0.0):
        c = math.cos(math.radians(rot)); n = math.sin(math.radians(rot))
        def R(px, py): return (x + px * c - py * n, y + px * n + py * c)
        self.pline([R(-w / 2, -h / 2), R(w / 2, -h / 2), R(w / 2, h / 2), R(-w / 2, h / 2)], closed=True)
        for k in (-0.25, 0.0, 0.25):
            self.line(R(-w / 2 + 0.1, k * h), R(w / 2 - 0.1, k * h), lw=9)

    def outdoor_unit(self, x, y, w=0.9, h=0.35, label="ODU"):
        self.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        self.circle(x, y, h * 0.4)
        self.text(x, y - h / 2 - 0.05, label, h=0.11, attach=2)

    def duct(self, pts, w=0.4, color=None, diffusers=(), grille_size=0.5, label=None):
        """rectangular duct as double line along pts; diffusers: list of (x,y)"""
        from ezdxf.math import offset_vertices_2d
        v = [Vec3(*self.P(*p)) for p in pts]
        for side in (w / 2, -w / 2):
            off = list(offset_vertices_2d(v, offset=side, closed=False))
            self.msp.add_lwpolyline([(p.x, p.y) for p in off], format="xy", dxfattribs=self.attribs(color))
        # end caps
        for a, b in ((v[0], v[1]), (v[-1], v[-2])):
            d = (b - a).normalize(); nrm = Vec3(-d.y, d.x, 0) * (w / 2)
            self.msp.add_line(a + nrm, a - nrm, dxfattribs=self.attribs(color))
        for (x, y) in diffusers:
            self.diffuser(x, y, grille_size)
        if label:
            mid = v[len(v) // 2]
            self.msp.add_mtext(label, dxfattribs={"layer": self.layer, "color": self.color if color is None else color, "char_height": 0.11, "attachment_point": 5}).set_location(mid + Vec3(0, w / 2 + 0.15, 0), attachment_point=5)

    def diffuser(self, x, y, s=0.5):
        h = s / 2
        self.rect(x - h, y - h, x + h, y + h)
        self.rect(x - h * 0.55, y - h * 0.55, x + h * 0.55, y + h * 0.55, lw=9)
        self.line((x - h, y - h), (x + h, y + h), lw=5); self.line((x - h, y + h), (x + h, y - h), lw=5)

    def grille(self, x, y, w=0.6, h=0.3, rot=0.0):
        c = math.cos(math.radians(rot)); n = math.sin(math.radians(rot))
        def R(px, py): return (x + px * c - py * n, y + px * n + py * c)
        self.pline([R(-w / 2, -h / 2), R(w / 2, -h / 2), R(w / 2, h / 2), R(-w / 2, h / 2)], closed=True)
        k = 5
        for i in range(1, k):
            t = -w / 2 + w * i / k
            self.line(R(t, -h / 2), R(t, h / 2), lw=5)

    def fan(self, x, y, r=0.3, label=None):
        self.circle(x, y, r)
        for a in (45, 135, 225, 315):
            self.line((x, y), (x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))))
        self.dot(x, y, r * 0.2)
        if label:
            self.text(x, y - r - 0.05, label, h=0.11, attach=2)

    def gas_point(self, x, y, label=None):
        self.circle(x, y, 0.12, lw=13)
        self.text(x, y, "G", h=0.11, attach=5)
        if label:
            self.text(x + 0.15, y + 0.15, label, h=0.09)

    def cylinder(self, x, y, r=0.2):
        self.circle(x, y, r); self.circle(x, y, r * 0.3, lw=9)

    def box_label(self, x, y, s, h=0.14, w=None, color=None, fill=None):
        """text with a surrounding box (notes)"""
        lines = s.count("\\P") + 1
        tw = w or max(len(t) for t in s.split("\\P")) * h * 0.55 + 0.3
        th = lines * h * 1.6 + 0.2
        if fill is not None:
            self.hatch([(x, y - th), (x + tw, y - th), (x + tw, y), (x, y)], color=fill, layer="LEGEND")
        self.rect(x, y - th, x + tw, y, color=color)
        self.text(x + tw / 2, y - th / 2, s, h=h, attach=5, color=color, width=tw - 0.1)
        return tw, th

    # ------------------------------------------------------------ legend table
    def legend(self, x, y, title, rows, w=6.6, rh=0.5, col_sym=1.0, h=0.13):
        """rows: list of (draw_fn(sheet, cx, cy), arabic_text, english_text). Draws downward from (x,y)."""
        n = len(rows)
        th = 0.5
        H = th + n * rh
        self.rect(x, y - H, x + w, y, color=7, layer="LEGEND")
        self.hatch([(x, y - th), (x + w, y - th), (x + w, y), (x, y)], color=254, layer="LEGEND")
        self.text(x + w / 2, y - th / 2, title, h=0.2, attach=5, color=7, layer="LEGEND")
        self.line((x + col_sym, y - th), (x + col_sym, y - H), color=7, layer="LEGEND")
        for i, (fn, ar, en) in enumerate(rows):
            cy = y - th - rh * (i + 0.5)
            self.line((x, cy - rh / 2), (x + w, cy - rh / 2), color=7, lw=5, layer="LEGEND")
            fn(self, x + col_sym / 2, cy)
            if en:
                self.text(x + w - 0.12, cy + rh * 0.27, ar, h=h, attach=6, color=7, layer="LEGEND", width=w - col_sym - 0.2)
                self.text(x + w - 0.12, cy - rh * 0.22, en, h=h * 0.75, attach=6, color=8, layer="LEGEND", width=w - col_sym - 0.2)
            else:
                self.text(x + w - 0.12, cy + 0.02, ar, h=h, attach=6, color=7, layer="LEGEND", width=w - col_sym - 0.2)
        return H

    def notes(self, x, y, lines, h=0.14, w=7.5, title=None):
        """numbered Arabic notes block (right aligned), drawn downward from (x,y) = top-right corner"""
        yy = y
        if title:
            self.text(x, yy, title, h=h * 1.3, attach=3, color=7, layer="NOTES"); yy -= h * 2.2
        for i, s in enumerate(lines, 1):
            self.text(x, yy, f"{s} -{i}", h=h, attach=3, color=7, layer="NOTES", width=w)
            yy -= h * 1.9
        return y - yy


def sheet_box(floor, col):
    x0, y0, x1, y1 = FRAME[floor]
    return (x0 + col * COL_STEP, y0, x1 + col * COL_STEP, y1)
