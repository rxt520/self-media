# 口播视频后处理脚本

这个目录提供一个跨平台 Python CLI，用于处理口播视频：

- 自动转写生成可编辑字幕
- 读取修正后的 `.srt`
- 生成带样式的 `.ass`
- 用 `ffmpeg` 按 `1.25x` 倍速烧录字幕并输出最终成片

## 目录结构

```text
scripts/video-editing/
├── video_postprocess.py
├── requirements.txt
├── README.md
├── video_postprocess/
│   ├── __init__.py
│   ├── ass_writer.py
│   ├── ffmpeg_ops.py
│   ├── paths.py
│   ├── srt_utils.py
│   └── transcribe.py
└── tests/
```

## 依赖

系统依赖：

- Python 3.10+
- ffmpeg

Python 依赖：

```bash
pip install -r requirements.txt
```

## 使用方式

### 1. 自动生成字幕草稿

```bash
python video_postprocess.py transcribe input.mp4 --out-dir output
```

默认会生成：

- `output/input.auto.srt`

可选参数：

```bash
python video_postprocess.py transcribe input.mp4 \
  --out-dir output \
  --language zh \
  --model-size small \
  --device auto
```

说明：

- `language` 默认 `zh`
- `model-size` 默认 `small`
- `device` 默认 `auto`，当前会回落到 CPU

### 2. 修正字幕

将自动生成的字幕人工修正后保存成：

- `output/input.edit.srt`

你也可以用任意路径，只要在渲染时通过 `--srt` 指定即可。

### 3. 渲染最终视频

```bash
python video_postprocess.py render input.mp4 --srt output/input.edit.srt --out-dir output
```

默认会生成：

- `output/input.ass`
- `output/input.final.mp4`

可选高亮词：

```bash
python video_postprocess.py render input.mp4 \
  --srt output/input.edit.srt \
  --out-dir output \
  --highlight "流程,剪辑,测试"
```

## 默认字幕样式

- 字体：`微软雅黑`
- 主字幕：白色
- 高亮词：黄色
- 位置：底部居中
- 背景：ASS 样式底色
- 倍速：`1.25x`

## 输出文件

输入视频 `clip.mp4` 时，输出目录默认使用这些文件名：

- `clip.auto.srt`
- `clip.edit.srt`
- `clip.ass`
- `clip.final.mp4`
- `tmp/`

## 测试

运行全部测试：

```bash
pytest -q
```

## 说明

- `transcribe` 依赖 `faster-whisper`
- `render` 依赖 `ffmpeg`
- 如果 `faster-whisper` 未安装，转写阶段会直接报错
- 如果 `ffmpeg` 不在 PATH 中，转写和渲染都会失败
