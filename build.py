"""Render the 19 November 2026 world-news front page to entry.png.

Build-time tool only: main.ts never runs this, it copies the committed PNG.
Every line is measured before it is drawn, and the finished layout is checked for
overlapping text, so a font or copy change fails loudly instead of shipping
clipped or garbled type.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "entry.png"

W = H = 1024
MARGIN = 36
CW = W - 2 * MARGIN            # 952 usable canvas width
TEXT_X = MARGIN + 26           # 62 text edge inside a story block
TEXT_W = W - MARGIN - TEXT_X   # 926 text column

BG = (246, 242, 233)
INK = (24, 24, 27)
PANEL = (238, 232, 219)
GRAY = (95, 90, 80)
HAIR = (203, 195, 179)
BAND_DIM = (198, 193, 182)

CRIMSON = (166, 34, 40)
BLUE = (27, 58, 143)
TEAL = (14, 92, 106)
ORANGE = (138, 74, 14)
GREEN = (15, 107, 69)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
_boxes = []                    # (x0, y0, x1, y1, text, bleed) for every drawn line


def advance(s, f, track):
    if not track:
        return d.textlength(s, font=f)
    return sum(d.textlength(ch, font=f) for ch in s) + track * (len(s) - 1)


def put(x, y, s, f, fill, track=0, limit=TEXT_W, bleed=False):
    """Draw one line at x, refusing to draw it if it would exceed `limit`.

    `bleed` marks masthead type on the edge-to-edge dark band, which is allowed
    to ignore the page margin.
    """
    w = advance(s, f, track)
    assert w <= limit, f"overflow {w:.1f} > {limit}: {s!r}"
    if track:
        cx = x
        for ch in s:
            d.text((cx, y), ch, font=f, fill=fill)
            cx += d.textlength(ch, font=f) + track
    else:
        d.text((x, y), s, font=f, fill=fill)
    _boxes.append((x, y + f.getbbox("Ag")[1], x + w, y + f.getbbox("Ag")[3], s, bleed))
    return w


def put_center(y, s, f, fill, track=0, limit=CW, bleed=False):
    w = advance(s, f, track)
    assert w <= limit, f"overflow {w:.1f} > {limit}: {s!r}"
    put((W - w) / 2, y, s, f, fill, track=track, limit=limit, bleed=bleed)


def rule(y, thickness, fill, x0=MARGIN, x1=W - MARGIN):
    d.rectangle([x0, y, x1, y + thickness - 1], fill=fill)


# --------------------------------------------------------------- masthead band
BAND_H = 148
d.rectangle([0, 0, W, BAND_H - 1], fill=INK)
put_center(18, "WORLD NEWS \u00b7 ONE PAGE", font(BOLD, 18), BAND_DIM, track=3, bleed=True)
put_center(42, "19 NOVEMBER 2026", font(BOLD, 64), (250, 247, 240), bleed=True)
put_center(116, "THURSDAY \u00b7 SIX STORIES FROM AROUND THE WORLD",
           font(BOLD, 18), BAND_DIM, track=2, bleed=True)
rule(BAND_H, 5, CRIMSON, 0, W)

# --------------------------------------------------------------- lead story
LEAD_TOP, LEAD_H = 166, 190
LEAD_BOTTOM = LEAD_TOP + LEAD_H
d.rectangle([MARGIN, LEAD_TOP, W - MARGIN, LEAD_BOTTOM], fill=PANEL)
d.rectangle([MARGIN, LEAD_TOP, MARGIN + 8, LEAD_BOTTOM], fill=CRIMSON)
put(TEXT_X, LEAD_TOP + 14, "LEAD STORY \u00b7 ASIA", font(BOLD, 18), CRIMSON, track=2)
put(TEXT_X, LEAD_TOP + 36, "ICJ RULES MYANMAR", font(BOLD, 50), INK)
put(TEXT_X, LEAD_TOP + 92, "COMMITTED GENOCIDE", font(BOLD, 50), INK)
put(TEXT_X, LEAD_TOP + 152, "UN's top court finds genocide against the Rohingya",
    font(REG, 21), GRAY)

# --------------------------------------------------------------- brief rows
BRIEF_TOP, ROW_H, PITCH = 366, 126, 132
briefs = [
    ("GLOBAL", BLUE, "TRUMP, PUTIN AND XI", "SIGN \u201cPEACE DECLARATION\u201d"),
    ("EUROPE \u00b7 UKRAINE", TEAL, "PUTIN VOWS \u201cFAR MORE", "PAINFUL\u201d REPLY ON CRIMEA"),
    ("AMERICAS", ORANGE, "VENEZUELA AND US", "SIGN MILITARY DEAL"),
    ("AFRICA", GREEN, "MIGRANT BOAT SINKS", "OFF SENEGAL COAST"),
]

for i, (tag, accent, l1, l2) in enumerate(briefs):
    t = BRIEF_TOP + i * PITCH
    d.rectangle([MARGIN, t + 6, MARGIN + 12, t + 18], fill=accent)
    put(TEXT_X, t + 4, tag, font(BOLD, 15), accent, track=2)
    put(TEXT_X, t + 26, l1, font(BOLD, 44), INK)
    put(TEXT_X, t + 72, l2, font(BOLD, 44), INK)
    if i < len(briefs) - 1:
        rule(t + ROW_H, 1, HAIR)

# --------------------------------------------------------------- also strip
rule(896, 2, INK)
f_also, f_src = font(BOLD, 24), font(REG, 16)
w_pre = put(TEXT_X, 908, "ALSO \u00b7 ", f_also, CRIMSON)
put(TEXT_X + w_pre, 908, "NVIDIA CEO JENSEN HUANG RESIGNS", f_also, GRAY)
put(TEXT_X, 938, "VAN GOGH PAINTING SELLS FOR A RECORD $190.4M", f_also, GRAY)
put(TEXT_X, 968, "SOURCES: BBC WORLD \u00b7 WIKIPEDIA IN THE NEWS", f_src, GRAY)

# --------------------------------------------------------------- layout checks
for i, (ax0, ay0, ax1, ay1, at, ab) in enumerate(_boxes):
    for bx0, by0, bx1, by1, bt, bb in _boxes[i + 1:]:
        clash = ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1
        assert not clash, f"text overlap: {at!r} / {bt!r}"
    assert ax0 >= 0 and ax1 <= W, f"runs off the canvas: {at!r}"
    assert ay1 <= H - 20, f"runs off the bottom: {at!r}"
    assert ab or ay0 >= MARGIN, f"inside the top margin: {at!r}"

img.save(OUT, "PNG", optimize=True)

with Image.open(OUT) as check:
    assert check.size == (W, H), check.size
    assert check.format == "PNG", check.format
size = OUT.stat().st_size
assert size <= 1048576, f"{size} bytes over the cap"
print(f"{OUT.name}: {W}x{H} {size} bytes, {len(_boxes)} text lines, no overlaps")
