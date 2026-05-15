"""Logo loading for main window."""

from __future__ import annotations

import customtkinter as ctk
from PIL import Image

from tiff2pdf_gui.paths import asset_path


def header_logo(size: tuple[int, int] = (56, 66)) -> ctk.CTkImage:
    pil = Image.open(asset_path("logo.png")).convert("RGBA")
    pil.thumbnail(size, Image.Resampling.LANCZOS)
    return ctk.CTkImage(pil, size=pil.size)
