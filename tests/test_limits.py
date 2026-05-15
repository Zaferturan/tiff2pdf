"""Tests for file size limits."""

from tiff2pdf_gui.limits import MAX_TIFF_BYTES, TIFF2PDF_MEMORY_LIMIT_BYTES, format_bytes


def test_max_is_2gb() -> None:
    assert MAX_TIFF_BYTES == 2 * 1024**3


def test_tiff2pdf_memory_matches_max() -> None:
    assert TIFF2PDF_MEMORY_LIMIT_BYTES == MAX_TIFF_BYTES
    assert TIFF2PDF_MEMORY_LIMIT_BYTES > 268_435_456


def test_format_bytes() -> None:
    assert "MB" in format_bytes(450 * 1024**2)
    assert "GB" in format_bytes(MAX_TIFF_BYTES)
