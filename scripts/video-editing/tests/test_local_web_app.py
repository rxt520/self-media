from pathlib import Path

from video_postprocess.local_web_app import build_page_html, main


def test_build_page_html_contains_loading_and_dropdown_controls() -> None:
    html = build_page_html()

    assert 'id="upload-form"' in html
    assert 'id="subtitle-list"' in html
    assert 'id="subtitle-loading"' in html
    assert 'id="speed-select"' in html
    assert 'id="cover-font-select"' in html
    assert 'id="transcribe-model-select"' in html
    assert 'name="model_size"' in html
    assert 'accept=".qt,.mov,.mp4,.m4v,.avi,.mkv,video/*,*/*"' in html
    assert "/api/upload" in html
    assert "/api/project/current" in html
    assert "/api/project/current/reset" in html


def test_main_prints_url_with_flush(monkeypatch, tmp_path: Path) -> None:
    printed = {}
    captured = {}

    class FakeServer:
        def __init__(self, address, handler):
            self.address = address

        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            printed["closed"] = True

    monkeypatch.setattr("video_postprocess.local_web_app.ThreadingHTTPServer", FakeServer)
    monkeypatch.setattr(
        "video_postprocess.local_web_app.LocalWebWorkflow",
        lambda workspace_dir, thread_factory=None, reset_workspace=False: captured.update(
            {"workspace_dir": workspace_dir, "reset_workspace": reset_workspace}
        )
        or object(),
    )
    monkeypatch.setattr(
        "video_postprocess.local_web_app.LocalWebService",
        lambda workflow, transcribe_runner, render_runner: object(),
    )
    monkeypatch.setattr(
        "builtins.print",
        lambda message, flush=False: printed.update({"message": message, "flush": flush}),
    )

    exit_code = main(["--host", "127.0.0.1", "--port", "8899", "--workspace", str(tmp_path)])

    assert exit_code == 0
    assert printed["message"] == "http://127.0.0.1:8899"
    assert printed["flush"] is True
    assert printed["closed"] is True
    assert captured["reset_workspace"] is True
