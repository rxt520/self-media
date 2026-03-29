from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import threading
import uuid

from video_postprocess.paths import OutputPaths, derive_output_paths


@dataclass
class WebProject:
    project_id: str
    project_dir: Path
    video_name: str
    video_path: Path
    output_paths: OutputPaths
    status: str = "created"
    error: str | None = None


def create_project(workspace_dir: Path, project_id: str, original_filename: str) -> WebProject:
    project_dir = Path(workspace_dir) / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    video_name = Path(original_filename).name or "upload.mp4"
    video_path = project_dir / video_name
    if not video_path.exists():
        video_path.touch()
    output_paths = derive_output_paths(video_path, project_dir / "output")
    output_paths.out_dir.mkdir(parents=True, exist_ok=True)
    output_paths.tmp_dir.mkdir(parents=True, exist_ok=True)
    return WebProject(
        project_id=project_id,
        project_dir=project_dir,
        video_name=video_name,
        video_path=video_path,
        output_paths=output_paths,
    )


def transcribe_project(project: WebProject, transcribe_runner, **transcribe_kwargs) -> None:
    project.status = "transcribing"
    project.error = None
    try:
        transcribe_runner(project.video_path, project.output_paths.auto_srt, **transcribe_kwargs)
        shutil.copyfile(project.output_paths.auto_srt, project.output_paths.edit_srt)
        project.status = "review"
    except Exception as exc:
        project.status = "error"
        project.error = str(exc)
        raise


def render_project(
    project: WebProject,
    render_runner,
    speed: float,
    cover_title: str,
    cover_subtitle: str,
    cover_font: str,
    intro_duration: float,
) -> None:
    project.status = "rendering"
    project.error = None
    try:
        render_runner(
            project.video_path,
            project.output_paths.edit_srt,
            project.output_paths.out_dir,
            speed,
            cover_title,
            cover_subtitle,
            cover_font,
            intro_duration,
        )
        project.status = "done"
    except Exception as exc:
        project.status = "error"
        project.error = str(exc)
        raise


class LocalWebWorkflow:
    def __init__(self, workspace_dir: Path, thread_factory=None, reset_workspace: bool = False) -> None:
        self.workspace_dir = Path(workspace_dir)
        if reset_workspace and self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.projects: dict[str, WebProject] = {}
        self.current_project_id: str | None = None
        self.thread_factory = thread_factory or threading.Thread

    def create_project(self, original_filename: str) -> WebProject:
        project_id = uuid.uuid4().hex[:8]
        project = create_project(self.workspace_dir, project_id=project_id, original_filename=original_filename)
        self.projects[project_id] = project
        self.current_project_id = project_id
        return project

    def get_project(self, project_id: str | None = None) -> WebProject | None:
        resolved_id = project_id or self.current_project_id
        if resolved_id is None:
            return None
        return self.projects.get(resolved_id)

    def clear_current_project(self) -> None:
        self.current_project_id = None

    def start_transcription(self, project_id: str, transcribe_runner, **transcribe_kwargs) -> None:
        project = self.projects[project_id]
        thread = self.thread_factory(
            target=lambda: transcribe_project(project, transcribe_runner, **transcribe_kwargs),
            daemon=True,
        )
        thread.start()

    def start_render(
        self,
        project_id: str,
        render_runner,
        speed: float,
        cover_title: str,
        cover_subtitle: str,
        cover_font: str,
        intro_duration: float,
    ) -> None:
        project = self.projects[project_id]
        thread = self.thread_factory(
            target=lambda: render_project(
                project,
                render_runner,
                speed=speed,
                cover_title=cover_title,
                cover_subtitle=cover_subtitle,
                cover_font=cover_font,
                intro_duration=intro_duration,
            ),
            daemon=True,
        )
        thread.start()
