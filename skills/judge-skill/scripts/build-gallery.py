"""Round 1: turn full-page PNG screenshots (<shots>/<repo>/<nn>-<route>-<1440|375>.png) into web JPEGs and a
manifest.json that a one-page gallery reads (tab per product, desktop beside phone).
Usage: python3 build-gallery.py <shots-dir> <out-dir> repo1 repo2 ..."""
import json, os, re, sys
from PIL import Image

src, out, order = sys.argv[1], sys.argv[2], sys.argv[3:]
manifest = {}
for repo in order:
    d = os.path.join(src, repo)
    if not os.path.isdir(d):
        continue
    os.makedirs(os.path.join(out, "img", repo), exist_ok=True)
    screens = {}
    for f in sorted(os.listdir(d)):
        m = re.match(r"(.+)-(1440|375|390)\.png$", f)
        if not m:
            continue
        key, w = m.group(1), m.group(2)
        im = Image.open(os.path.join(d, f)).convert("RGB")
        target = 1200 if w == "1440" else int(w)
        if im.width > target:
            im = im.resize((target, round(im.height * target / im.width)), Image.LANCZOS)
        cap = 6000 if w == "1440" else 7000
        if im.height > cap:
            im = im.crop((0, 0, im.width, cap))
        name = f"img/{repo}/{key}-{w}.jpg"
        im.save(os.path.join(out, name), quality=72, optimize=True, progressive=True)
        screens.setdefault(key, {})["desktop" if w == "1440" else "phone"] = {"src": name, "w": im.width, "h": im.height}
    manifest[repo] = screens
json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
print({k: len(v) for k, v in manifest.items()})
