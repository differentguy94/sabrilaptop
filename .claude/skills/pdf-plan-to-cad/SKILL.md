---
name: pdf-plan-to-cad
description: Turn architectural floor-plan PDFs (vector, usually AutoCAD "Print to PDF") into (1) areas in m² for a price quote and (2) an AutoCAD DXF at real scale (metres) that matches the PDF exactly. Use whenever the user uploads plan PDFs and asks for "المساحة", "مساحة الدور الأرضي/العلوي/الميزانين/التراس", "عرض سعر", "حوّل الـ PDF لأوتوكاد / كروكي / DWG / DXF", "بالمقاسات الفعلية", or wants a tool to measure areas from a PDF. Debugged on a real job (Nov 2026: coffee shop unit 12, ground + upper floor); follow the fast path and the whole job takes ~15 minutes.
---

# PDF floor plan → areas + AutoCAD (real scale)

The user is a fit-out / interior designer (Arabic, Levantine). Clients send plan PDFs from the mall or
architect; the user needs the AREAS first (to send a quote), then a DXF/DWG to draw on. Deliver in that
order, each part as soon as it is done (text message for areas, SendUserFile for the DXF), then extras.

## Fast path

```bash
S=.claude/skills/pdf-plan-to-cad/scripts
pip install pymupdf ezdxf defusedxml numpy scipy            # ~30 s
cp <upload>.pdf work/plan.pdf                               # copy uploads to the scratchpad
python3 $S/pdf2dxf.py dims work/plan.pdf --png work/dims.png   # every dimension line: id, length in PDF pt
python3 $S/pdf_area.py labels work/plan.pdf                    # areas written on the plan (if any)
python3 $S/pdf_area.py render work/plan.pdf -o work/crop.png --clip x0,y0,x1,y1 --zoom 4   # read dims
```

1. **Look** at the PDF (Read tool renders it) and at `dims.png`; zoom crops with `render` to read the
   dimension numbers. Numbers are usually Arabic-Indic with a comma: `١٠,٢` = 10.2, `٢٦,٠٢` = 26.02
   (careful: ٢ = 2, ٣ = 3, ٦ = 6 look alike when small; check against the geometry/ratios).
2. **Scale**: pair dimension ids with their values and fit:
   `python3 $S/pdf2dxf.py convert plan.pdf out.dxf --dim-values "2606=10.2,203=14,3103=18.6"`
   prints pt-per-metre + residuals. Expect residuals ≤ 5 mm when the plan is drawn to scale; a residual
   of metres means a misread number (or 18.06 vs 18.6 kind of mistake).
