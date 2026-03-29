# Self-Media Open Source Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize `self-media` into a GitHub-ready open-source repository that keeps only reusable scripts, templates, and methodology public while isolating private working materials.

**Architecture:** Keep the repository split into five top-level areas: `scripts/` for executable tooling, `skills/` for reusable Codex skills, `templates/` for reusable content frameworks, `docs/` for public methodology, and `private/` for ignored working materials. Apply safety rails first with a root `.gitignore`, then move private content out of the public surface, then relocate public code and documentation and fix path references.

**Tech Stack:** Git, PowerShell, Python 3.10+, pytest, Markdown

---

## File Structure Map

### Public files and directories

- Create: `.gitignore`
- Create: `README.md`
- Create: `scripts/`
- Create: `scripts/video-editing/`
- Move: `script/README.md` -> `scripts/video-editing/README.md`
- Move: `script/requirements.txt` -> `scripts/video-editing/requirements.txt`
- Move: `script/video_postprocess.py` -> `scripts/video-editing/video_postprocess.py`
- Move: `script/web_app.py` -> `scripts/video-editing/web_app.py`
- Move: `script/video_postprocess/` -> `scripts/video-editing/video_postprocess/`
- Move: `script/tests/` -> `scripts/video-editing/tests/`
- Move: `video-cut-skills/README.md` -> `skills/video-editing/README.md`
- Move: `video-cut-skills/dictionary-correcting-subtitles/` -> `skills/video-editing/dictionary-correcting-subtitles/`
- Move: `video-cut-skills/rendering-talking-head-video/` -> `skills/video-editing/rendering-talking-head-video/`
- Move: `video-cut-skills/reviewing-subtitles-in-browser/` -> `skills/video-editing/reviewing-subtitles-in-browser/`
- Move: `video-cut-skills/running-talking-head-postprocess/` -> `skills/video-editing/running-talking-head-postprocess/`
- Move: `video-cut-skills/transcribing-talking-head-subtitles/` -> `skills/video-editing/transcribing-talking-head-subtitles/`
- Move: `video-cut-skills/tests/` -> `skills/video-editing/tests/`
- Move: `口播脚本1.5分钟版本/` -> `templates/script-frameworks/`
- Move: `口播脚本1.5分钟版本辅助/` -> `templates/cover-opening-frameworks/`
- Move: `抖音口播脚本生成规则.md` -> `docs/rules/抖音口播脚本生成规则.md`
- Move: `规则迭代结论.md` -> `docs/methodology/规则迭代结论.md`
- Move: `30天规划.md` -> `docs/planning/30天规划.md`
- Move: `30天规划-10子代理版.md` -> `docs/planning/30天规划-10子代理版.md`
- Move: `6条短稿拍摄顺序与14天执行规划.md` -> `docs/planning/6条短稿拍摄顺序与14天执行规划.md`

### Private files and directories

- Create: `private/data/`
- Create: `private/reviews/`
- Create: `private/drafts/`
- Create: `private/generated/`
- Move: `_work_data_summary.md` -> `private/data/_work_data_summary.md`
- Move: `提取作品数据2026年03月28日11时24分29秒.xlsx` -> `private/data/提取作品数据2026年03月28日11时24分29秒.xlsx`
- Move: `竞品调研.xlsx` -> `private/data/竞品调研.xlsx`
- Move: `自媒体+ai有关选题.xlsx` -> `private/data/自媒体+ai有关选题.xlsx`
- Move: `花花提取作品数据2026年03月28日11时21分15秒.xlsx` -> `private/data/花花提取作品数据2026年03月28日11时21分15秒.xlsx`
- Move: `多代理脚本评审-第1轮.md` -> `private/reviews/多代理脚本评审-第1轮.md`
- Move: `多代理脚本评审-第2轮.md` -> `private/reviews/多代理脚本评审-第2轮.md`
- Move: `多代理脚本评审-第3轮.md` -> `private/reviews/多代理脚本评审-第3轮.md`
- Move: `大纲` -> `private/drafts/大纲`
- Move: `关注转化版-3类内容/` -> `private/drafts/attention-conversion-content/`
- Move: `口播脚本1.5分钟版本填充内容/` -> `private/drafts/filled-script-examples/`
- Move: `script/web_runs/` -> `private/generated/web_runs/` if no code path depends on the original location
- Move: `script/smoke/out/` -> `private/generated/smoke-out/` if no tests require the generated outputs

### Files requiring content edits after moves

