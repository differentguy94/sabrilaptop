# Einstein Burger – discipline sheets specification

Project: burger restaurant "Einstein Burger" (client of ZWorks / Eng. Mohammad Ramahi). Industrial style:
exposed concrete walls, black glossy subway tiles (kitchen + counter), polished concrete floor with islands of
black/white patterned cement tiles, exposed concrete ceiling painted dark with undulating timber-slat "wave"
panels and hanging greenery, exposed black ducts, track lights + black dome pendants + globe lights on the
black metal planter frames, black leather booths, live-edge wood tables, neon signs, TV screens, a circular
"EINSTEIN BURGER" ring sign over the hall, facade = black fascia with the logo + black-framed glass curtain
wall between concrete columns + concrete wall with an Einstein sketch mural.

Reference images (open with the Read tool):
- gridded plans with 1 m grid (coordinates!): `grid_A2.p01_q1..q4.png` (ground floor quadrants),
  `grid_A2.p02_q1..q4.png` (mezzanine). Full pages: `grid_A2.p01.png`, `grid_A2.p02.png`.
- renders contact sheets: `contact_1.png` (facade p1-5, hall p6-24), `contact_2.png` (hall/booths/counter p25-46,
  kitchen p47-48), `contact_3.png` (kitchen p49, mezzanine prep/wash/store/office p50-55, branding),
  `contact_4.png` (more hall views). Single pages: `renders.pdf` (Read with pages="N").
- the already finished electrical sheet (style reference): `einstein_all.p03.png` (ground), `einstein_all.p04.png` (mezz).

## Code framework (do NOT edit lib.py / sitemodel.py / build.py – only your own disc_<key>.py)
- `sitemodel.py`: dict `G` (ground) and `M` (mezzanine) with all coordinates: hall polygon, kitchen polygon,
  counter, prep, boh rooms, wc_m, columns, `equipment` list (name,x0,x1,y0,y1,needs), `hood`, `seating`
  list (kind,cx,cy,w,h), `planters`, `tree`, `tv`, `menu_board`; `M["rooms"]`, `M["doors"]`, `M["equipment"]`,
  `M["wc_fix"]`, `M["stairs"]`, `M["beds"]`, `M["void"]`; `FACADE`; `EMPTY_G`, `EMPTY_M` = free areas for legends.
  READ IT. Coordinates are metres in the frame system of the gridded PNGs (ground y 23..45, mezz y -2..20).
