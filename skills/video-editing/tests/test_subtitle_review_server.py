from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_module(module_path: Path, module_name: str):
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_review_server_parses_srt_blocks(tmp_path: Path) -> None:
    module = load_module(
        Path(__file__).resolve().parents[1]
        / "reviewing-subtitles-in-browser"
        / "subtitle_review_server.py",
        "subtitle_review_server",
    )
    srt_path = tmp_path / "clip.edit.srt"
    srt_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n第一句\n\n"
        "2\n00:00:01,200 --> 00:00:02,000\n第二句\n",
        encoding="utf-8",
    )

    entries = module.load_srt_entries(srt_path)

    assert entries[0]["text"] == "第一句"
    assert entries[1]["start"] == "00:00:01,200"


def test_review_server_writes_back_srt(tmp_path: Path) -> None:
    module = load_module(
        Path(__file__).resolve().parents[1]
        / "reviewing-subtitles-in-browser"
        / "subtitle_review_server.py",
        "subtitle_review_server_2",
    )
    srt_path = tmp_path / "clip.edit.srt"
    entries = [
        {"index": 1, "start": "00:00:00,000", "end": "00:00:01,000", "text": "修正后字幕"},
    ]

    module.save_srt_entries(srt_path, entries)

    assert "修正后字幕" in srt_path.read_text(encoding="utf-8")
