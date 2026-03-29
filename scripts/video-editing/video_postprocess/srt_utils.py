from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


TIMESTAMP_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2},\d{3})$"
)


@dataclass(frozen=True)
class SubtitleEntry:
    index: int
    start_ms: int
    end_ms: int
    text: str


def _timestamp_to_ms(value: str) -> int:
    hours, minutes, seconds_ms = value.split(":")
    seconds, millis = seconds_ms.split(",")
    return (
        int(hours) * 3_600_000
        + int(minutes) * 60_000
        + int(seconds) * 1_000
        + int(millis)
    )


def load_srt(srt_path: Path) -> list[SubtitleEntry]:
    content = Path(srt_path).read_text(encoding="utf-8").lstrip("\ufeff").strip()
    blocks = re.split(r"\r?\n\r?\n", content)
    entries: list[SubtitleEntry] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            raise ValueError(f"invalid subtitle block: {block}")

        index = int(lines[0])
        timestamp_match = TIMESTAMP_RE.match(lines[1])
        if not timestamp_match:
            raise ValueError(f"invalid timestamp line: {lines[1]}")

        start_ms = _timestamp_to_ms(timestamp_match.group("start"))
        end_ms = _timestamp_to_ms(timestamp_match.group("end"))
        if end_ms <= start_ms:
            raise ValueError("subtitle end must be after start")

        entries.append(
            SubtitleEntry(
                index=index,
                start_ms=start_ms,
                end_ms=end_ms,
                text="\n".join(lines[2:]),
            )
        )

    return entries