- Modify: `scripts/video-editing/README.md`
- Modify: `skills/video-editing/README.md`
- Modify: `skills/video-editing/dictionary-correcting-subtitles/SKILL.md`
- Modify: `skills/video-editing/rendering-talking-head-video/SKILL.md`
- Modify: `skills/video-editing/reviewing-subtitles-in-browser/SKILL.md`
- Modify: `skills/video-editing/running-talking-head-postprocess/SKILL.md`
- Modify: `skills/video-editing/transcribing-talking-head-subtitles/SKILL.md`

### Test and verification files

- Test: `scripts/video-editing/tests/test_cli.py`
- Test: `scripts/video-editing/tests/test_local_web_app.py`
- Test: `scripts/video-editing/tests/test_web_workflow.py`
- Test: `skills/video-editing/tests/test_apply_dictionary.py`
- Test: `skills/video-editing/tests/test_subtitle_review_server.py`

### Task 1: Add Safety Rails And Root Repository Docs

**Files:**
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Capture the current unsafe repository state**

Run: `git -C 'C:\custom\project1\ideas\self-media' status --short`
Expected: many root files and directories appear as untracked, including private materials.

- [ ] **Step 2: Write the root `.gitignore`**

Add entries for:

```gitignore
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
private/
Thumbs.db
.DS_Store
scripts/video-editing/web_runs/
scripts/video-editing/smoke/out/
*.final.mp4
*.auto.srt
*.edit.srt
*.ass
```

- [ ] **Step 3: Verify the ignore rules work before moving files**

Run: `git -C 'C:\custom\project1\ideas\self-media' status --short --ignored`
Expected: ignored entries are shown with `!!`, proving private and generated content will stay out of the public commit surface.

- [ ] **Step 4: Write the root `README.md`**

Include:

```markdown
# self-media

Open-source scripts, templates, and methodology for a talking-head self-media workflow.

## Structure
- `scripts/`: runnable tooling
- `skills/`: reusable Codex skills
- `templates/`: reusable script frameworks
- `docs/`: public methodology and planning notes
- `private/`: local-only working materials, ignored by git
```

- [ ] **Step 5: Re-read the README commands for path accuracy**

Check that every command uses `scripts/video-editing/` rather than the old `script/` path.

- [ ] **Step 6: Commit the safety-rail changes**

```bash
git -C 'C:\custom\project1\ideas\self-media' add .gitignore README.md
git -C 'C:\custom\project1\ideas\self-media' commit -m "chore: add repo docs and ignore rules"
```

### Task 2: Isolate Private Working Materials

**Files:**
- Create: `private/data/`
- Create: `private/reviews/`
- Create: `private/drafts/`
- Create: `private/generated/`
- Modify: root-level placement of current private files

- [ ] **Step 1: Create the private directory skeleton**

Run:

```powershell
New-Item -ItemType Directory -Force -Path `
  'C:\custom\project1\ideas\self-media\private\data', `
  'C:\custom\project1\ideas\self-media\private\reviews', `
  'C:\custom\project1\ideas\self-media\private\drafts', `
  'C:\custom\project1\ideas\self-media\private\generated'
```

- [ ] **Step 2: Move private data and review files**

Move these files:

```text
_work_data_summary.md
提取作品数据2026年03月28日11时24分29秒.xlsx
竞品调研.xlsx
自媒体+ai有关选题.xlsx
花花提取作品数据2026年03月28日11时21分15秒.xlsx
多代理脚本评审-第1轮.md
多代理脚本评审-第2轮.md
多代理脚本评审-第3轮.md
大纲
```

- [ ] **Step 3: Move private draft directories**

Move:

```text
关注转化版-3类内容/ -> private/drafts/attention-conversion-content/
口播脚本1.5分钟版本填充内容/ -> private/drafts/filled-script-examples/
```

- [ ] **Step 4: Move generated runtime outputs if tests do not depend on them**

Check whether `script/web_runs/` and `script/smoke/out/` are referenced by tests. If not, move them into `private/generated/`; if they are referenced, leave them in place and rely on `.gitignore`.

- [ ] **Step 5: Verify private files no longer clutter the root**

Run: `Get-ChildItem -Force -Path 'C:\custom\project1\ideas\self-media'`
Expected: root keeps only public-oriented directories plus `private/`.

- [ ] **Step 6: Verify private content is ignored**

Run: `git -C 'C:\custom\project1\ideas\self-media' status --short --ignored`
Expected: `private/` contents show as ignored, not staged.

- [ ] **Step 7: Commit the private-content isolation**

