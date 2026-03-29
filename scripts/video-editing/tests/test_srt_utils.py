from pathlib import Path

import pytest

from video_postprocess.srt_utils import SubtitleEntry, load_srt


def test_load_srt_parses_entries_in_order(tmp_path: Path) -> None:
    srt_path = tmp_path / "clip.edit.srt"
    srt_path.write_text(
        "1\n"
        "00:00:00,500 --> 00:00:02,000\n"
        "第一句\n"
        "\n"
        "2\n"
        "00:00:02,100 --> 00:00:03,600\n"
        "第二句\n",
        encoding="utf-8",
    )

    entries = load_srt(srt_path)

    assert entries == [
        SubtitleEntry(index=1, start_ms=500, end_ms=2000, text="第一句"),
        SubtitleEntry(index=2, start_ms=2100, end_ms=3600, text="第二句"),
    ]


def test_load_srt_rejects_invalid_timestamp_block(tmp_path: Path) -> None:
    srt_path = tmp_path / "broken.srt"
    srt_path.write_text(
        "1\n"
        "not-a-timestamp\n"
        "字幕\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="timestamp"):
        load_srt(srt_path)


def test_load_srt_rejects_end_before_start(tmp_path: Path) -> None:
    srt_path = tmp_path / "broken.srt"
    srt_path.write_text(
        "1\n"
        "00:00:03,000 --> 00:00:01,000\n"
        "字幕\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="after start"):
        load_srt(srt_path)


def test_load_srt_accepts_utf8_bom(tmp_path: Path) -> None:
    srt_path = tmp_path / "bom.srt"
    srt_path.write_text(
        "\ufeff1\n"
        "00:00:00,000 --> 00:00:01,000\n"
        "测试字幕\n",
        encoding="utf-8",
    )

    entries = load_srt(srt_path)

    assert entries[0].index == 1
    assert entries[0].text == "测试字幕"
