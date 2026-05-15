"""Worker tests with mocked subprocess."""

from __future__ import annotations

import queue
import threading
from pathlib import Path
from unittest.mock import patch

from tiff2pdf_gui.conflicts import ConflictChoice
from tiff2pdf_gui.worker import JobConfig, run_conversion


def test_skip_on_conflict(tmp_path: Path) -> None:
    inp = tmp_path / "in"
    out = tmp_path / "out"
    inp.mkdir()
    tif = inp / "doc.tif"
    tif.write_bytes(b"x")
    pdf = out / "doc.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"pdf")

    cfg = JobConfig(
        input_root=inp,
        output_root=out,
        files=[tif],
        resolve_conflict=lambda _rel: ConflictChoice.SKIP,
    )
    q: queue.Queue = queue.Queue()
    cancel = threading.Event()
    logs: list[str] = []

    with patch("tiff2pdf_gui.worker.tiff2pdf_executable", return_value=tmp_path / "fake" / "tiff2pdf"):
        run_conversion(cfg, q, cancel, logs.append)

    msgs = []
    while not q.empty():
        msgs.append(q.get())
    assert msgs[-1]["skipped"] == 1
    assert msgs[-1]["converted"] == 0


def test_cancel_on_conflict(tmp_path: Path) -> None:
    inp = tmp_path / "in"
    out = tmp_path / "out"
    inp.mkdir()
    tif = inp / "doc.tif"
    tif.write_bytes(b"x")
    pdf = out / "doc.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"pdf")

    cfg = JobConfig(
        input_root=inp,
        output_root=out,
        files=[tif],
        resolve_conflict=lambda _rel: ConflictChoice.CANCEL,
    )
    q: queue.Queue = queue.Queue()
    cancel = threading.Event()

    with patch("tiff2pdf_gui.worker.tiff2pdf_executable", return_value=tmp_path / "fake" / "tiff2pdf"):
        run_conversion(cfg, q, cancel, lambda _s: None)

    msgs = []
    while not q.empty():
        msgs.append(q.get())
    assert any(m.get("type") == "cancelled" for m in msgs)
