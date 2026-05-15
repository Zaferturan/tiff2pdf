"""Conflict resolution when an output PDF already exists."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum


class ConflictChoice(Enum):
    OVERWRITE = "overwrite"
    SKIP = "skip"
    CANCEL = "cancel"


@dataclass
class PendingConflict:
    relative: str
    event: threading.Event = field(default_factory=threading.Event)
    choice: ConflictChoice | None = None
    apply_to_all: bool = False
