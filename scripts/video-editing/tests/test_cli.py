from pathlib import Path

from video_postprocess import ass_writer
from video_postprocess import cover_generator
from video_postprocess import ffmpeg_ops
from video_postprocess import transcribe as transcribe_module
import video_postprocess as package


def test_main_transcribe_writes_auto_srt(tmp_path: Path, monkeypatch) -> None:
    video_path = tmp_path / "clip.mp4"
    video_path.write_bytes(b"video")
    out_dir = tmp_path / "output"

    monkeypatch.setattr(ffmpeg_ops, "ensure_command_available", lambda _: "ffmpeg")
    monkeypatch.setattr(
        transcribe_module,
        "transcribe_video_to_srt",
        lambda video_path, auto_srt_path, language="zh", model_size="medium", device="auto": auto_srt_path.write_text(
            "1\n00:00:00,000 --> 00:00:01,000\n测试字幕\n",
            encoding="utf-8",
        ),
    )

    exit_code = package.main(["transcribe", str(video_path), "--out-dir", str(out_dir)])

    assert exit_code == 0
    assert (out_dir / "clip.auto.srt").exists()


def test_main_render_writes_ass_and_calls_ffmpeg(tmp_path: Path, monkeypatch) -> None:
    video_path = tmp_path / "clip.mp4"
    video_path.write_bytes(b"video")
    srt_path = tmp_path / "clip.edit.srt"
    srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试流程\n", encoding="utf-8")
    out_dir = tmp_path / "output"
    recorded = {}

    monkeypatch.setattr(ffmpeg_ops, "ensure_command_available", lambda _: "ffmpeg")
    monkeypatch.setattr(
        ffmpeg_ops,
        "run_command",
        lambda command: recorded.setdefault("command", command),
    )

    exit_code = package.main(["render", str(video_path), "--srt", str(srt_path), "--out-dir", str(out_dir)])

    assert exit_code == 0
    assert (out_dir / "clip.ass").exists()
    assert recorded["command"][-1] == str(out_dir / "clip.final.mp4")
    assert any("subtitles='" in str(part) for part in recorded["command"])


def test_main_render_uses_highlight_terms(tmp_path: Path, monkeypatch) -> None:
    video_path = tmp_path / "clip.mp4"
    video_path.write_bytes(b"video")
    srt_path = tmp_path / "clip.edit.srt"
    srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试流程\n", encoding="utf-8")
    out_dir = tmp_path / "output"
    captured = {}

    monkeypatch.setattr(ffmpeg_ops, "ensure_command_available", lambda _: "ffmpeg")
    monkeypatch.setattr(ffmpeg_ops, "run_command", lambda command: None)

    original_build = ass_writer.build_ass_document

    def capture_build(entries, style, highlight_terms=None):
        captured["highlight_terms"] = highlight_terms
        return original_build(entries, style, highlight_terms=highlight_terms)

    monkeypatch.setattr(ass_writer, "build_ass_document", capture_build)

    exit_code = package.main(
        ["render", str(video_path), "--srt", str(srt_path), "--out-dir", str(out_dir), "--highlight", "流程,测试"]
    )

    assert exit_code == 0
    assert captured["highlight_terms"] == ["流程", "测试"]


def test_main_render_auto_detects_highlight_terms_when_not_provided(tmp_path: Path, monkeypatch) -> None:
    video_path = tmp_path / "clip.mp4"
    video_path.write_bytes(b"video")
    srt_path = tmp_path / "clip.edit.srt"
    srt_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n今天分享口播流程\n\n"
        "2\n00:00:01,000 --> 00:00:02,000\n这个流程能让口播更轻松\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "output"
    captured = {}

    monkeypatch.setattr(ffmpeg_ops, "ensure_command_available", lambda _: "ffmpeg")
    monkeypatch.setattr(ffmpeg_ops, "run_command", lambda command: None)

    original_build = ass_writer.build_ass_document

    def capture_build(entries, style, highlight_terms=None):
        captured["highlight_terms"] = highlight_terms
        return original_build(entries, style, highlight_terms=highlight_terms)

    monkeypatch.setattr(ass_writer, "build_ass_document", capture_build)

    exit_code = package.main(["render", str(video_path), "--srt", str(srt_path), "--out-dir", str(out_dir)])

    assert exit_code == 0
    assert "流程" in captured["highlight_terms"]
    assert "口播" in captured["highlight_terms"]


def test_main_render_generates_cover_assets_and_intro(tmp_path: Path, monkeypatch) -> None:
    video_path = tmp_path / "clip.mp4"
    video_path.write_bytes(b"video")
    srt_path = tmp_path / "clip.edit.srt"
    srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试流程\n", encoding="utf-8")
    out_dir = tmp_path / "output"
    captured = {}

    monkeypatch.setattr(ffmpeg_ops, "ensure_command_available", lambda _: "ffmpeg")
    monkeypatch.setattr(ffmpeg_ops, "run_command", lambda command: None)

    def fake_build_render_command(ffmpeg_bin, video_path, ass_path, output_path, speed=1.25, intro_video=None):
        captured["intro_video"] = intro_video
        return ["ffmpeg", str(output_path)]

    monkeypatch.setattr(ffmpeg_ops, "build_render_command", fake_build_render_command)
    monkeypatch.setattr(
        cover_generator,
        "extract_cover_frame",
        lambda ffmpeg_bin, video_path, output_path: output_path.write_bytes(b"frame"),
    )
    monkeypatch.setattr(
        cover_generator,
        "create_cover_image",
        lambda frame_path, output_path, title, subtitle, font_name="Microsoft YaHei": output_path.write_bytes(b"cover"),
    )
    monkeypatch.setattr(
        cover_generator,
        "create_intro_video",
        lambda ffmpeg_bin, image_path, output_path, duration=0.5: output_path.write_bytes(b"intro"),
    )

    exit_code = package.main(
        [
            "render",
            str(video_path),
            "--srt",
            str(srt_path),
            "--out-dir",
            str(out_dir),
            "--cover-title",
            "别人刷了你好几次还是记不住你在讲什么",
            "--cover-subtitle",
            "先让人记住你在讲什么",
        ]
    )

    assert exit_code == 0
    assert (out_dir / "clip.cover-frame.jpg").exists()
    assert (out_dir / "clip.cover.jpg").exists()
    assert (out_dir / "clip.intro.mp4").exists()
    assert captured["intro_video"] == out_dir / "clip.intro.mp4"
