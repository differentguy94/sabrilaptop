# We Chicks (Oct 2026): filling the engineer's own 28 pre-made frames in place
wlib.Sheet(in_place=True) deletes old DIMENSION entities per frame and draws discipline content with its own dims;
point_dims() chains dims point-to-point and to wall corners. Two extra columns copied from the base frames.
Run: python3 wbuild.py --out wechicks_all (plot) ; python3 wfinal.py (TOC, split, DWG copy). Stray diagonal lines and
surrogate chars in the source file must be removed before ODA conversion.
