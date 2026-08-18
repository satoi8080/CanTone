# CanTone

[繁體中文](README.md) · [简体中文](README-zh-Hans.md) · [English](README-en.md) · **日本語**

**広東語（粤拼）の声調数字 1〜9 を音高の輪郭に変える読書補助フォント。**

CanTone は粤拼（Jyutping）の声調番号 **1〜9** を、「数字＋趙氏五度式の声調輪郭」として
描画します。数字が何の声調かを暗記しなくても、各音節の音高の動きをひと目で「見る」ことが
できます。

![CanTone 声調一覧](assets/CanTone_Chart.png)

## 概要

粤拼を読むとき、`nei5 hou2` の数字こそが声調記号ですが、初学者は「5 は低昇、2 は中昇」と
なかなか覚えられません。CanTone は数字をそのまま残し、その上に趙元任の五度式音高輪郭を
描くことで、抽象的な番号を目に見える音高に変えます。等幅フォント（Noto Sans Mono ベース）で、
印字可能な ASCII をすべてそのまま通すため、粤拼の一行をすべて同じフォントで表示できます。

![粤拼サンプル](assets/CanTone_Sample.png)

## 声調の描き方

CanTone は各声調を趙氏五度式の音高輪郭で表します：

| 声調の型 | 数字 | 描き方 |
| --- | --- | --- |
| **平らな声調** | 1・3・6・7・8・9 | 1 本の水平線（音高が一定） |
| **曲折声調** | 2・4・5 | つなげた 1 本の斜線（音高の上昇・下降） |

基準の縦棒は常に右側にあり、中国語の五度式表記の慣例に従っています。

## 2 つの標準：香港と広州

CanTone は 2 つのフォントを用意しており、違いは**陰平（第 1 声）だけ**です：

| フォント | 陰平（1） | その他の声調 |
| --- | --- | --- |
| **CanTone Sans HK**（香港） | 高平 `55`（水平線） | 同一 |
| **CanTone Sans GZ**（広州） | 高降 `53`（下降する斜線） | 同一 |

これは港穗（香港・広州）粤語で文献的裏づけのある唯一の調値差です。広州（および年配層）は
高降 53 を保ち、現代香港ではほぼ高平 55 に統合されました。残る六声は両者で同一です。

## 声調値

5 が最高音。7／8／9 は入声（促音）で、音高はそれぞれ 1／3／6 と同じです。

| 数字 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 調類 | 陰平 | 陰上 | 陰去 | 陽平 | 陽上 | 陽去 | 陰入 | 中入 | 陽入 |
| 香港 HK | 55 | 35 | 33 | 21 | 13 | 22 | 5 | 3 | 2 |
| 広州 GZ | 53 | 35 | 33 | 21 | 13 | 22 | 5 | 3 | 2 |

## ダウンロード

[Releases](https://github.com/satoi8080/CanTone/releases) から最新の `CanToneSans-*.zip` を取得してください。
展開すると `CanToneSansHK-Regular.ttf`、`CanToneSansGZ-Regular.ttf` と
フォントのライセンス `OFL.txt` が入っています。

## 使い方

- **エディタ／ターミナル**：フォントを `CanTone Sans HK` または `CanTone Sans GZ` に設定。
- **Web**：`font-family: 'CanTone Sans HK', monospace;`

インストールは macOS／Windows なら `.ttf` をダブルクリック、Linux なら `~/.fonts/` にコピー。

## ライセンス

本リポジトリは二部構成のライセンスです：

- **フォント**（CanTone Sans HK／GZ）：[SIL Open Font License 1.1](OFL.txt)。
  [Noto Sans Mono](https://fonts.google.com/noto/specimen/Noto+Sans+Mono)（同じく OFL 1.1）
  からビルドしており、OFL の条件により派生フォントも OFL で配布する必要があります。
- **ソースコードとビルドツール**：[MIT](LICENSE)。

同じ作者による姉妹プロジェクト [KanaKira](https://github.com/satoi8080/KanaKira) と
同じ発想です。

---

> ここから先は開発者向けです。一般の利用者はここまでで十分です。

## ソースからのビルド

Python 3.12+ と [uv](https://docs.astral.sh/uv/) が必要です。

```bash
uv sync
uv run main.py          # CanToneSansHK / CanToneSansGZ の 2 つの .ttf を生成
uv run python scripts/gen_preview.py   # プレビュー SVG を再生成（inkscape 等で PNG 化）
uv run python scripts/package.py       # CanToneSans-v<バージョン>.zip を作成（OFL.txt 同梱）
```

グリフの形状（数字の縮尺、声調枠のサイズ、線の太さ、縦棒の位置）は `config.json` で調整でき、
2 つの調値表（`TONES_HK` と `TONES_GZ`）は `main.py` にあります。
