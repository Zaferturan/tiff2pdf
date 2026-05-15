"""Rotate portrait PDF pages to landscape via /Rotate (no TIFF re-encode)."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

# pypdf rotates clockwise; 270° = 90° counter-clockwise.
PORTRAIT_ROTATE_DEGREES = 270


def _page_dimensions(page) -> tuple[float, float]:
    box = page.mediabox
    return float(box.width), float(box.height)


def is_portrait_page(page) -> bool:
    """True when taller than wide; square pages are excluded."""
    width, height = _page_dimensions(page)
    return height > width


def rotate_portrait_pages(pdf_path: Path) -> int:
    """
    Set PDF /Rotate on each portrait page (height > width).

    Returns the number of pages rotated. Rewrites the file only when needed.
    """
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    rotated = 0

    for page in reader.pages:
        if is_portrait_page(page):
            page.rotate(PORTRAIT_ROTATE_DEGREES)
            rotated += 1
        writer.add_page(page)

    if rotated == 0:
        return 0

    tmp_path = pdf_path.with_suffix(".rotating.pdf")
    try:
        with open(tmp_path, "wb") as out:
            writer.write(out)
        tmp_path.replace(pdf_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return rotated
