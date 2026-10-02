#!/usr/bin/env bash
# One-shot environment setup for the dwg-to-pdf skill (Ubuntu/Debian cloud container).
# Idempotent: safe to re-run. Takes ~2-3 min on a fresh container, seconds afterwards.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS="${DWG2PDF_TOOLS:-$HOME/.dwg2pdf-tools}"
mkdir -p "$TOOLS"

echo "== python deps"
python3 -c "import ezdxf, pymupdf, fontTools, arabic_reshaper, bidi, PIL" 2>/dev/null || \
  pip3 install -q ezdxf pymupdf fonttools arabic-reshaper python-bidi pillow 2>&1 | grep -v -i warning || true

echo "== arabic fonts (apt)"
if ! fc-list | grep -qi "NotoNaskhArabic"; then
  (apt-get update -qq && apt-get install -y -qq fonts-noto-core fonts-liberation) >/dev/null 2>&1 || \
    echo "apt failed (no root?) - continuing; make_fonts.py will fall back to DejaVu Sans"
fi

echo "== DWG -> DXF converter (libredwg dwg2dxf)"
if ! command -v dwg2dxf >/dev/null 2>&1 && [ ! -x "$TOOLS/mmenv/bin/dwg2dxf" ]; then
  # libredwg is not in Ubuntu apt; prebuilt binary comes from conda-forge via micromamba.
  # (GitHub release downloads work through the proxy; GNU ftp mirrors do not.)
  if [ ! -x "$TOOLS/micromamba" ]; then
    curl -sS -L --max-time 180 -o "$TOOLS/micromamba" \
      "https://github.com/mamba-org/micromamba-releases/releases/latest/download/micromamba-linux-64"
    chmod +x "$TOOLS/micromamba"
  fi
  "$TOOLS/micromamba" create -y -q -p "$TOOLS/mmenv" -c conda-forge libredwg >/dev/null
fi
if [ -x "$TOOLS/mmenv/bin/dwg2dxf" ]; then echo "dwg2dxf: $TOOLS/mmenv/bin/dwg2dxf"; else echo "dwg2dxf: $(command -v dwg2dxf)"; fi

echo "== substitute TrueType fonts (Arial/Georgia/Tahoma... with Arabic glyphs)"
python3 "$HERE/make_fonts.py"
echo "== setup done"
