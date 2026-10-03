"""Cover / index sheet: list of all drawings with page numbers."""
LAYER = "LEGEND"
ROWS = []   # filled by build.py: (page, title, floor)

def draw_G(s):
    s.erase_plan()
    s.text(19.3, 44.1, "EINSTEIN BURGER - مطعم اينشتاين بورجر", h=0.8, attach=5, color=7)
    s.text(19.3, 43.0, "المخططات التنفيذية: الطابق الأرضي + الميزانين", h=0.4, attach=5, color=7)
    s.text(19.3, 42.3, "ARCHITECTURAL / MEP WORKING DRAWINGS SET - A2", h=0.26, attach=5, color=8)
    x0, y0 = 8.0, 41.6
    w, rh = 22.6, 0.40
    cols = (1.6, 14.0, 7.0)      # page, title, floor
    n = len(ROWS)
    s.rect(x0, y0 - rh * (n + 1), x0 + w, y0, color=7, lw=35)
    s.hatch([(x0, y0 - rh), (x0 + w, y0 - rh), (x0 + w, y0), (x0, y0)], color=254)
    s.text(x0 + cols[0] / 2, y0 - rh / 2, "رقم", h=0.2, attach=5, color=7)
    s.text(x0 + cols[0] + cols[1] / 2, y0 - rh / 2, "اسم المخطط - DRAWING", h=0.2, attach=5, color=7)
    s.text(x0 + cols[0] + cols[1] + cols[2] / 2, y0 - rh / 2, "الطابق - FLOOR", h=0.2, attach=5, color=7)
    s.line((x0 + cols[0], y0), (x0 + cols[0], y0 - rh * (n + 1)), color=7)
    s.line((x0 + cols[0] + cols[1], y0), (x0 + cols[0] + cols[1], y0 - rh * (n + 1)), color=7)
    for i, (page, title, floor) in enumerate(ROWS, 1):
        cy = y0 - rh * i - rh / 2
        s.line((x0, cy - rh / 2), (x0 + w, cy - rh / 2), color=8, lw=5)
        s.text(x0 + cols[0] / 2, cy, f"{page:02d}", h=0.16, attach=5, color=7)
        s.text(x0 + cols[0] + cols[1] - 0.2, cy, title, h=0.16, attach=6, color=7)
        s.text(x0 + cols[0] + cols[1] + cols[2] / 2, cy, floor, h=0.14, attach=5, color=7)
    s.text(19.3, 27.0, "تصميم وإعداد: ZWORKS - م. محمد الرماحي | جوال 0565187917 | SUPPORT@ZWORKS.NET", h=0.22, attach=5, color=8)

def draw_M(s):
    pass
