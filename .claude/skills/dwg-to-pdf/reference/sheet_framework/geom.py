"""Extract a site model from the base plan: walls, equipment/furniture clusters, labels, doors, columns."""
import ezdxf, re, json, collections, math
from ezdxf import recover
from ezdxf.math import Vec3
doc, _ = recover.readfile("einstein.dxf"); msp = doc.modelspace()
FRAMES = {"G": (3.446, 23.050, 35.131, 45.392), "M": (3.446, -1.903, 35.131, 20.439)}
def frame_of(x, y):
    for k, f in FRAMES.items():
        if f[0]-0.3 <= x <= f[2]+0.3 and f[1]-0.3 <= y <= f[3]+0.3: return k
    return None
def ent_bbox(e):
    t = e.dxftype()
    try:
        if t == "LINE": pts = [e.dxf.start, e.dxf.end]
        elif t == "LWPOLYLINE": pts = [Vec3(p[0], p[1], 0) for p in e.get_points("xy")]
        elif t == "POLYLINE": pts = [v.dxf.location for v in e.vertices]
        elif t in ("CIRCLE", "ARC"):
            c, r = e.dxf.center, e.dxf.radius; pts = [Vec3(c.x-r, c.y-r, 0), Vec3(c.x+r, c.y+r, 0)]
        elif t == "ELLIPSE":
            c = e.dxf.center; r = e.dxf.major_axis.magnitude; pts = [Vec3(c.x-r, c.y-r, 0), Vec3(c.x+r, c.y+r, 0)]
        elif t == "INSERT":
            from ezdxf.bbox import extents
            bb = extents([e], fast=True)
            if not bb.has_data: return None
            pts = [bb.extmin, bb.extmax]
        elif t == "HATCH":
            pts = [Vec3(v[0], v[1], 0) for p in e.paths for v in getattr(p, "vertices", [])]
            if not pts: return None
        elif t == "SPLINE": pts = [Vec3(p) for p in e.control_points]
        else: return None
    except Exception: return None
    xs = [p.x for p in pts]; ys = [p.y for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))
# ---- collect by frame & category
cats = collections.defaultdict(list)   # (frame, category) -> list of bbox
LAYCAT = {"block works": "wall", "WALL": "wall", "02-GROUND FLOOR PLAN$0$AW-PLN-PRO": "shell", "COLUMNS AND AXIS BASEMENT TO MEZZANINE$0$AW-STR-PRO 4TH 5TH 6TH": "column",
          "COLUMNS AND AXIS BASEMENT TO MEZZANINE$0$AW-STR-PRO BASEMENT only": "column", "COLUMNS AND AXIS BASEMENT TO MEZZANINE$0$AW-STR-PRO-ALL": "column", "COLUMNS AND AXIS BASEMENT TO MEZZANINE$0$AW-STR-PRO 4TH": "column",
          "02-GROUND FLOOR PLAN$0$AW-CUR-GLS": "glass", "02-GROUND FLOOR PLAN$0$AW-CUR": "glass", "02-GROUND FLOOR PLAN$0$AW-DOR-PLN": "door", "02-GROUND FLOOR PLAN$0$AW-DOR-HID": "door", "DOOR": "door",
          "مطبخ": "kitchen", "Kıtc-002 Çizg": "kitchen", "معدات": "kitchen", "FIX": "fixture", "X-IN-MF-1000$0$I-WC-NEWW": "wc", "02-GROUND FLOOR PLAN$0$AW-PLN-EL3": "el3", "02-GROUND FLOOR PLAN$0$AW-SEC-FIN": "fin"}
