"""Generate release preview images (chart + sample) as SVG.

Writes ``assets/CanTone_Chart.svg`` and ``assets/CanTone_Sample.svg``. Render them
to PNG with a deterministic SVG renderer, e.g.::

    inkscape assets/CanTone_Chart.svg --export-type=png \\
        --export-filename=assets/CanTone_Chart.png --export-width=1600
"""

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = str(Path(__file__).resolve().parent.parent)
HK = f"{ROOT}/CanToneSansHK-Regular.ttf"
GZ = f"{ROOT}/CanToneSansGZ-Regular.ttf"

INK = "#1b1b1f"
MUTED = "#9aa0a6"
ACCENT = "#c0392b"
BG = "#ffffff"
PANEL = "#fafafb"
LINE = "#ececef"


def load(path):
    f = TTFont(path)
    return f, f.getBestCmap(), f["glyf"]


def gpath(glyf, name):
    pen = SVGPathPen(glyf)
    glyf[name].draw(pen, glyf)
    return pen.getCommands()


def glyph(f_tuple, ch, bx, by, s, fill=INK):
    f, cmap, glyf = f_tuple
    cp = ord(ch)
    if cp not in cmap:
        return ""
    d = gpath(glyf, cmap[cp])
    return f'<g transform="translate({bx:.1f},{by:.1f}) scale({s},{-s})"><path d="{d}" fill="{fill}"/></g>'


def text_line(f_tuple, s, x0, baseline, scale, fill=INK):
    out = []
    for i, ch in enumerate(s):
        out.append(glyph(f_tuple, ch, x0 + i * 600 * scale, baseline, scale, fill))
    return "".join(out)


# ---------------------------------------------------------------- chart
def build_chart():
    hk = load(HK)
    gz = load(GZ)
    # Chao five-degree values per standard; the two differ only in 陰平 (tone 1).
    chao_hk = ["55", "35", "33", "21", "13", "22", "5", "3", "2"]
    chao_gz = ["53", "35", "33", "21", "13", "22", "5", "3", "2"]

    M = 72  # symmetric outer margin
    pitch, panel_w, panel_h = 120, 108, 150
    n, s = 9, 0.135
    content_w = (n - 1) * pitch + panel_w
    W = 2 * M + content_w  # left margin == right margin == M

    title_y = 86
    r1_label_y, r1_panel_y = 156, 174
    r1_chao_y = r1_panel_y + panel_h + 27
    r2_label_y = r1_chao_y + 46
    r2_panel_y = r2_label_y + 18
    r2_chao_y = r2_panel_y + panel_h + 27
    footer_y = r2_chao_y + 44
    H = footer_y + (title_y - 34)  # bottom margin mirrors top

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system,Helvetica,Arial,sans-serif">'
    ]
    svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    svg.append(
        f'<text x="{M}" y="{title_y}" font-size="34" font-weight="700" fill="{INK}">CanTone</text>'
    )
    svg.append(
        f'<text x="{M + 200}" y="{title_y}" font-size="20" fill="{MUTED}">粵拼聲調閱讀輔助字型 · Jyutping tone reading aid</text>'
    )

    rows = [
        ("CanTone Sans GZ", "廣州 Guangzhou", gz, chao_gz, r1_label_y, r1_panel_y, r1_chao_y),
        ("CanTone Sans HK", "香港 Hong Kong", hk, chao_hk, r2_label_y, r2_panel_y, r2_chao_y),
    ]
    for title, sub, ft, chao, label_y, panel_y, chao_y in rows:
        svg.append(
            f'<text x="{M}" y="{label_y}" font-size="19" font-weight="600" fill="{INK}">{title}</text>'
        )
        svg.append(
            f'<text x="{M + 250}" y="{label_y}" font-size="16" fill="{MUTED}">{sub}</text>'
        )
        for i in range(1, 10):
            cx = M + (i - 1) * pitch
            svg.append(
                f'<rect x="{cx}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="10" fill="{PANEL}" stroke="{LINE}"/>'
            )
            baseline = panel_y + panel_h - 26
            gx = cx + panel_w / 2 - (600 * s) / 2
            svg.append(glyph(ft, str(i), gx, baseline, s))
            # Highlight 陰平 (tone 1), the only HK/GZ difference.
            fill = ACCENT if i == 1 else MUTED
            svg.append(
                f'<text x="{cx + panel_w / 2}" y="{chao_y}" font-size="15" fill="{fill}" text-anchor="middle">{chao[i - 1]}</text>'
            )

    svg.append(
        f'<text x="{M}" y="{footer_y}" font-size="14" fill="{MUTED}">數字下方為趙氏五度調值,兩者僅 陰平（1）不同 · digit shown with Chao pitch value; the two differ only in tone 1</text>'
    )
    svg.append("</svg>")
    open(f"{ROOT}/assets/CanTone_Chart.svg", "w").write("\n".join(svg))


# ---------------------------------------------------------------- sample / hero
def build_sample():
    font = load(HK)
    lines = [
        ("nei5 hou2 maa3", "你好嗎"),
        ("gwong2 dung1 waa2", "廣東話"),
        ("m4 goi1 saai3", "唔該晒"),
    ]
    M = 80  # symmetric outer margin
    s, lh = 0.105, 120
    W = 1440  # gloss right-aligned at W-M -> right margin == M
    gloss_x = W - M
    title_y = 70
    first_baseline = 196
    H = first_baseline + 2 * lh + 21 + (title_y - 18)  # bottom margin mirrors top
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system,Helvetica,Arial,sans-serif">'
    ]
    svg.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    svg.append(
        f'<text x="{M}" y="{title_y}" font-size="24" font-weight="600" fill="{INK}">CanTone Sans HK</text>'
    )
    svg.append(
        f'<text x="{M + 240}" y="{title_y}" font-size="20" fill="{MUTED}">聲調以趙氏輪廓繪於數字之上</text>'
    )
    for idx, (jp, han) in enumerate(lines):
        baseline = first_baseline + idx * lh
        svg.append(text_line(font, jp, M, baseline, s))
        svg.append(
            f'<text x="{gloss_x}" y="{baseline - 4}" font-size="34" fill="{MUTED}" text-anchor="end">{han}</text>'
        )
    svg.append("</svg>")
    open(f"{ROOT}/assets/CanTone_Sample.svg", "w").write("\n".join(svg))


build_chart()
build_sample()
print("wrote chart + sample svg")
