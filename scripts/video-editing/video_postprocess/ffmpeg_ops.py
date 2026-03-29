from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def ensure_command_available(command_name: str) -> str:
    resolved = shutil.which(command_name)
    if not resolved:
        raise RuntimeError(f"required command not found: {command_name}")
    return resolved


def escape_ass_filter_path(path_value: str | Path) -> str:
    normalized = str(path_value).replace("\\", "/")
    if len(normalized) >= 2 and normalized[1] == ":":
        normalized = normalized[0] + r"\:" + normalized[2:]
    return normalized


def build_render_command(
    ffmpeg_bin: str,
    video_path: Path,
    ass_path: Path,
    output_path: Path,
    speed: float = 1.25,
    intro_video: Path | None = None,
) -> list[str]:
    video_filter = f"subtitles='{escape_ass_filter_path(ass_path)}',setpts={1 / speed:.6f}*PTS"
    audio_filter = f"atempo={speed}"
    if intro_video is not None:
        filter_complex = (
            f"[1:v]{video_filter}[mainv];"
            f"[1:a]{audio_filter}[maina];"
            "[0:v][0:a][mainv][maina]concat=n=2:v=1:a=1[outv][outa]"
        )
        return [
            ffmpeg_bin,
            "-y",
            "-i",
            str(intro_video),
            "-i",
            str(video_path),
            "-filter_complex",
            filter_complex,
            "-map",
            "[outv]",
            "-map",
            "[outa]",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output_path),
        ]
    return [
        ffmpeg_bin,
        "-y",
        "-i",
        str(video_path),
        "-vf",
        video_filter,
        "-af",
        audio_filter,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(output_path),
    ]


def build_cover_frame_command(ffmpeg_bin: str, video_path: Path, output_path: Path) -> list[str]:
    return [
        ffmpeg_bin,
        "-y",
        "-i",
        str(video_path),
        "-vf",
        "thumbnail=180",
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output_path),
    ]


def build_intro_command(ffmpeg_bin: str, image_path: Path, output_path: Path, duration: float = 0.5) -> list[str]:
    return [
        ffmpeg_bin,
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-t",
        f"{duration:g}",
        "-shortest",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(output_path),
    ]


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "command failed")
