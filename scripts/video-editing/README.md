# 鍙ｆ挱瑙嗛鍚庡鐞嗚剼鏈?
杩欎釜鐩綍鎻愪緵涓€涓法骞冲彴鐨?Python CLI锛岀敤浜庡鐞嗗彛鎾棰戯細

- 鑷姩杞啓鐢熸垚鍙紪杈戝瓧骞?- 璇诲彇淇鍚庣殑 `.srt`
- 鐢熸垚甯︽牱寮忕殑 `.ass`
- 鐢?`ffmpeg` 鎸?`1.25x` 鍊嶉€熺儳褰曞瓧骞曡緭鍑烘渶缁堟垚鐗?
## 鐩綍缁撴瀯

```text
scripts/video-editing/
鈹溾攢鈹€ video_postprocess.py
鈹溾攢鈹€ requirements.txt
鈹溾攢鈹€ README.md
鈹溾攢鈹€ video_postprocess/
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹溾攢鈹€ ass_writer.py
鈹?  鈹溾攢鈹€ ffmpeg_ops.py
鈹?  鈹溾攢鈹€ paths.py
鈹?  鈹溾攢鈹€ srt_utils.py
鈹?  鈹斺攢鈹€ transcribe.py
鈹斺攢鈹€ tests/
```

## 渚濊禆

绯荤粺渚濊禆锛?
- Python 3.10+
- ffmpeg

Python 渚濊禆锛?
```bash
pip install -r requirements.txt
```

## 浣跨敤鏂瑰紡

### 1. 鑷姩鐢熸垚瀛楀箷鑽夌

```bash
python video_postprocess.py transcribe input.mp4 --out-dir output
```

榛樿浼氱敓鎴愶細

- `output/input.auto.srt`

鍙€夊弬鏁帮細

```bash
python video_postprocess.py transcribe input.mp4 \
  --out-dir output \
  --language zh \
  --model-size small \
  --device auto
```

璇存槑锛?
- `language` 榛樿 `zh`
- `model-size` 榛樿 `small`
- `device` 榛樿 `auto`锛屽綋鍓嶄細鍥炶惤鍒?CPU

### 2. 淇瀛楀箷

灏嗚嚜鍔ㄧ敓鎴愮殑瀛楀箷浜哄伐淇鍚庝繚瀛樻垚锛?
- `output/input.edit.srt`

浣犱篃鍙互鐢ㄤ换鎰忚矾寰勶紝鍙鍦ㄦ覆鏌撴椂閫氳繃 `--srt` 鎸囧畾鍗冲彲銆?
### 3. 娓叉煋鏈€缁堣棰?
```bash
python video_postprocess.py render input.mp4 --srt output/input.edit.srt --out-dir output
```

榛樿浼氱敓鎴愶細

- `output/input.ass`
- `output/input.final.mp4`

鍙€夐珮浜瘝锛?
```bash
python video_postprocess.py render input.mp4 \
  --srt output/input.edit.srt \
  --out-dir output \
  --highlight "娴佺▼,鍓緫,娴嬭瘯"
```

## 榛樿瀛楀箷鏍峰紡

- 瀛椾綋锛歚寰蒋闆呴粦`
- 涓诲瓧骞曪細鐧借壊
- 楂樹寒璇嶏細榛勮壊
- 浣嶇疆锛氬簳閮ㄥ眳涓?- 鑳屾櫙锛欰SS 鏍峰紡搴曡壊
- 鍊嶉€燂細`1.25x`

## 杈撳嚭鏂囦欢

杈撳叆瑙嗛 `clip.mp4` 鏃讹紝杈撳嚭鐩綍榛樿浣跨敤杩欎簺鏂囦欢鍚嶏細

- `clip.auto.srt`
- `clip.edit.srt`
- `clip.ass`
- `clip.final.mp4`
- `tmp/`

## 娴嬭瘯

杩愯鍏ㄩ儴娴嬭瘯锛?
```bash
pytest -q
```

## 璇存槑

- `transcribe` 渚濊禆 `faster-whisper`
- `render` 渚濊禆 `ffmpeg`
- 濡傛灉 `faster-whisper` 鏈畨瑁咃紝杞啓闃舵浼氱洿鎺ユ姤閿?- 濡傛灉 `ffmpeg` 涓嶅湪 PATH 涓紝杞啓鍜屾覆鏌撻兘浼氬け璐?