walls = {"G": [], "M": []}
for e in msp:
    bb = ent_bbox(e)
    if bb is None: continue
    cx, cy = (bb[0]+bb[2])/2, (bb[1]+bb[3])/2
    f = frame_of(cx, cy)
    if not f: continue
    lay = e.dxf.layer; col = e.dxf.color; t = e.dxftype()
    cat = LAYCAT.get(lay)
    if cat is None:
        if lay == "0" and col == 32 and t in ("LINE", "ARC", "LWPOLYLINE"): cat = "furniture"
        elif lay == "0" and col in (251, 252) and t in ("LINE", "ARC", "LWPOLYLINE"): cat = "grey"
        elif lay == "0" and col == 114: cat = "green"
        elif lay == "0" and col == 256 and t in ("LINE", "LWPOLYLINE"): cat = "line0"
        elif t == "INSERT": cat = "insert:" + e.dxf.name[:20]
        elif t == "HATCH": cat = "hatch"
        elif t == "DIMENSION": cat = "dim"
        elif t in ("MTEXT", "TEXT"): cat = "text"
        else: cat = f"other:{t}:{lay}:{col}"
    cats[(f, cat)].append(bb)
    if cat == "wall" and t == "LINE":
        s, q = e.dxf.start, e.dxf.end
        if (s - q).magnitude > 0.3: walls[f].append((round(s.x,2), round(s.y,2), round(q.x,2), round(q.y,2)))
print("CATEGORY COUNTS:")
for k in sorted(cats): print("  ", k, len(cats[k]), "extent", tuple(round(v,1) for v in (min(b[0] for b in cats[k]), min(b[1] for b in cats[k]), max(b[2] for b in cats[k]), max(b[3] for b in cats[k]))))
# ---- cluster furniture / kitchen bboxes into pieces (gap < 0.12)
def cluster(bbs, gap=0.12):
    bbs = sorted(bbs); groups = []
    for b in bbs:
        merged = None
        for g in groups:
            if b[0] <= g[2]+gap and b[2] >= g[0]-gap and b[1] <= g[3]+gap and b[3] >= g[1]-gap:
                g[0]=min(g[0],b[0]); g[1]=min(g[1],b[1]); g[2]=max(g[2],b[2]); g[3]=max(g[3],b[3]); g[4]+=1; merged = g; break
        if merged is None: groups.append([b[0],b[1],b[2],b[3],1])
    # second pass merge
    changed = True
    while changed:
        changed = False
        for i in range(len(groups)):
            for j in range(i+1, len(groups)):
                a, b = groups[i], groups[j]
                if a[0] <= b[2]+gap and a[2] >= b[0]-gap and a[1] <= b[3]+gap and a[3] >= b[1]-gap:
                    a[0]=min(a[0],b[0]); a[1]=min(a[1],b[1]); a[2]=max(a[2],b[2]); a[3]=max(a[3],b[3]); a[4]+=b[4]; groups.pop(j); changed = True; break
            if changed: break
    return groups
labels = []
for e in msp.query("MTEXT TEXT"):
    raw = e.text if e.dxftype()=="MTEXT" else e.dxf.text
    plain = re.sub(r"\\[A-Za-z][^;]*;|[{}]", "", raw).replace("\\P", " ").strip()
    f = frame_of(e.dxf.insert.x, e.dxf.insert.y)
    if f and plain: labels.append((f, round(e.dxf.insert.x,2), round(e.dxf.insert.y,2), plain))
site = {"frames": FRAMES, "walls": walls, "labels": labels, "clusters": {}}
for f in ("G", "M"):
    for cat in ("kitchen", "furniture", "wc", "fixture", "column", "door", "glass", "green", "grey"):
        gs = cluster(cats.get((f, cat), []), gap=0.15 if cat != "furniture" else 0.08)
        gs = [g for g in gs if (g[2]-g[0]) > 0.15 or (g[3]-g[1]) > 0.15]
        site["clusters"][f"{f}:{cat}"] = [[round(v,2) for v in g[:4]] + [g[4]] for g in gs]
        print(f"\n{f} {cat}: {len(gs)} clusters")
        for g in sorted(gs, key=lambda g: (-g[1], g[0]))[:60]:
            near = min(((math.hypot((g[0]+g[2])/2-l[1], (g[1]+g[3])/2-l[2]), l[3]) for l in labels if l[0]==f), default=(99,""))
            print(f"   [{g[0]:6.2f},{g[1]:6.2f} -> {g[2]:6.2f},{g[3]:6.2f}] w={g[2]-g[0]:.2f} h={g[3]-g[1]:.2f} n={g[4]:3d}  near={near[1][:30]!r}@{near[0]:.1f}")
json.dump(site, open("site.json", "w"), ensure_ascii=False, indent=1)
print("\nWALL segments G:", len(walls["G"]), "M:", len(walls["M"]))
