"""Unit tests for TIFF discovery and output path mapping."""

from pathlib import Path

from tiff2pdf_gui.scanner import list_tiff_files, output_pdf_path


def test_list_tiff_recursive(tmp_path: Path) -> None:
    (tmp_path / "a.tif").write_bytes(b"x")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.TIFF").write_bytes(b"y")
    (sub / "note.txt").write_bytes(b"z")
    names = [p.name for p in list_tiff_files(tmp_path)]
    assert sorted(names) == ["a.tif", "b.TIFF"]


def test_output_pdf_mirrors_tree(tmp_path: Path) -> None:
    inp = tmp_path / "in"
    out = tmp_path / "out"
    tif = inp / "a" / "b" / "scan.tif"
    tif.parent.mkdir(parents=True)
    tif.write_bytes(b"x")
    pdf = output_pdf_path(inp, out, tif)
    assert pdf == out / "a" / "b" / "scan.pdf"
