from __future__ import annotations

from pathlib import Path
import re

from video_postprocess.web_workflow import LocalWebWorkflow, WebProject


TIMESTAMP_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2},\d{3})$"
)


class LocalWebService:
    def __init__(self, workflow: LocalWebWorkflow, transcribe_runner, render_runner) -> None:
        self.workflow = workflow
        self.transcribe_runner = transcribe_runner
        self.render_runner = render_runner

    def create_project_from_upload(self, filename: str, content: bytes, model_size: str = "medium") -> WebProject:
        project = self.workflow.create_project(filename)
        project.video_path.write_bytes(content)
        self.workflow.start_transcription(project.project_id, self.transcribe_runner, model_size=model_size)
        return project

    def serialize_project(self, project: WebProject | None) -> dict[str, object] | None:
        if project is None:
            return None
        payload: dict[str, object] = {
            "project_id": project.project_id,
            "status": project.status,
            "error": project.error,
            "video_name": project.video_name,
            "video_url": f"/projects/{project.project_id}/video",
            "edit_srt_path": str(project.output_paths.edit_srt),
        }
        if project.output_paths.final_video.exists():
            payload["final_video_url"] = f"/projects/{project.project_id}/artifacts/final"
        if project.output_paths.cover_image.exists():
            payload["cover_image_url"] = f"/projects/{project.project_id}/artifacts/cover"
        return payload

    def get_project(self, project_id: str | None = None) -> WebProject | None:
        return self.workflow.get_project(project_id)

    def clear_current_project(self) -> None:
        self.workflow.clear_current_project()

    def load_subtitles(self, project_id: str) -> list[dict[str, str | int]]:
        project = self.workflow.get_project(project_id)
        if project is None:
            raise KeyError(project_id)
        content = project.output_paths.edit_srt.read_text(encoding="utf-8").lstrip("\ufeff").strip()
        if not content:
            return []

        entries: list[dict[str, str | int]] = []
        blocks = re.split(r"\r?\n\r?\n", content)
        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if len(lines) < 3:
                continue
            entries.append(
                {
                    "index": int(lines[0]),
                    "start": TIMESTAMP_RE.match(lines[1]).group("start"),  # type: ignore[union-attr]
                    "end": TIMESTAMP_RE.match(lines[1]).group("end"),  # type: ignore[union-attr]
                    "text": "\n".join(lines[2:]),
                }
            )
        return entries

    def save_subtitles(self, project_id: str, entries: list[dict[str, str | int]]) -> None:
        project = self.workflow.get_project(project_id)
        if project is None:
            raise KeyError(project_id)
        blocks = []
        for idx, entry in enumerate(entries, start=1):
            blocks.append(
                "\n".join(
                    [
                        str(entry.get("index", idx)),
                        f"{entry['start']} --> {entry['end']}",
                        str(entry.get("text", "")),
                    ]
                )
            )
        project.output_paths.edit_srt.write_text("\n\n".join(blocks).strip() + "\n", encoding="utf-8")

    def start_render(
        self,
        project_id: str,
        speed: float,
        cover_title: str,
        cover_subtitle: str,
        cover_font: str,
        intro_duration: float,
    ) -> dict[str, object] | None:
        self.workflow.start_render(
            project_id,
            self.render_runner,
            speed=speed,
            cover_title=cover_title,
            cover_subtitle=cover_subtitle,
            cover_font=cover_font,
            intro_duration=intro_duration,
        )
        return self.serialize_project(self.workflow.get_project(project_id))


def guess_artifact_path(project: WebProject, artifact_name: str) -> Path:
    if artifact_name == "final":
        return project.output_paths.final_video
    if artifact_name == "cover":
        return project.output_paths.cover_image
    raise KeyError(artifact_name)
