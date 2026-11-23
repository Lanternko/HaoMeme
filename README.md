# 豪老師梗圖產生器

![網站畫面](screenshot.png)

https://lanternko.github.io/HaoMeme/

點開就能用，不用安裝。這是一個網頁小工具，可以自己打字、換表情，做出仿 YouTube 頻道「拆書人」封面風格的梗圖。

## 怎麼用

1. **選版型**：在「版型」點「教育我了？」或「翻車了？」，切換不同的背景與字體風格。
2. **打字**：在「大字」框輸入台詞，按 Enter 換行，每行字會自動放大到剛好排得下。
3. **上色**：反白選取文字（沒選字就改游標那一行），點「白」、「黃」或「紅」換色，也可勾選「紅色筆刷」。
4. **換人像**：點選內建表情、按「隨機換一張」，或按「上傳自己的」換照片；背景也能按「上傳背景圖」更換、按「用預設」還原。
5. **調位置**：切換人像在「左」或「右」、勾選「翻轉」，或拉動「字體大小」、「旋轉」、「大小」滑桿；想重來就按「重設位置大小」。
6. **下載或複製**：按右上角的「下載 PNG」存成圖片檔，或按「複製圖片」直接貼給朋友。

## 小技巧

- **直接拖曳**：在預覽圖點選文字、人像，或點空白處選取背景，就能直接用滑鼠拖曳移動。
- **縮放與旋轉**：拉動選取框角落的圓點或滾動滑鼠滾輪可以縮放；拉動文字框上方的圓點可以旋轉。
- **鍵盤微調**：點選物件後按方向鍵可微調位置（按住 Shift 移動更快），按 Esc 取消選取。
- **雙擊改字**：在預覽圖的文字上連點兩下，就會直接跳到文字框並全選改字。
- **背景顯示調整**：上傳背景後可點「填滿畫面」或「完整顯示」（直的圖預設完整顯示），並可勾選「背景沒蓋滿時，從圖片邊緣往外延伸補滿」。

## 注意

輸出圖片為 1280×720。內建人像來自「拆書人」頻道原始封面，是真人肖像，只能私下玩梗，不要拿去冒充本人發文。

## 給想改程式的人

- **本機執行**：不需架設伺服器，直接用瀏覽器打開 `index.html` 就能跑（人像已打包在 `portraits.js` 中）。
- **重新產生人像**：若要重新去背、計算對齊座標並打包 `portraits.js`，請安裝對應的 Python 套件後依序執行：
  ```bash
  pip install "rembg[cpu]" pillow numpy opencv-python
  python tools/cutout.py           # 去背裁切人像，輸出 portraits/<key>.png（需 rembg[cpu]、pillow、numpy；可加參數如 A F 只跑指定圖）
  python tools/find_anchors.py     # 比對 portraits_orig/ 與 portraits/，寫入 portraits/anchors.json（需 pillow、numpy、opencv-python）
  python tools/build_portraits.py  # 將 portraits/*.png 與 anchors.json 轉為 base64 WebP 打包進 portraits.js（需 pillow）
  ```
- **字體來源與授權**：字體檔位於 `fonts/`，皆採用 SIL OFL（`fonts/OFL.txt`）授權：
  - 梗圖大字：**Glow Sans TC / SC Extended Heavy**（`GlowSansTC-Extended-Heavy.otf`，以及補齊繁體版缺字「告值真教清填慎鎮顛巔」10 字的 `GlowSansSC-Extended-Heavy-10.otf`），來源：https://github.com/welai/glow-sans
  - 標題標準字：**Outfit**（`outfit-500.ttf`、`outfit-700.ttf`）
