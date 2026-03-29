from pathlib import Path

from video_postprocess.paths import derive_output_paths


def test_derive_output_paths_uses_source_stem_and_output_dir(tmp_path: Path) -> None:
    video_path = tmp_path / "clip.mp4"
    video_path.write_bytes(b"video")
    out_dir = tmp_path / "output"

    paths = derive_output_paths(video_path, out_dir)

    assert paths.base_name == "clip"
    assert paths.out_dir == out_dir
    assert paths.auto_srt == out_dir / "clip.auto.srt"
    assert paths.edit_srt == out_dir / "clip.edit.srt"
    assert paths.ass_subtitle == out_dir / "clip.ass"
    assert paths.final_video == out_dir / "clip.final.mp4"
    assert paths.cover_frame == out_dir / "clip.cover-frame.jpg"
    assert paths.cover_image == out_dir / "clip.cover.jpg"
    assert paths.intro_video == out_dir / "clip.intro.mp4"
    assert paths.tmp_dir == out_dir / "tmp"


def test_derive_output_paths_rejects_missing_video(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.mp4"

    try:
        derive_output_paths(missing_path, tmp_path / "output")
    except FileNotFoundError as exc:
        assert "missing.mp4" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")
