# Round 1 brief: judge every screen, add the generated art, polish

A human will judge the UI of every product from screenshots. The UI must look premium and must be distinct from
the other products in the same event: no two may look like one team made them. Don't ask questions; take the
recommended path. Be frugal: use page text and DOM checks for verification, and take full screenshots only for
the deliverable.

## Inputs
- Repo: `<PROJECTS>/<repo>`. The round-0 fixes are already committed; don't change contracts or server logic.
- Generated art for this product in `<WORKSPACE>/assets/<repo>/`: `hero.png`, `obj-*.png` (real alpha),
  `empty.png`, `og.png` and `prompts.md`. Look at each one before using it.
- Your design bar, if you have one written down, at `<YOUR_DESIGN_BAR.md>`. If you keep a library of reference
  shots, pick 3–5 that fit this product and compare against them while you QA.

## Steps
1. **Run it on real data.** Run the product against a local fork or dev backend on your assigned ports, then
   seed it through its own UI or scripts so screens show real data, not just empty states.
2. **Judge every route** at 1440 and 375 like a strict design judge: hierarchy, spacing rhythm, type scale,
   contrast, alignment, density, empty/loading/error states, overflow, tap targets, focus rings, consistency
   and copy length. Write the findings and a before score to `<WORKSPACE>/judging/<repo>-ui.md`.
3. **Integrate the art.**
   - **Placement:** the hero art is the centrepiece. Float 1–3 objects with a slow CSS drift (6–12 s,
     transform/opacity only, off under `prefers-reduced-motion`). Use the empty-state art in empty states and
     the OG card as the OpenGraph image.
   - **Files:** convert to webp, each under about 300 KB, with width, height and alt. Lazy-load anything below
     the fold.
   - **Bad images:** mask or skip any image with a painted checkerboard or a clashing background. Never ship
     text the image invented.
4. **Fix every finding.** Keep the product's own fonts, palette and metaphor. Add 150–250 ms transitions. Show
   real data only, and keep the required legal and compliance notices.
5. **Prove it still works.** Build and lint must pass, and test counts must not go down.
6. **Take the deliverable screenshots** with a small Playwright script, not a browser pane: `fullPage`, wait
   for network idle and fonts, every route at 1440 and 375, plus one key open state such as a modal or sheet.
   Save them as `<WORKSPACE>/shots/round1/<repo>/<nn>-<route>-<1440|375>.png`, numbered in journey order.
7. **Re-judge** and write the after score.
8. **Commit and clean up.**
   - Commit 1–3 commits, each describing only its diff. Don't push.
   - Kill every process you started, by PID.
   - Never open `.env` files.

Report in under 15 lines: score before → after, the biggest fixes, the art used, the commits and the
screenshot folder.
