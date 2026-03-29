from __future__ import annotations

import argparse
from email.parser import BytesParser
from email.policy import default as email_default_policy
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from video_postprocess import ass_writer
from video_postprocess import cover_generator
from video_postprocess import ffmpeg_ops
from video_postprocess import transcribe
from video_postprocess.paths import derive_output_paths
from video_postprocess.srt_utils import load_srt
from video_postprocess.web_service import LocalWebService, guess_artifact_path
from video_postprocess.web_workflow import LocalWebWorkflow


def build_page_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>口播视频后处理</title>
  <style>
    :root {
      --bg-a:#fff1d6;
      --bg-b:#f4e3c9;
      --card:rgba(255, 250, 241, 0.96);
      --line:#e2d4bf;
      --ink:#171717;
      --muted:#6a6055;
      --accent:#101010;
      --accent-2:#f2b633;
      --danger:#c91d1d;
    }
    * { box-sizing:border-box; }
    body {
      margin:0;
      min-height:100vh;
      font-family:"Microsoft YaHei","PingFang SC",sans-serif;
      color:var(--ink);
      background:
        radial-gradient(circle at top left, rgba(255,255,255,.6) 0, rgba(255,255,255,0) 22%),
        linear-gradient(135deg, var(--bg-a) 0%, var(--bg-b) 100%);
    }
    .wrap { width:min(1260px, calc(100vw - 28px)); margin:18px auto 40px; }
    .hero {
      padding:22px 24px;
      border-radius:28px;
      background:linear-gradient(135deg, rgba(255,255,255,.74), rgba(255,247,234,.92));
      border:1px solid rgba(255,255,255,.7);
      box-shadow:0 18px 50px rgba(107, 76, 18, .12);
      margin-bottom:18px;
    }
    .hero-top { display:flex; justify-content:space-between; gap:16px; align-items:flex-start; flex-wrap:wrap; }
    h1 { margin:0 0 10px; font-size:34px; letter-spacing:.02em; }
    .sub { color:var(--muted); font-size:14px; line-height:1.7; max-width:720px; }
    .steps { display:flex; gap:10px; flex-wrap:wrap; }
    .step-pill {
      padding:10px 14px;
      border-radius:999px;
      background:rgba(16,16,16,.06);
      border:1px solid rgba(16,16,16,.08);
      font-size:12px;
      font-weight:700;
    }
    .grid { display:grid; grid-template-columns:360px 1fr; gap:18px; align-items:start; }
    .stack { display:flex; flex-direction:column; gap:16px; }
    .card {
      background:var(--card);
      border:1px solid var(--line);
      border-radius:26px;
      padding:18px;
      box-shadow:0 20px 44px rgba(82, 54, 14, .08);
      backdrop-filter: blur(16px);
    }
    .card h2 { margin:0 0 12px; font-size:20px; }
    .card-head { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:10px; }
    .label {
      display:inline-flex; align-items:center; justify-content:center;
      min-width:34px; height:34px; border-radius:999px;
      background:var(--accent);
      color:#fff; font-size:13px; font-weight:700;
    }
    .field { display:flex; flex-direction:column; gap:6px; }
    .field label { font-size:12px; font-weight:700; color:var(--muted); }
    input, select, button, textarea { font:inherit; }
    input[type="text"], input[type="file"], select, textarea {
      width:100%;
      border:1px solid var(--line);
      border-radius:16px;
      padding:12px 14px;
      background:#fff;
    }
    textarea {
      min-height:78px;
      resize:vertical;
      line-height:1.6;
    }
    .field-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
    .field-grid.single { grid-template-columns:1fr; }
    .hint { font-size:12px; color:var(--muted); line-height:1.6; }
    .btn-row { display:flex; gap:10px; flex-wrap:wrap; }
    button {
      border:0;
      cursor:pointer;
      border-radius:999px;
      padding:12px 18px;
      font-weight:700;
    }
    button.primary {
      background:linear-gradient(135deg, #151515, #2b2b2b);
      color:#fff;
      box-shadow:0 14px 26px rgba(0,0,0,.16);
    }
    button.secondary {
      background:#fff;
      color:var(--accent);
      border:1px solid var(--line);
    }
    button:disabled { opacity:.6; cursor:not-allowed; }
    .status {
      padding:14px 16px;
      border-radius:18px;
      background:#fff;
      border:1px solid var(--line);
      color:var(--muted);
      min-height:66px;
      white-space:pre-wrap;
      line-height:1.65;
    }
    .result-links { display:flex; gap:12px; flex-wrap:wrap; margin-top:12px; }
    .result-links a { color:#0b57d0; text-decoration:none; font-weight:700; }
    .workspace {
      display:grid;
      grid-template-columns:minmax(320px, 420px) minmax(0, 1fr);
      gap:18px;
      align-items:start;
    }
    .phone {
      padding:16px;
      border-radius:30px;
      background:linear-gradient(180deg, #151515 0%, #090909 100%);
      box-shadow:0 24px 50px rgba(0,0,0,.22);
    }
    .phone-screen {
      aspect-ratio:9 / 16;
      overflow:hidden;
      border-radius:22px;
      background:#000;
    }
    video { width:100%; height:100%; display:block; background:#000; }
    .subtitle-panel { min-height:680px; }
    .subtitle-toolbar { display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
    .subtitle-loading {
      display:flex;
      flex-direction:column;
      align-items:center;
      justify-content:center;
      gap:14px;
      min-height:360px;
      border:1px dashed var(--line);
      border-radius:22px;
      background:linear-gradient(180deg, rgba(255,255,255,.74), rgba(255,246,231,.92));
      text-align:center;
      padding:24px;
    }
    .spinner {
      width:44px;
      height:44px;
      border-radius:999px;
      border:4px solid rgba(16,16,16,.12);
      border-top-color:var(--accent-2);
      animation:spin 1s linear infinite;
    }
    .loading-title { font-size:20px; font-weight:800; }
    .loading-sub { color:var(--muted); line-height:1.7; max-width:420px; }
    .subtitle-list { display:flex; flex-direction:column; gap:12px; max-height:72vh; overflow:auto; padding-right:4px; }
    .subtitle-item {
      background:#fff;
      border:1px solid var(--line);
      border-radius:18px;
      padding:12px;
      box-shadow:0 10px 24px rgba(87, 61, 21, .05);
    }
    .time { font-size:12px; color:var(--muted); margin-bottom:8px; }
    .hidden { display:none !important; }
    @keyframes spin { to { transform: rotate(360deg); } }
    @media (max-width: 980px) {
      .grid, .workspace { grid-template-columns:1fr; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="hero-top">
        <div>
          <h1>口播视频后处理</h1>
          <div class="sub">上传视频，自动转字幕，在网页里逐条修字幕，再生成封面、片头和最终成片。整个流程更像剪映类自媒体工具，而不是后台表单。</div>
        </div>
        <div class="steps">
          <div class="step-pill">1 上传视频</div>
          <div class="step-pill">2 自动转字幕</div>
          <div class="step-pill">3 网页修字幕</div>
          <div class="step-pill">4 生成成片</div>
        </div>
      </div>
    </section>

    <div class="grid">
      <aside class="stack">
        <section class="card">
          <div class="card-head">
            <h2><span class="label">1</span> 上传视频</h2>
          </div>
          <form id="upload-form" class="stack">
            <div class="field">
              <label for="video-file">选择视频</label>
              <input id="video-file" type="file" name="video" accept=".qt,.mov,.mp4,.m4v,.avi,.mkv,video/*,*/*" required>
            </div>
            <div class="field">
              <label for="transcribe-model-select">转写模型</label>
              <select id="transcribe-model-select" name="model_size">
                <option value="small">small</option>
                <option value="medium" selected>medium</option>
                <option value="large-v3">large-v3</option>
              </select>
            </div>
            <div class="btn-row">
              <button class="primary" type="submit">开始转字幕</button>
              <button id="reset-project" class="secondary" type="button">重新选择视频</button>
            </div>
          </form>
          <div class="hint">支持 `.qt`、`.mov`、`.mp4` 等常见格式。如果系统文件选择器没有显示 `.qt`，可以切到“所有文件”。</div>
        </section>

        <section class="card">
          <div class="card-head">
            <h2><span class="label">2</span> 生成设置</h2>
          </div>
          <form id="render-form" class="stack">
            <div class="field-grid">
              <div class="field">
                <label for="speed-select">倍速</label>
                <select id="speed-select">
                  <option value="1.00">1.00x</option>
                  <option value="1.10">1.10x</option>
                  <option value="1.15">1.15x</option>
                  <option value="1.20">1.20x</option>
                  <option value="1.25" selected>1.25x</option>
                  <option value="1.30">1.30x</option>
                  <option value="1.50">1.50x</option>
                </select>
              </div>
              <div class="field">
                <label for="cover-font-select">封面字体</label>
                <select id="cover-font-select">
                  <option value="Microsoft YaHei" selected>Microsoft YaHei</option>
                  <option value="SimHei">SimHei</option>
                  <option value="PingFang SC">PingFang SC</option>
                </select>
              </div>
            </div>
            <div class="field">
              <label for="cover-title">主标题</label>
              <input id="cover-title" type="text" value="第一句就垮">
            </div>
            <div class="field">
              <label for="cover-subtitle">副标题</label>
              <input id="cover-subtitle" type="text" value="方法篇">
            </div>
            <div class="btn-row">
              <button class="primary" type="submit">生成成片</button>
            </div>
          </form>
        </section>

        <section class="card">
          <div class="card-head">
            <h2><span class="label">3</span> 当前状态</h2>
          </div>
          <div id="status" class="status">还没有项目，先上传视频。</div>
          <div id="result-links" class="result-links"></div>
        </section>
      </aside>

      <main class="stack">
        <section class="workspace">
          <div class="phone">
            <div class="phone-screen">
              <video id="video" controls></video>
            </div>
          </div>

          <section class="card subtitle-panel">
            <div class="subtitle-toolbar">
              <h2><span class="label">4</span> 字幕工作台</h2>
              <div class="btn-row">
                <button id="save-subtitles" class="secondary" type="button">保存字幕</button>
              </div>
            </div>

            <div id="subtitle-loading" class="subtitle-loading">
              <div class="spinner"></div>
              <div class="loading-title">正在转字幕...</div>
              <div class="loading-sub" id="subtitle-loading-text">Whisper 正在听音频并生成可编辑字幕，完成后这里会自动切换成字幕编辑区。</div>
            </div>

            <div id="subtitle-list" class="subtitle-list hidden"></div>
          </section>
        </section>
      </main>
    </div>
  </div>

  <script>
    let currentProject = null;
    let subtitles = [];

    async function fetchJson(url, options) {
      const response = await fetch(url, options);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Request failed');
      }
      return await response.json();
    }

    function setStatus(message) {
      document.getElementById('status').textContent = message;
    }

    function renderResultLinks(project) {
      const wrap = document.getElementById('result-links');
      wrap.innerHTML = '';
      if (!project) return;
      const links = [];
      if (project.final_video_url) links.push(`<a href="${project.final_video_url}" target="_blank">查看成片</a>`);
      if (project.cover_image_url) links.push(`<a href="${project.cover_image_url}" target="_blank">查看封面</a>`);
      wrap.innerHTML = links.join('');
    }

    function setSubtitleLoading(visible, title, subtitle) {
      const loading = document.getElementById('subtitle-loading');
      const list = document.getElementById('subtitle-list');
      const textNode = document.getElementById('subtitle-loading-text');
      loading.querySelector('.loading-title').textContent = title;
      textNode.textContent = subtitle;
      loading.classList.toggle('hidden', !visible);
      list.classList.toggle('hidden', visible);
    }

    function renderSubtitles() {
      const list = document.getElementById('subtitle-list');
      if (!subtitles.length) {
        list.innerHTML = '';
        return;
      }
      list.innerHTML = subtitles.map((item, index) => `
        <div class="subtitle-item">
          <div class="time">${index + 1}. ${item.start} --> ${item.end}</div>
          <textarea data-index="${index}">${item.text}</textarea>
        </div>
      `).join('');
      document.querySelectorAll('#subtitle-list textarea').forEach((node) => {
        node.addEventListener('input', (event) => {
          subtitles[Number(event.target.dataset.index)].text = event.target.value;
        });
      });
    }

    async function loadSubtitles() {
      if (!currentProject || !['review', 'rendering', 'done'].includes(currentProject.status)) {
        subtitles = [];
        renderSubtitles();
        return;
      }
      subtitles = await fetchJson('/api/project/current/subtitles');
      renderSubtitles();
    }

    async function refreshProject() {
      currentProject = await fetchJson('/api/project/current');
      const video = document.getElementById('video');

      if (!currentProject) {
        setStatus('还没有项目，先上传视频。');
        renderResultLinks(null);
        subtitles = [];
        renderSubtitles();
        setSubtitleLoading(true, '等待上传视频', '上传视频后，这里会显示“正在转字幕”动效，完成后自动切换为可编辑字幕列表。');
        video.removeAttribute('src');
        video.load();
        return;
      }

      let statusText = `当前状态：${currentProject.status}`;
      if (currentProject.status === 'transcribing') {
        statusText += '\\n正在自动听音频生成字幕，完成后右侧会出现可编辑字幕。';
        setSubtitleLoading(true, '正在转字幕...', 'Whisper 正在听音频并生成可编辑字幕，预计完成后这里会自动切换成字幕编辑区。');
      } else if (currentProject.status === 'review') {
        statusText += '\\n字幕已经生成，可以直接在右侧修改并保存。';
        setSubtitleLoading(false, '', '');
      } else if (currentProject.status === 'rendering') {
        statusText += '\\n正在生成封面、片头和最终成片。';
        setSubtitleLoading(true, '正在生成成片...', '正在处理封面、片头、字幕烧录和视频导出，请稍等。');
      } else if (currentProject.status === 'done') {
        statusText += '\\n生成完成，可以查看成片和封面。';
        setSubtitleLoading(false, '', '');
      } else if (currentProject.status === 'error') {
        setSubtitleLoading(true, '处理失败', currentProject.error || '发生未知错误，请把状态里的报错发给我。');
      }

      if (currentProject.error) {
        statusText += `\\n错误：${currentProject.error}`;
      }
      setStatus(statusText);

      if (currentProject.video_url && video.getAttribute('src') !== currentProject.video_url) {
        video.src = currentProject.video_url;
        video.load();
      }

      renderResultLinks(currentProject);
      await loadSubtitles();
    }

    document.getElementById('upload-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const form = new FormData(event.target);
      setStatus('开始上传并转字幕...');
      setSubtitleLoading(true, '正在转字幕...', '视频已提交，Whisper 正在听音频并生成字幕。');
      try {
        await fetchJson('/api/upload', { method: 'POST', body: form });
        await refreshProject();
      } catch (error) {
        setStatus(`上传失败：${error.message}`);
        setSubtitleLoading(true, '上传失败', '请重新选择视频后再试。');
      }
    });

    document.getElementById('save-subtitles').addEventListener('click', async () => {
      if (!currentProject) return;
      await fetchJson('/api/project/current/subtitles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subtitles),
      });
      setStatus('字幕已保存。');
    });

    document.getElementById('reset-project').addEventListener('click', async () => {
      await fetchJson('/api/project/current/reset', { method: 'POST' });
      document.querySelector('#video-file').value = '';
      await refreshProject();
    });

    document.getElementById('render-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!currentProject) return;
      const payload = {
        speed: Number(document.getElementById('speed-select').value || '1.25'),
        cover_title: document.getElementById('cover-title').value,
        cover_subtitle: document.getElementById('cover-subtitle').value,
        cover_font: document.getElementById('cover-font-select').value || 'Microsoft YaHei',
        intro_duration: 0.5,
      };
      setStatus('开始生成成片...');
      setSubtitleLoading(true, '正在生成成片...', '正在处理封面、片头、字幕烧录和视频导出，请稍等。');
      try {
        await fetchJson('/api/project/current/render', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        await refreshProject();
      } catch (error) {
        setStatus(`生成失败：${error.message}`);
        setSubtitleLoading(true, '生成失败', '请检查状态区报错信息。');
      }
    });

    setSubtitleLoading(true, '等待上传视频', '上传视频后，这里会显示“正在转字幕”动效，完成后自动切换为可编辑字幕列表。');
    refreshProject();
    setInterval(refreshProject, 2000);
  </script>
</body>
</html>"""


def default_transcribe_runner(
    video_path: Path,
    auto_srt_path: Path,
    language: str = "zh",
    model_size: str = "medium",
    device: str = "auto",
    ffmpeg_bin: str = "ffmpeg",
) -> None:
    resolved_ffmpeg = ffmpeg_ops.ensure_command_available(ffmpeg_bin)
    transcribe.transcribe_video_to_srt(
        video_path=video_path,
        auto_srt_path=auto_srt_path,
        language=language,
        model_size=model_size,
        device=device,
        ffmpeg_bin=resolved_ffmpeg,
    )


def default_render_runner(
    video_path: Path,
    srt_path: Path,
    out_dir: Path,
    speed: float,
    cover_title: str,
    cover_subtitle: str,
    cover_font: str,
    intro_duration: float,
) -> None:
    ffmpeg_bin = ffmpeg_ops.ensure_command_available("ffmpeg")
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = derive_output_paths(video_path, out_dir)
    entries = load_srt(srt_path)
    highlight_terms = ass_writer.detect_highlight_terms(entries)
    ass_text = ass_writer.build_ass_document(entries, ass_writer.AssStyle.default(), highlight_terms=highlight_terms)
    paths.ass_subtitle.write_text(ass_text, encoding="utf-8")

    intro_video = None
    if cover_title:
        cover_generator.extract_cover_frame(ffmpeg_bin, video_path, paths.cover_frame)
        cover_generator.create_cover_image(
            frame_path=paths.cover_frame,
            output_path=paths.cover_image,
            title=cover_title,
            subtitle=cover_subtitle,
            font_name=cover_font,
        )
        cover_generator.create_intro_video(ffmpeg_bin, paths.cover_image, paths.intro_video, duration=intro_duration)
        intro_video = paths.intro_video

    command = ffmpeg_ops.build_render_command(
        ffmpeg_bin=ffmpeg_bin,
        video_path=video_path,
        ass_path=paths.ass_subtitle,
        output_path=paths.final_video,
        speed=speed,
        intro_video=intro_video,
    )
    ffmpeg_ops.run_command(command)


def guess_content_type(path: Path) -> str:
    guessed, _encoding = mimetypes.guess_type(str(path))
    if guessed:
        return guessed
    if path.suffix.lower() in {".mov", ".qt"}:
        return "video/quicktime"
    if path.suffix.lower() == ".mp4":
        return "video/mp4"
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        return "image/jpeg"
    return "application/octet-stream"


def parse_multipart_form(content_type: str, body: bytes) -> tuple[dict[str, tuple[str, bytes]], dict[str, str]]:
    message = BytesParser(policy=email_default_policy).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
    )
    files: dict[str, tuple[str, bytes]] = {}
    fields: dict[str, str] = {}
    for part in message.iter_parts():
        content_disposition = part.get("Content-Disposition", "")
        if "form-data" not in content_disposition:
            continue
        name = part.get_param("name", header="Content-Disposition")
        filename = part.get_filename()
        if not name:
            continue
        if filename:
            files[name] = (filename, part.get_payload(decode=True) or b"")
        else:
            fields[name] = part.get_content().strip()
    return files, fields


def make_handler(service: LocalWebService):
    class LocalWebHandler(BaseHTTPRequestHandler):
        def _send_json(self, payload: object, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, file_path: Path) -> None:
            if not file_path.exists():
                self.send_error(404, "file not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", guess_content_type(file_path))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(file_path.stat().st_size))
            self.end_headers()
            with file_path.open("rb") as handle:
                self.wfile.write(handle.read())

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                body = build_page_html().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/api/project/current":
                self._send_json(service.serialize_project(service.get_project()))
                return
            if parsed.path == "/api/project/current/subtitles":
                project = service.get_project()
                if project is None:
                    self._send_json([], status=200)
                    return
                self._send_json(service.load_subtitles(project.project_id))
                return
            if parsed.path.startswith("/projects/"):
                parts = parsed.path.strip("/").split("/")
                if len(parts) == 3 and parts[2] == "video":
                    project = service.get_project(parts[1])
                    if project is None:
                        self.send_error(404, "project not found")
                        return
                    self._send_file(project.video_path)
                    return
                if len(parts) == 4 and parts[2] == "artifacts":
                    project = service.get_project(parts[1])
                    if project is None:
                        self.send_error(404, "project not found")
                        return
                    try:
                        artifact = guess_artifact_path(project, parts[3])
                    except KeyError:
                        self.send_error(404, "artifact not found")
                        return
                    self._send_file(artifact)
                    return
            self.send_error(404, "not found")

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/api/upload":
                content_type = self.headers.get("Content-Type", "")
                content_length = int(self.headers.get("Content-Length", "0"))
                files, fields = parse_multipart_form(content_type, self.rfile.read(content_length))
                if "video" not in files:
                    self._send_json({"error": "video file is required"}, status=400)
                    return
                filename, content = files["video"]
                model_size = fields.get("model_size", "medium")
                project = service.create_project_from_upload(Path(filename).name, content, model_size=model_size)
                self._send_json(service.serialize_project(project), status=201)
                return
            if parsed.path == "/api/project/current/subtitles":
                project = service.get_project()
                if project is None:
                    self._send_json({"error": "project not found"}, status=404)
                    return
                content_length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                service.save_subtitles(project.project_id, payload)
                self._send_json({"success": True})
                return
            if parsed.path == "/api/project/current/render":
                project = service.get_project()
                if project is None:
                    self._send_json({"error": "project not found"}, status=404)
                    return
                content_length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                result = service.start_render(
                    project.project_id,
                    speed=float(payload.get("speed", 1.25)),
                    cover_title=str(payload.get("cover_title", "")),
                    cover_subtitle=str(payload.get("cover_subtitle", "")),
                    cover_font=str(payload.get("cover_font", "Microsoft YaHei")),
                    intro_duration=float(payload.get("intro_duration", 0.5)),
                )
                self._send_json(result)
                return
            if parsed.path == "/api/project/current/reset":
                service.clear_current_project()
                self._send_json({"success": True})
                return
            self.send_error(404, "not found")

        def log_message(self, format: str, *args) -> None:
            return

    return LocalWebHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local single-user web app for talking-head video postprocess")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8899, help="Bind port")
    parser.add_argument(
        "--workspace",
        default=str(Path(__file__).resolve().parents[1] / "web_runs"),
        help="Workspace directory",
    )
    args = parser.parse_args(argv)

    workflow = LocalWebWorkflow(Path(args.workspace), reset_workspace=True)
    service = LocalWebService(workflow, transcribe_runner=default_transcribe_runner, render_runner=default_render_runner)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(service))
    print(f"http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
