"""Startup splash screen."""

from __future__ import annotations

import customtkinter as ctk
from PIL import Image

from tiff2pdf_gui.paths import asset_path

SPLASH_MS = 3000
SPLASH_TEXT = (
    "Nilüfer Belediyesi Bilgi İşlem Müdürlüğü'nün\n"
    "tüm kurumlara hediyesidir."
)


def _logo_image(max_size: tuple[int, int] = (260, 300)) -> ctk.CTkImage:
    pil = Image.open(asset_path("logo.png")).convert("RGBA")
    pil.thumbnail(max_size, Image.Resampling.LANCZOS)
    return ctk.CTkImage(pil, size=pil.size)


class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        width, height = 480, 420
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - width) // 2)
        y = max(0, (sh - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        frame = ctk.CTkFrame(self, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(frame, text="", image=_logo_image()).pack(pady=(28, 12))
        ctk.CTkLabel(
            frame,
            text=SPLASH_TEXT,
            font=ctk.CTkFont(size=14),
            justify="center",
            wraplength=420,
        ).pack(padx=24, pady=(0, 28))

        self.update_idletasks()


def show_splash_then(main_factory) -> None:
    """Show splash for SPLASH_MS, then run main_factory() (starts mainloop)."""
    root = ctk.CTk()
    root.withdraw()
    root.geometry("920x680")

    splash = SplashScreen(root)
    splash.update()

    def open_main() -> None:
        splash.destroy()
        root.destroy()
        app = main_factory()
        app.mainloop()

    root.after(SPLASH_MS, open_main)
    root.mainloop()
