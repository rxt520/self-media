# Video Cut Skills For Codex

这个目录是面向 Codex 的本地 skill 包，不复用 `C:\custom\project1\ideas\videocut-skills` 的原始组织方式。

这里的 skill 统一调用：

- [video_postprocess.py](C:/custom/project1/ideas/self-media/scripts/video-editing/video_postprocess.py)

核心脚本目录：

- `~/self-media/skills/video-editing/`

## 当前 Skill

- `transcribing-talking-head-subtitles`
  - 从视频生成可编辑 `.auto.srt`
- `rendering-talking-head-video`
  - 读取修正后的 `.srt` 输出 `.final.mp4`
- `running-talking-head-postprocess`
  - 组织完整工作流
- `dictionary-correcting-subtitles`
  - 用术语词典批量修正字幕
- `reviewing-subtitles-in-browser`
  - 起本地网页，边看视频边改字幕文字

## 推荐使用方式

1. 先用 `transcribing-talking-head-subtitles`
2. 修正 `.srt`
3. 再用 `rendering-talking-head-video`

如果用户只说“把这条口播视频处理完”，优先使用 `running-talking-head-postprocess`。

## 常用组合

### 组合 1：标准流程

1. `transcribing-talking-head-subtitles`
2. `dictionary-correcting-subtitles`
3. `reviewing-subtitles-in-browser`
4. `rendering-talking-head-video`

### 组合 2：快速流程

1. `transcribing-talking-head-subtitles`
2. 直接手改 `.srt`
3. `rendering-talking-head-video`

## 辅助脚本

- [apply_dictionary.py](C:/custom/project1/ideas/self-media/skills/video-editing/dictionary-correcting-subtitles/apply_dictionary.py)
- [subtitle_review_server.py](C:/custom/project1/ideas/self-media/skills/video-editing/reviewing-subtitles-in-browser/subtitle_review_server.py)

## 后续增强方向

后续可以继续往这里补：

- 去停顿 skill
- 精确剪口播 skill
- 批量处理 skill
