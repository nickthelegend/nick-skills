"""Tile every image in the given folders into one contact sheet so a human can review the art at a glance.
Usage: python3 contact-sheet.py out.jpg folder1 [folder2 ...]"""
import glob, os, sys
from PIL import Image, ImageDraw

out, folders = sys.argv[1], sys.argv[2:]
tiles = []
for folder in folders:
    for f in sorted(glob.glob(os.path.join(folder, "*.png"))):
        im = Image.open(f).convert("RGBA")
        bg = Image.new("RGBA", im.size, (48, 48, 52, 255))
        bg.alpha_composite(im)
        bg = bg.convert("RGB")
        bg.thumbnail((360, 240))
        t = Image.new("RGB", (360, 262), (20, 20, 22))
        t.paste(bg, ((360 - bg.width) // 2, (240 - bg.height) // 2))
        ImageDraw.Draw(t).text((6, 244), os.path.relpath(f, os.path.dirname(folder))[:-4], fill=(230, 230, 230))
        tiles.append(t)
cols = 5
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 364 + 4, rows * 266 + 4), (10, 10, 12))
for i, t in enumerate(tiles):
    sheet.paste(t, (4 + (i % cols) * 364, 4 + (i // cols) * 266))
sheet.save(out, quality=82)
print(len(tiles), "images ->", out)
