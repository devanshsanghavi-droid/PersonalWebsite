#!/usr/bin/env python3
"""
Generate responsive derivatives for every image the site displays.

For each source it writes WebP plus a same-format fallback at a few widths,
into images/opt/. index.html references only those; images/ keeps the masters.
Re-run after adding or replacing a source image.

    python3 scripts/optimize-images.py
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images", "opt")

# widths to emit, and whether the source is a photograph (JPEG fallback) or
# flat-colour UI / line art (PNG fallback, which stays crisp)
SOURCES = {
    "civicpulse-rotary.png":       dict(widths=(400, 672, 1344), photo=True),
    "math-kangaroo-mentoring.png": dict(widths=(400, 672, 1344), photo=True),
    "mogp-benchmark.png":          dict(widths=(672, 1344),      photo=False),
    "carta-home.png":              dict(widths=(200, 400),       photo=False),
    "carta-explanation.png":       dict(widths=(200, 400),       photo=False),
}

def main():
    os.makedirs(OUT, exist_ok=True)
    total_src = total_out = 0
    for name, cfg in SOURCES.items():
        src = os.path.join(ROOT, "images", name)
        if not os.path.exists(src):
            print("  skip (missing):", name); continue
        im = Image.open(src)
        stem = os.path.splitext(name)[0]
        total_src += os.path.getsize(src)
        made = []
        for w in cfg["widths"]:
            if w > im.width:
                continue
            r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            wp = os.path.join(OUT, "%s-%d.webp" % (stem, w))
            r.convert("RGB" if cfg["photo"] else r.mode).save(
                wp, "WEBP", quality=82 if cfg["photo"] else 90, method=6)
            if cfg["photo"]:
                fb = os.path.join(OUT, "%s-%d.jpg" % (stem, w))
                r.convert("RGB").save(fb, "JPEG", quality=82, optimize=True, progressive=True)
            else:
                fb = os.path.join(OUT, "%s-%d.png" % (stem, w))
                r.save(fb, "PNG", optimize=True)
            made.append((w, os.path.getsize(wp), os.path.getsize(fb)))
            total_out += os.path.getsize(wp)
        print("  %-30s %dx%d  ->  %s" % (name, im.width, im.height,
              ", ".join("%dw webp %dKB / fb %dKB" % (w, a/1024, b/1024) for w, a, b in made)))
    print("\n  masters %.2f MB   webp set %.2f MB" % (total_src/1048576, total_out/1048576))

if __name__ == "__main__":
    main()
