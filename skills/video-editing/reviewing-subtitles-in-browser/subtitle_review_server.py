from __future__ import annotations

import argparse
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


def load_srt_entries(srt_path: Path) -> list[dict[str, str | int]]:
    content = Path(srt_path).read_text(encoding="utf-8").lstrip("\ufeff").strip()
    if not content:
        return []

    blocks = re.split(r"\r?\n\r?\n", content)
    entries: list[dict[str, str | int]] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        entries.append(
            {
                "index": int(lines[0]),
                "start": lines[1].split(" --> ")[0],
                "end": lines[1].split(" --> ")[1],
                "text": "\n".join(lines[2:]),
            }
        )
    return entries


def save_srt_entries(srt_path: Path, entries: list[dict[str, str | int]]) -> None:
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
    Path(srt_path).write_text("\n\n".join(blocks).strip() + "\n", encoding="utf-8")


def build_app_html(video_name: str, srt_name: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>字幕审核</title>
  <style>
    body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 0; background: #f3f1eb; color: #1d1d1d; }}
    .wrap {{ display: grid; grid-template-columns: 1.2fr 1fr; min-height: 100vh; }}
    .video-pane {{ padding: 24px; background: linear-gradient(180deg, #e6dccf 0%, #f7f4ef 100%); }}
    .list-pane {{ padding: 24px; overflow: auto; }}
    h1 {{ margin: 0 0 12px; font-size: 24px; }}
    .meta {{ margin-bottom: 18px; color: #5f5448; }}
    video {{ width: 100%; max-height: 72vh; background: #000; border-radius: 16px; }}
    .toolbar {{ display: flex; gap: 12px; margin: 16px 0; }}
    button {{ border: 0; border-radius: 999px; padding: 10px 16px; background: #1d1d1d; color: #fff; cursor: pointer; }}
    .item {{ background: #fff; border-radius: 14px; padding: 14px; margin-bottom: 12px; box-shadow: 0 8px 20px rgba(0,0,0,.06); }}
    .time {{ font-size: 12px; color: #7a6f63; margin-bottom: 8px; }}
    textarea {{ width: 100%; min-height: 64px; resize: vertical; border: 1px solid #ddd4c8; border-radius: 10px; padding: 10px; font: inherit; }}
    .status {{ margin-left: 8px; color: #3f7a36; }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="video-pane">
      <h1>字幕审核</h1>
      <div class="meta">视频: {video_name} | 字幕: {srt_name}</div>
      <video id="video" controls>
        <source src="/video" type="video/mp4">
      </video>
      <div class="toolbar">
        <button onclick="save()">保存字幕</button>
        <span class="status" id="status"></span>
      </div>
    </section>
    <section class="list-pane">
      <div id="list"></div>
    </section>
  </div>
  <script>
    let subtitles = [];
    async function load() {{
      const res = await fetch('/api/subtitles');
      subtitles = await res.json();
      render();
    }}
    function render() {{
      const list = document.getElementById('list');
      list.innerHTML = subtitles.map((item, index) => `
        <div class="item">
          <div class="time">${{index + 1}}. ${{item.start}} --> ${{item.end}}</div>
          <textarea data-index="${{index}}">${{item.text}}</textarea>
        </div>
      `).join('');
      document.querySelectorAll('textarea').forEach((node) => {{
        node.addEventListener('input', (event) => {{
          subtitles[Number(event.target.dataset.index)].text = event.target.value;
        }});
      }});
    }}
    async function save() {{
      const res = await fetch('/api/subtitles', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(subtitles)
      }});
      const data = await res.json();
      document.getElementById('status').textContent = data.success ? '已保存' : '保存失败';
    }}
    load();
  </script>
</body>
</html>"""


def make_handler(video_path: Path, srt_path: Path):
    class SubtitleReviewHandler(BaseHTTPRequestHandler):
        def _send_json(self, payload: object, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                html = build_app_html(video_path.name, srt_path.name).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
                return
            if parsed.path == "/api/subtitles":
                self._send_json(load_srt_entries(srt_path))
                return
            if parsed.path == "/video":
                if not video_path.exists():
                    self.send_error(404, "video not found")
                    return
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(video_path.stat().st_size))
                self.end_headers()
                with video_path.open("rb") as handle:
                    self.wfile.write(handle.read())
                return
            self.send_error(404, "not found")

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/api/subtitles":
                self.send_error(404, "not found")
                return
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            save_srt_entries(srt_path, payload)
            self._send_json({"success": True, "path": str(srt_path)})

        def log_message(self, format: str, *args) -> None:
            return

    return SubtitleReviewHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local browser subtitle review server")
    parser.add_argument("video", help="Input video path")
    parser.add_argument("--srt", required=True, help="Editable subtitle path")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8898, help="Bind port")
    args = parser.parse_args(argv)

    video_path = Path(args.video)
    srt_path = Path(args.srt)
    if not video_path.exists():
        raise SystemExit(f"video not found: {video_path}")
    if not srt_path.exists():
        raise SystemExit(f"srt not found: {srt_path}")

    server = ThreadingHTTPServer((args.host, args.port), make_handler(video_path, srt_path))
    print(f"http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
