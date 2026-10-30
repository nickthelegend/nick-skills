# Round 2 brief: one raw walkthrough recording per product, unedited

A human judges a raw screen recording of each product being driven end to end, then cuts it to about 3 minutes
in round 3. So record more than needed: 6–10 minutes that show every feature that can win, strongest first after
a short landing tour. No narration, captions, music, cuts, speed-ups or edits of any kind. It must be a real
run of the real product.

## Setup
- **Repo:** `<PROJECTS>/<repo>`. Don't change product code unless a real bug blocks the walkthrough; then fix it
  minimally and commit it.
- **Stack:** run the real stack on your assigned ports with a production build, so no dev overlay appears.
  Every on-chain or backend action in the video is real and made through the product UI.
- **Work folder:** keep every working file (recorder script, logs, pid files, webm) in
  `<WORKSPACE>/videos/round2/work/<repo>/`. Persistent disk survives reboots; temp folders don't.
- **Recorder:** Playwright (`<PLAYWRIGHT_DIR>`), one context with
  `recordVideo: { size: { width: 1920, height: 1080 } }` and a 1920x1080 viewport.
  - **Cursor:** inject a visible cursor dot and a click ripple.
  - **Pace:** move along smooth paths, type at human speed, hover before clicking, scroll smoothly, and pause
    2–4 s on each result.
- **What to show:**
  - the landing and its animation;
  - the core flow end to end (twice if the second run shows something new);
  - every secondary screen;
  - one refused action (a guard rail working);
  - the product's key mechanic with before and after numbers;
  - about 30 s of the phone view: render the app at 390x844 in a centred, scaled frame so it fills the shot;
  - the legal or compliance notice.

## Output
- **Video:** H.264 mp4 (`-c:v libx264 -crf 20 -pix_fmt yuv420p`, 1920x1080, real timing) at
  `<WORKSPACE>/videos/round2/<repo>-raw.mp4`.
- **Chapters:** `<WORKSPACE>/videos/round2/<repo>-raw.md` lists `mm:ss → what happens`, with every tx hash
  and every off-camera step (clock jumps, funding, admin calls).
- **QA:** take one frame every 20 s (`ffmpeg -vf fps=1/20,scale=640:-1,tile=4x4`) and look at it. Re-record if
  it has blank stretches over ~8 s, error overlays or cut-off content.
- **Cleanup:** delete the webm after verifying the mp4, and kill everything you started by PID.

Report in under 12 lines: the mp4 path, its duration, the chapter highlights, and anything that couldn't be
shown and why.
