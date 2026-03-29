from pathlib import Path

import pytest

from video_postprocess.ffmpeg_ops import (
    build_cover_frame_command,
    build_intro_command,
    build_render_command,
    ensure_command_available,
    escape_ass_filter_path,
)


def test_ensure_command_available_returns_resolved_path() -> None:
    resolved = ensure_command_available("python")

    assert resolved
    assert Path(resolved).name.lower().startswith("python")


def test_ensure_command_available_raises_for_missing_binary() -> None:
    with pytest.raises(RuntimeError, match="not found"):
        ensure_command_available("definitely-missing-binary-xyz")


def test_escape_ass_filter_path_handles_windows_drive_and_backslashes() -> None:
    escaped = escape_ass_filter_path(r"C:\clips\demo.ass")

    assert escaped == "C\\:/clips/demo.ass"


def test_build_render_command_uses_ass_subtitles_and_125x_speed(tmp_path: Path) -> None:
    video_path = tmp_path / "clip.mp4"
    ass_path = tmp_path / "clip.ass"
    output_path = tmp_path / "clip.final.mp4"

    command = build_render_command(
        ffmpeg_bin="ffmpeg",
        video_path=video_path,
        ass_path=ass_path,
        output_path=output_path,
        speed=1.25,
    )

    command_text = " ".join(str(part) for part in command)
    video_filter = command[command.index("-vf") + 1]
    assert command[:3] == ["ffmpeg", "-y", "-i"]
    assert "subtitles=" in command_text
    assert "setpts=0.800000*PTS" in command_text
    assert "atempo=1.25" in command_text
    assert video_filter.startswith("subtitles='")
    assert ",setpts=0.800000*PTS" in video_filter
    assert str(output_path) == command[-1]


def test_build_render_command_with_intro_uses_concat_filter(tmp_path: Path) -> None:
    video_path = tmp_path / "clip.mp4"
    ass_path = tmp_path / "clip.ass"
    intro_path = tmp_path / "clip.intro.mp4"
    output_path = tmp_path / "clip.final.mp4"

    command = build_render_command(
        ffmpeg_bin="ffmpeg",
        video_path=video_path,
        ass_path=ass_path,
        output_path=output_path,
        speed=1.25,
        intro_video=intro_path,
    )

    command_text = " ".join(str(part) for part in command)
    filter_complex = command[command.index("-filter_complex") + 1]
    assert command.count("-i") == 2
    assert str(intro_path) in command_text
    assert "[1:v]subtitles=" in filter_complex
    assert "concat=n=2:v=1:a=1" in filter_complex


def test_build_cover_frame_command_uses_thumbnail_filter(tmp_path: Path) -> None:
    video_path = tmp_path / "clip.mp4"
    output_path = tmp_path / "clip.cover-frame.jpg"

    command = build_cover_frame_command("ffmpeg", video_path, output_path)

    assert command[:3] == ["ffmpeg", "-y", "-i"]
    assert "thumbnail" in command[command.index("-vf") + 1]
    assert command[-1] == str(output_path)


def test_build_intro_command_creates_short_silent_clip(tmp_path: Path) -> None:
    image_path = tmp_path / "clip.cover.jpg"
    output_path = tmp_path / "clip.intro.mp4"

    command = build_intro_command("ffmpeg", image_path, output_path, duration=0.5)
    command_text = " ".join(str(part) for part in command)

    assert command[:3] == ["ffmpeg", "-y", "-loop"]
    assert "anullsrc" in command_text
    assert "0.5" in command_text
    assert command[-1] == str(output_path)
