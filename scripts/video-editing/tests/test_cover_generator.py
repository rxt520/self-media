from pathlib import Path

from PIL import Image

from video_postprocess.cover_generator import _layout_cover_text, create_cover_image


def test_create_cover_image_writes_jpg_file(tmp_path: Path) -> None:
    frame_path = tmp_path / "frame.jpg"
    output_path = tmp_path / "cover.jpg"
    Image.new("RGB", (1080, 1920), color=(30, 30, 30)).save(frame_path, format="JPEG")

    create_cover_image(
        frame_path=frame_path,
        output_path=output_path,
        title="别人刷了你好几次还是记不住你在讲什么",
        subtitle="先让人记住你在讲什么",
        font_name="Microsoft YaHei",
    )

    assert output_path.exists()
    rendered = Image.open(output_path)
    assert rendered.size == (1080, 1920)


def test_layout_cover_text_centers_title_and_subtitle() -> None:
    layout = _layout_cover_text(
        width=1080,
        height=1920,
        title="无痛搞短视频的方法",
        subtitle="方法篇",
        font_name="Microsoft YaHei",
    )

    assert layout["title"]["lines"]
    assert layout["subtitle"]["lines"] == ["方法篇"]
    assert 300 < layout["title"]["top"] < 1200
    assert layout["title"]["center_x"] == 540
    assert layout["subtitle"]["center_x"] == 540
    assert layout["subtitle"]["top"] > layout["title"]["top"]


def test_layout_cover_text_wraps_long_title_and_keeps_subtitle_clear() -> None:
    layout = _layout_cover_text(
        width=1080,
        height=1920,
        title="第一句录了十二遍最后还是像在念检讨",
        subtitle="方法篇",
        font_name="Microsoft YaHei",
    )

    title_lines = layout["title"]["lines"]
    title_height = layout["title"]["height"]
    title_bottom = layout["title"]["top"] + title_height

    assert len(title_lines) >= 2
    assert layout["subtitle"]["top"] >= title_bottom + 36


def test_layout_cover_text_pushes_title_up_and_subtitle_down_for_jianying_style() -> None:
    layout = _layout_cover_text(
        width=1080,
        height=1920,
        title="第一句就垮",
        subtitle="方法篇",
        font_name="Microsoft YaHei",
    )

    assert layout["title"]["top"] <= 700
    assert layout["subtitle"]["top"] >= 980
