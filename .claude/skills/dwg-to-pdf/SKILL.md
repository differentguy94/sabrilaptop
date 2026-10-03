---
name: dwg-to-pdf
description: Plot AutoCAD DWG/DXF drawings to a multi-page vector PDF, one page per sheet frame (title-block rectangle), at A2/A1/A3 etc., with Arabic text shaped and ordered correctly. Use whenever the user uploads a .dwg/.dxf and wants PDF/plot/print output, "كل مربع صفحة", "مخططات PDF", "A2 high resolution", "حافظ على العربي", or asks to split a drawing's frames into pages. Everything here was debugged once (Oct 2026); follow it verbatim and the whole job takes ~5 minutes and a few tool calls.
---

# DWG → per-frame PDF (Arabic-safe)

## Fast path (do exactly this, no exploration)

```bash
S=.claude/skills/dwg-to-pdf/scripts          # this skill's folder (repo root), or ~/.claude/skills/...
bash $S/setup.sh                             # ~2 min first time: pip deps, Noto Arabic fonts, libredwg via micromamba, Arial/Georgia substitutes
python3 $S/dwg2pdf_frames.py in.dwg --list-frames        # sanity: frame count + titles (seconds)
python3 $S/dwg2pdf_frames.py in.dwg --dump-arabic         # unique Arabic lines in stored order
python3 $S/dwg2pdf_frames.py in.dwg -o out.pdf --page A2 --flip-file flip.txt --preview 1
```

1. Copy the upload to the scratchpad and run `setup.sh` (idempotent; prints `setup done`).
2. `--list-frames`: expect one line per sheet with its biggest text as title (e.g. `مخطط الكهرباء`).
   Wrong count → `--frame-size WxH` (drawing units) or `--layer NAME`, or explicit `--frames`
   (`--frames "x0,y0,x1,y1;..." --keep-order` plots the boxes in the given order = page order).
3. `--dump-arabic`: read the list once. Lines whose WORD ORDER reads backwards
   (e.g. `2م 243 = الاجمالية المساحة`, `ستيل طاولة`, `5 = العدد`) go into `flip.txt`, one per
   line, exactly as printed. Titles typed properly (`مخطط نقاط أفياش الكهرباء`) stay out.
   `reference/flip_zworks_shop.txt` is the list for the ZWorks shop drawing: reuse it for
   drawings from that author/template (unknown lines are simply ignored).
4. Render. ~1 min for 16 A2 pages. Open the `--preview` PNG with the Read tool and check:
   title block texts in their cells, Arabic connected and reading right-to-left, no labels
   hugging the left page edge. Then deliver the PDF with SendUserFile (the `.p01.png` is
   just for you). Pushing a big PDF into the repo may be refused by the permission
   classifier; the file in the working directory plus SendUserFile is the deliverable.

Reading rendered Arabic in a PNG: the glyph sequence left→right must be the LAST letter
of the last word first (e.g. `مخطط المحل` shows the final ل at the far left and the initial
م of مخطط at the far right). Do not "fix" that; it is correct. Only trust 150+ dpi crops.

## Why the script does what it does (keep these when editing it)

- **DWG→DXF**: `libredwg dwg2dxf` (conda-forge via micromamba; not in Ubuntu apt, GNU ftp is
  blocked by the proxy, GitHub release downloads work). Version 0.11 handles 2013-2017 DWG fine.
- **Everything lives in modelspace** in these drawings; paperspace layouts are empty. Frames
  are closed LWPOLYLINE rectangles of identical size laid out in a row; pages are sorted
  top-to-bottom, left-to-right. Frame aspect ≈ √2 so A-series landscape fits with 4 mm margins.
- **Arabic**: ezdxf has no bidi/shaping; it draws glyphs left-to-right as given. The script
  reshapes (presentation forms) + `bidi.get_display` per MTEXT paragraph piece before layout.
  AutoCAD files mix logical-order text and visual-order (word-reversed) labels, hence
  `--flip-file`. Fonts: Arial is absent → `make_fonts.py` merges Liberation Sans + Noto Naskh
  Arabic (UPM scaled to 2048, family renamed to "Arial") so `\fArial|...` inline codes resolve
  and Latin text keeps Arial-like metrics. Same for Georgia/Tahoma/Times/etc.
- **Process modelspace once**: iterating `doc.blocks` includes `*Model_Space`; processing twice
  reverses the Arabic back (mirrored text) and doubles indents. The script excludes it.
- **MTEXT `\pi` indents** are stored in DRAWING UNITS by AutoCAD in these files; ezdxf
  multiplies by char_height. Auto-detected (median indent/width ratio); drawing units are
  applied by shifting the insert point for single-paragraph texts (exact, no wrap quirks) and
  by rescaling + widening the box for multi-paragraph ones. Symptom when wrong: title-block
  words glued to the left cell border or labels outside the frame.
- **ezdxf `PyMuPdfBackend` mutates its recording** on every `get_pdf_bytes`; `MultiPageBackend`
  copies the player per page, otherwise pages 2..n come out empty.
- White background with true colours (`--mono` for a monochrome.ctb look), absolute lineweights
  with a 0.10 mm floor, 256-segment circles. Output is vector: resolution-independent.

## Generating NEW discipline sheets from a base plan (done for Einstein Burger, Oct 2026)
When the user wants new drawings (electrical, plumbing, HVAC, ...) drawn on copies of their plan: the
reusable framework lives in `reference/sheet_framework/` (lib.py = Sheet class: copies one frame of the base
plan to a new column with the title replaced, symbol primitives in the user's style, legend/notes/dimension
helpers; build.py = assembler; SPEC.md = per-discipline requirements; disc_*.py = examples). Pitfalls:
collect base entities by INSERT point (ezdxf's fast MTEXT bbox is wrong), purge stray entities outside the
frames before copying, keep `\pi` prefixes when replacing title/date texts, Python module names must not
shadow stdlib (`site`), MTEXTs carrying AutoCAD dynamic-column data (`has_columns`) re-flow into a second column
when copied/re-titled → set `_columns=None`, `defined_height=0`, drop the ACAD xdata. Real DWG output: ODA File Converter (.deb from opendesign.com, needs
`xvfb-run -a` + libopengl0 libxkbcommon-x11-0), command
`ODAFileConverter in_dir out_dir ACAD2018 DWG 0 1 "*.dxf"`; libredwg's dxf2dwg is NOT usable.

## Deliverable wording (Arabic user)

Short: pages count, page size, vector, Arabic preserved, which labels' word order was
normalised, and where the file is. No process narration.

## Learning loop with the engineer (قواعد المهندس)
`LESSONS.md` next to this file holds the engineer's corrections; `reference/corrections/` holds his corrected
DWG/PDF files. At the start of any job, read `LESSONS.md`; when asked to compare, open his corrected file with
`dwg2dxf` + ezdxf next to the generated one in `reference/sheet_framework/`, list the concrete differences (symbol
shapes, text heights, layer names/colours, legend layout, where dims/callouts go, what quantities he adds) and
append them as rules under this heading. Rules written here override the defaults above.

### قواعد المهندس (تُضاف تلقائياً من المقارنات)
- (لا توجد قواعد بعد)
