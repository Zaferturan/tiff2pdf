"""Bridge worker-thread conflict checks to the Tk main thread."""

from __future__ import annotations

import queue
import threading
from typing import TYPE_CHECKING

from tiff2pdf_gui.conflicts import ConflictChoice, PendingConflict

if TYPE_CHECKING:
    pass


class ConflictBridge:
    def __init__(self, event_queue: queue.Queue) -> None:
        self._event_queue = event_queue
        self._overwrite_all = False
        self._skip_all = False
        self._lock = threading.Lock()

    def reset(self) -> None:
        with self._lock:
            self._overwrite_all = False
            self._skip_all = False

    def resolve(self, relative_path: str) -> ConflictChoice:
        with self._lock:
            if self._overwrite_all:
                return ConflictChoice.OVERWRITE
            if self._skip_all:
                return ConflictChoice.SKIP

        pending = PendingConflict(relative=relative_path)
        self._event_queue.put({"type": "conflict", "pending": pending})
        pending.event.wait()

        choice = pending.choice or ConflictChoice.CANCEL
        if pending.apply_to_all:
            with self._lock:
                if choice == ConflictChoice.OVERWRITE:
                    self._overwrite_all = True
                elif choice == ConflictChoice.SKIP:
                    self._skip_all = True
        return choice
