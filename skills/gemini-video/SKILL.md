---
name: gemini-video
description: Generate short cinematic video clips (hero loops for landing pages, film openers, b-roll for demo videos) with Google's Veo model on gemini.google.com, driven in the user's real Chrome where they are signed in. Covers the prompt, the daily quota, downloading the clip as a blob, encoding it for the web and for films, and keeping Gemini's visible mark. Use it when a landing page or demo film needs a generated motion clip, when someone says "make the video with Gemini", or types /gemini-video.
---

# /gemini-video

Veo makes one roughly 8–10 second, 720p clip per request. It's good for a landing-page hero loop or a
film's opening beat. It is **not** for showing the product working: that footage must be a real screen
recording of the real product (`/judge-skill` round 2).

## Budget first
- The user's plan allows very few Veo clips per day. In our runs a second request on the same day was refused.
  So **plan one clip per product per day**, and write the prompt carefully before sending.
- If Gemini says the limit is reached, report it and move on (use a still from `/chatgpt-assets` instead).
  Never switch accounts and never try to get around it.

## 1. Write the shot
One shot, one idea, no text on screen (the model garbles it), no real brands or people. Template:

```
<camera move>, <subject doing one thing>, <setting>, <light>, <palette as words + hex>, <style>,
8 seconds, seamless loop, no text, no logos, no people's faces
```

Example: "Slow push-in on a paper lantern slowly lighting up in a dark Tokyo alley at night, warm amber glow
(#F5A524) against deep indigo (#14122B), soft film grain, cinematic, 8 seconds, seamless loop, no text, no logos."

Match the product's `docs/ART.md` (from `/chatgpt-assets`), so the clip and the stills look like one brand.

## 2. Generate (Claude in Chrome)
1. Load the Chrome tools in one ToolSearch call (`tabs_context_mcp`, `tabs_create_mcp`, `navigate`, `computer`,
   `javascript_tool`, `find`, `tabs_close_mcp`, `browser_batch`).
2. Open `https://gemini.google.com/app` in a new tab. Pick the video option (Veo) in the composer's tools menu.
   Take a screenshot, find it, and click it. Insert the prompt with `execCommand('insertText', …)` and send.
3. Generation takes a few minutes. Check with a screenshot every minute or so.
4. Download as a blob from inside the page:

   ```js
   const v = [...document.querySelectorAll('video')].at(-1);
   const blob = await (await fetch(v.currentSrc || v.src)).blob();
   const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: '<product>-hero.mp4' });
   document.body.appendChild(a); a.click(); a.remove();
   `${blob.type} ${blob.size}`
   ```

   If the source is a blob or MediaSource URL that won't fetch, use Gemini's own download button instead (find
   it with `find`).

## 3. Encode
- **Web hero loop** (muted autoplay):
  ```bash
  ffmpeg -i in.mp4 -an -vf "scale=1280:-2,fps=30" -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -movflags +faststart hero.mp4
  ```
  Also make a `hero.webm` (`-c:v libvpx-vp9 -crf 36 -b:v 0`) and a poster frame (`-frames:v 1 hero.jpg`).
  Use `<video autoplay muted loop playsinline poster>`, and fall back to the poster under
  `prefers-reduced-motion`.
- **Film b-roll:** scale to 1920×1080 only in the film's own render. Never upscale the web file.

## 4. Honesty
- **Keep Gemini's visible sparkle watermark.** Don't crop, blur or cover it.
- Credit it in the README and in the film's end card, for example "Opening clip generated with Gemini (Veo)".
- Never present a generated clip as product footage or as a real event. A hero loop is mood, not proof.
