import ezdxf
from ezdxf import recover
def load_fixed(path="einstein.dxf"):
    doc, aud = recover.readfile(path)
    styles = {s.dxf.name for s in doc.styles}
    for ds in doc.dimstyles:
        if ds.dxf.get("dimtxsty") and ds.dxf.dimtxsty not in styles:
            ds.dxf.dimtxsty = "Standard"
        for k in ("dimblk", "dimblk1", "dimblk2", "dimldrblk"):
            v = ds.dxf.get(k)
            if v and v not in doc.blocks:
                ds.dxf.set(k, "")
        if ds.dxf.get("dimltype") and ds.dxf.dimltype not in doc.linetypes: ds.dxf.dimltype = ""
        if ds.dxf.get("dimltex1") and ds.dxf.dimltex1 not in doc.linetypes: ds.dxf.dimltex1 = ""
        if ds.dxf.get("dimltex2") and ds.dxf.dimltex2 not in doc.linetypes: ds.dxf.dimltex2 = ""
    a = doc.audit()
    return doc
if __name__ == "__main__":
    doc = load_fixed(); doc.saveas("einstein_fixed.dxf"); print("saved einstein_fixed.dxf")
