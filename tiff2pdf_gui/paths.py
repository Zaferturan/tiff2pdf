"""Resolve bundled `tiff2pdf` and vendor directory (dev vs PyInstaller)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def project_root() -> Path:
    """Workspace root (parent of `tiff2pdf_gui` package)."""
    return Path(__file__).resolve().parent.parent


def vendor_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "vendor"
    return project_root() / "vendor"


def tiff2pdf_executable() -> Path:
    """
    Return path to `tiff2pdf` binary.

    Windows release: `vendor/tiff2pdf.exe` (+ DLLs alongside it).
    Development on Linux/macOS: `tiff2pdf` on PATH if .exe missing.
    """
    vendor = vendor_dir()
    win = vendor / "tiff2pdf.exe"
    if win.exists():
        return win
    posix = vendor / "tiff2pdf"
    if posix.exists():
        return posix
    which = shutil.which("tiff2pdf")
    if which:
        return Path(which)
    raise FileNotFoundError(
        "tiff2pdf bulunamadı. `vendor` klasörüne Windows için tiff2pdf.exe ve "
        "gerekli DLL dosyalarını koyun (bkz. vendor/README.txt)."
    )
