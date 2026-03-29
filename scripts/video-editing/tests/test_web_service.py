from pathlib import Path

from video_postprocess.web_service import LocalWebService
from video_postprocess.web_workflow import LocalWebWorkflow


class ImmediateThread:
    def __init__(self, target, daemon=True):
        self._target = target

    def start(self):
        self._target()


def test_create_project_from_upload_stores_video_and_starts_transcription(tmp_path: Path) -> None:
    workflow = LocalWebWorkflow(tmp_path / "runs", thread_factory=ImmediateThread)
    captured = {}

    def fake_transcribe(video_path, auto_srt_path, language="zh", model_size="medium", device="auto", ffmpeg_bin="ffmpeg"):
        captured["model_size"] = model_size
        auto_srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试字幕\n", encoding="utf-8")

    service = LocalWebService(workflow, transcribe_runner=fake_transcribe, render_runner=lambda *args, **kwargs: None)

    project = service.create_project_from_upload("clip.mp4", b"video", model_size="large-v3")
    payload = service.serialize_project(project)

    assert project.video_path.read_bytes() == b"video"
    assert payload["status"] == "review"
    assert payload["video_url"].endswith("/video")
    assert captured["model_size"] == "large-v3"


def test_load_and_save_subtitles_use_edit_srt(tmp_path: Path) -> None:
    workflow = LocalWebWorkflow(tmp_path / "runs", thread_factory=ImmediateThread)
    service = LocalWebService(workflow, transcribe_runner=lambda *args, **kwargs: None, render_runner=lambda *args, **kwargs: None)
    project = workflow.create_project("clip.mp4")
    project.video_path.write_bytes(b"video")
    project.output_paths.edit_srt.parent.mkdir(parents=True, exist_ok=True)
    project.output_paths.edit_srt.write_text("1\n00:00:00,000 --> 00:00:01,000\n原字幕\n", encoding="utf-8")

    entries = service.load_subtitles(project.project_id)
    entries[0]["text"] = "新字幕"
    service.save_subtitles(project.project_id, entries)

    assert service.load_subtitles(project.project_id)[0]["text"] == "新字幕"


def test_start_render_returns_done_payload_with_artifacts(tmp_path: Path) -> None:
    workflow = LocalWebWorkflow(tmp_path / "runs", thread_factory=ImmediateThread)

    def fake_render(video_path, srt_path, out_dir, speed, cover_title, cover_subtitle, cover_font, intro_duration):
        (out_dir / "clip.final.mp4").write_bytes(b"final")
        (out_dir / "clip.cover.jpg").write_bytes(b"cover")

    service = LocalWebService(workflow, transcribe_runner=lambda *args, **kwargs: None, render_runner=fake_render)
    project = workflow.create_project("clip.mp4")
    project.video_path.write_bytes(b"video")
    project.output_paths.edit_srt.parent.mkdir(parents=True, exist_ok=True)
    project.output_paths.edit_srt.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试字幕\n", encoding="utf-8")

    payload = service.start_render(
        project.project_id,
        speed=1.25,
        cover_title="第一句就垮",
        cover_subtitle="方法篇",
        cover_font="Microsoft YaHei",
        intro_duration=0.5,
    )

    assert payload["status"] == "done"
    assert payload["final_video_url"].endswith("/artifacts/final")
    assert payload["cover_image_url"].endswith("/artifacts/cover")


def test_clear_current_project_resets_current_payload(tmp_path: Path) -> None:
    workflow = LocalWebWorkflow(tmp_path / "runs", thread_factory=ImmediateThread)

    def fake_transcribe(video_path, auto_srt_path, language="zh", model_size="medium", device="auto", ffmpeg_bin="ffmpeg"):
        auto_srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试字幕\n", encoding="utf-8")

    service = LocalWebService(workflow, transcribe_runner=fake_transcribe, render_runner=lambda *args, **kwargs: None)
    service.create_project_from_upload("clip.mp4", b"video")

    service.clear_current_project()

    assert service.serialize_project(service.get_project()) is None
