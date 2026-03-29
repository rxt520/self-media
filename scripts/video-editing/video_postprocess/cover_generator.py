from __future__ import annotations

import os
import platform
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from video_postprocess import ffmpeg_ops


def extract_cover_frame(ffmpeg_bin: str, video_path: Path, output_path: Path) -> None:
    ffmpeg_ops.run_command(ffmpeg_ops.build_cover_frame_command(ffmpeg_bin, video_path, output_path))


def create_intro_video(ffmpeg_bin: str, image_path: Path, output_path: Path, duration: float = 0.5) -> None:
    ffmpeg_ops.run_command(ffmpeg_ops.build_intro_command(ffmpeg_bin, image_path, output_path, duration))


def create_cover_image(
    frame_path: Path,
    output_path: Path,
    title: str,
    subtitle: str,
    font_name: str = "Microsoft YaHei",
) -> None:
    with Image.open(frame_path) as original:
        canvas = original.convert("RGB")

    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)
    layout = _layout_cover_text(width=width, height=height, title=title, subtitle=subtitle, font_name=font_name)

    _draw_centered_lines(
        draw=draw,
        lines=layout["title"]["lines"],
        font=layout["title"]["font"],
        center_x=layout["title"]["center_x"],
        y=layout["title"]["top"],
        fill=(255, 215, 40),
        stroke_fill=(0, 0, 0),
        shadow_fill=(196, 10, 10),
        shadow_offset=(8, 8),
        stroke_width=max(4, layout["title"]["font"].size // 10),
        line_spacing=layout["title"]["line_spacing"],
    )
    _draw_centered_lines(
        draw=draw,
        lines=layout["subtitle"]["lines"],
        font=layout["subtitle"]["font"],
        center_x=layout["subtitle"]["center_x"],
        y=layout["subtitle"]["top"],
        fill=(255, 255, 255),
        stroke_fill=(0, 0, 0),
        shadow_fill=None,
        shadow_offset=(0, 0),
        stroke_width=max(3, layout["subtitle"]["font"].size // 14),
        line_spacing=layout["subtitle"]["line_spacing"],
    )
    canvas.convert("RGB").save(output_path, format="JPEG", quality=95)


def _layout_cover_text(width: int, height: int, title: str, subtitle: str, font_name: str) -> dict[str, dict[str, object]]:
    probe = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(probe)
    max_text_width = int(width * 0.88)

    title_font, title_lines = _fit_text(draw, title.strip(), font_name, max_text_width, 3, int(height * 0.10), 48)
    subtitle_font, subtitle_lines = _fit_text(draw, subtitle.strip(), font_name, int(width * 0.56), 1, int(height * 0.05), 28)

    title_line_height = _line_height(title_font)
    subtitle_line_height = _line_height(subtitle_font)
    title_spacing = max(8, title_font.size // 8)
    subtitle_spacing = max(6, subtitle_font.size // 9)
    title_height = len(title_lines) * title_line_height + max(0, len(title_lines) - 1) * title_spacing
    subtitle_height = len(subtitle_lines) * subtitle_line_height + max(0, len(subtitle_lines) - 1) * subtitle_spacing
    gap = max(60, int(height * 0.062))
    total_height = title_height + subtitle_height + (gap if subtitle_lines else 0)
    title_top = int(height * 0.37 - total_height / 2)
    title_top = max(int(height * 0.18), min(title_top, int(height * 0.46)))
    subtitle_top = title_top + title_height + gap + int(height * 0.03)
    subtitle_top = max(subtitle_top, int(height * 0.54))

    return {
        "title": {
            "lines": title_lines,
            "font": title_font,
            "center_x": width // 2,
            "top": title_top,
            "height": title_height,
            "line_spacing": title_spacing,
        },
        "subtitle": {
            "lines": subtitle_lines,
            "font": subtitle_font,
            "center_x": width // 2,
            "top": subtitle_top,
            "height": subtitle_height,
            "line_spacing": subtitle_spacing,
        },
    }


def _fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_name: str,
    max_width: int,
    max_lines: int,
    start_size: int,
    min_size: int,
) -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, list[str]]:
    if not text:
        return (_load_font(font_name, min_size), [])

    for font_size in range(start_size, min_size - 1, -2):
        font = _load_font(font_name, font_size)
        lines = _wrap_text(draw, text, font, max_width)
        if len(lines) <= max_lines and all(_text_width(draw, line, font) <= max_width for line in lines):
            return font, lines
    font = _load_font(font_name, min_size)
    return font, _wrap_text(draw, text, font, max_width)


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if current and _text_width(draw, candidate, font) > max_width:
            lines.append(current)
            current = char
            continue
        current = candidate
    if current:
        lines.append(current)
    if len(lines) >= 2 and len(lines[-1]) == 1:
        lines[-2] += lines[-1]
        lines.pop()
    return lines


def _draw_centered_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    center_x: int,
    y: int,
    fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int],
    shadow_fill: tuple[int, int, int] | None,
    shadow_offset: tuple[int, int],
    stroke_width: int,
    line_spacing: int,
) -> None:
    current_y = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=stroke_width)
        x = int(center_x - (bbox[2] - bbox[0]) / 2)
        if shadow_fill is not None:
            draw.text(
                (x + shadow_offset[0], current_y + shadow_offset[1]),
                line,
                font=font,
                fill=shadow_fill,
                stroke_width=stroke_width,
                stroke_fill=(0, 0, 0),
            )
        draw.text(
            (x, current_y),
            line,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        current_y += _line_height(font) + line_spacing


def _text_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> int:
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=max(1, getattr(font, "size", 20) // 14))
    return bbox[2] - bbox[0]


def _line_height(font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> int:
    bbox = font.getbbox("测A")
    return bbox[3] - bbox[1]


def _load_font(font_name: str, font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_path = _resolve_font_path(font_name)
    if font_path:
        try:
            return ImageFont.truetype(font_path, font_size)
        except OSError:
            pass
    return ImageFont.load_default()


def _resolve_font_path(font_name: str) -> str | None:
    candidate = Path(font_name)
    if candidate.exists():
        return str(candidate)

    normalized = font_name.lower()
    candidates: list[Path] = []
    if platform.system() == "Windows":
        fonts_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        candidates.extend(
            [
                fonts_dir / "msyhbd.ttc",
                fonts_dir / "msyh.ttc",
                fonts_dir / "simhei.ttf",
            ]
        )
    elif platform.system() == "Darwin":
        candidates.extend(
            [
                Path("/System/Library/Fonts/PingFang.ttc"),
                Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
                Path("/Library/Fonts/Arial Unicode.ttf"),
            ]
        )

    if "yahei" in normalized or "微软雅黑" in normalized:
        for candidate_path in candidates:
            if candidate_path.exists():
                return str(candidate_path)

    for candidate_path in candidates:
        if candidate_path.exists():
            return str(candidate_path)
    return None
