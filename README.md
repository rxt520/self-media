# self-media

一个面向口播自媒体工作流的开源仓库，公开可复用的脚本、模板和方法论，不公开真实数据、评审记录和具体业务草稿。

## 目录结构

- `scripts/`: 可运行的工具脚本
- `skills/`: 可复用的本地技能和辅助脚本
- `templates/`: 可复用的口播模板和封面开场框架
- `docs/`: 方法论、规则和规划文档
- `private/`: 本地工作资料，默认由 git 忽略

## 从哪里开始

- 剪辑和字幕后处理：看 `scripts/video-editing/`，对应的本地 skill 在 `skills/video-editing/`
- 口播文案生成：看 `skills/script-writing/`，规则和方法论在 `docs/rules/` 与 `docs/methodology/`
- 口播模板和结构参考：看 `templates/`

## 快速开始

1. 安装 Python 3.10+ 和 `ffmpeg`
2. 进入 `scripts/video-editing/`
3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 生成字幕草稿

```bash
python video_postprocess.py transcribe input.mp4 --out-dir output
```

5. 使用修正后的字幕渲染最终视频

```bash
python video_postprocess.py render input.mp4 --srt output/input.edit.srt --out-dir output
```

## 使用方式

如果你只想使用脚本，直接看 `scripts/video-editing/README.md`。

如果你想复用本地 skill 工作流，查看 `skills/video-editing/README.md`。

## 开源边界

以下内容不应进入公开仓库：

- 真实业务数据和 Excel
- 评审记录
- 具体选题稿件和填充后的工作草稿
- 本地运行生成的字幕、中间文件和导出视频

## 发布到 GitHub

```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```
