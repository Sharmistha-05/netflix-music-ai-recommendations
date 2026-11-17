"""Render every page of the exported PDF to a PNG (1920 px wide) for screenshots."""
import sys
from pathlib import Path

import fitz  # PyMuPDF

pdf, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for old in out.glob("slide_*.png"):
    old.unlink()
doc = fitz.open(pdf)
for i, page in enumerate(doc, 1):
    zoom = 1920 / page.rect.width
    page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(out / f"slide_{i:02d}.png")
print(f"Rendered {doc.page_count} slides to {out}")