3. **Areas**: compute from the WRITTEN dimensions (that is what the client's architect specified), and
   cross-check with polygons on the geometry (`pdf_area.py area --poly/--rect/--seed`). Compare with
   any area written on the plan and explain differences (e.g. 483 = (12.15+6.45)×26.02 = indoor +
   terrace without the 1.5×10.2 protrusion; 189 = 10.2×18.6 truncated). Report a table:
   ground indoor, upper indoor, terrace, outdoor seating (side/front), totals, with the formula per row
   and 3-4 short notes (what is excluded, e.g. "خدمات خارجية 121 م² not counted", heights).
4. **DXF**: write a small job script like `projects/coffee-12/build_coffee12.py` (copy it): it fits the
   scales from the dim values, places each floor with `convert_page(...)` (origin at a meaningful
   corner, upper floor rotated back if the PDF was plotted rotated, aligned on the same front/back
   lines and offset sideways so a MOVE stacks it), overrides the editable labels with the exact Arabic
   strings, and draws the area outlines on AREA-* layers (off). Render it back and compare with the PDF:
   `projects/coffee-12` has a preview PNG; ezdxf's drawing add-on with the PyMuPDF backend works.
5. **Deliver** the DXF with SendUserFile + a few lines (units = metres, layers, what is where, how to
   stack the floors, Save As DWG). Commit project files under `projects/<name>/`.

## What the converter does (scripts/pdf2dxf.py) and why

- **Coordinates**: "Microsoft: Print To PDF" quantises to 600 dpi = 0.12 pt. With ~20 pt/m that is
  6 mm, so a DXF built by one affine transform (scale 1/k, flip y, rotate, translate) is exact to the
  plot. Every dimension measured tick-centre to tick-centre agreed within 4 mm on the coffee-12 job.
- **Dimension detection**: a dim = one PDF path with a long H/V line and 45° ticks (2.5-12 pt) at both
  ends. Dimension NUMBERS are stroked (SHX) and cannot be read as text: read them visually.
- **Duplicates**: AutoCAD plots draw walls 2-3 times; identical primitives are removed (last one kept,
  it is the visible one in z-order).
- **Text**: PDF text from AutoCAD is in visual order with kashida filler glyphs (U+0467 "ѧ") and
  per-span reversed words, so extraction is unreliable. The DXF gets (a) exact glyph OUTLINES as solid
  hatches on `*-TEXT-PDF` (from PyMuPDF `get_svg_image(text_as_path=True)`), and (b) editable MTEXT on
  `*-TEXT-EDIT` (OFF). `text_lines()` reconstructs most labels; pass `text_override` with exact strings
  for anything it garbles (it got كافيه, مصعد طلبات, المساحة 121 متر, ارتفاع 5 متر wrong).
- **Filled outlines** (titles exported as polygons, images of column fills): PDF fills are non-zero,
  DXF hatches are odd-even. `_hatch` splits overlapping outer contours (kashida over letters) into
  separate hatches and keeps opposite-wound contours as holes. Symptom when wrong: gaps in «الـدور».
- **Images**: tiny black JPEGs = solid column fills → SOLID hatch rectangles.
- **Layers**: `<prefix><COLOUR>` with true RGB + lineweight; `<prefix>DIMS` for dims and their stroked
  numbers; `AREA-*` outlines with m² labels (OFF). DXF R2010, $INSUNITS = metres.
- **DWG**: needs ODA File Converter (opendesign.com). In the cloud container that host was blocked by
  the network policy (Nov 2026) → deliver DXF (AutoCAD opens it; Save As DWG). libredwg dxf2dwg is not
  usable. If opendesign.com is allowed: `xvfb-run -a ODAFileConverter in out ACAD2018 DWG 0 1 "*.dxf"`.

## The web tool (tool/)

`tool/plan-area.html` = «مسّاح المخططات», a single page (pdf.js 3.11.174 from jsDelivr with SRI):
upload PDFs → written areas, auto scale from dims whose numbers are real text (else click one green
dimension and type its value), room click (raster flood fill: dimension lines erased except at
crossings, holes filled, half the measured wall line added back; refuses leaks and paints them red),
polygon/rectangle with endpoint snapping, closing lines, results table across files, copy as TSV.
Published for the user as a private Artifact: https://claude.ai/artifact/N6HSQEBgFwV6JN1hrQrTSB
To change it: edit `plan_area_template.html`, run `python3 tool/build_tool.py`, test (below), then
publish `tool/plan-area.html` to the same URL (Artifact tool with `url`).
Testing without internet: `npm install pdfjs-dist@3.11.174`, serve `plan-area-standalone.html` with
`python3 -m http.server`, and in Playwright `page.route('https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/*', ...)`
to the local files with `Access-Control-Allow-Origin: *` (SRI is then checked for real).
Known accuracy: polygon/rectangle exact (189.73 vs 189.68 m² with a one-dimension calibration);
room click within ~0.2-0.6 % of the dimensioned area when the room is closed.

## Lessons from the first job (coffee-12)

- The PDF the client sends may be cropped by the mall: keep what is on the page, do not invent the rest.
- The upper floor was plotted rotated 90° (title text direction (0,1)): rotate it back CCW so it reads
  like the ground floor; its depth (12.15 + 6.45 = 18.6) matched the ground unit depth (18.6) and the
  yellow dashed outline 1.5 m in front of the ground floor was the upper floor's protrusion.
- Read the small print: "18,6" vs "18,06" and "26,02" vs "36,02" were resolved by checking the dims'
  measured lengths (369.96 pt / 19.886 = 18.60; 783.12 / 30.098 = 26.02).
- Areas the user wants for a quote: indoor per floor, terrace, outdoor seating, totals; mention
  anything on the plan that may or may not be in scope (back-of-house "خدمات خارجية").
- Area written on the plan ≈ truncated product of the main dims; say so instead of "correcting" it.

`LESSONS.md` is where the engineer writes corrections; read it before a new job and fold new rules
into this file.
