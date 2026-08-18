# CanTone

[繁體中文](README.md) · [简体中文](README-zh-Hans.md) · **English** · [日本語](README-ja.md)

**A reading-aid font that turns Cantonese (Jyutping) tone digits 1–9 into pitch contours.**

CanTone renders the Jyutping tone numbers **1–9** as the digit *plus* a Chao
"five-degree" tone contour drawn above it, so you can *see* the pitch shape of each
syllable instead of memorising what each number means.

![CanTone tone chart](assets/CanTone_Chart.png)

## What it does

When reading Jyutping, the digits in `nei5 hou2` *are* the tone markers — but beginners
rarely remember that "5 is low-rising, 2 is mid-rising." CanTone keeps the digit and
draws Yuen Ren Chao's five-degree pitch contour above it, turning an abstract number
into a visible pitch. It's monospaced (built on Noto Sans Mono) and passes through all
printable ASCII, so a whole line of Jyutping renders in one font.

![Jyutping sample](assets/CanTone_Sample.png)

## How tones are drawn

CanTone marks each tone with a Chao five-degree pitch contour:

| Tone type | Digits | Drawing |
| --- | --- | --- |
| **Level** | 1, 3, 6, 7, 8, 9 | a single horizontal bar (steady pitch) |
| **Contour** | 2, 4, 5 | one connecting diagonal (rising or falling pitch) |

The reference stave is always on the right, following the Chinese five-degree convention.

## Two standards: Hong Kong and Guangzhou

CanTone ships two fonts that differ **only in 陰平 (tone 1)**:

| Font | 陰平 (tone 1) | Other tones |
| --- | --- | --- |
| **CanTone Sans HK** (Hong Kong) | high level `55` (horizontal bar) | identical |
| **CanTone Sans GZ** (Guangzhou) | high falling `53` (falling diagonal) | identical |

This is the one HK/GZ tone-value difference with solid support in the literature:
Guangzhou (and older speakers) keep the high-falling 53, while modern Hong Kong has
largely merged it into the high-level 55. The other six tones are identical in both.

## Tone values

5 = highest pitch; tones 7/8/9 are the checked (entering) tones and share the pitch of
1/3/6.

| Digit | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tone | 陰平 | 陰上 | 陰去 | 陽平 | 陽上 | 陽去 | 陰入 | 中入 | 陽入 |
| Hong Kong | 55 | 35 | 33 | 21 | 13 | 22 | 5 | 3 | 2 |
| Guangzhou | 53 | 35 | 33 | 21 | 13 | 22 | 5 | 3 | 2 |

## Download

Grab the latest `CanToneSans-*.zip` from the [Releases page](https://github.com/satoi8080/CanTone/releases).
Unzip it for `CanToneSansHK-Regular.ttf`, `CanToneSansGZ-Regular.ttf` and `OFL.txt`,
the fonts' license.

## Usage

- **Editors / terminals**: set the font to `CanTone Sans HK` or `CanTone Sans GZ`.
- **Web**: `font-family: 'CanTone Sans HK', monospace;`

Install by double-clicking the `.ttf` (macOS/Windows) or copying it to `~/.fonts/`
(Linux).

## License

This repository is licensed in two parts:

- **The fonts** (CanTone Sans HK/GZ): [SIL Open Font License 1.1](OFL.txt). They are
  built from [Noto Sans Mono](https://fonts.google.com/noto/specimen/Noto+Sans+Mono),
  also under OFL 1.1; the OFL requires derivative fonts to stay under the OFL.
- **Source code and build tooling**: [MIT](LICENSE).

A sibling project to [KanaKira](https://github.com/satoi8080/KanaKira) by the same
author, sharing the same concept.

---

> The rest is for developers; regular users can stop here.

## Build from source

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run main.py          # writes CanToneSansHK and CanToneSansGZ .ttf files
uv run python scripts/gen_preview.py   # regenerate preview SVGs (then rasterise, e.g. with inkscape)
uv run python scripts/package.py       # bundle into CanToneSans-v<version>.zip (with OFL.txt)
```

Glyph geometry (digit scale, tone-box size, stroke weight, stave position) is tunable in
`config.json`; the two tone tables (`TONES_HK` and `TONES_GZ`) live in `main.py`.
