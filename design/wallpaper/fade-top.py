#!/usr/bin/env python3
"""Fade the top of a wallpaper to black, so the top panel stands out against it.

    fade-top.py SOURCE OUT [--px 40]

Always start from the untouched source, so re-running gives the same result. kOMA Powder:
    fade-top.py ../Raw-assets/wallpapers/kOMA-Powder-source.jpg \\
        wallpapers/kOMA-Powder/contents/images/1363x784.jpg
"""

import argparse
from pathlib import Path

from PIL import Image


def fade_top(img, px):
    img = img.convert("RGB")
    # black at the top edge, easing out to the untouched image at px
    shade = Image.new("L", img.size, 255)
    for y in range(min(px, img.height)):
        t = y / px
        shade.paste(round(255 * t * t * (3 - 2 * t)), (0, y, img.width, y + 1))
    return Image.composite(img, Image.new("RGB", img.size), shade)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--px", type=int, default=40)
    a = ap.parse_args()
    fade_top(Image.open(a.source), a.px).save(a.out, quality=98, subsampling=0, optimize=True)
    print(a.out)


if __name__ == "__main__":
    main()
