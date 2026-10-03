# Sheet framework (Einstein Burger, Oct 2026) — generate new discipline sheets from a client's base plan

Files (copied from the working project; paths inside them point at the scratchpad and must be adapted):

- `fixdoc.py`   — `load_fixed()`: opens the DXF (from `dwg2dxf`), repairs dangling dimstyle refs, runs `doc.audit()`.
- `sitemodel.py` — all plan coordinates (walls, rooms, counter, equipment, seating...) measured once from the base plan
                   (render the frame with a 1 m grid overlay to read them). Everything else is drawn from these dicts.
- `lib.py`      — `Ctx` (layers, purge strays outside frames, drop MTEXT column data, anchor-by-insert collection) and
                   `Sheet` (copy a base frame to column N, replace the title keeping the `\pi` prefix, erase the plan if
                   needed; primitives + symbols + legend/notes/dim/leader helpers in the user's style).
- `disc_elec.py` — example discipline module (`LAYER`, `draw_G(s)`, `draw_M(s)`, legend, quantity table, dims, callouts).
- `disc_index.py` — cover/index sheet (table of sheets).
- `build.py`    — assembles all sheets into one DXF column row and plots every frame to A2 via `../../scripts/dwg2pdf_frames.py`.
- `furn_catalog.py` — PyMuPDF pages with isolated furniture renders (Higgsfield nano_banana_2) + specs/dimensions.
- `qa_sheets.py` — contact sheets (6 pages per PNG) for visual QA of the final PDF.
- `finalize.sh` — build → append catalogue → TOC → ODA File Converter DWG → copy deliverables.
- `SPEC.md`     — per-discipline content requirements + style rules (what every sheet must contain).

Workflow that worked: 1) dwg2dxf, 2) measure coordinates into `sitemodel.py`, 3) write `SPEC.md`, 4) one module per
discipline (parallel agents are fine, but at most 2 concurrent on 4 CPUs), 5) `build.py --only elec` for quick checks,
6) full build + `qa_sheets.py`, 7) `finalize.sh`. Quantities/specs tables and dimensions (red) on every sheet.
