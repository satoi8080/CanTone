# CanTone

**繁體中文** · [简体中文](README-zh-Hans.md) · [English](README-en.md) · [日本語](README-ja.md)

**把粵拼聲調數字 1–9 變成音高輪廓的閱讀輔助字型。**

CanTone 會把粵拼（Jyutping）的聲調數字 **1–9** 渲染成「數字 + 趙氏五度聲調輪廓」，
讓你一眼看出每個音節的音高走向，而不必死記每個數字代表甚麼調。

![CanTone 聲調對照表](assets/CanTone_Chart.png)

## 簡介

讀粵拼時，`nei5 hou2` 裡的數字就是聲調標記，但初學者往往記不住「5 是低升、2 是中升」。
CanTone 保留原本的數字，只在它上方畫一條趙元任五度標記法的音高輪廓——把抽象的數字變成
看得見的音高。整套字型以等寬的 Noto Sans Mono 為基礎，並保留全部可列印 ASCII，因此整段粵拼都能用同一個字型顯示。

![粵拼範例](assets/CanTone_Sample.png)

## 聲調畫法

CanTone 用趙氏五度標記法的音高輪廓來標注每個聲調：

| 調型 | 數字 | 畫法 |
| --- | --- | --- |
| **平調** | 1、3、6、7、8、9 | 一條水平橫線（音高不變） |
| **曲折調** | 2、4、5 | 一條連起來的斜線（音高上升或下降） |

豎標一律位於右側，沿用中文五度標記法的慣例。

## 兩種標準：香港與廣州

CanTone 提供兩個字型，差別**只在陰平（第 1 聲）**：

| 字型 | 陰平（1） | 其餘各調 |
| --- | --- | --- |
| **CanTone Sans HK**（香港） | 高平 `55`（水平橫線） | 相同 |
| **CanTone Sans GZ**（廣州） | 高降 `53`（下降斜線） | 相同 |

這是港穗粵語唯一有充分文獻支持的調值差異：廣州（及老派）保留高降 53，當代香港多已併入
高平 55。其餘六調兩地一致，學界並無另立兩套調值。

## 聲調對照表

5 為最高音；7／8／9 為入聲（短促），音高分別與 1／3／6 相同。

| 數字 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 調類 | 陰平 | 陰上 | 陰去 | 陽平 | 陽上 | 陽去 | 陰入 | 中入 | 陽入 |
| 香港 HK | 55 | 35 | 33 | 21 | 13 | 22 | 5 | 3 | 2 |
| 廣州 GZ | 53 | 35 | 33 | 21 | 13 | 22 | 5 | 3 | 2 |

## 下載

到 [Releases](https://github.com/satoi8080/CanTone/releases) 下載最新的 `CanToneSans-*.zip`，解壓後即得
`CanToneSansHK-Regular.ttf`、`CanToneSansGZ-Regular.ttf` 與字型授權 `OFL.txt`。

## 使用方式

- **編輯器／終端機**：把字型設為 `CanTone Sans HK` 或 `CanTone Sans GZ`。
- **網頁**：`font-family: 'CanTone Sans HK', monospace;`

安裝：在 macOS／Windows 雙擊 `.ttf` 安裝，或在 Linux 複製到 `~/.fonts/`。

## 授權

本倉庫分兩部分授權：

- **字型**（CanTone Sans HK／GZ）：[SIL Open Font License 1.1](OFL.txt)。字型以
  [Noto Sans Mono](https://fonts.google.com/noto/specimen/Noto+Sans+Mono)（同為 OFL 1.1）製作，
  依 OFL 條款，衍生字型須同樣以 OFL 發佈。
- **原始碼與建置工具**：[MIT](LICENSE)。

與同作者的 [KanaKira](https://github.com/satoi8080/KanaKira) 為姊妹項目，理念一脈相承。

---

> 以下為開發者內容；一般使用者讀到這裡即可。

## 從原始碼編譯

需要 Python 3.12+ 與 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync
uv run main.py          # 產生 CanToneSansHK / CanToneSansGZ 兩個 .ttf
uv run python scripts/gen_preview.py   # 重新產生預覽 SVG（再用 inkscape 等轉成 PNG）
uv run python scripts/package.py       # 打包成 CanToneSans-v<版本>.zip（含 OFL.txt）
```

字形幾何（數字縮放、聲調框尺寸、筆畫粗細、豎標位置）可在 `config.json` 調整；
兩套調值（`TONES_HK` 與 `TONES_GZ`）在 `main.py`。
