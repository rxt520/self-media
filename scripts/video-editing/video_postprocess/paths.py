from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OutputPaths:
    base_name: str
    out_dir: Path
    auto_srt: Path
    edit_srt: Path
    ass_subtitle: Path
    final_video: Path
    cover_frame: Path
    cover_image: Path
    intro_video: Path
    tmp_dir: Path


def derive_output_paths(video_path: Path, out_dir: Path) -> OutputPaths:
    video = Path(video_path)
    if not video.exists():
        raise FileNotFoundError(f"input video not found: {video}")

    target_dir = Path(out_dir)
    base_name = video.stem
    return OutputPaths(
        base_name=base_name,
        out_dir=target_dir,
        auto_srt=target_dir / f"{base_name}.auto.srt",
        edit_srt=target_dir / f"{base_name}.edit.srt",
        ass_subtitle=target_dir / f"{base_name}.ass",
        final_video=target_dir / f"{base_name}.final.mp4",
        cover_frame=target_dir / f"{base_name}.cover-frame.jpg",
        cover_image=target_dir / f"{base_name}.cover.jpg",
        intro_video=target_dir / f"{base_name}.intro.mp4",
        tmp_dir=target_dir / "tmp",
    )
