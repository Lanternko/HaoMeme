# 豪老師梗圖產生器

![網站畫面](screenshot.png)

https://lanternko.github.io/HaoMeme/

點開就能用，不用安裝。這是一個網頁小工具，可以自己打字、換表情，做出仿 YouTube 頻道「拆書人」封面風格的梗圖。

## 怎麼用

1. **選版型**：在「版型」點「教育我了？」、「翻車了？」、「免談」或「律師傳票」，切換不同的字體風格與預設背景。
2. **打字**：在「大字」框輸入台詞，按 Enter 換行，每行字會自動放大到剛好排得下。
3. **上色**：反白選取文字（沒選字就改游標那一行），點「白」、「黃」或「紅」換色，也可勾選「紅色筆刷」；人像很大、把筆刷擋住時，勾「筆刷在人像前」就會把筆刷畫在人像上面（仍在字的下面）。在手機上打字時，鍵盤正上方也會出現一排白黃紅，選好字直接點就好。
4. **換人像**：點選內建表情、按「隨機換一張」，或按「上傳自己的」換照片（上傳的照片會放在最後一格，換成別張後也能點回來）；背景可以在「背景」點選紅光、灰牆、藍霧燈條、暗色，或按「上傳背景圖」換自己的；上傳的圖會放在第五格，點其他背景後也能點回來。
5. **調位置**：切換人像在「左」或「右」、勾選「翻轉」，或拉動「筆刷大小」、「字體大小」、「旋轉」、「大小」滑桿，或勾選「斜體」讓字往右斜（「翻車了？」預設會勾）；想重來就按「重設位置大小」。
6. **下載或複製**：按右上角的「下載 PNG」存成圖片檔（iPhone／iPad 上這顆按鈕會變成「存到照片」，按了選「儲存影像」就會存進照片），或按「複製圖片」直接貼給朋友。在手機上按這兩顆按鈕，還會跳出整張圖：存不下來或貼不上時，長按圖片選「下載圖片」或「複製圖片」就好（在 LINE、Discord 這類 App 裡開的網頁常常存不了，可以改用瀏覽器開啟）。

## 小技巧

- **直接拖曳**：在預覽圖點選文字、紅色筆刷、人像，或點空白處選取背景，就能直接用滑鼠拖曳移動（點在字上是選文字，點在字旁邊露出的筆刷是選筆刷）。
- **縮放與旋轉**：拉動選取框角落的圓點、滾動滑鼠滾輪或在手機上用兩指捏合可以縮放；拉動文字框上方的圓點可以旋轉。
- **鍵盤微調**：點選物件後按方向鍵可微調位置（按住 Shift 移動更快），按 Esc 取消選取。
- **雙擊改字**：在預覽圖的文字上連點兩下，就會直接跳到文字框並全選改字。
- **背景顯示調整**：上傳背景後可點「填滿畫面」或「完整顯示」（直的圖預設完整顯示），並可勾選「背景沒蓋滿時，從圖片邊緣往外延伸補滿」；拉「背景虛化」可以讓背景像拍照失焦一樣變模糊，人像和字會更突出。

## 注意

輸出圖片為 1280×720。內建人像來自「拆書人」頻道原始封面，是真人肖像，只能私下玩梗，不要拿去冒充本人發文。

## 授權

- **程式碼**：MIT 授權（見 [`LICENSE`](LICENSE)；範圍見 [`NOTICE.md`](NOTICE.md)），可以自由使用、修改、轉發，保留版權聲明即可。
- **圖片不在 MIT 範圍內**：`portraits/`、`portraits_orig/`、`src_photos/`、`src_thumbs/` 裡的人像與截圖、`portraits.js` 和 `backgrounds.js` 內嵌的圖片資料，以及用它們做的截圖與圖示（`screenshot.png`、`og.jpg`、`sample-*.png`、`compare-*.png`、`zoom-*.png`、`favicon*`、`apple-touch-icon.png`），版權與肖像權屬原作者（YouTube 頻道「拆書人」）。放在這裡只是為了讓工具能用，fork 或轉用時請自行換掉或取得授權。
- **字型**：`fonts/`（包括切好的 `fonts/woff2/`）依各自作者的 SIL OFL 1.1 授權（見 `fonts/OFL.txt`）。

## 給想改程式的人

- **本機執行**：不需架設伺服器，直接用瀏覽器打開 `index.html` 就能跑（人像已打包在 `portraits.js` 中）。
- **重新產生人像**：若要重新去背、計算對齊座標並打包 `portraits.js`，請安裝對應的 Python 套件後依序執行：
  ```bash
  pip install "rembg[cpu]" pillow numpy opencv-python
  python tools/cutout.py           # 去背裁切人像，輸出 portraits/<key>.png（需 rembg[cpu]、pillow、numpy；可加參數如 A F 只跑指定圖）
  python tools/find_anchors.py     # 比對 portraits_orig/ 與 portraits/，寫入 portraits/anchors.json（需 pillow、numpy、opencv-python）
  python tools/build_portraits.py  # 將 portraits/*.png 與 anchors.json 轉為 base64 WebP 打包進 portraits.js（需 pillow）
  python tools/build_backgrounds.py  # 從 src_photos/ 產生照片背景與紅色筆刷，打包成 backgrounds.js（需 pillow、numpy）
  ```
  `cutout.py` 的原圖預設讀影片封面，`src_photos/` 放的是另外提供的照片（人像 J、K、L、藍霧燈條背景，以及「翻車了？」和「免談」的紅色筆刷都從這裡來）。「律師傳票」的人像 N、紅色筆刷、黑色塗抹和三條黃線，是照原封面請 Gemini 重畫成高解析度後放進 `src_photos/sue_*` 的（人像是綠幕版，去背後存成 `portraits/N.png`）。
- **字體來源與授權**：字體檔位於 `fonts/`，皆採用 SIL OFL（`fonts/OFL.txt`）授權：
  - 梗圖大字：**Glow Sans TC / SC Extended Heavy**（`GlowSansTC-Extended-Heavy.otf`，以及補齊繁體版缺字「告值真教清填慎鎮顛巔」10 字的 `GlowSansSC-Extended-Heavy-10.otf`），來源：https://github.com/welai/glow-sans
  - 「律師傳票」大字：同一家族的窄版 **Glow Sans TC / SC Condensed Heavy**（`GlowSansTC-Condensed-Heavy.otf`、補缺字的 `GlowSansSC-Condensed-Heavy-10.otf`），只在選到這個版型時才下載
  - 標題標準字：**Outfit**（`outfit-500.ttf`、`outfit-700.ttf`）
  - 網頁實際載入的是 `fonts/woff2/` 裡切好的小塊（每塊約 750 字，打到哪些字才下載哪幾塊），以及對應的 `fonts/fonts.css`。改過上面的原始字體後，用 `pip install fonttools brotli` 再執行 `python tools/split_fonts.py` 重新切。
