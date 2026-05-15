"""CustomTkinter GUI for batch TIFF→PDF conversion."""

from __future__ import annotations

import math
import queue
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from tiff2pdf_gui import __version__
from tiff2pdf_gui.conflict_bridge import ConflictBridge
from tiff2pdf_gui.conflicts import ConflictChoice, PendingConflict
from tiff2pdf_gui.dialogs import ConflictDialog
from tiff2pdf_gui.paths import tiff2pdf_executable
from tiff2pdf_gui.scanner import list_tiff_files
from tiff2pdf_gui.worker import JobConfig, run_conversion


class Tiff2PdfApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"TIFF → PDF  v{__version__}")
        self.geometry("920x680")
        self.minsize(720, 560)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self._input_var = ctk.StringVar(value="")
        self._output_var = ctk.StringVar(value="")
        self._tiff_files: list[Path] = []
        self._event_queue: queue.Queue = queue.Queue()
        self._cancel_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._running = False
        self._pulse_after_id: str | None = None
        self._pulse_phase = 0.0
        self._rescan_after: str | None = None
        self._conflict_bridge = ConflictBridge(self._event_queue)
        self._conflict_dialog: ConflictDialog | None = None

        self._build_ui()
        self.after(80, self._poll_queue)

    def _build_ui(self) -> None:
        title = ctk.CTkLabel(self, text="TIFF dosyalarını PDF’e dönüştür", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(anchor="w", padx=16, pady=(16, 8))

        # Input row
        f_in = ctk.CTkFrame(self, fg_color="transparent")
        f_in.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(f_in, text="Girdi klasörü", width=110).pack(side="left")
        self._entry_in = ctk.CTkEntry(f_in, textvariable=self._input_var, placeholder_text="TIFF’lerin bulunduğu klasör…")
        self._entry_in.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._btn_browse_in = ctk.CTkButton(f_in, text="Gözat…", width=100, command=self._browse_input)
        self._btn_browse_in.pack(side="left")

        # Output row
        f_out = ctk.CTkFrame(self, fg_color="transparent")
        f_out.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(f_out, text="Çıktı klasörü", width=110).pack(side="left")
        self._entry_out = ctk.CTkEntry(f_out, textvariable=self._output_var, placeholder_text="PDF’lerin yazılacağı kök klasör…")
        self._entry_out.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._btn_browse_out = ctk.CTkButton(f_out, text="Gözat…", width=100, command=self._browse_output)
        self._btn_browse_out.pack(side="left")

        self._count_label = ctk.CTkLabel(self, text="TIFF sayısı: —", anchor="w")
        self._count_label.pack(fill="x", padx=16, pady=(8, 4))

        ctk.CTkLabel(
            self,
            text="Aynı isimde PDF varsa her dosya için sorulur.",
            anchor="w",
            text_color="gray60",
        ).pack(fill="x", padx=16, pady=4)

        # Overall progress
        ctk.CTkLabel(self, text="Genel ilerleme", anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        self._overall_bar = ctk.CTkProgressBar(self)
        self._overall_bar.pack(fill="x", padx=16, pady=4)
        self._overall_bar.set(0)
        self._overall_text = ctk.CTkLabel(self, text="", anchor="w")
        self._overall_text.pack(fill="x", padx=16, pady=0)

        # Current file
        ctk.CTkLabel(self, text="Geçerli dosya", anchor="w").pack(fill="x", padx=16, pady=(12, 0))
        self._file_bar = ctk.CTkProgressBar(self)
        self._file_bar.pack(fill="x", padx=16, pady=4)
        self._file_bar.set(0)
        self._file_label = ctk.CTkLabel(self, text="—", anchor="w", wraplength=860)
        self._file_label.pack(fill="x", padx=16, pady=0)

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=16)
        self._btn_start = ctk.CTkButton(btn_row, text="Başlat", width=140, command=self._start)
        self._btn_start.pack(side="left", padx=12, pady=6)
        self._btn_cancel = ctk.CTkButton(btn_row, text="İptal", width=140, fg_color="gray40", command=self._request_cancel, state="disabled")
        self._btn_cancel.pack(side="left", padx=12, pady=6)

        ctk.CTkLabel(self, text="Günlük", anchor="w").pack(fill="x", padx=16, pady=(4, 0))
        self._log = ctk.CTkTextbox(self, height=200, font=ctk.CTkFont(family="Consolas", size=12))
        self._log.pack(fill="both", expand=True, padx=16, pady=8)

        hint = ctk.CTkLabel(
            self,
            text="Alt klasör yapısı çıktıda korunur.",
            anchor="w",
            text_color="gray60",
            wraplength=880,
        )
        hint.pack(fill="x", padx=16, pady=(0, 12))

        self._input_var.trace_add("write", lambda *_: self._schedule_rescan())
        self._entry_in.bind("<FocusOut>", lambda e: self._rescan_input())

    def _schedule_rescan(self) -> None:
        if self._rescan_after is not None:
            self.after_cancel(self._rescan_after)
        self._rescan_after = self.after(350, self._rescan_rescan_done)

    def _rescan_rescan_done(self) -> None:
        self._rescan_after = None
        self._rescan_input()

    def _browse_input(self) -> None:
        d = filedialog.askdirectory(title="Girdi klasörünü seçin")
        if d:
            self._input_var.set(d)
            self._rescan_input()

    def _browse_output(self) -> None:
        d = filedialog.askdirectory(title="Çıktı klasörünü seçin")
        if d:
            self._output_var.set(d)

    def _rescan_input(self) -> None:
        p = self._input_var.get().strip()
        if not p:
            self._tiff_files = []
            self._count_label.configure(text="TIFF sayısı: —")
            return
        root = Path(p)
        if not root.is_dir():
            self._tiff_files = []
            self._count_label.configure(text="TIFF sayısı: — (geçersiz klasör)")
            return
        self._tiff_files = list_tiff_files(root)
        n = len(self._tiff_files)
        self._count_label.configure(text=f"TIFF sayısı: {n}")

    def _log_line(self, line: str) -> None:
        self._log.insert("end", line + "\n")
        self._log.see("end")

    def _set_running(self, running: bool) -> None:
        self._running = running
        state = "disabled" if running else "normal"
        self._btn_start.configure(state=state)
        self._btn_cancel.configure(state="normal" if running else "disabled")
        self._entry_in.configure(state=state)
        self._entry_out.configure(state=state)
        self._btn_browse_in.configure(state=state)
        self._btn_browse_out.configure(state=state)

    def _start(self) -> None:
        if self._running:
            return
        in_p = self._input_var.get().strip()
        out_p = self._output_var.get().strip()
        if not in_p or not out_p:
            messagebox.showwarning("Eksik bilgi", "Girdi ve çıktı klasörlerini seçin.", parent=self)
            return
        input_root = Path(in_p)
        output_root = Path(out_p)
        if not input_root.is_dir():
            messagebox.showerror("Hata", "Girdi klasörü bulunamadı.", parent=self)
            return
        try:
            tiff2pdf_executable()
        except FileNotFoundError as e:
            messagebox.showerror("tiff2pdf yok", str(e), parent=self)
            return

        self._rescan_input()
        if not self._tiff_files:
            messagebox.showinfo("TIFF yok", "Seçilen klasörde TIFF dosyası bulunamadı.", parent=self)
            return

        self._log.delete("1.0", "end")
        self._log_line("İşlem başlıyor…")
        self._cancel_event.clear()
        self._conflict_bridge.reset()
        self._set_running(True)
        self._overall_bar.set(0)
        self._overall_text.configure(text="0 / 0")
        self._file_bar.set(0)
        self._file_label.configure(text="—")

        cfg = JobConfig(
            input_root=input_root,
            output_root=output_root,
            files=list(self._tiff_files),
            resolve_conflict=self._conflict_bridge.resolve,
        )
        self._worker = threading.Thread(
            target=run_conversion,
            args=(cfg, self._event_queue, self._cancel_event, self._log_line_safe),
            daemon=True,
        )
        self._worker.start()
        self._start_file_pulse()

    def _log_line_safe(self, line: str) -> None:
        self._event_queue.put({"type": "log", "line": line})

    def _request_cancel(self) -> None:
        if self._running:
            self._cancel_event.set()
            self._log_line_safe("İptal istendi…")

    def _start_file_pulse(self) -> None:
        self._pulse_phase = 0.0
        self._pulse_tick()

    def _stop_file_pulse(self) -> None:
        if self._pulse_after_id is not None:
            self.after_cancel(self._pulse_after_id)
            self._pulse_after_id = None
        self._file_bar.set(0)

    def _pulse_tick(self) -> None:
        if not self._running:
            self._stop_file_pulse()
            return
        self._pulse_phase += 0.25
        v = 0.35 + 0.3 * (math.sin(self._pulse_phase) * 0.5 + 0.5)
        self._file_bar.set(v)
        self._pulse_after_id = self.after(120, self._pulse_tick)

    def _poll_queue(self) -> None:
        try:
            while True:
                msg = self._event_queue.get_nowait()
                self._handle_message(msg)
        except queue.Empty:
            pass
        self.after(80, self._poll_queue)

    def _handle_message(self, msg: dict) -> None:
        t = msg.get("type")
        if t == "log":
            self._log_line(str(msg.get("line", "")))
            return
        if t == "conflict":
            self._show_conflict_dialog(msg["pending"])
            return
        if t == "file_start":
            total = int(msg["total"])
            idx = int(msg["index"])
            rel = str(msg.get("relative", ""))
            self._overall_text.configure(text=f"{idx} / {total}")
            if total:
                self._overall_bar.set(max(0, min(1, (idx - 1) / total)))
            self._file_label.configure(text=rel)
            self._file_bar.set(0.15)
            return
        if t == "file_done":
            total = int(msg["total"])
            idx = int(msg["index"])
            if total:
                self._overall_bar.set(max(0, min(1, idx / total)))
            self._overall_text.configure(text=f"{idx} / {total}")
            self._file_bar.set(1.0)
            return
        if t == "cancelled":
            self._stop_file_pulse()
            self._set_running(False)
            conv = int(msg.get("converted", 0))
            sk = int(msg.get("skipped", 0))
            self._log_line(f"İptal edildi. Tamamlanan dönüşüm: {conv}, atlanan: {sk}.")
            messagebox.showinfo("İptal", "İşlem iptal edildi.", parent=self)
            return
        if t == "finished":
            self._stop_file_pulse()
            self._set_running(False)
            self._overall_bar.set(1.0)
            errors = msg.get("errors") or []
            conv = int(msg.get("converted", 0))
            sk = int(msg.get("skipped", 0))
            out_p = self._output_var.get().strip()
            if errors and out_p:
                log_path = Path(out_p) / "errors.log"
                try:
                    log_path.write_text(
                        "\n".join(f"{a}\t{b}" for a, b in errors),
                        encoding="utf-8",
                    )
                    self._log_line(f"Hatalar yazıldı: {log_path}")
                except OSError as e:
                    self._log_line(f"errors.log yazılamadı: {e}")
            self._log_line(f"Bitti. Dönüştürülen: {conv}, atlanan: {sk}, hata: {len(errors)}.")
            if errors:
                messagebox.showwarning(
                    "Tamamlandı (hatalar var)",
                    f"{len(errors)} dosyada hata oluştu. Ayrıntılar günlükte ve errors.log dosyasında.",
                    parent=self,
                )
            else:
                messagebox.showinfo("Tamamlandı", "Tüm dosyalar işlendi.", parent=self)
            return

    def _show_conflict_dialog(self, pending: PendingConflict) -> None:
        if self._conflict_dialog is not None:
            try:
                self._conflict_dialog.destroy()
            except Exception:
                pass

        def on_result(dlg: ConflictDialog) -> None:
            self._conflict_dialog = None
            pending.choice = dlg.choice or ConflictChoice.CANCEL
            pending.apply_to_all = dlg.apply_to_all
            pending.event.set()

        self._conflict_dialog = ConflictDialog(self, pending.relative, on_result=on_result)


def run_app() -> None:
    app = Tiff2PdfApp()
    app.mainloop()
