---
name: transcribing-talking-head-subtitles
description: Use when a talking-head video needs editable subtitles generated from speech before review, correction, or final burn-in
---

# Transcribing Talking-Head Subtitles

## Overview

Use this skill when the user has already shot a talking-head video and needs an editable subtitle draft. This skill wraps the local Python CLI in `C:\custom\project1\ideas\self-media\scripts\video-editing`.

Core rule: this skill stops at `.auto.srt`. It does not burn subtitles into video.

## When to Use

- The user says "加字幕", "转写字幕", "生成 srt", or "先出字幕稿"
- The input is a local video file
- The user wants to manually correct subtitle text before rendering

Do not use this skill when the user already has a corrected `.srt` and only needs final export. Use `rendering-talking-head-video` instead.

## Command

Run from:

```powershell
Set-Location 'C:\custom\project1\ideas\self-media\scripts\video-editing'
```

Generate editable subtitles:

```powershell
python video_postprocess.py transcribe 'C:\path\to\input.mp4' --out-dir 'C:\path\to\output'
```

Optional flags:

```powershell
python video_postprocess.py transcribe 'C:\path\to\input.mp4' --out-dir 'C:\path\to\output' --language zh --model-size small --device auto
```

## Expected Output

For `input.mp4`, the command writes:

- `input.auto.srt`
- `tmp/`

The subtitle draft should then be reviewed and corrected by the user or by a later subtitle review workflow.

## Common Mistakes

- Passing a directory instead of a video file
- Claiming the video is ready for publishing after only generating `.auto.srt`
- Skipping the manual subtitle correction step for brand names or jargon

## Verification

Minimum verification after running:

- Confirm the command exits with code `0`
- Confirm `<out-dir>\<video-stem>.auto.srt` exists
- If the source video is silent, expect an empty or near-empty subtitle file
