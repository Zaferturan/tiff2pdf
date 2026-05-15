"""Discover TIFF files and map output paths."""

from __future__ import annotations

from pathlib import Path

TIFF_SUFFIXES = frozenset({".tif", ".tiff"})


def list_tiff_files(input_root: Path) -> list[Path]:
    """Recursive, stable-sorted list of TIFF paths under input_root."""
    root = input_root.resolve()
    found: list[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TIFF_SUFFIXES:
            found.append(p)
    return sorted(found, key=lambda x: str(x).lower())


def output_pdf_path(input_root: Path, output_root: Path, tif_path: Path) -> Path:
    """Mirror directory layout: input_root/a/b/x.tif -> output_root/a/b/x.pdf."""
    rel = tif_path.resolve().relative_to(input_root.resolve())
    return (output_root / rel).with_suffix(".pdf")
