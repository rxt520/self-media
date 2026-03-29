# Self-Media Open Source Restructure Design

## Goal

Restructure `C:\custom\project1\ideas\self-media` into a repository that can be published to GitHub as an open-source project. The public repository should contain only reusable scripts, templates, and methodology. Private working materials such as real datasets, review notes, generated outputs, and concrete draft content must be isolated from the public surface.

## Current State

- The root directory mixes Python tooling, Codex skills, planning notes, review notes, spreadsheets, templates, and generated artifacts.
- `script/` contains the reusable Python CLI, tests, smoke files, and generated outputs.
- `video-cut-skills/` contains reusable local skills and helper scripts, but its documentation references the old `script/` path through absolute paths.
- Root-level Markdown and spreadsheet files combine public methodology with private planning and working data.
- `self-media` is not currently a git repository.

## Repository Boundary

The future public repository should include only:

- reusable scripts
- reusable skills
- reusable templates and frameworks
- reusable methodology and usage documentation

The future public repository should exclude from version control by default:

- spreadsheets and extracted data
- review round notes
- concrete topic drafts and filled-in scripts tied to current work
- generated subtitles, preview outputs, and exported videos
- local caches and Python build artifacts

## Proposed Structure

```text
self-media/
├─ .gitignore
├─ README.md
├─ scripts/
│  └─ video-editing/
│     ├─ README.md
│     ├─ requirements.txt
│     ├─ video_postprocess.py
│     ├─ web_app.py
│     ├─ video_postprocess/
│     └─ tests/
├─ skills/
│  └─ video-editing/
│     ├─ README.md
│     ├─ dictionary-correcting-subtitles/
│     ├─ rendering-talking-head-video/
│     ├─ reviewing-subtitles-in-browser/
│     ├─ running-talking-head-postprocess/
│     ├─ transcribing-talking-head-subtitles/
│     └─ tests/
├─ templates/
│  ├─ script-frameworks/
│  └─ cover-opening-frameworks/
├─ docs/
│  ├─ methodology/
│  ├─ planning/
│  ├─ rules/
│  └─ superpowers/
│     └─ specs/
└─ private/
   ├─ data/
   ├─ reviews/
   ├─ drafts/
   └─ generated/
```

## Planned Moves

### Public content

- Move `script/` to `scripts/video-editing/`
- Move `video-cut-skills/` to `skills/video-editing/`
- Move `口播脚本1.5分钟版本/` to `templates/script-frameworks/`
- Move `口播脚本1.5分钟版本辅助/` to `templates/cover-opening-frameworks/`
- Move `抖音口播脚本生成规则.md` to `docs/rules/`
- Move `规则迭代结论.md` to `docs/methodology/`
- Move `30天规划.md`, `30天规划-10子代理版.md`, and `6条短稿拍摄顺序与14天执行规划.md` to `docs/planning/`

### Private content

- Move `关注转化版-3类内容/` to `private/drafts/attention-conversion-content/`
- Move `口播脚本1.5分钟版本填充内容/` to `private/drafts/filled-script-examples/`
- Move `多代理脚本评审-第1轮.md`, `多代理脚本评审-第2轮.md`, and `多代理脚本评审-第3轮.md` to `private/reviews/`
- Move all root-level `.xlsx` files to `private/data/`
- Move `_work_data_summary.md` to `private/data/`
- Move `大纲` to `private/drafts/`
- Move generated runtime outputs under the script area into `private/generated/` when practical, otherwise keep them in place and ignore them through `.gitignore`

## Documentation Changes

### Root README

Create a root `README.md` that covers:

- project purpose and open-source scope
- top-level directory guide
- prerequisites
- quick start for the Python video editing script
- how the reusable skills relate to the script
- what is intentionally not committed

### Script README

Update the existing script README after relocation so:

- relative paths reflect `scripts/video-editing/`
- commands still run from the new directory
- examples remain minimal and copyable

### Skills README and Skill Files

Update `skills/video-editing/README.md` and every affected `SKILL.md` so:

- old absolute paths pointing to `self-media\script` are changed to `self-media\scripts\video-editing`
- old absolute paths pointing to `self-media\video-cut-skills` are changed to `self-media\skills\video-editing`
- helper script references remain valid after the move

## Git Ignore Strategy

The root `.gitignore` should ignore at minimum:

- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- `.venv/`
- `venv/`
- `private/`
- `Thumbs.db`
- `.DS_Store`
- script runtime outputs such as `web_runs/`
- smoke output directories and rendered media outputs

The ignore policy should allow the reusable smoke fixture inputs and test files to remain versioned if they are useful for testing, while excluding generated outputs.

## Git Initialization

Initialize git in `self-media` as part of the implementation so the directory is ready for GitHub publication. The first tracked state should reflect the cleaned structure and `.gitignore`.

## Error Handling And Safety

- Preserve all existing files by moving them rather than deleting them.
- Update references after moves so documentation and skills do not break.
- Treat ambiguous content as private by default if it appears tied to current work rather than reusable framework material.
- Avoid committing private content by ensuring `.gitignore` is added before the first broad `git add`.

## Testing And Verification

Implementation should verify:

- the Python CLI still imports and runs from `scripts/video-editing/`
- tests under the moved script package still run
- helper scripts in the moved skills package still resolve correctly
- README commands match the new paths
- `git status --short` shows private content ignored as intended

## Open Questions Resolved In This Design

- Physical file moves should happen now rather than staging a gradual migration.
- Only reusable scripts, templates, and methodology belong in the public repository.
- Existing concrete drafts, review notes, spreadsheets, and generated outputs belong in `private/` and should be ignored by git.
