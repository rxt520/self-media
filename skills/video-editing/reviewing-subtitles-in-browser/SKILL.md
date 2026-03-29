---
name: reviewing-subtitles-in-browser
description: Use when a user needs to preview a local talking-head video and edit subtitle text in a browser before saving the corrected srt file
---

# Reviewing Subtitles In Browser

## Overview

Use this skill when plain text editing is too slow and the user wants a local browser review loop with video preview. This skill runs a small local HTTP server and edits subtitle text only.

Core rule: this skill edits subtitle text, not timestamp timing.

## Files

- helper script: [subtitle_review_server.py](C:/custom/project1/ideas/self-media/skills/video-editing/reviewing-subtitles-in-browser/subtitle_review_server.py)

## Command

Run:

```powershell
python 'C:\custom\project1\ideas\self-media\skills\video-editing\reviewing-subtitles-in-browser\subtitle_review_server.py' `
  'C:\path\to\input.mp4' `
  --srt 'C:\path\to\input.edit.srt' `
  --port 8898
```

Then open:

```text
http://127.0.0.1:8898
```

## What It Does

- previews the video in the browser
- loads subtitle text from the `.srt`
- allows direct text editing
- saves the edited subtitle back to the same `.srt`

## When Not to Use

- when the user needs precise timestamp retiming
- when the user only needs deterministic term replacement
- when the final video is already rendered

## Verification

- the local URL opens
- subtitle rows appear
- editing and pressing save updates the `.srt` file on disk

