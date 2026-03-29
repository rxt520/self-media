from __future__ import annotations

import argparse
from pathlib import Path


def load_dictionary(dictionary_path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for raw_line in Path(dictionary_path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=>" not in line:
            continue
        source, target = line.split("=>", 1)
        source = source.strip()
        target = target.strip()
        if source and target:
            mapping[source] = target
    return mapping


def apply_dictionary_text(text: str, mapping: dict[str, str]) -> str:
    corrected = text
    for source, target in mapping.items():
        corrected = corrected.replace(source, target)
    return corrected


def apply_dictionary_file(srt_path: Path, dictionary_path: Path, output_path: Path) -> str:
    mapping = load_dictionary(dictionary_path)
    content = Path(srt_path).read_text(encoding="utf-8")
    corrected = apply_dictionary_text(content, mapping)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(corrected, encoding="utf-8")
    return corrected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply subtitle term dictionary corrections")
    parser.add_argument("srt", help="Input subtitle file")
    parser.add_argument("--dictionary", required=True, help="Dictionary file path")
    parser.add_argument("--output", required=True, help="Corrected subtitle output path")
    args = parser.parse_args(argv)

    apply_dictionary_file(Path(args.srt), Path(args.dictionary), Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
