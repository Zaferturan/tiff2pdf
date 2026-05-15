"""Modal dialogs (main thread only)."""

from __future__ import annotations

import customtkinter as ctk

from collections.abc import Callable

from tiff2pdf_gui.conflicts import ConflictChoice


class ConflictDialog(ctk.CTkToplevel):
    """Ask whether to overwrite an existing PDF."""

    def __init__(
        self,
        parent: ctk.CTk,
        relative_path: str,
        on_result: Callable[["ConflictDialog"], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self.title("Dosya zaten var")
        self.geometry("520x220")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._on_result = on_result
        self.choice: ConflictChoice | None = None
        self.apply_to_all = False

        ctk.CTkLabel(
            self,
            text="Bu konumda aynı isimde bir PDF zaten var:",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            self,
            text=relative_path,
            anchor="w",
            font=ctk.CTkFont(weight="bold"),
            wraplength=480,
        ).pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(
            self,
            text="Ne yapılsın?",
            anchor="w",
            text_color="gray70",
        ).pack(fill="x", padx=20, pady=(0, 8))

        self._apply_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self,
            text="Seçimi kalan tüm çakışan dosyalar için de uygula",
            variable=self._apply_var,
        ).pack(anchor="w", padx=20, pady=4)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=16)
        ctk.CTkButton(row, text="Üzerine yaz", width=120, command=lambda: self._done(ConflictChoice.OVERWRITE)).pack(
            side="left", padx=4
        )
        ctk.CTkButton(row, text="Atla", width=120, fg_color="gray40", command=lambda: self._done(ConflictChoice.SKIP)).pack(
            side="left", padx=4
        )
        ctk.CTkButton(row, text="İptal", width=120, fg_color="#8B0000", command=lambda: self._done(ConflictChoice.CANCEL)).pack(
            side="left", padx=4
        )

        self.protocol("WM_DELETE_WINDOW", lambda: self._done(ConflictChoice.CANCEL))
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def _done(self, choice: ConflictChoice) -> None:
        self.choice = choice
        self.apply_to_all = bool(self._apply_var.get())
        self.grab_release()
        if self._on_result is not None:
            self._on_result(self)
        self.destroy()
