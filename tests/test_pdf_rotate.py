"""Tests for portrait PDF page rotation."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from tiff2pdf_gui.pdf_rotate import is_portrait_page, rotate_portrait_pages


def _write_sample_pdf(path: Path) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=200)  # portrait
    writer.add_blank_page(width=300, height=150)  # landscape
    writer.add_blank_page(width=120, height=120)  # square
    writer.add_blank_page(width=80, height=160)  # portrait
    with path.open("wb") as f:
        writer.write(f)


def test_is_portrait_page() -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=200)
    writer.add_blank_page(width=200, height=100)
    writer.add_blank_page(width=100, height=100)
    pages = writer.pages
    assert is_portrait_page(pages[0]) is True
    assert is_portrait_page(pages[1]) is False
    assert is_portrait_page(pages[2]) is False


def test_rotate_portrait_pages(tmp_path: Path) -> None:
    pdf = tmp_path / "mix.pdf"
    _write_sample_pdf(pdf)

    count = rotate_portrait_pages(pdf)
    assert count == 2

    reader = PdfReader(str(pdf))
    assert reader.pages[0].get("/Rotate") == 270
    assert reader.pages[1].get("/Rotate") is None
    assert reader.pages[2].get("/Rotate") is None
    assert reader.pages[3].get("/Rotate") == 270


def test_rotate_portrait_pages_noop_on_landscape_only(tmp_path: Path) -> None:
    pdf = tmp_path / "wide.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=400, height=200)
    with pdf.open("wb") as f:
        writer.write(f)

    assert rotate_portrait_pages(pdf) == 0
    reader = PdfReader(str(pdf))
    assert reader.pages[0].get("/Rotate") is None
