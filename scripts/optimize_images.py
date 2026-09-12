#!/usr/bin/env python3
"""
Recompress site-local image assets (brand art, banners) to WebP.

This is a local dev tool, not part of the storefront runtime or the Apps
Script feed/publish pipeline — nothing here touches the master sheet or
product photos on Drive. Run it whenever a new brand asset lands in
assets/brand/ (or wherever ASSETS below points) and is too heavy to ship
as-is.

Usage:
    python3 scripts/optimize_images.py

Requires Pillow (pip install Pillow). Not a runtime dependency of the site.
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (source PNG/JPEG, output WebP, quality, max width in px)
# max width caps the encode size for a source wider than it's ever displayed;
# quality ~78-82 is the sweet spot for photographic banners (visually
# lossless at storefront display sizes, well under half the PNG's weight).
ASSETS = [
    (os.path.join(ROOT, 'assets/brand/hero-optum.png'),
     os.path.join(ROOT, 'assets/brand/hero-optum.webp'),
     80, 1600),
]


def optimize(src, dst, quality, max_width):
    if not os.path.exists(src):
        print(f'skip (missing): {src}')
        return
    with Image.open(src) as im:
        im = im.convert('RGB') if im.mode in ('P', 'CMYK') else im
        if im.width > max_width:
            h = round(im.height * max_width / im.width)
            im = im.resize((max_width, h), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=quality, method=6)

    # Verify the file we just wrote is a valid, openable image before
    # trusting it — a truncated/corrupt encode should never reach the site.
    with Image.open(dst) as check:
        check.verify()

    before = os.path.getsize(src)
    after = os.path.getsize(dst)
    pct = 100 * (1 - after / before)
    print(f'{os.path.relpath(src, ROOT)} -> {os.path.relpath(dst, ROOT)}: '
          f'{before/1024:.0f}KB -> {after/1024:.0f}KB ({pct:.0f}% smaller)')


if __name__ == '__main__':
    for src, dst, quality, max_width in ASSETS:
        optimize(src, dst, quality, max_width)
