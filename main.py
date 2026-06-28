"""Build the CanTone fonts.

CanTone renders Cantonese (Jyutping) tone digits 1-9 with a Chao "five-degree"
tone-letter contour drawn above each digit, as a reading aid.

Two fonts are produced, one per tone standard; they differ *only* in 陰平 (tone 1):

  * CanTone Sans HK  (Hong Kong)  - 陰平 = high level 55.
  * CanTone Sans GZ  (Guangzhou)  - 陰平 = high falling 53.

Contour tones (2, 4, 5 - and 1 in GZ) are drawn as one stave plus a single sloped
line: the two pitch marks are connected into one diagonal stroke, so a
rising/falling tone reads as a continuous contour.

Each tone digit is a single codepoint mapped through ``cmap`` to its own composite
glyph, so no OpenType ``liga`` feature is required - the contour is purely a matter
of how we draw the glyph.
"""

import json
import time
import tomllib
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable

HERE = Path(__file__).resolve().parent
CONFIG_FILE = HERE / "config.json"

with open(CONFIG_FILE) as f:
    CONFIG = json.load(f)

with open(HERE / "pyproject.toml", "rb") as f:
    PYPROJECT = tomllib.load(f)

MONO_FONT = HERE / CONFIG["fonts"]["input"]["mono"]

DIGIT_SCALE = CONFIG["scaling"]["digit_scale"]

TB = CONFIG["tone_box"]
X_LEFT = TB["x_left"]
X_RIGHT = TB["x_right"]
Y_BOTTOM = TB["y_bottom"]
Y_TOP = TB["y_top"]
STROKE = TB["stroke"]
STAVE = TB["stave"]

ADVANCE = 600  # Noto Sans Mono is monospaced at 600 upm units


# Jyutping tone -> Chao pitch contour (5 = highest pitch). A single level means a
# level tone (one horizontal bar); two levels mean a contour tone (rising/falling).
# Hong Kong values: 55 35 33 21 13 22; checked tones 7/8/9 = 5 3 2.
TONES_HK: dict[str, list[int]] = {
    "1": [5],  # 55 high level
    "2": [3, 5],  # 35 mid rising
    "3": [3],  # 33 mid level
    "4": [2, 1],  # 21 low falling
    "5": [1, 3],  # 13 low rising
    "6": [2],  # 22 low level
    "7": [5],  # 5  high checked (entering)
    "8": [3],  # 3  mid checked (entering)
    "9": [2],  # 2  low checked (entering)
}

# Guangzhou differs from Hong Kong only in 陰平 (tone 1): the high-falling 53 that
# Guangzhou (and older speakers) retain, vs the high-level 55 of modern Hong Kong.
# This is the one HK/GZ tone-value difference with solid support in the literature.
TONES_GZ: dict[str, list[int]] = {**TONES_HK, "1": [5, 3]}  # 53 high falling

TONE_TABLES = {"hongkong": TONES_HK, "guangzhou": TONES_GZ}

# Printable ASCII passed through unchanged (so full Jyutping text renders in one
# monospaced font). Digits 1-9 are excluded; they become tone composites instead.
PASSTHROUGH = [cp for cp in range(0x20, 0x7F) if not (0x31 <= cp <= 0x39)]


def pitch_y(level: int) -> float:
    """y coordinate of a Chao pitch level (1..5) within the tone box."""
    return Y_BOTTOM + (level - 1) * (Y_TOP - Y_BOTTOM) / 4.0


def _signed_area(pts: list[tuple[float, float]]) -> float:
    a = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return a / 2.0


def poly(pen: TTGlyphPen, pts: list[tuple[float, float]]) -> None:
    """Draw a filled polygon, forced clockwise (TrueType outer-fill direction)."""
    if _signed_area(pts) > 0:  # counter-clockwise -> reverse
        pts = list(reversed(pts))
    pen.moveTo(pts[0])
    for p in pts[1:]:
        pen.lineTo(p)
    pen.closePath()


def rect(pen: TTGlyphPen, x0: float, y0: float, x1: float, y1: float) -> None:
    poly(pen, [(x0, y1), (x1, y1), (x1, y0), (x0, y0)])


