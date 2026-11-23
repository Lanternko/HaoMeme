# 豪老師梗圖產生器

仿「拆書人」頻道封面的梗圖產生器：人像 + 大字（白／黃／紅）+ 紅色筆刷。

## 用法

直接用瀏覽器打開 `index.html`（不用裝東西、不用伺服器）。

- 版型：「教育我了？」（紅黑漸層、字下紅筆刷）、「翻車了？」（斜字、字後紅筆刷）
- 大字最多三行，每行可選白／黃／紅，會自動縮放填滿
- 人像 8 張可換、可隨機、可上傳自己的（建議已去背的 PNG）
- 可上傳背景圖；輸出 1280×720 PNG，或直接複製到剪貼簿

字體用系統的 Noto Sans TC（Windows 11 內建），沒有時退回微軟正黑體。

## 重新產生人像

人像取自頻道原始封面（`src_thumbs/`），去背後存在 `portraits/`，再打包進 `portraits.js`。

```
pip install "rembg[cpu]" pillow
python tools/cutout.py            # 去背，可加 key 只跑幾張：python tools/cutout.py A F
python tools/build_portraits.py   # 打包成 portraits.js
```

目前 `portraits/` 是用 Gemini 把兩邊肩膀補齊的版本（原本的去背備份在 `portraits_orig/`），翻轉換邊時才不會缺一角。`portraits/anchors.json` 記錄原本的去背在新圖裡的位置；頁面依這個框定位，所以預設畫面和原本一樣，多補的那側肩膀會超出畫面邊緣。換過人像後要重跑：

```
python tools/find_anchors.py      # 需要 opencv-python、numpy
python tools/build_portraits.py
```

## 注意

人像是真人肖像，僅供私下玩梗，不要做成看起來像本人發的公開貼文。

## 字體

標題字用 `fonts/GlowSansTC-Extended-Heavy.otf`（未來熒黑 Glow Sans TC Extended Heavy，SIL OFL 授權，來源 https://github.com/welai/glow-sans 的 v0.93 release）。這個檔案不見時會退回系統的 Noto Sans TC／微軟正黑體。
