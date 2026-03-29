---
name: running-talking-head-postprocess
description: Use when a user needs the full local workflow for a talking-head video from subtitle draft generation through corrected burn-in export
---

# Running Talking-Head Postprocess

## Overview

Use this skill for the end-to-end workflow around the local postprocess CLI in `C:\custom\project1\ideas\self-media\scripts\video-editing`.

This skill orchestrates the workflow. It does not replace the more focused skills:

- `transcribing-talking-head-subtitles`
- `rendering-talking-head-video`

## Workflow

1. Generate subtitle draft
2. Ask the user to review and correct the `.srt`
3. Render the final video with burned-in subtitles

## Step 1: Generate Draft Subtitles

Use:

```powershell
Set-Location 'C:\custom\project1\ideas\self-media\scripts\video-editing'
python video_postprocess.py transcribe 'C:\path\to\input.mp4' --out-dir 'C:\path\to\output'
```

Expected file:

- `input.auto.srt`

## Step 2: Correction Checkpoint

Tell the user to review the generated subtitle file before final render.

Expected corrected file:

- `input.edit.srt`

If the user wants keyword emphasis, ask for comma-separated highlight terms before rendering.

## Step 3: Render Final Video

Use:

```powershell
Set-Location 'C:\custom\project1\ideas\self-media\scripts\video-editing'
python video_postprocess.py render 'C:\path\to\input.mp4' --srt 'C:\path\to\input.edit.srt' --out-dir 'C:\path\to\output'
```

Optional highlight example:

```powershell
python video_postprocess.py render 'C:\path\to\input.mp4' --srt 'C:\path\to\input.edit.srt' --out-dir 'C:\path\to\output' --highlight '流程,剪辑'
```

## Verification Checklist

- `.auto.srt` exists after transcription
- corrected `.srt` exists before render
- `.ass` exists after render
- `.final.mp4` exists after render

## Escalation Path

If the user wants stronger capabilities later, extend the workflow in this order:

1. term dictionary correction
2. local subtitle review web UI
3. pause filler removal
4. segment-based precision cutting
