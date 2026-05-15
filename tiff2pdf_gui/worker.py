"""Background conversion using `tiff2pdf` subprocess."""

from __future__ import annotations

import queue
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from tiff2pdf_gui.conflicts import ConflictChoice
from tiff2pdf_gui.paths import tiff2pdf_executable
from tiff2pdf_gui.scanner import output_pdf_path


@dataclass
class JobConfig:
    input_root: Path
    output_root: Path
    files: list[Path]
    resolve_conflict: Callable[[str], ConflictChoice]


def _subprocess_flags() -> int:
    if sys.platform == "win32":
        try:
            return subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
        except AttributeError:
            return 0
    return 0


def run_conversion(
    cfg: JobConfig,
    event_queue: queue.Queue,
    cancel: threading.Event,
    log_line: Callable[[str], None],
) -> None:
    """Run in a worker thread; posts dict messages to event_queue."""
    exe = tiff2pdf_executable()
    total = len(cfg.files)
    errors: list[tuple[str, str]] = []
    skipped = 0
    converted = 0

    try:
        for idx, tif_path in enumerate(cfg.files, start=1):
            if cancel.is_set():
                event_queue.put({"type": "cancelled", "converted": converted, "skipped": skipped})
                return

            rel = str(tif_path.resolve().relative_to(cfg.input_root.resolve()))
            pdf_path = output_pdf_path(cfg.input_root, cfg.output_root, tif_path)
            event_queue.put(
                {
                    "type": "file_start",
                    "index": idx,
                    "total": total,
                    "tif": str(tif_path),
                    "relative": rel,
                    "pdf": str(pdf_path),
                }
            )

            if pdf_path.exists():
                choice = cfg.resolve_conflict(rel)
                if choice == ConflictChoice.CANCEL:
                    event_queue.put({"type": "cancelled", "converted": converted, "skipped": skipped})
                    return
                if choice == ConflictChoice.SKIP:
                    skipped += 1
                    log_line(f"Atlandı (mevcut): {rel}")
                    event_queue.put(
                        {
                            "type": "file_done",
                            "index": idx,
                            "total": total,
                            "ok": True,
                            "skipped": True,
                        }
                    )
                    continue

            try:
                pdf_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                errors.append((rel, str(e)))
                log_line(f"HATA dizin: {rel} — {e}")
                event_queue.put(
                    {
                        "type": "file_done",
                        "index": idx,
                        "total": total,
                        "ok": False,
                        "skipped": False,
                    }
                )
                continue

            cmd = [str(exe), "-o", str(pdf_path), str(tif_path)]
            creationflags = _subprocess_flags()
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(exe.parent),
                    creationflags=creationflags,
                )
            except OSError as e:
                errors.append((rel, str(e)))
                log_line(f"HATA başlatma: {rel} — {e}")
                event_queue.put(
                    {
                        "type": "file_done",
                        "index": idx,
                        "total": total,
                        "ok": False,
                        "skipped": False,
                    }
                )
                continue

            while proc.poll() is None:
                if cancel.is_set():
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    event_queue.put({"type": "cancelled", "converted": converted, "skipped": skipped})
                    return
                time.sleep(0.05)

            stdout_b, stderr_b = proc.communicate()
            rc = proc.returncode or 0
            if rc != 0:
                err = (stderr_b or b"").decode(errors="replace")
                out = (stdout_b or b"").decode(errors="replace")
                detail = (err or out or f"exit {rc}").strip()
                errors.append((rel, detail[:2000]))
                log_line(f"HATA dönüşüm: {rel} — {detail[:500]}")
                event_queue.put(
                    {
                        "type": "file_done",
                        "index": idx,
                        "total": total,
                        "ok": False,
                        "skipped": False,
                    }
                )
            else:
                converted += 1
                log_line(f"Tamam: {rel}")
                event_queue.put(
                    {
                        "type": "file_done",
                        "index": idx,
                        "total": total,
                        "ok": True,
                        "skipped": False,
                    }
                )
    except Exception as e:  # noqa: BLE001 — surface unexpected failures
        errors.append(("<iş>", str(e)))
        log_line(f"KRİTİK: {e}")

    event_queue.put(
        {
            "type": "finished",
            "errors": errors,
            "converted": converted,
            "skipped": skipped,
        }
    )
