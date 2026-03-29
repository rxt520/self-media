from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

from video_postprocess.srt_utils import SubtitleEntry


STOP_TERMS = {
    "今天",
    "这个",
    "那个",
    "我们",
    "你们",
    "就是",
    "然后",
    "可以",
    "因为",
    "所以",
    "如果",
    "怎么",
    "什么",
    "时候",
    "已经",
    "开始",
    "分享",
    "自己",
    "一个",
    "一些",
    "一下",
    "不是",
    "不要",
    "这样",
    "那种",
    "真的",
    "可能",
    "出来",
    "后面",
}

CHINESE_RUN_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
CHINESE_TERM_RE = re.compile(r"^[\u4e00-\u9fff]{2,8}$")
PREFERRED_BREAK_AFTER = set("，。！？；：、）》」』〕】")
DISCOURAGED_BREAK_AFTER = set("的了呢吗啊呀和与及在把被对将让给")


@dataclass(frozen=True)
class AssStyle:
    font_name: str
    font_size: int
    highlight_font_size: int
    primary_color: str
    secondary_color: str
    outline_color: str
    back_color: str
    alignment: int
    margin_l: int
    margin_r: int
    margin_v: int
    border_style: int
    outline: int
    shadow: int
    max_chars_per_line: int

    @classmethod
    def default(cls) -> "AssStyle":
        return cls(
            font_name="Microsoft YaHei",
            font_size=13,
            highlight_font_size=14,
            primary_color="&H00FFFFFF",
            secondary_color="&H00CCFF&",
            outline_color="&H00333333",
            back_color="&H00000000",
            alignment=2,
            margin_l=72,
            margin_r=72,
            margin_v=42,
            border_style=1,
            outline=1,
            shadow=0,
            max_chars_per_line=12,
        )


