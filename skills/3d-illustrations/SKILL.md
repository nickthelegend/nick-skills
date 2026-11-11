---
name: 3d-illustrations
description: Generate a consistent set of premium 3D object illustrations (glossy single objects with a tiny friendly face, like the chrome coins and cards on xoox.fun, but in each product's own colours and materials) with ChatGPT's image model in the user's real Chrome, then wire them into a web UI. Use it when a landing page, launchpad, game or dashboard needs hero objects, feature icons, empty states or badges in 3D, when someone says "3D illustrations", "make 3D art like xoox", or types /3d-illustrations.
---

# /3d-illustrations

One polished 3D object per image, a soft studio light, rounded bevels, and a tiny friendly face. This makes a product feel
finished and premium. The **object style** came from xoox.fun (chrome coins, fanned cards, a coin stack on a ring tray).
**Never copy their silver, their pill-eye mascot or their logo.** Every product gets its own colour, material and face.

## 1. Pick the product's kit (write it down before any prompt)
Save these 5 lines as `docs/ART-3D.md` in the repo:
- **Material:** one family per product, e.g. glossy candy enamel, anodized aluminium, frosted glass with an inner glow,
  matte ceramic with a gloss rim, soft-touch rubber, polished brass. Silver/chrome only if the user asks for it.
- **Palette:** the product's own brand colours as hex. One main colour for the objects, one accent for details, one
  rim-light colour. Check other products' `ART-3D.md` files so no two products in one event share a palette.
- **Face:** the product's own tiny mark, e.g. two curved ink drops, a small smile line, one round eye, a visor slit.
  Keep it on objects where a face fits, not every one.
- **Background:** transparent for UI objects (they sit on light or dark surfaces), or a seamless studio sweep in a
  tint of the palette for hero shots.
- **Subjects:** the product's own metaphors (for comics: a comic issue, a speech bubble, a pen nib; for a game: a crown,
  a card, a tower, a chest; for DeFi: a vault, a coin stack, a key).

## 2. Prompt template (reuse the same style line in every prompt, so the set matches)
```
Create an image: <subject, one object, simple composition>. <MATERIAL> 3D render in <main hex> with <accent hex>
details and a soft <rim hex> rim light, soft studio lighting, crisp reflections, rounded bevelled edges, gentle
toy-like proportions, <face line>, centred, transparent background (no background, no ground shadow), square
1024x1024, no text, no letters, no logos.
```
Ask for 8–12 subjects: one hero, 3–5 feature objects, empty-state, success/error state, a badge or trophy, and a logo
mark candidate.

## 3. Generate (ChatGPT in the user's real Chrome)
Use the `/chatgpt-assets` workflow: load the Claude-in-Chrome tools in ONE ToolSearch call, open chatgpt.com in a new
tab (the user is signed in), use a fresh chat per product, send one image per message, and download each image as a
blob into `~/Downloads` named `<product>-3d-<subject>.png`. Don't upload reference images (another brand's art). If
ChatGPT refuses or rate-limits, stop and say so.

## 4. Check the set before wiring it in
- Make a contact sheet of all images and look at it. Regenerate any image with the wrong colour, extra objects, text,
  a cut-off subject, a cast shadow on a transparent image, or a face that doesn't match the kit.
- Check each object at 48 px. It must still read as the subject.
- Convert to webp (transparent: `cwebp -q 85 -alpha_q 90 -resize 640 0`; hero: `-q 82 -resize 1400 0`), keep files
  under ~400 KB, and put them in the app's public art folder.

## 5. Wire into the UI
- Objects go in framed feature cards, hero corners, empty states, badges and toasts. One object per card, generous
  padding, no glow halos and no sticker borders.
- Gentle float (2–6 px over 4–7 s) or a slight parallax, turned off under `prefers-reduced-motion`. Width and height
  set, so nothing shifts as the page loads; alt text describes the object.
- On dark UIs, add a soft radial light behind the object (one tint of the palette) so its rim reads.
- README credit: "3D art generated with ChatGPT".

Related: `/chatgpt-assets` (generation mechanics), `/dribbble-frontend` (layout and finish).
