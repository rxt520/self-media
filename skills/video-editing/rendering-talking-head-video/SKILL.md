---
name: rendering-talking-head-video
description: Use when a talking-head video already has a corrected subtitle file and needs a final burned-in export with fixed style and playback speed
---

# Rendering Talking-Head Video

## Overview

Use this skill when the user already has a corrected `.srt` and wants the final exported MP4. This skill wraps the local Python CLI in `C:\custom\project1\ideas\self-media\scripts\video-editing`.

Core rule: rendering uses the project's fixed style defaults unless the user explicitly asks for different output behavior.

## When to Use

- The user says "烧录字幕", "导出成片", "最终视频", or "渲染"
- A corrected `.srt` file already exists
- The user wants the default style:
  - `微软雅黑`
  - white subtitles
  - yellow highlights
  - bottom-center placement
  - `1.25x` playback speed

Do not use this skill for speech recognition. Use `transcribing-talking-head-subtitles` first.

## Command

Run from:

```powershell
Set-Location 'C:\custom\project1\ideas\self-media\scripts\video-editing'
```

Render final video:

```powershell
python video_postprocess.py render 'C:\path\to\input.mp4' --srt 'C:\path\to\input.edit.srt' --out-dir 'C:\path\to\output'
```

Render with highlighted terms:

```powershell
python video_postprocess.py render 'C:\path\to\input.mp4' --srt 'C:\path\to\input.edit.srt' --out-dir 'C:\path\to\output' --highlight '流程,剪辑,测试'
```

## Expected Output

For `input.mp4`, the command writes:

- `input.ass`
- `input.final.mp4`
- `tmp/`

## Styling Defaults

- font: `Microsoft YaHei`
- main text: white
- highlight text: yellow
- placement: bottom center
- speed: `1.25x`

## Verification

After render, confirm:

- the corrected `.srt` existed
- the `.ass` file was generated
- the `.final.mp4` file was generated

If render fails because `ffmpeg` is unavailable, stop and surface that dependency issue.