- `lib.py`: `Sheet` methods (all take frame coordinates, add the column offset themselves):
  line, pline(pts, closed, width, linetype), rect, circle, arc, dot (filled), hatch(pts, pattern, scale, color),
  text(x,y,s,h,color,attach,width,rotation), label (centered), dim(p1,p2,offset,color,h,horizontal) linear
  dimension (ezdxf-rendered, red by default color=3? -> use color=1 red like the user's), leader(pts),
  elec_point, floor_drain, water_point(kind C/H/CH), valve, camera(x,y,rot,cone), speaker, device_dot(letter),
  spot, track(pts, heads), pendant, globe, led_panel, downlight, strip, cassette, split_unit, outdoor_unit,
  duct(pts, w, diffusers), diffuser, grille, fan, gas_point, cylinder, box_label, legend(x,y,title,rows,w,rh),
  notes(x,y,lines,h,w,title). Read lib.py once for signatures.
- Module contract: `LAYER = "<layer name from lib.LAYERS>"`, `def draw_G(s: Sheet)`, `def draw_M(s: Sheet)`.
  Colors default to the layer color; pass `color=` to override (ACI numbers: 1 red, 2 yellow, 3 green,
  4 cyan, 5 blue, 6 magenta, 7 black, 8 grey, 30 orange, 150 blue, 250 dark grey).
- Build & look: `python3 build.py --only <key> --out test_<key>` (≈90 s) → `test_<key>.p03.png` = your ground
  sheet, `test_<key>.p04.png` = your mezzanine sheet (p01/p02 are the base plans). ALWAYS open both PNGs with
  Read and fix overlaps / misplacements / text outside the frame; iterate until it looks professional.

## Style rules (the user's own style – mandatory)
1. Every element you add must be DIMENSIONED: distances between devices / from walls / sizes of ducts,
   hoods, zones (use `s.dim(...)`, red, text 0.12). At least 8–15 dimension strings per sheet.
2. Descriptive CALLOUTS: short Arabic tags next to the main elements (e.g. "هود شفط 8.10×1.20 م",
   "دكت رئيسي Ø400 مكشوف أسود"), with a leader line (`s.leader`) when the tag is away from the element.
   Arabic text is typed normally (logical order); the plotter shapes it. Keep lines ≤ 60 characters, use
   `\\P` for line breaks. Text heights: tags 0.11–0.14, titles 0.2, legend 0.13.
3. A LEGEND table at the free area (`EMPTY_G` top-left of the ground sheet: start at (4.2, 45.2);
   `EMPTY_M`: start at (4.2, 20.2)) using `s.legend(...)` with a symbol-drawing lambda per row, Arabic + English.
4. NOTES block top-right: `s.notes(34.8, 45.0, [...], h=0.14, w=9.0, title="...")` (mezz: (34.8, 20.0)).
   Include quantities ("العدد = N") and specifications (sizes, heights, materials, standards).
5. A SCHEDULE/count table where relevant (quantities per type) – you may draw it with rect/line/text.
6. Symbols must stay inside the plan area (ground: x 7..32, y 26.6..43; mezz: x 7..32, y 1.5..18.5) and
   never over the title block (ground y < 26.4, mezz y < 1.4). Do not cover the room-name texts of the base plan.
7. Nothing may be placed outside the frame x 3.5..35.1.
8. On the mezzanine sheet mark the void: `s.text(19.5, 4.2, "فراغ مزدوج الارتفاع فوق صالة الجلوس\\PDOUBLE HEIGHT VOID", h=0.3, attach=5, color=8)`.
9. Use the layer color of your discipline for symbols; dimensions red (1); legends/notes black (7).
10. Match the renders: when the renders show something (duct routing, lamp types, finishes), follow them.

## Ground floor geometry summary (metres)
- Facade glass line y=27.0 from x 7.4 to 31.5; entrance double door x 18.5–20.6; columns at the facade
  x 7.0–7.4, 15.1–15.6, 23.3–23.8 (y 26.8–28.9). Right side glass wall x≈31.7, y 30.4–38.9.
- Dining hall polygon: (7.4,27)-(31.5,27)-(31.5,35)-(15.3,35)-(15.3,36.5)-(7.4,36.5). Hall height ≈ 6.0 m
  (double height, exposed slab). Kitchen (15.3..24.3, 35..38.9) behind the counter (15.0..21.0, 35..35.65).
  Prep area 20.5..24.3 × 36..37.6. Cooking line along the back wall y 37.65–38.45, x 15.55–23.3 (see
  `G["equipment"]`); hand sinks x 24.3–25.4; stairs 25.7–28.8 × 37.4–38.9; store 26.1–28.2 × 35–37.4;
  prayer room 28.2–30.4 × 35–37; women WC 30.4–31.5 × 35–38.9; service/electrical room 30.5–31.5 × 31.6–33.
  Men WC block 7.4–9.5 × 36.5–39.7 (2 cubicles), spiral stair room 7.4–9.5 × 39.7–42.4.
- Seating: left-wall booths at x≈8.4 (y 28.0, 29.4, 30.9, 31.8, 33.7); three 4-tops at y 35.6 (x 10.3,
  12.35, 14.4); communal table 4.8×0.9 centred (12.4, 31.45) with olive-tree stone pot at (14.4, 31.45);
  facade booths (11.15, 28.1), (13.45, 28.1); waiting bench (17.0, 28.5); right-front booths (22.65, 28.6),
  (22.65, 30.2); right row booths at y 32.3 (x 24.6, 26.7, 28.8, 30.2); bar stools y 34.25 (x 15.6..19.2).
  Planters (black metal frames with globe lights): (24.3,31.3)-(30.5,31.6), (24.3,27.9)-(24.6,31.3),
  (21.5,27.9)-(21.8,31.3), (13.4,30.7)-(15.4,32.2). TVs on walls at (7.45,32), (31.45,33.5), (12.5,36.45).

## Mezzanine geometry summary
- Same footprint, 24.953 m lower in the sheet (y). Rooms r3 7.4–11.6, r2 11.8–16.4, r1 16.6–20.9 (y 6.5–9.7),
  corridor 7.4–20.9 × 9.7–11.5, kitchenette on the left wall (sink 12.3–13.1, gas oven 11.4–12.3, fridge
  10.2–11.2 at x 7.6–8.0), WC-A 15.5–18.9 × 11.5–13.6, WC-B 19.0–20.9 × 10.4–13.6, freezer/fridges column
  x 21.2–21.9 (y 7.1–11.3), prep/wash area 22–31.5 × 11.4–13.5 (double sink 23.6–25 at y 12.9–13.4,
  3-compartment sinks 25.2–27.6 and 28.5–31.0 at y 11.9–12.6, stairs 25–29 × 12.3–13.4), long steel table
  23.3–29.5 × 9.5–10.2, central walk-in freezer 23.3–26.5 × 6.5–9.4, store 26.7–29.6 × 6.5–9.4, office
  29.7–31.5 × 6.5–8.0, shelving along the right wall x 31.1–31.5 (y 8.1–13.4), spiral stair (8.4,15.6).
  Front strip y 2–6.3 = double-height void over the hall. Ceiling height mezzanine ≈ 2.7 m.

## Per-discipline requirements

### plumb  (LAYER "P-PLUMB", orange 40) – مخطط السباكة
Symbols: cold water point (blue 150), hot water point (red 1), floor drain F/D (orange square, `floor_drain`),
drain line (magenta 6, lw 35), cold water pipe (blue 150, linetype "DASHED"), hot water pipe (red 1, DASHED),
grease trap (magenta circle r 0.4 + "G.T"), water heater WH (rect 0.5×0.3 + text), inspection chamber I.C
(square 0.6 + X, magenta), cleanout C.O (green circle r 0.12), main water inlet text "نقطة تغذية الماء
الرئيسية" (color 32, h 0.3) at the back wall near (24.5, 39.3), stop valves (`valve`).
Ground: water (C+H) + drain for hand sinks (24.55,38.2),(25.15,38.2); men WC toilet (8.5,39.1) [C + 4" drain],
basins (7.75,38.8),(7.75,37.2) [C+H]; women WC toilet (30.6,38.1), basin (30.9,37.6); prayer room ablution
tap (28.5, 36.9); kitchen floor drains (16.3,37.2),(19.5,37.2),(22.5,37.2),(24.6,36.4), counter area
(18.0,35.8), salad fridge condensate (18.1,36.9); WC floor drains (8.3,38.5),(8.3,37.0),(31.0,37.0);
grease trap (24.8, 36.5) collecting kitchen drains → inspection chamber outside the back wall (24.8, 39.5)
→ public sewer. Cold water main from the street along the back wall; WH ×2 (kitchen (23.8,38.7) 80 L,
men WC (9.3, 39.5) 30 L). Draw pipe runs (double/dashed lines) connecting points to the mains, pipe sizes
as callouts (drain 4"/2", PPR 3/4"/1/2"), slopes 1-2 %. Dimension drain positions along the cooking line.
Mezz: 3-compartment sinks (each basin C+H), double sink, kitchenette sink (7.8,12.7) C+H, WC-A toilet
(16.6,13.1) basin (15.75,12.75), WC-B basin (19.2,13.2) toilet (20.5,10.95); floor drains prep (26.5,11.7),
(29.6,11.7), (24.3,12.7), WCs (16.2,12.3),(20.0,12.3); WH ×2 (24.3,13.3),(29.7,13.3) 50 L; drain stack
down to the ground grease trap (riser symbol circle "D.P" at (31.3,13.4)); roof tank note. Legend + notes
(pipe materials PPR/UPVC, grease trap mandatory, test pressure).

### hvac  (LAYER "M-HVAC", magenta 6) – مخطط التكييف - الدكت
Industrial EXPOSED ductwork as in renders p9/p10/p15/p39 (black round/rectangular ducts under the slab).
Ground: 3 ducted split units 5 TR (60 000 BTU) concealed above the BOH ceiling: AHU-1 at (26.5,36.2),
AHU-2 at (29.3,36.4), AHU-3 (kitchen unit, 3 TR) at (22.5,36.9). Supply: duct A Ø450 exposed black along
y=33.6 from x=31.0 to x=8.0 with round diffusers Ø300 every 2.5 m; duct B Ø450 along y=29.6 from x=31.0 to
x=8.0 with diffusers every 2.5 m; connect both to the AHUs through the BOH wall with a header along y=34.6
(x 25..31). Return air grilles 600×600 ×3 in the BOH wall (y 35.0 at x 25.5, 27.8, 30.0). Fresh-air intake
duct Ø250 from the right glass side top (31.5, 34.2). Kitchen: supply duct Ø300 along y=36.6 x 16..24 with
3 diffusers (kitchen make-up/comfort). Thermostats T ×3 (hall (12,36.3),(30,34.8); kitchen (24,36)). Outdoor
condensing units ×4 on the roof above the BOH – draw them at (26..31, 40.0) with the label "وحدات خارجية على
السطح". Draw ducts with `s.duct(pts, w=0.45, diffusers=[...])`, size labels, flow (CFM) tags, duct bottom
height +3.60 m (hall) / +2.80 (kitchen) in callouts. Dimension diffuser spacing and duct offsets from walls.
Mezz: wall-mounted splits 18 000 BTU in r1, r2, r3 (on the wall y 6.6, x centred, `split_unit`), 12 000 in the
office (31.3, 7.3, rot 90), 2 × 24 000 ceiling cassettes in the prep/wash area at (24.5,12.6)? no – the sinks
are there; place cassettes at (24.0,10.9) and (29.0,10.9) over the free zone; a 12 000 split in the corridor
(14,11.3 on the wall y 11.5). Outdoor units ×6 on the roof (draw at y 15..16). Condensate drain lines to the
nearest floor drain. Legend (duct, diffuser, grille, split, cassette, ODU, thermostat), schedule table
(unit tag, type, capacity BTU, location, qty) and notes (duct material GI 24 g painted matt black, insulation,
flexible connectors, fire dampers at kitchen wall, balance to 50 Pa negative in kitchen).

### gas  (LAYER "G-GAS", orange 30) – مخطط الغاز
LPG system. Cylinder bank cage OUTSIDE the building behind the back wall: draw the cage 2.4×1.0 at
(25.0..27.4, 39.6..40.6) with 4 cylinders (`cylinder`), manifold, regulator "منظم ضغط", meter "عداد", main
shut-off valve. Main line 3/4" copper (orange, width 0.04) entering the wall at (24.0, 38.9), running along the
back wall at y=38.6 to x=15.5 with branch drops + isolation valves + flexible hose to: fryers ×3 (centre of
each fryer), flat grill (18.15), char-broiler (19.2), 2-burner stove (20.1). Gas detectors ×2 (16.5,38.6),
(21.0,38.6) wired to the solenoid valve at the entry; emergency shut-off push button at (24.2,36.1) and at the
cage. Mezz: riser from the ground line up at (9.6,38.8) → mezz corridor wall → oven (7.8,11.85) with valve,
detector (8.4,12.0); mark the riser on both sheets ("صاعد غاز"). Pipe lengths dimensioned, drop heights
(+1.20 m valves), legend (pipe, valve, regulator, detector, solenoid, shut-off), notes (SASO / Civil
Defence code, cage ventilated and 1 m from openings, pressure test 1.5× for 24 h, pipe painted yellow).

### exhaust  (LAYER "M-EXHAUST", red 1) – مخطط الشفاط والتهوية
Kitchen hood over the cooking line: rectangle `G["hood"]` = (15.4,37.5)-(23.5,38.7), draw double outline +
diagonals, label "هود شفط ستانلس 8.10 × 1.20 م مع فلاتر دهون + نظام إطفاء", with a dedicated section over the
charcoal grill (22.4..23.4) "فلتر مانع للشرر". Exhaust duct 600×400 from the hood collar at (19.5,38.7)
through the back wall to the roof fan: draw the duct to (19.5,40.2) and the centrifugal exhaust fan
"مروحة شفط 6000 CFM" at (19.5,40.6) + odour/ESP filter unit at (21.8,40.2). Make-up air fan "مروحة هواء
تعويضي 5000 CFM" at (15.8,40.4) with duct to a grille in the kitchen at (16.3,38.8). WC extract fans
(Ø150, 150 CFM): men's cubicles (8.5,39.4),(8.5,37.5), women's (30.9,38.4), prayer (29.3,36.0), store
(27.1,36.2), service room (31.0,32.3); hall general extract ×2 at the back wall (10,36.3)? no – keep hall
extraction via the AHU return; add 2 wall fans at the top of the right glass wall (31.3, 34.0),(31.3,31.0)
for smoke purge. Mezz: kitchenette oven hood 0.9×0.6 at (7.8,11.85) with duct to the roof via the left wall
(fan on the roof (7.5,19.0) outside the frame? keep inside: (7.8,14.0) riser symbol), prep/wash extract fans
×2 (25,13.4),(29,13.4), WC fans ×2 (16.5,13.4),(19.5,13.4), store/freezer-room ventilation grille, rooms
fresh-air grilles. Dimension hood overhangs, duct sizes, fan positions. Legend + notes (duct 1.2 mm GI welded
grease duct, cleaning access doors every 3 m, fire-rated enclosure, 0.3 m hood overhang, 500 CFM/m).

### cctv  (LAYER "E-CCTV", cyan 4) – مخطط كاميرات المراقبة
Use `s.camera(x, y, rot, cone=True, r_cone=3.5, span=80)`; rot = viewing direction in degrees (0 = +x,
90 = +y). Ground (indoor dome 4 MP): entrance inside (19.5,27.5) rot 90; hall corners (7.7,36.2) rot -40,
(7.7,27.3) rot 40, (31.2,27.3) rot 140, (31.2,34.8) rot 220; counter/cashier (19.8,35.8) rot 270; delivery
window (22.5,35.8) rot 270; kitchen (15.6,38.7) rot -35, (24.0,38.7) rot 215; BOH corridor (25.0,35.3)
rot 90; stairs (28.5,37.3) rot 90; outdoor bullet cameras under the fascia (11,26.6) rot 270, (27,26.6)
rot 270. NVR 32 ch + monitor in the service room (31.0,32.2) (box label), monitor at the cashier. Mezz:
corridor (9.7,11.3) rot 0 and (20.7,11.3) rot 180; prep (22.3,13.3) rot -30, (31.3,13.3) rot 210; lobby
(23.0,9.0) rot 0; stairs (24.9,13.3) rot 0; office monitor. No cameras in WCs/rooms. Number every camera
(C1..Cn) with a small tag, count table (indoor/outdoor), dimension distances from walls/corners, legend
(dome, bullet, NVR, coverage), notes (IP PoE 4 MP, 30 days 24/7 recording, Cat6 to the NVR, UPS 1 h).

### speak  (LAYER "E-SPEAKER", cyan 4) – مخطط السماعات
Ceiling/pendant speakers 6" 6 W 100 V line (user's style = `s.speaker(x,y)` with coverage ring). Ground
hall: (9.5,29.0),(9.5,33.5),(13.5,29.0),(13.5,33.5),(18.0,29.5),(18.0,33.5),(22.5,29.5),(22.5,33.5),
(27.0,29.5),(27.0,33.5),(30.5,31.5); kitchen (19.5,36.5); men WC (8.5,38.5); women WC (31.0,37.5);
entrance (19.5,28.0). Amplifier 120 W + mixer + Bluetooth source at the cashier (20.0,35.3) (box label
"مضخم صوت 120W + مشغل"), volume controls ×3 (hall, kitchen, WC) as small squares with "V". Mezz: prep
(26.5,12.5), corridor (14.0,10.6), office (30.6,7.0). Dimension the grid spacing (4.5 m etc.), legend,
count ("العدد = N"), notes (speaker height = exposed slab pendant mounts at +4.0 m in the hall; cable 2×1.5).

### insect  (LAYER "E-INSECT", color 146) – مخطط الناموسية
UV electric insect killers (wall mounted h = 2.0 m, 30 W) – `s.device_dot(x,y,0.35,cover=0,letter="IK")`
style like the user's (solid dot + ring): entrance inside left of door (17.9,27.5); delivery window
(22.5,35.7); kitchen side walls (15.5,37.0),(24.0,37.0) – never above food; BOH corridor (26.0,35.4);
back door/stairs (28.6,37.2); WCs none. AIR CURTAINS (ستارة هوائية) above the entrance 2.0 m (18.4..20.7,
27.1) and above the delivery window (21.6..23.5, 35.45): draw as a thick bar with label. Fly screens on
openable windows note. Mezz: prep (23.0,13.3),(30.0,13.3), kitchenette (8.4,12.8), corridor (14.0,11.3).
Dimension heights/positions, legend (IK unit, air curtain), notes (2 m from food surfaces, replace tubes
every 12 months, count).

### fresh  (LAYER "E-FRESH", cyan 4) – مخطط معطر الجو
Automatic aerosol dispensers (wall h 2.0 m) `device_dot(letter="AF")`: men WC (9.3,39.0),(9.3,37.6); women
WC (31.3,38.3); prayer (29.3,35.3); hall (7.6,30.5),(12.0,36.3),(24.5,34.8),(31.3,32.5); entrance
(18.3,27.5); mezz WCs (15.7,13.4),(20.7,13.4), corridor (14.0,11.3), lobby (22.5,8.0). Also a scent diffuser
machine (HVAC duct scent system) at AHU-1 location (26.5,36.2) labelled. Dimension positions, legend, count,
notes (refill every 30 days, 2 scents: hall / WC).

### floor  (LAYER "A-FLOOR", green 3) – مخطط الأرضية
Floor finish zones with hatches, codes, areas, quantities (+10 % waste) and dimensions:
FL1 polished micro-cement/concrete grey over the hall (`G["hall"]` minus the tile islands) – hatch "DOTS"
scale 1.5 color 8; FL2 patterned cement tiles 20×20 black/white "بلاط إسمنتي مزخرف" islands: under the
communal table (9.8,30.2)-(15.6,32.7), entrance carpet zone (17.6,27.2)-(21.4,29.3), right booths row
(23.4,31.5)-(30.6,33.2), left booths strip (7.4,27.3)-(9.5,34.6), counter front strip (15.0,33.6)-(21.0,34.9) –
hatch "ANSI37" scale 0.35 color 250; FL3 non-slip porcelain 60×60 grey R11 with epoxy grout in the kitchen
polygon + BOH (24.3..31.5 × 35..38.9) + counter back zone – hatch "NET" scale 4.8 color 3; FL4 porcelain 60×60
anti-slip in WCs/prayer – hatch "NET" scale 4.8 color 4; FL5 stair room concrete. Draw zone outlines (lw 35),
code bubbles (circle r 0.3 with the code), area text "المساحة = NN م2", dimensions of each island, slope arrows
to floor drains in the kitchen (1 %). Schedule table: code, material, size, colour, area, quantity (+10 %).
Mezz: FL6 ceramic 60×60 beige in rooms + corridor; FL3 in prep/wash/kitchenette; FL4 WCs; FL7 epoxy in the
walk-in freezer; office laminate. Threshold strips, skirting 10 cm note.

### light  (LAYER "E-LIGHT", magenta 6) – مخطط الانارة - التراك لايت
Warm light 3000 K (renders). Ground: TRACK LIGHTS (black 1-phase track, 3 spot heads 12 W per 2 m):
T1 (8.0,34.8)-(15.0,34.8) 4 heads; T2 (8.0,29.6)-(15.0,29.6) 4 heads; T3 (16.5,29.6)-(31.0,29.6) 7 heads;
T4 (16.5,33.8)-(31.0,33.8) 7 heads; T5 (16.0,36.9)-(24.0,36.9) kitchen pass 4 heads (`s.track(pts, heads)`).
PENDANTS black dome Ø30 (`pendant`): one above every booth/4-top table centre (from `G["seating"]`, kinds
booth/table4), three above the communal table (10.8,31.45),(12.4,31.45),(14.0,31.45), one above the waiting
bench. GLOBE LIGHTS Ø25 on the black metal planter frames (`globe`): every 1.2 m along (24.3..30.5, 31.45),
two on (24.45, 28.8/30.4), two on (21.65, 28.8/30.4), two on the tree planter (13.6,31.45),(15.2,31.45), two
between the left booths (8.4,29.0),(8.4,32.3). LED STRIPS (`strip`, yellow): under the counter top front
(15.0..21.0, 34.95), menu board backlight (15.6..23.3, 38.85), under the bar stools ledge, along the facade
fascia inside (7.4..31.5, 27.05) accent. NEON signs: "I ♥ BURGER" on the back wall (12.5,36.45) area and
"IT IS RUDE TO STARE…" (27.5,34.9) (mark with box labels). Kitchen: LED tri-proof battens 1.2 m 36 W ×6
(x 16,18,20,22 at y 37.0 and 36.0 … arrange 2 rows), under-hood lights ×3. WCs: downlights ×2 each cubicle,
women ×2; prayer ×2; store ×1; stairs ×2 (spiral); service room ×1. Outdoor: fascia wash spots ×6 (facade
sheet also). Mezz: LED panels 60×60 36 W ×2 per room, corridor ×3, prep/wash ×6, WC downlights ×2 each,
office ×1 panel, store/freezer battens ×2, lobby ×2, stair ×2. Dimension track lengths and spacing, pendant
heights in callouts (pendants 2.2 m above floor, tracks at +4.2 m, globes at +1.8 m). Legend + SCHEDULE
table (type, W, qty, colour temperature). Switch/dimmer locations at the cashier ("لوحة تحكم إضاءة").

### ceil  (LAYER "A-CEILING", magenta 6) – مخطط السقف
Ground hall (exposed slab at +6.0 m painted matt dark grey RAL 7016, exposed black ducts/conduits): draw
4 undulating timber-slat WAVE PANEL bands (مظلات شرائح خشب متموجة, 1.0 m wide, suspended at +4.0..+4.6 m)
across the hall parallel to the facade at y ≈ 28.6, 30.6, 32.6, 34.6 from x 8 to 31 – draw each band as two
sinusoidal polylines (amplitude 0.25, period 3 m, 60 points) + hatch "ANSI31" scale 0.3 color 32; hanging
greenery boxes 0.3 m wide along both edges of each band (dashed green lines + tag "صناديق نباتات صناعية
معلقة"); circular ring sign Ø2.4 m "EINSTEIN BURGER" (two circles r 1.2 / 1.0, color 7, text) centred at
(18.5,31.3) at +3.5 m; black exposed ducts are referenced ("انظر مخطط التكييف"). Kitchen + BOH: moisture
resistant gypsum board ceiling at +2.80 m painted white washable (hatch "ANSI31" scale 0.5 color 8 light);
WCs + prayer: gypsum +2.60 m; counter zone: black timber slat bulkhead above the counter (15..21 × 34.9..35.7)
at +2.6 m with the menu board. Mezz: gypsum tile ceiling 60×60 at +2.60 in prep/wash (hatch "NET" scale 4.8),
gypsum board +2.70 in rooms/corridor/office; walk-in freezer insulated panels. Mark ceiling heights "+X.XX"
in every zone with a level tag, dimension band spacing and widths, legend (C1..C6 materials), notes
(fire-rated boards above the cooking line, access panels, paint system).

### wall  (LAYER "A-WALL", green 3) – مخطط الجدران والتشطيبات
Wall finish codes drawn as coloured thick strips (`pline` width 0.08) INSIDE each wall line with a code
bubble every ~4 m: W1 exposed-concrete look micro-cement plaster, grey (hall walls: left wall x 7.4, the
wall y 36.5 x 9.5..15.3, columns, BOH wall y 35 x 24.3..31.5); W2 black glossy subway tile 7.5×15 cm, dark
grout (kitchen walls full height 2.8 m: back wall y 38.9 x 15.3..24.3, side wall x 15.3; counter front and
counter back wall band (15..21 at y 35.65) up to +1.2 m); W3 white glossy subway tile 7.5×15 (men's WC
block inside, women's WC, prayer dado 1.2 m); W4 perforated black metal panels with Ø8 cm holes feature wall
(right-front wall x 23.4..24.3 and the wall behind the right booth row y 31.3 planter frame, and x 31.5
near the service room – per renders p13/p28/p31); W5 wood slat cladding behind the facade booths (y 27.1
partition and the WC-block wall y 36.5?) ; W6 painted gypsum light grey (mezz rooms, office); W7 vertical
"EINSTEIN" lettering sign on the column (15.3,36.5) and (7.4,33) ; W8 neon sign "IT IS RUDE TO STARE JUST
EAT IT" on the BOH wall at (27.5,34.9); W9 TV 65" wall mounts ×3 (`G["tv"]`); W10 menu/chalk board above the
counter. Elevation markers (circle with letter + arrow) for 4 key walls. Legend table (code, material, size,
colour, height), dimensions of tiled heights/lengths, notes (waterproofing behind tiles in wet areas,
cement board backing, fire retardant paint on timber). Mezz: W3 2.4 m in prep/wash/kitchenette/WCs,
W6 rooms + corridor, insulated panels for the freezer room (W11), skirting.

### furn  (LAYER "A-FURN", orange 32) – مخطط الأثاث
Code every furniture item with a bubble (circle r 0.28 + code, color 32) and dimension it: F1 booth sofa
1.20×0.70 h 1.10 black leather / wood frame (all booths in `G["seating"]`); F2 live-edge wood table
1.20×0.70 h 0.75 black steel legs; F3 table 0.70×0.70; F4 communal live-edge table 4.80×0.90 h 0.75 + 2
benches 2.0×0.4; F5 dining chair black metal/wood (count them: 2 per booth table, 4 per 4-top, 14 at the
communal table); F6 bar stool h 0.75 ×5; F7 planter box 1.0×0.3×0.9 black metal frame h 1.8 with globe
lights (along `G["planters"]`); F8 waiting bench 2.0×0.5 wood; F9 front counter 5.50×0.65 h 1.05 black
subway tile front + solid wood top; F10 olive tree stone pot Ø1.5 (`G["tree"]`); F11 wooden barrel décor ×2
at (9.7,30.2),(16.3,32.6); F12 TV 65" ×3; F13 illuminated menu boards ×3 above the counter; F14 condiment/
pick-up shelf at the delivery window; F15 coat hooks. Draw a FURNITURE SCHEDULE table (code, description,
size, material/finish, qty) in the free area and dimension the main items (table sizes, booth pitch 2.0 m,
aisle widths ≥ 1.2 m). Mezz: F16 single bed 2.0×1.0 ×6 (draw them from `M["beds"]`), F17 wardrobe 1.0×0.6
×3, F18 office desk L 1.4×0.6 + chair, F19 stainless shelving 4-tier 1.2×0.5 ×6 (store + shelving wall),
F20 steel work tables (existing), F21 lockers. Schedule + dims.

### facade  (LAYER "A-FACADE", black 7) – مخطط الواجهة   (ground sheet only; use `Sheet(..., copy_base="frame")` is done by build.py? NO – build.py creates the sheet normally; in draw_G you receive a sheet that already carries the plan.)
IMPORTANT: build.py passes a normal sheet (plan copy). For the facade we want an ELEVATION, so draw_G must
first call `s.erase_plan()` (available in lib: removes copied plan entities above the title block) and then
draw the front elevation at 1:1 metres inside the frame: ground line at y = 30.0 from x = 7.0 to 31.9
(`FACADE`): concrete columns 0.45 wide full height 5.0 m (hatch AR-CONC scale 0.05 or DOTS), glass curtain
wall panels 2.1 m modules × 3.3 m high with black aluminium mullions (lw 35) between columns 7.45..15.1 and
15.55..23.3, entrance double door 2.1 m at x 18.5..20.6 with pull handles, black fascia band y 33.3..34.5
(hatch SOLID color 250) spanning x 7.0..23.75 with the logo: text "EINSTEIN BURGER" (h 0.45, color 7 on a
white box or color 255) centred at x 15.4 plus a simple mustache + glasses icon above it (two small circles
+ an arc), fascia wash spotlights ×6 at the top; right solid concrete wall x 23.75..31.9 full height with
the Einstein sketch mural zone (hatch DOTS light, label "جدارية رسم اينشتاين – طباعة على الخرسانة") and the
secondary logo; parapet line at 5.0 m; "I ♥ BURGER" neon visible through the glass (dashed box). Below the
elevation (y 27.5..29.5) draw a thin plan key of the facade line (glass line, columns, door) aligned to the
same x. Dimension everything (column spacing, panel widths 2.10, door 2.10, heights 3.30/4.50/5.00, fascia
1.20). Material legend (F1 black ACP fascia, F2 12 mm tempered glass + black powder-coated frame, F3 exposed
concrete, F4 3D acrylic illuminated letters, F5 mural, F6 LED spot 20 W). Notes. Title block stays.
draw_M is not called for the facade.