def _ms_to_ass_time(value_ms: int) -> str:
    centiseconds = round(value_ms / 10)
    hours, remainder = divmod(centiseconds, 360_000)
    minutes, remainder = divmod(remainder, 6_000)
    seconds, centiseconds = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def _escape_ass_text(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")


def _split_long_line(text: str, max_chars_per_line: int) -> str:
    compact = text.replace("\n", "").strip()
    if len(compact) <= max_chars_per_line:
        return compact
    min_first = max(2, len(compact) - max_chars_per_line)
    max_first = min(max_chars_per_line, len(compact) - 2)
    if min_first > max_first:
        return compact[:max_chars_per_line] + "\n" + compact[max_chars_per_line:]

    preferred_boundaries = set(_collect_token_boundaries(compact))
    target = min(max_first, max(min_first, round(len(compact) / 2)))
    best_index = min_first
    best_score: tuple[int, int, int] | None = None

    for index in range(min_first, max_first + 1):
        first = compact[:index]
        second = compact[index:]
        score = _score_breakpoint(first, second, index in preferred_boundaries, target)
        if best_score is None or score < best_score:
            best_score = score
            best_index = index

    return compact[:best_index] + "\n" + compact[best_index:]


def _collect_token_boundaries(text: str) -> list[int]:
    try:
        import jieba
    except ImportError:
        return []

    boundaries: list[int] = []
    current = 0
    for token in jieba.cut(text, cut_all=False):
        current += len(token)
        if 1 < current < len(text):
            boundaries.append(current)
    return boundaries


def _score_breakpoint(first: str, second: str, on_token_boundary: bool, target: int) -> tuple[int, int, int]:
    balance_penalty = abs(len(first) - len(second))
    distance_penalty = abs(len(first) - target)
    boundary_penalty = 0 if on_token_boundary else 2
    previous_char = first[-1]
    if previous_char in PREFERRED_BREAK_AFTER:
        boundary_penalty -= 3
    if previous_char in DISCOURAGED_BREAK_AFTER:
        boundary_penalty += 3
    if len(second) <= 2:
        boundary_penalty += 6
    return (boundary_penalty, balance_penalty, distance_penalty)


def _fallback_candidates(entries: list[SubtitleEntry]) -> list[str]:
    counter: Counter[str] = Counter()
    for entry in entries:
        for run in CHINESE_RUN_RE.findall(entry.text):
            for size in range(2, 6):
                if len(run) < size:
                    continue
                for index in range(0, len(run) - size + 1):
                    term = run[index : index + size]
                    if term in STOP_TERMS:
                        continue
                    counter[term] += 1
    ranked = sorted(counter.items(), key=lambda item: (-item[1], -len(item[0]), item[0]))
    return [term for term, _count in ranked]


def _keyword_candidates_with_jieba(text: str) -> list[str]:
    try:
        import jieba
        import jieba.analyse
    except ImportError:
        return []

    counter: Counter[str] = Counter()
    for token in jieba.cut(text, cut_all=False):
        term = token.strip()
        if CHINESE_TERM_RE.fullmatch(term) and term not in STOP_TERMS:
            counter[term] += 2

    for term in jieba.analyse.extract_tags(text, topK=20, withWeight=False):
        if CHINESE_TERM_RE.fullmatch(term) and term not in STOP_TERMS:
            counter[term] += 3

    ranked = sorted(counter.items(), key=lambda item: (-item[1], -len(item[0]), item[0]))
    return [term for term, _score in ranked]


def _prune_overlapping_terms(terms: list[str], limit: int) -> list[str]:
    selected: list[str] = []
    for term in terms:
        if any(term in existing for existing in selected):
            continue
        selected.append(term)
        if len(selected) >= limit:
            break
    return selected


def _rank_candidate_terms(joined_text: str, entries: list[SubtitleEntry]) -> list[str]:
    score_map: Counter[str] = Counter()
    for term in _keyword_candidates_with_jieba(joined_text):
        score_map[term] += 30
    for term in _fallback_candidates(entries):
        score_map[term] += 10

    for term in list(score_map):
        score_map[term] += joined_text.count(term) * 8 + len(term)

    candidates = sorted(score_map, key=lambda term: (-score_map[term], -len(term), term))
    for longer in candidates:
        longer_count = joined_text.count(longer)
        if longer_count < 2:
            continue
        for shorter in candidates:
            if shorter == longer:
                continue
            if shorter in longer:
                score_map[longer] += 40
                score_map[shorter] -= 20

    return sorted(score_map, key=lambda term: (-score_map[term], -len(term), term))


def detect_highlight_terms(entries: list[SubtitleEntry], limit: int = 3) -> list[str]:
    joined_text = "\n".join(entry.text for entry in entries)
    return _prune_overlapping_terms(_rank_candidate_terms(joined_text, entries), limit)


def _select_entry_highlight_terms(entry: SubtitleEntry, global_terms: list[str]) -> list[str]:
    local_text = entry.text.strip()
    matched_terms = [term for term in global_terms if term and term in local_text]
    if matched_terms:
        return sorted(matched_terms, key=len, reverse=True)[:1]
    local_terms = _prune_overlapping_terms(_rank_candidate_terms(local_text, [entry]), 1)
    return local_terms


def _apply_highlights(text: str, highlight_terms: list[str], style: AssStyle) -> str:
    escaped = _escape_ass_text(text)
    replaced = False
    for term in sorted(set(highlight_terms), key=len, reverse=True):
        if not term:
            continue
        escaped_term = _escape_ass_text(term)
        escaped, replace_count = re.subn(
            re.escape(escaped_term),
            lambda match: (
                r"{\fs"
                + str(style.highlight_font_size)
                + r"\c"
                + style.secondary_color
                + r"}"
                + match.group(0)
                + r"{\r}"
            ),
            escaped,
            count=1,
        )
        if replace_count:
            replaced = True
    if replaced:
        return escaped

    fallback_term = _find_fallback_highlight_term(text)
    if not fallback_term:
        return escaped
    escaped_fallback = _escape_ass_text(fallback_term)
    escaped, _replace_count = re.subn(
        re.escape(escaped_fallback),
        lambda match: (
            r"{\fs"
            + str(style.highlight_font_size)
            + r"\c"
            + style.secondary_color
            + r"}"
            + match.group(0)
            + r"{\r}"
        ),
        escaped,
        count=1,
    )
    return escaped


def _find_fallback_highlight_term(text: str) -> str | None:
    for segment in text.splitlines():
        stripped = segment.strip()
        if not stripped:
            continue
        entry = SubtitleEntry(index=1, start_ms=0, end_ms=0, text=stripped)
        candidates = _rank_candidate_terms(stripped, [entry])
        if candidates:
            return candidates[0]
        match = CHINESE_RUN_RE.search(stripped)
        if not match:
            continue
        run = match.group(0)
        if len(run) >= 4:
            return run[:4]
        if len(run) >= 2:
            return run[:2]
    return None


def build_ass_document(
    entries: list[SubtitleEntry], style: AssStyle, highlight_terms: list[str] | None = None
) -> str:
    highlight_terms = highlight_terms or []
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding",
        (
            "Style: Default,"
            f"{style.font_name},{style.font_size},{style.primary_color},{style.secondary_color},"
            f"{style.outline_color},{style.back_color},1,0,0,0,100,100,0,0,{style.border_style},"
            f"{style.outline},{style.shadow},{style.alignment},{style.margin_l},{style.margin_r},{style.margin_v},1"
        ),
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    for entry in entries:
        entry_highlight_terms = _select_entry_highlight_terms(entry, highlight_terms)
        wrapped = _split_long_line(entry.text, style.max_chars_per_line)
        text = _apply_highlights(wrapped, entry_highlight_terms, style)
        lines.append(
            f"Dialogue: 0,{_ms_to_ass_time(entry.start_ms)},{_ms_to_ass_time(entry.end_ms)},"
            f"Default,,0,0,0,,{text}"
        )

    return "\n".join(lines) + "\n"
