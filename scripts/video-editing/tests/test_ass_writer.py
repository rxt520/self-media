from video_postprocess.ass_writer import AssStyle, build_ass_document, detect_highlight_terms
from video_postprocess.srt_utils import SubtitleEntry


def test_build_ass_document_includes_style_and_dialogue() -> None:
    entries = [
        SubtitleEntry(index=1, start_ms=500, end_ms=2000, text="先把视频流程跑通"),
        SubtitleEntry(index=2, start_ms=2100, end_ms=3600, text="再去追求高级剪辑"),
    ]

    ass_text = build_ass_document(entries, AssStyle.default())

    assert "Style: Default,Microsoft YaHei" in ass_text
    assert "Style: Default,Microsoft YaHei,13" in ass_text
    assert ",1,1,0,2,72,72,42,1" in ass_text
    assert "Dialogue: 0,0:00:00.50,0:00:02.00,Default" in ass_text
    assert "Dialogue: 0,0:00:02.10,0:00:03.60,Default" in ass_text


def test_build_ass_document_highlights_keywords() -> None:
    entries = [SubtitleEntry(index=1, start_ms=0, end_ms=2000, text="先把视频流程跑通")]

    ass_text = build_ass_document(entries, AssStyle.default(), highlight_terms=["流程"])

    assert "{\\fs14\\c&H00CCFF&}流程{\\r}" in ass_text


def test_build_ass_document_wraps_long_lines_into_two_rows() -> None:
    entries = [SubtitleEntry(index=1, start_ms=0, end_ms=2000, text="这样你的每一段都能够录到你比较好的一个状态")]

    ass_text = build_ass_document(entries, AssStyle.default())

    assert "\\N" in ass_text


def test_build_ass_document_ensures_each_entry_has_a_highlight() -> None:
    entries = [
        SubtitleEntry(index=1, start_ms=0, end_ms=1000, text="短视频一定要先完成"),
        SubtitleEntry(index=2, start_ms=1000, end_ms=2000, text="先让别人记住你在讲什么"),
    ]

    ass_text = build_ass_document(entries, AssStyle.default(), highlight_terms=["短视频"])
    dialogue_lines = [line for line in ass_text.splitlines() if line.startswith("Dialogue:")]

    assert len(dialogue_lines) == 2
    assert all("{\\fs14\\c" in line for line in dialogue_lines)


def test_build_ass_document_keeps_highlight_after_line_wrap() -> None:
    entries = [SubtitleEntry(index=1, start_ms=0, end_ms=1000, text="那我一开始拍第一条短视频的时候")]

    ass_text = build_ass_document(entries, AssStyle.default(), highlight_terms=["短视频"])

    dialogue_line = next(line for line in ass_text.splitlines() if line.startswith("Dialogue:"))
    assert "{\\fs14\\c" in dialogue_line


def test_build_ass_document_falls_back_to_local_phrase_when_no_global_term_matches() -> None:
    entries = [SubtitleEntry(index=1, start_ms=0, end_ms=1000, text="那我一开始拍第一条短视频的时候")]

    ass_text = build_ass_document(entries, AssStyle.default())

    dialogue_line = next(line for line in ass_text.splitlines() if line.startswith("Dialogue:"))
    assert "{\\fs14\\c" in dialogue_line


def test_detect_highlight_terms_picks_repeated_content_words() -> None:
    entries = [
        SubtitleEntry(index=1, start_ms=0, end_ms=1000, text="今天分享口播流程"),
        SubtitleEntry(index=2, start_ms=1000, end_ms=2000, text="这个流程能让口播更轻松"),
        SubtitleEntry(index=3, start_ms=2000, end_ms=3000, text="拍口播不要先追求完美"),
    ]

    terms = detect_highlight_terms(entries)

    assert "流程" in terms
    assert "口播" in terms


def test_detect_highlight_terms_prefers_complete_short_video_term() -> None:
    entries = [
        SubtitleEntry(index=1, start_ms=0, end_ms=1000, text="短视频一定要先完成"),
        SubtitleEntry(index=2, start_ms=1000, end_ms=2000, text="这条短视频讲的是拍摄流程"),
    ]

    terms = detect_highlight_terms(entries)

    assert "短视频" in terms
