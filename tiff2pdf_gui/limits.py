"""Input file size limits."""

from __future__ import annotations

# Maximum single TIFF input size (2 GiB).
MAX_TIFF_BYTES = 2 * 1024 * 1024 * 1024

# Log a note when conversion may take longer.
LARGE_FILE_BYTES = 100 * 1024 * 1024


def format_bytes(num: int) -> str:
    if num >= 1024**3:
        return f"{num / 1024**3:.2f} GB"
    if num >= 1024**2:
        return f"{num / 1024**2:.1f} MB"
    if num >= 1024:
        return f"{num / 1024:.1f} KB"
    return f"{num} B"
