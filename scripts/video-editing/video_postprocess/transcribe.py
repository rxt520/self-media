from __future__ import annotations

import tempfile
from pathlib import Path

from video_postprocess.ffmpeg_ops import run_command


def _format_srt_timestamp(milliseconds: float) -> str:
    total_ms = max(0, int(round(milliseconds)))
    hours = total_ms // 3_600_000
    remainder = total_ms % 3_600_000
    minutes = remainder // 60_000
    remainder %= 60_000
    seconds = remainder // 1_000
    millis = remainder % 1_000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def _segments_to_srt(segments) -> str:
    blocks: list[str] = []
    for index, segment in enumerate(segments, start=1):
        blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{_format_srt_timestamp(segment.start * 1000)} --> {_format_srt_timestamp(segment.end * 1000)}",
                    (segment.text or "").strip(),
                ]
            )
        )
    return "\n\n".join(blocks).strip() + "\n"


def _load_whisper_model(model_size: str, device: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("faster-whisper is not installed") from exc

    resolved_device = "cpu" if device == "auto" else device
    compute_type = "int8" if resolved_device == "cpu" else "float16"
    return WhisperModel(model_size, device=resolved_device, compute_type=compute_type)


def transcribe_video_to_srt(
    video_path: Path,
    auto_srt_path: Path,
    language: str = "zh",
    model_size: str = "small",
    device: str = "auto",
    ffmpeg_bin: str = "ffmpeg",
) -> None:
    auto_srt_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / "audio.wav"
        run_command(
            [
                ffmpeg_bin,
                "-y",
                "-i",
                str(video_path),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                str(audio_path),
            ]
        )

        model = _load_whisper_model(model_size=model_size, device=device)
        segments, _info = model.transcribe(str(audio_path), language=language, vad_filter=True)
        auto_srt_path.write_text(_segments_to_srt(list(segments)), encoding="utf-8")
