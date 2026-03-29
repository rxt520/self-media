from pathlib import Path

from video_postprocess.web_workflow import (
    LocalWebWorkflow,
    create_project,
    transcribe_project,
    render_project,
)


def test_create_project_builds_workspace_and_output_paths(tmp_path: Path) -> None:
    project = create_project(tmp_path, project_id="demo001", original_filename="clip.mp4")

    assert project.project_id == "demo001"
    assert project.project_dir == tmp_path / "demo001"
    assert project.video_path == project.project_dir / "clip.mp4"
    assert project.output_paths.out_dir == project.project_dir / "output"
    assert project.output_paths.edit_srt == project.project_dir / "output" / "clip.edit.srt"
    assert project.status == "created"


def test_transcribe_project_copies_auto_srt_to_edit_srt_and_updates_status(tmp_path: Path) -> None:
    project = create_project(tmp_path, project_id="demo001", original_filename="clip.mp4")
    project.video_path.write_bytes(b"video")

    def fake_transcribe(video_path, auto_srt_path, language="zh", model_size="medium", device="auto", ffmpeg_bin="ffmpeg"):
        auto_srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试字幕\n", encoding="utf-8")

    transcribe_project(project, fake_transcribe)

    assert project.status == "review"
    assert project.output_paths.auto_srt.exists()
    assert project.output_paths.edit_srt.read_text(encoding="utf-8") == project.output_paths.auto_srt.read_text(encoding="utf-8")


def test_render_project_updates_status_and_keeps_result_paths(tmp_path: Path) -> None:
    project = create_project(tmp_path, project_id="demo001", original_filename="clip.mp4")
    project.video_path.write_bytes(b"video")
    project.output_paths.edit_srt.parent.mkdir(parents=True, exist_ok=True)
    project.output_paths.edit_srt.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试字幕\n", encoding="utf-8")

    def fake_render(video_path, srt_path, out_dir, speed, cover_title, cover_subtitle, cover_font, intro_duration):
        (out_dir / "clip.final.mp4").write_bytes(b"final")
        (out_dir / "clip.cover.jpg").write_bytes(b"cover")

    render_project(
        project,
        fake_render,
        speed=1.25,
        cover_title="第一句就垮",
        cover_subtitle="方法篇",
        cover_font="Microsoft YaHei",
        intro_duration=0.5,
    )

    assert project.status == "done"
    assert project.output_paths.final_video.exists()
    assert project.output_paths.cover_image.exists()


def test_local_web_workflow_tracks_current_project(tmp_path: Path) -> None:
    workflow = LocalWebWorkflow(tmp_path)

    project = workflow.create_project("clip.mp4")

    assert workflow.current_project_id == project.project_id
    assert workflow.get_project(project.project_id) is project


def test_local_web_workflow_can_clear_current_project(tmp_path: Path) -> None:
    workflow = LocalWebWorkflow(tmp_path)
    project = workflow.create_project("clip.mp4")

    workflow.clear_current_project()

    assert workflow.current_project_id is None
    assert workflow.get_project() is None
    assert workflow.get_project(project.project_id) is project


def test_local_web_workflow_can_reset_workspace_on_start(tmp_path: Path) -> None:
    stale_dir = tmp_path / "old-project"
    stale_dir.mkdir(parents=True, exist_ok=True)
    (stale_dir / "stale.txt").write_text("old", encoding="utf-8")

    workflow = LocalWebWorkflow(tmp_path, reset_workspace=True)

    assert workflow.current_project_id is None
    assert workflow.projects == {}
    assert not stale_dir.exists()


def test_local_web_workflow_can_run_transcription_in_background(tmp_path: Path) -> None:
    events: list[str] = []

    class ImmediateThread:
        def __init__(self, target, daemon=True):
            self._target = target

        def start(self):
            events.append("started")
            self._target()

    workflow = LocalWebWorkflow(tmp_path, thread_factory=ImmediateThread)
    project = workflow.create_project("clip.mp4")
    project.video_path.write_bytes(b"video")

    def fake_transcribe(video_path, auto_srt_path, language="zh", model_size="medium", device="auto", ffmpeg_bin="ffmpeg"):
        auto_srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试字幕\n", encoding="utf-8")

    workflow.start_transcription(project.project_id, fake_transcribe)

    assert events == ["started"]
    assert project.status == "review"
    assert project.output_paths.edit_srt.exists()


def test_local_web_workflow_can_run_render_in_background(tmp_path: Path) -> None:
    class ImmediateThread:
        def __init__(self, target, daemon=True):
            self._target = target

        def start(self):
            self._target()

    workflow = LocalWebWorkflow(tmp_path, thread_factory=ImmediateThread)
    project = workflow.create_project("clip.mp4")
    project.video_path.write_bytes(b"video")
    project.output_paths.edit_srt.parent.mkdir(parents=True, exist_ok=True)
    project.output_paths.edit_srt.write_text("1\n00:00:00,000 --> 00:00:01,000\n测试字幕\n", encoding="utf-8")

    def fake_render(video_path, srt_path, out_dir, speed, cover_title, cover_subtitle, cover_font, intro_duration):
        (out_dir / "clip.final.mp4").write_bytes(b"final")
        (out_dir / "clip.cover.jpg").write_bytes(b"cover")

    workflow.start_render(
        project.project_id,
        fake_render,
        speed=1.25,
        cover_title="第一句就垮",
        cover_subtitle="方法篇",
        cover_font="Microsoft YaHei",
        intro_duration=0.5,
    )

    assert project.status == "done"
    assert project.output_paths.final_video.exists()