def hbar(pen: TTGlyphPen, x0: float, x1: float, y: float) -> None:
    """Horizontal pitch mark of thickness STROKE centred on y."""
    rect(pen, x0, y - STROKE / 2, x1, y + STROKE / 2)


def vstave(pen: TTGlyphPen, x_right: float, height_levels=(1, 5)) -> None:
    """Vertical reference stave at x_right, spanning the given pitch levels."""
    rect(
        pen,
        x_right - STAVE,
        pitch_y(height_levels[0]),
        x_right,
        pitch_y(height_levels[1]),
    )


def diagline(pen: TTGlyphPen, p0: tuple[float, float], p1: tuple[float, float]) -> None:
    """Thick sloped stroke of thickness STROKE between two points."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    length = (dx * dx + dy * dy) ** 0.5 or 1.0
    nx, ny = -dy / length * STROKE / 2, dx / length * STROKE / 2
    poly(
        pen,
        [
            (x0 + nx, y0 + ny),
            (x1 + nx, y1 + ny),
            (x1 - nx, y1 - ny),
            (x0 - nx, y0 - ny),
        ],
    )


def draw_tone(pen: TTGlyphPen, levels: list[int]) -> None:
    """Draw the Chao tone mark above the digit.

    Level tones are one stave + one horizontal pitch mark; contour tones are one
    stave + a single sloped line connecting the two pitches.
    """
    if len(levels) == 1:
        # Level tone: single stave on the right + one horizontal pitch mark.
        vstave(pen, X_RIGHT)
        hbar(pen, X_LEFT, X_RIGHT, pitch_y(levels[0]))
        return

    # Contour tone: one stave on the right; a single sloped line connecting the
    # two pitches, meeting the stave at the ending pitch.
    a, b = levels[0], levels[1]
    vstave(pen, X_RIGHT)
    diagline(pen, (X_LEFT, pitch_y(a)), (X_RIGHT, pitch_y(b)))


def draw_scaled(
    pen: TTGlyphPen, src: TTFont, gname: str, scale: float, dx: float, dy: float
) -> None:
    src["glyf"][gname].draw(
        TransformPen(pen, (scale, 0, 0, scale, dx, dy)), src["glyf"]
    )


def make_tone_glyph(
    mono: TTFont, digit: str, dst: TTFont, tones: dict[str, list[int]]
) -> str:
    """Composite glyph: the digit (scaled, centred) plus its tone mark above."""
    src_name = mono.getBestCmap()[ord(digit)]
    aw, _ = mono["hmtx"][src_name]
    pen = TTGlyphPen(None)
    dx = (ADVANCE - aw * DIGIT_SCALE) / 2.0
    draw_scaled(pen, mono, src_name, DIGIT_SCALE, dx, 0)
    draw_tone(pen, tones[digit])
    name = f"tone{digit}"
    dst["glyf"][name] = pen.glyph()
    dst["hmtx"][name] = (ADVANCE, 0)
    return name


def make_passthrough_glyph(mono: TTFont, cp: int, dst: TTFont) -> str:
    """Copy an ASCII glyph unchanged (composites flattened) at full advance."""
    src_name = mono.getBestCmap()[cp]
    aw, _ = mono["hmtx"][src_name]
    pen = TTGlyphPen(None)
    mono["glyf"][src_name].draw(pen, mono["glyf"])  # scale 1.0, flattens components
    name = f"ascii_{cp:02X}"
    dst["glyf"][name] = pen.glyph()
    dst["hmtx"][name] = (aw, 0)
    return name


def set_names(font: TTFont, info: dict) -> None:
    fam, full, ps = info["family_name"], info["full_name"], info["postscript_name"]
    version = PYPROJECT["project"]["version"]
    name = font["name"]
    platforms = [(3, 1, 0x409), (0, 3, 0), (1, 1, 0)]
    for pid, eid, lid in platforms:
        name.setName(fam, 1, pid, eid, lid)
        name.setName("Regular", 2, pid, eid, lid)
        name.setName(f"{ps}-{version}", 3, pid, eid, lid)
        name.setName(full, 4, pid, eid, lid)
        name.setName(ps, 6, pid, eid, lid)
        name.setName(
            "Copyright 2026 Akira (https://github.com/satoi8080/CanTone). "
            "Portions Copyright 2022 The Noto Project Authors "
            "(https://github.com/notofonts/latin-greek-cyrillic).",
            0,
            pid,
            eid,
            lid,
        )
        name.setName(f"Version {version}", 5, pid, eid, lid)
        name.setName("Akira", 8, pid, eid, lid)
        name.setName("Akira", 9, pid, eid, lid)
        name.setName(
            PYPROJECT["project"]["description"] + " Built from Noto Sans Mono.",
            10,
            pid,
            eid,
            lid,
        )
        name.setName("https://github.com/satoi8080/CanTone", 11, pid, eid, lid)
        name.setName(
            "This Font Software is licensed under the SIL Open Font License, "
            "Version 1.1. This license is available with a FAQ at "
            "https://openfontlicense.org",
            13,
            pid,
            eid,
            lid,
        )
        name.setName("https://openfontlicense.org", 14, pid, eid, lid)
        name.setName(fam, 16, pid, eid, lid)
        name.setName("Regular", 17, pid, eid, lid)


def build_variant(tones: dict[str, list[int]], info: dict, out_name: str) -> None:
    print(f"» Building {info['family_name']} …")
    mono = TTFont(str(MONO_FONT))

    font = TTFont()
    for tag in ("head", "hhea", "maxp", "OS/2", "post"):
        font[tag] = deepcopy(mono[tag])
    font["name"] = newTable("name")
    font["name"].names = []

    jst = timezone(timedelta(hours=9))
    font["head"].created = (
        int(datetime(2026, 6, 28, tzinfo=jst).timestamp()) + 2082844800
    )
    font["head"].modified = int(time.time()) + 2082844800
    parts = PYPROJECT["project"]["version"].split(".")
    font["head"].fontRevision = float(f"{parts[0]}.{parts[1]}")

    font["glyf"] = newTable("glyf")
    font["glyf"].glyphs = {}
    font["hmtx"] = newTable("hmtx")
    font["hmtx"].metrics = {}
    font["loca"] = newTable("loca")

    font.setGlyphOrder([".notdef"])
    font["glyf"][".notdef"] = deepcopy(mono["glyf"][".notdef"])
    font["hmtx"][".notdef"] = mono["hmtx"][".notdef"]

    cmap_map: dict[int, str] = {}
    for digit in tones:
        gname = make_tone_glyph(mono, digit, font, tones)
        cmap_map[ord(digit)] = gname
    for cp in PASSTHROUGH:
        if cp in mono.getBestCmap():
            cmap_map[cp] = make_passthrough_glyph(mono, cp, font)

    order = list(font["glyf"].glyphs.keys())
    font.setGlyphOrder(order)
    font["glyf"].glyphOrder = order

    cmap_tbl = deepcopy(mono["cmap"])
    for sub in cmap_tbl.tables[:]:
        sub.cmap = {cp: cmap_map[cp] for cp in sub.cmap if cp in cmap_map}
        if not sub.cmap:
            cmap_tbl.tables.remove(sub)
    font["cmap"] = cmap_tbl

    glyf = font["glyf"]
    for g in glyf.glyphs.values():
        g.recalcBounds(glyf)

    top = max(
        (g.yMax for g in glyf.glyphs.values() if g.numberOfContours), default=Y_TOP
    )
    hhea, os2 = font["hhea"], font["OS/2"]
    if top + 20 > hhea.ascent:
        inc = top + 20 - hhea.ascent
        hhea.ascent += inc
        os2.sTypoAscender += inc
        os2.usWinAscent += inc

    font["hhea"].numberOfHMetrics = len(order)
    font["maxp"].numGlyphs = len(order)
    font["maxp"].recalc(font)

    set_names(font, info)

    out = HERE / out_name
    font.save(str(out))
    print("✓ Saved", out.relative_to(HERE))


def build() -> None:
    for spec in CONFIG["variants"]:
        build_variant(TONE_TABLES[spec["standard"]], spec["font_info"], spec["output"])


if __name__ == "__main__":
    build()
