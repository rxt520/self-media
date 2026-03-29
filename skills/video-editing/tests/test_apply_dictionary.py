from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_module(module_path: Path, module_name: str):
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_apply_dictionary_replaces_terms_in_srt_text(tmp_path: Path) -> None:
    module = load_module(
        Path(__file__).resolve().parents[1]
        / "dictionary-correcting-subtitles"
        / "apply_dictionary.py",
        "apply_dictionary",
    )
    srt_path = tmp_path / "clip.auto.srt"
    dictionary_path = tmp_path / "dictionary.txt"
    srt_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n扣子空间和扣子罗盘\n",
        encoding="utf-8",
    )
    dictionary_path.write_text("扣子空间 => Coze Space\n扣子罗盘 => Coze Compass\n", encoding="utf-8")

    result = module.apply_dictionary_file(srt_path, dictionary_path, tmp_path / "clip.edit.srt")

    assert "Coze Space" in result
    assert "Coze Compass" in result


def test_load_dictionary_skips_blank_and_comment_lines(tmp_path: Path) -> None:
    module = load_module(
        Path(__file__).resolve().parents[1]
        / "dictionary-correcting-subtitles"
        / "apply_dictionary.py",
        "apply_dictionary_2",
    )
    dictionary_path = tmp_path / "dictionary.txt"
    dictionary_path.write_text(
        "# comment\n\n扣子 => Coze\n无箭头这一行\n",
        encoding="utf-8",
    )

    mapping = module.load_dictionary(dictionary_path)

    assert mapping == {"扣子": "Coze"}
