"""shared layout for the We Chicks sheets"""
from wlib import point_dims, table
from wmodel import G, M
# ground: legend top-right, notes right, tables on the free left strip ; mezzanine: narrow right strip + bottom-right
LEG_G = (20.4, 54.7, 7.2); NOTE_G = (27.6, 45.2, 7.2); TAB_G = (-3.4, 54.7)
LEG_M = (24.0, 28.9, 3.8); NOTE_M = (27.8, 16.0, 4.0); TAB_M = (24.0, 21.5)
ROOMS_G = [G["hall"], G["kitchen"], G["dish"], G["prep"], (12.9, 49.0, 14.4, 50.6)]
ROOMS_M = [M["seating"], M["corridor"], M["wc_men"], M["wc_lobby"], M["wc_women"], M["wc_staff"], M["freezer_room"], (15.6, 25.0, 18.0, 28.3),
           M["store"], M["open_office"], M["exec_office"], M["mgr_office"], M["server"], M["meeting"], M["void"], M["service"]]
def dims_G(s, pts): point_dims(s, pts, ROOMS_G, outside=G["wall"], override={"B": 37.6})
def dims_M(s, pts): point_dims(s, pts, ROOMS_M, outside=M["wall"], override={"B": 10.5, "T": 27.6})
def legend(s, floor, title, rows):
    x, y, w = LEG_G if floor == "G" else LEG_M
    return s.legend(x, y, title, rows, w=w, rh=0.5 if floor == "G" else 0.56, h=0.12 if floor == "G" else 0.1)
def notes(s, floor, lines, title):
    x, y, w = NOTE_G if floor == "G" else NOTE_M
    s.notes(x, y, lines, title=title, w=w, h=0.13 if floor == "G" else 0.11)
def sched(s, floor, title, header, rows, widths=None, y=None):
    if floor == "G":
        x, y0 = TAB_G; widths = widths or [1.6, 5.4, 1.1]; rh, h = 0.36, 0.12
    else:
        x, y0 = TAB_M; widths = widths or [0.8, 2.4, 0.6]; rh, h = 0.42, 0.095
    return table(s, x, y if y is not None else y0, title, header, rows, widths, rh=rh, h=h)
def head(s, floor, text):
    if floor == "G": s.text(2.0, 54.7, text, h=0.14, attach=1, color=7, layer="NOTES", width=12)
    else: s.text(-3.6, 29.1, text, h=0.12, attach=1, color=7, layer="NOTES", width=20)
def rect_label(s, r, txt, h=0.11, color=None, dy=0.0):
    s.label((r[0] + r[2]) / 2, (r[1] + r[3]) / 2 + dy, txt, h=h, color=color)
