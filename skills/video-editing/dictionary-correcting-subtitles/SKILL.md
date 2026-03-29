---
name: dictionary-correcting-subtitles
description: Use when auto-generated subtitles contain recurring jargon, brand names, or repeated recognition mistakes that should be corrected consistently before final render
---

# Dictionary Correcting Subtitles

## Overview

Use this skill after `transcribing-talking-head-subtitles` and before `rendering-talking-head-video`. It applies deterministic term replacements to a subtitle file.

Core rule: this skill corrects recurring terms only. It does not review timing, punctuation, or sentence segmentation.

## When to Use

- The same brand name is repeatedly mistranscribed
- The user has a stable vocabulary list
- The subtitle draft is mostly correct but terminology is noisy

## Files

- skill dictionary: [dictionary.txt](C:/custom/project1/ideas/self-media/skills/video-editing/dictionary-correcting-subtitles/dictionary.txt)
- helper script: [apply_dictionary.py](C:/custom/project1/ideas/self-media/skills/video-editing/dictionary-correcting-subtitles/apply_dictionary.py)

## Command

Run:

```powershell
python 'C:\custom\project1\ideas\self-media\skills\video-editing\dictionary-correcting-subtitles\apply_dictionary.py' `
  'C:\path\to\clip.auto.srt' `
  --dictionary 'C:\custom\project1\ideas\self-media\skills\video-editing\dictionary-correcting-subtitles\dictionary.txt' `
  --output 'C:\path\to\clip.edit.srt'
```

## Dictionary Format

One rule per line:

```text
鍘熻瘝 => 淇璇?```

Blank lines and lines starting with `#` are ignored.

## Verification

- Confirm the output `.srt` exists
- Confirm known terms were replaced
- Still review the subtitle manually before final render

