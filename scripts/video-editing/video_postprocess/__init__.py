from __future__ import annotations

import argparse
from pathlib import Path

from video_postprocess import ass_writer
from video_postprocess import cover_generator
from video_postprocess import ffmpeg_ops
from video_postprocess import transcribe
from video_postprocess.paths import derive_output_paths
from video_postprocess.srt_utils import load_srt


def _parse_highlight_terms(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return [term.strip() for term in raw_value.split(",") if term.strip()]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Talking-head video postprocess tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    transcribe_parser = subparsers.add_parser("transcribe", help="Generate editable auto subtitles from a video")
    transcribe_parser.add_argument("video", help="Input video path")
    transcribe_parser.add_argument("--out-dir", required=True, help="Output directory")
    transcribe_parser.add_argument("--language", default="zh", help="Whisper language")
    transcribe_parser.add_argument("--model-size", default="medium", help="Whisper model size")
    transcribe_parser.add_argument("--device", default="auto", help="Whisper device")

    render_parser = subparsers.add_parser("render", help="Render final video with styled burned subtitles")
    render_parser.add_argument("video", help="Input video path")
    render_parser.add_argument("--srt", required=True, help="Corrected SRT path")
    render_parser.add_argument("--out-dir", required=True, help="Output directory")
    render_parser.add_argument("--speed", type=float, default=1.25, help="Playback speed")
    render_parser.add_argument("--highlight", help="Comma-separated highlight terms")
    render_parser.add_argument("--cover-title", help="Cover title text")
    render_parser.add_argument("--cover-subtitle", default="", help="Cover subtitle text")
    render_parser.add_argument("--cover-font", default="Microsoft YaHei", help="Cover font name or font path")
    render_parser.add_argument("--intro-duration", type=float, default=0.5, help="Static intro duration in seconds")
    return parser


def _handle_transcribe(args: argparse.Namespace) -> int:
    ffmpeg_ops.ensure_command_available("ffmpeg")
    video_path = Path(args.video)
    paths = derive_output_paths(video_path, Path(args.out_dir))
    paths.out_dir.mkdir(parents=True, exist_ok=True)
    paths.tmp_dir.mkdir(parents=True, exist_ok=True)
    transcribe.transcribe_video_to_srt(
        video_path=video_path,
        auto_srt_path=paths.auto_srt,
        language=args.language,
        model_size=args.model_size,
        device=args.device,
    )
    return 0


def _handle_render(args: argparse.Namespace) -> int:
    ffmpeg_bin = ffmpeg_ops.ensure_command_available("ffmpeg")
    video_path = Path(args.video)
    srt_path = Path(args.srt)
    paths = derive_output_paths(video_path, Path(args.out_dir))
    paths.out_dir.mkdir(parents=True, exist_ok=True)
    paths.tmp_dir.mkdir(parents=True, exist_ok=True)

    entries = load_srt(srt_path)
    highlight_terms = _parse_highlight_terms(args.highlight)
    if not highlight_terms:
        highlight_terms = ass_writer.detect_highlight_terms(entries)
    ass_text = ass_writer.build_ass_document(
        entries,
        ass_writer.AssStyle.default(),
        highlight_terms=highlight_terms,
    )
    paths.ass_subtitle.write_text(ass_text, encoding="utf-8")
    intro_video = None
    if args.cover_title:
        cover_generator.extract_cover_frame(ffmpeg_bin, video_path, paths.cover_frame)
        cover_generator.create_cover_image(
            frame_path=paths.cover_frame,
            output_path=paths.cover_image,
            title=args.cover_title,
            subtitle=args.cover_subtitle,
            font_name=args.cover_font,
        )
        cover_generator.create_intro_video(
            ffmpeg_bin=ffmpeg_bin,
            image_path=paths.cover_image,
            output_path=paths.intro_video,
            duration=args.intro_duration,
        )
        intro_video = paths.intro_video

    command = ffmpeg_ops.build_render_command(
        ffmpeg_bin=ffmpeg_bin,
        video_path=video_path,
        ass_path=paths.ass_subtitle,
        output_path=paths.final_video,
        speed=args.speed,
        intro_video=intro_video,
    )
    ffmpeg_ops.run_command(command)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "transcribe":
        return _handle_transcribe(args)
    if args.command == "render":
        return _handle_render(args)
    raise RuntimeError(f"unsupported command: {args.command}")


__all__ = ["cover_generator", "derive_output_paths", "main", "transcribe"]
