# Round 3 brief: cut the raw walkthrough into a ~3 minute submission film

Inputs: `<repo>-raw.mp4`, its chapter list, and the human's notes from watching it. The notes win over
everything below.

## Shape
1. **Problem in plain words (20–40 s).** A judge who knows nothing about the field must get it. Then say what
   the product does in one line.
2. **The strongest feature first**, live from the raw take, then the rest in the order the notes ask for.
3. **Close** with what is real (tx hashes, test counts) and what's next, in one card.

## Craft
- **Captions:** one short line at a time. A voiceover is optional; if used, check every line with a speech
  recognizer and rephrase anything it mishears.
- **Zooms:** 1–3 focus zooms per scene on the thing the narration names (a refused line, a hash, a counter),
  with the zoomed text fully inside the frame.
- **Provenance:** a badge on every demo scene, e.g. `LIVE · local fork of <chain>` or `REPLAY · recorded <date>`.
- **Honesty:** never text-edit a program's real output. Redact only with a visible box. Cut dead waits;
  speed-ups carry an on-screen "sped up Nx" badge.
- **Look:** use the product's own fonts, palette and art. Each product's film looks different.

## QA
Build a contact sheet (one frame every 4 s) and look at all of it:
- text is readable and zooms are framed;
- badges don't cover content and captions never overlap;
- no frozen stretch runs over ~6 s, and no UI is stale.

Fix and re-render until it's clean. Ship an mp4 under the event's size limit, plus a phone copy under 30 MB.
