---
name: chatgpt-assets
description: Generate on-brand product art (hero illustrations, isometric objects, icons, logos, empty states, OG cards) with ChatGPT's image model on chatgpt.com, driven in the user's real Chrome where they are signed in, then download each image as a blob and wire it into the repo. Use it when a landing page, dashboard or film needs real generated art instead of CSS placeholders, when someone says "make assets with ChatGPT", or types /chatgpt-assets.
---

# /chatgpt-assets

Real art on a landing page makes it look like a product instead of a template. ChatGPT's image model is the best
one this user has, and their ChatGPT session lives in their real Chrome (Claude in Chrome tools). The in-app
browser pane is logged out, so don't use it.

## 1. Write the art direction first (one per product)

Before any prompt, fix the look in four lines and save them to `docs/ART.md`:

- **Style:** for example "bold manga ink, cel shading, sticker outlines", or "soft isometric clay, matte, studio
  light".
- **Palette:** the product's own brand colours, as hex.
- **Subject vocabulary:** the product's metaphor made literal. A ticket product gets perforated passes; a vault
  product gets a vault door.
- **Banned:** real brands, logos, people and readable text (the model misspells it). No other designers' work,
  so **never upload Dribbble or other reference images** as input.

Products in the same event must not share a style. Check the other products' `docs/ART.md` files.

## 2. The asset set

| Asset | Size to ask for | Notes |
|---|---|---|
| Hero illustration | 1536×1024 (landscape) | the product's metaphor, room for the headline on one side |
| 2–3 floating objects | 1024×1024, **transparent background** | ask for "transparent PNG, no background, no shadow on the ground" |
| Empty state | 1024×1024, transparent | a small, calm version of the metaphor |
| OG / social card | 1536×1024 | no text; the page adds the text |
| App icon / logo mark | 1024×1024 | simple, works at 32 px; check it small |

Put the shared style line at the end of **every** prompt, so the set stays consistent.

## 3. Generate (Claude in Chrome)

1. Load the Chrome tools in one ToolSearch call (`tabs_context_mcp`, `tabs_create_mcp`, `navigate`, `computer`,
   `javascript_tool`, `find`, `tabs_close_mcp`, `browser_batch`).
2. Open `https://chatgpt.com/` in a new tab. Start a fresh chat per product so earlier styles don't bleed in.
3. Send **one image per message**: `Create an image: <subject>. <style line>. <size>. <transparent?>`.
   - Insert long prompts with `document.execCommand('insertText', …)`, as in `/grok-ideation`'s
     `scripts/grok-insert.md`. Then press Return.
   - Each image takes about 1 minute. Take a screenshot to see when it's done; don't poll in a tight loop.
4. **Download as a blob.** The image URL is signed and short-lived, so fetch it from inside the page:

   ```js
   const imgs = [...document.querySelectorAll('img')].filter(i => /generated image/i.test(i.alt) || i.src.includes('oaiusercontent'));
   const src = imgs.at(-1).src;
   const blob = await (await fetch(src)).blob();
   const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: 'noren-hero.png' });
   document.body.appendChild(a); a.click(); a.remove();
   `${blob.type} ${blob.size}`
   ```

   Files land in `~/Downloads`. Name every file `<product>-<asset>.png`.
5. If ChatGPT refuses or hits a rate limit, say so and stop. Never work around a limit, and never solve a CAPTCHA.

## 4. Into the repo

- **Move and convert:**
  ```bash
  mv ~/Downloads/<product>-*.png <repo>/<app>/public/art/
  ```
  - Hero and OG: convert to WebP or JPEG at quality 82–88 (`sips -s format jpeg -s formatOptions 85 in.png --out out.jpg`).
  - Transparent PNGs: keep as PNG and squeeze them with `pngquant` if it is available.
  - Keep each file under about 400 KB.
- **Contact sheet:** look at every image together before wiring it in, for example with
  `ffmpeg -i '%*.png' -filter_complex tile=3x2 sheet.jpg` or `/judge-skill`'s `contact-sheet.py`. Regenerate any
  image that has misspelled text, an extra limb, a cut-off subject or the wrong palette.
- **Wire in with gentle motion:** a float of 2–6 px, or a slow parallax. Switch it off under
  `prefers-reduced-motion`. Give every image width/height or an aspect-ratio box so there is no layout shift. Use
  `alt` text that says what it shows.
- **Credit the tool:** "Art generated with ChatGPT" in the README.

## 5. When the user likes a set, keep it
Once the user approves a style, never swap it for "more premium" glossy 3D on your own. "Premium" means polish
in layout and motion, not new art. If they ask for changes, change only what they named.

## Headless alternative
The Codex CLI's image tool on a ChatGPT plan can generate without a browser. See `/judge-skill`'s
`scripts/assets-codex.sh`. Use it when the Chrome bridge is down.

## 3D object style (Nick, Nov 2026): see the `/3d-illustrations` skill
The full workflow lives in `skills/3d-illustrations/SKILL.md`. Each product gets its OWN colours and material (silver only on request); the notes below are the original chrome reference.

### Original chrome reference
Nick's favourite product-art style, from xoox.fun: **polished chrome or brushed-silver 3D objects**, soft studio light,
crisp reflections, a white or transparent background, one simple object per image (a coin, a stack of cards, a coin
stack on a ring tray), and a tiny friendly face of two soft rounded marks. Use it for launchpads, memecoin and creator
products, especially on a **dark UI**: generate on a transparent background so the silver pops on near-black.
- Prompt line: "Polished chrome / brushed silver 3D render, soft studio lighting, crisp reflections, rounded bevelled
  edges, centred single object, transparent background (no background, no ground shadow), square 1024×1024, no text."
- Make the subject the product's own metaphor (for a comics launchpad: a chrome comic book, a speech-bubble coin, an ink
  pen nib, stacked panels), and give each product its **own** face or mark. Never reuse xoox's mascot face or logo.
