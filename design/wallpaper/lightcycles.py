#!/usr/bin/env python3
"""Render the kOMA Lightcycles wallpaper: the kOMA mark centered on a dark grid,
with one light-cycle trail per kOMA color scheme (Tron Aqua, McLaren, Ferrari, Lambo).

    lightcycles.py OUT_DIR [--sizes 1920x1080,2560x1440,3840x2160]

Drawn at 3840x2160 and scaled down, so every size has the same composition.
Needs Pillow and rsvg-convert (librsvg).
"""

import argparse
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 3840, 2160
ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / "branding" / "koma.svg"

# the four kOMA color schemes' accent colors (DecorationFocus)
AQUA = (35, 200, 255)
MCLAREN = (255, 135, 0)
FERRARI = (255, 50, 69)
LAMBO = (104, 220, 69)

# Trails as fractions of the screen: the tail enters from an edge, the last point is
# the bike. All turns are right angles, and every path stays clear of the logo area.
TRAILS = [
    (AQUA, [(-0.02, 0.20), (0.27, 0.20), (0.27, 0.11), (0.71, 0.11), (0.71, 0.24), (0.86, 0.24), (0.86, 0.38)]),
    (MCLAREN, [(1.02, 0.14), (0.93, 0.14), (0.93, 0.52), (0.79, 0.52), (0.79, 0.66)]),
    (FERRARI, [(1.02, 0.86), (0.74, 0.86), (0.74, 0.76), (0.55, 0.76), (0.55, 0.91), (0.33, 0.91)]),
    (LAMBO, [(0.11, 1.02), (0.11, 0.62), (0.21, 0.62), (0.21, 0.34), (0.08, 0.34), (0.08, 0.27)]),
]


def px(p):
    return (p[0] * W, p[1] * H)


def background():
    """Near-black, slightly lighter in the middle, with a faint blue grid."""
    bg = Image.radial_gradient("L").resize((W, H), Image.Resampling.BICUBIC)
    # radial_gradient is 0 at the center and 255 at the edge
    centre, edge = (11, 17, 26), (2, 3, 6)
    img = Image.merge(
        "RGB",
        [bg.point(lambda v, a=c, b=e: round(a + (b - a) * min(v, 255) / 255)) for c, e in zip(centre, edge)],
    )
    grid = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(grid)
    step = 120
    for x in range(0, W, step):
        d.line([(x, 0), (x, H)], fill=(9, 28, 38), width=2)
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=(9, 28, 38), width=2)
    return ImageChops.add(img, grid)


def trail_layers(colour, points):
    """Core line plus two glows; brightness rises from the tail to the bike."""
    pts = [px(p) for p in points]
    segs = list(zip(pts, pts[1:]))
    total = sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in segs)
    core = Image.new("RGB", (W, H))
    halo = Image.new("RGB", (W, H))
    dc, dh = ImageDraw.Draw(core), ImageDraw.Draw(halo)
    walked = 0.0
    for a, b in segs:
        length = abs(b[0] - a[0]) + abs(b[1] - a[1])
        steps = max(1, int(length // 6))
        for i in range(steps):
            t0, t1 = i / steps, (i + 1) / steps
            p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            k = 0.18 + 0.82 * ((walked + length * t1) / total) ** 1.6
            hot = tuple(round(c * k + 255 * k * 0.35) for c in colour)
            dc.line([p0, p1], fill=tuple(min(255, v) for v in hot), width=7)
            dh.line([p0, p1], fill=tuple(round(c * k) for c in colour), width=22)
        walked += length
    # the bike: a bright capsule at the head
    hx, hy = pts[-1]
    (px_, py_) = pts[-2]
    dx, dy = (hx > px_) - (hx < px_), (hy > py_) - (hy < py_)
    bike = [(hx - dx * 46 - abs(dy) * 13, hy - dy * 46 - abs(dx) * 13), (hx + abs(dy) * 13, hy + abs(dx) * 13)]
    bike = [(min(bike[0][0], bike[1][0]), min(bike[0][1], bike[1][1])), (max(bike[0][0], bike[1][0]), max(bike[0][1], bike[1][1]))]
    dc.rounded_rectangle(bike, radius=12, fill=(255, 255, 255))
    dh.rounded_rectangle(bike, radius=12, fill=colour)
    glow = ImageChops.add(halo.filter(ImageFilter.GaussianBlur(18)), halo.filter(ImageFilter.GaussianBlur(70)))
    return ImageChops.add(glow, core)


def svg_image(svg, width=None, height=None):
    with tempfile.TemporaryDirectory() as tmp:
        src, out = Path(tmp) / "in.svg", Path(tmp) / "out.png"
        src.write_text(svg) if isinstance(svg, str) else src.write_bytes(svg.read_bytes())
        size = (["-w", str(width)] if width else []) + (["-h", str(height)] if height else [])
        subprocess.run(["rsvg-convert", *size, "-o", str(out), str(src)], check=True)
        return Image.open(out).convert("RGBA")


def logo(size):
    return svg_image(LOGO, size, size)


# "kOMA" drawn in the mark's stroke style: square ends, an open O like its rings,
# the k in McLaren orange and OMA in Tron Aqua. No font needed.
WORDMARK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -8 346 116">
<g fill="none" stroke-width="10" stroke-linecap="square" stroke-linejoin="miter">
<path stroke="#FF8700" d="M 4,0 V 100 M 44,42 L 4,74 M 18,63 L 46,100"/>
<g stroke="#23C8FF">
<path d="M 131.9,34.3 A 34,46 0 1 1 119.5,12.3"/>
<path d="M 160,100 V 0 L 195,58 L 230,0 V 100"/>
<path d="M 256,100 L 292,0 L 328,100 M 270,64 H 314"/>
</g>
</g>
</svg>"""


def render():
    img = background()
    for colour, points in TRAILS:
        img = ImageChops.add(img, trail_layers(colour, points))
    size = round(H * 0.30)
    mark = logo(size)
    pos = ((W - size) // 2, (H - size) // 2)
    glow = Image.new("RGB", (W, H))
    glow.paste(mark.convert("RGB"), pos, mark)
    # a soft halo only; the mark itself stays crisp
    img = ImageChops.add(img, glow.filter(ImageFilter.GaussianBlur(40)).point(lambda v: v * 35 // 100))
    img.paste(mark, pos, mark)

    # centered along the bottom, so screens that crop the sides (16:10) keep it whole
    word = svg_image(WORDMARK, height=round(H * 0.045 * 0.75 * 0.8))
    margin = round(H * 0.018)
    wpos = ((W - word.width) // 2, H - word.height - margin)
    wglow = Image.new("RGB", (W, H))
    wglow.paste(word.convert("RGB"), wpos, word)
    img = ImageChops.add(img, wglow.filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 40 // 100))
    img.paste(word, wpos, word)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--sizes", default="1920x1080,2560x1440,3840x2160")
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    img = render()
    for size in a.sizes.split(","):
        w, h = (int(v) for v in size.split("x"))
        out = a.out_dir / f"{w}x{h}.png"
        img.resize((w, h), Image.Resampling.LANCZOS).save(out, optimize=True)
        print(out)


if __name__ == "__main__":
    main()