```bash
git -C 'C:\custom\project1\ideas\self-media' add private
git -C 'C:\custom\project1\ideas\self-media' commit -m "chore: isolate private working materials"
```

### Task 3: Move The Public Python Tooling

**Files:**
- Create: `scripts/`
- Create: `scripts/video-editing/`
- Move: `script/*` public code and tests into `scripts/video-editing/`
- Modify: `scripts/video-editing/README.md`

- [ ] **Step 1: Create the destination directories**

Run:

```powershell
New-Item -ItemType Directory -Force -Path `
  'C:\custom\project1\ideas\self-media\scripts\video-editing'
```

- [ ] **Step 2: Move the reusable Python files and tests**

Move:

```text
script/README.md
script/requirements.txt
script/video_postprocess.py
script/web_app.py
script/video_postprocess/
script/tests/
script/smoke/   (keep only if its input fixtures are useful for testing)
```

- [ ] **Step 3: Remove Python cache directories from the moved tree if they still exist**

Delete only these caches if present:

```text
scripts/video-editing/.pytest_cache/
scripts/video-editing/tests/__pycache__/
scripts/video-editing/video_postprocess/__pycache__/
```

- [ ] **Step 4: Update the moved script README**

Replace old structure examples and commands so they point at:

```text
scripts/video-editing/
python video_postprocess.py transcribe ...
python video_postprocess.py render ...
```

- [ ] **Step 5: Verify the CLI still starts from the new location**

Run: `Set-Location 'C:\custom\project1\ideas\self-media\scripts\video-editing'; python .\video_postprocess.py --help`
Expected: CLI usage output prints without import errors.

- [ ] **Step 6: Run focused regression tests for the moved script package**

Run:

```bash
pytest 'C:\custom\project1\ideas\self-media\scripts\video-editing\tests\test_cli.py' -q
pytest 'C:\custom\project1\ideas\self-media\scripts\video-editing\tests\test_local_web_app.py' -q
pytest 'C:\custom\project1\ideas\self-media\scripts\video-editing\tests\test_web_workflow.py' -q
```

Expected: tests pass, or any failure is clearly about missing external tools rather than broken imports from the directory move.

- [ ] **Step 7: Commit the public Python tooling move**

```bash
git -C 'C:\custom\project1\ideas\self-media' add scripts
git -C 'C:\custom\project1\ideas\self-media' commit -m "refactor: move video editing tooling into scripts"
```

### Task 4: Move The Public Skills Package And Fix References

**Files:**
- Create: `skills/`
- Create: `skills/video-editing/`
- Move: `video-cut-skills/*` public files into `skills/video-editing/`
- Modify: `skills/video-editing/README.md`
- Modify: `skills/video-editing/dictionary-correcting-subtitles/SKILL.md`
- Modify: `skills/video-editing/rendering-talking-head-video/SKILL.md`
- Modify: `skills/video-editing/reviewing-subtitles-in-browser/SKILL.md`
- Modify: `skills/video-editing/running-talking-head-postprocess/SKILL.md`
- Modify: `skills/video-editing/transcribing-talking-head-subtitles/SKILL.md`

- [ ] **Step 1: Create the destination skills directory**

Run:

```powershell
New-Item -ItemType Directory -Force -Path `
  'C:\custom\project1\ideas\self-media\skills\video-editing'
```

- [ ] **Step 2: Move the reusable skills and helper tests**

Move:

```text
video-cut-skills/README.md
video-cut-skills/dictionary-correcting-subtitles/
video-cut-skills/rendering-talking-head-video/
video-cut-skills/reviewing-subtitles-in-browser/
video-cut-skills/running-talking-head-postprocess/
video-cut-skills/transcribing-talking-head-subtitles/
video-cut-skills/tests/
```

- [ ] **Step 3: Remove cache directories from the moved skills tree**

Delete only these caches if present:

```text
skills/video-editing/.pytest_cache/
skills/video-editing/dictionary-correcting-subtitles/__pycache__/
skills/video-editing/reviewing-subtitles-in-browser/__pycache__/
skills/video-editing/tests/__pycache__/
```

- [ ] **Step 4: Rewrite old absolute paths in the skills documentation**

Replace:

```text
C:\custom\project1\ideas\self-media\script
```

with:

```text
C:\custom\project1\ideas\self-media\scripts\video-editing
```

And replace:

```text
C:\custom\project1\ideas\self-media\video-cut-skills
```

with:

```text
C:\custom\project1\ideas\self-media\skills\video-editing
```

- [ ] **Step 5: Verify no old skill paths remain**

Run:

```bash
rg -n "self-media\\\\script|self-media\\\\video-cut-skills" 'C:\custom\project1\ideas\self-media\skills\video-editing'
```

Expected: no matches.

- [ ] **Step 6: Run focused tests for the moved helper scripts**

Run:

```bash
pytest 'C:\custom\project1\ideas\self-media\skills\video-editing\tests\test_apply_dictionary.py' -q
pytest 'C:\custom\project1\ideas\self-media\skills\video-editing\tests\test_subtitle_review_server.py' -q
```

Expected: tests pass after the move and doc path rewrites.

- [ ] **Step 7: Commit the skills package move**

```bash
git -C 'C:\custom\project1\ideas\self-media' add skills
git -C 'C:\custom\project1\ideas\self-media' commit -m "refactor: move reusable video editing skills"
```

### Task 5: Move Public Templates And Public Methodology Docs

**Files:**
- Create: `templates/script-frameworks/`
- Create: `templates/cover-opening-frameworks/`
- Create: `docs/methodology/`
- Create: `docs/planning/`
- Create: `docs/rules/`
- Move: public template directories and public docs into those locations

- [ ] **Step 1: Create the destination directories**

Run:

```powershell
New-Item -ItemType Directory -Force -Path `
  'C:\custom\project1\ideas\self-media\templates\script-frameworks', `
  'C:\custom\project1\ideas\self-media\templates\cover-opening-frameworks', `
  'C:\custom\project1\ideas\self-media\docs\methodology', `
  'C:\custom\project1\ideas\self-media\docs\planning', `
  'C:\custom\project1\ideas\self-media\docs\rules'
```

- [ ] **Step 2: Move the reusable template directories**

Move:

```text
口播脚本1.5分钟版本/ -> templates/script-frameworks/
口播脚本1.5分钟版本辅助/ -> templates/cover-opening-frameworks/
```

- [ ] **Step 3: Move the reusable public methodology documents**

Move:

```text
抖音口播脚本生成规则.md -> docs/rules/
规则迭代结论.md -> docs/methodology/
30天规划.md -> docs/planning/
30天规划-10子代理版.md -> docs/planning/
6条短稿拍摄顺序与14天执行规划.md -> docs/planning/
```

- [ ] **Step 4: Verify the root is now public-facing**

Run: `Get-ChildItem -Force -Path 'C:\custom\project1\ideas\self-media'`
Expected: root mostly contains `.git`, `.gitignore`, `README.md`, `docs`, `private`, `scripts`, `skills`, and `templates`.

- [ ] **Step 5: Commit the public content reorganization**

```bash
git -C 'C:\custom\project1\ideas\self-media' add templates docs
git -C 'C:\custom\project1\ideas\self-media' commit -m "refactor: reorganize public templates and docs"
```

### Task 6: Final Verification And GitHub-Ready Snapshot

**Files:**
- Modify: whole repository staging state only

- [ ] **Step 1: Run the full script test suite from the new location**

Run:

```bash
Set-Location 'C:\custom\project1\ideas\self-media\scripts\video-editing'
pytest -q
```

Expected: the existing script suite passes, or any failures are documented as environment-specific.

- [ ] **Step 2: Run the full skills helper test suite from the new location**

Run:

```bash
Set-Location 'C:\custom\project1\ideas\self-media\skills\video-editing'
pytest tests -q
```

Expected: helper tests pass.

- [ ] **Step 3: Verify the repository no longer contains old public paths**

Run:

```bash
rg -n --hidden --glob '!private/**' --glob '!.git/**' "self-media\\\\script|self-media\\\\video-cut-skills|^script/|^video-cut-skills/" 'C:\custom\project1\ideas\self-media'
```

Expected: no live references outside the historical spec and plan documents.

- [ ] **Step 4: Verify git tracking is safe for the first public push**

Run:

```bash
git -C 'C:\custom\project1\ideas\self-media' status --short --ignored
```

Expected:
- public files are staged or trackable
- `private/` stays ignored
- cache directories stay ignored

- [ ] **Step 5: Create the cleaned repository snapshot commit**

```bash
git -C 'C:\custom\project1\ideas\self-media' add .
git -C 'C:\custom\project1\ideas\self-media' status --short
git -C 'C:\custom\project1\ideas\self-media' commit -m "feat: prepare self-media for open-source release"
```

- [ ] **Step 6: Record the push instructions in the root README if missing**

Ensure the README includes a short "Publish to GitHub" section with:

```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```
