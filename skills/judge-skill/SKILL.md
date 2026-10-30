---
name: judge-skill
description: Judge, fix and film a batch of hackathon products in three rounds that a human approves one at a time. Round 0 has a cheap coding model judge and fix everything except the UI. Round 1 judges every screen at desktop and phone width, adds generated brand art, fixes the UI and publishes a screenshot gallery. Round 2 records one raw, unedited 6–10 minute walkthrough per product. Round 3 cuts each one to about 3 minutes using the human's notes. Use it when someone wants several projects judged, polished and turned into demo videos before a deadline, or types /judge-skill.
---

# /judge-skill

This is the loop we used to take six hackathon entries from "it works on my fork" to submission-ready in one
day, with a human approving each round from a phone between classes. The orchestrator (you) mostly writes
briefs, launches workers, reviews diffs and delivers results. The workers do the heavy lifting.

```
 round 0  judge + fix (non-UI)   cheap coding model, two lanes    -> judging/<repo>.md, commits
 round 1  UI judge + art + fix   one design agent per product      -> shots/round1/<repo>/, a gallery link
 round 2  raw walkthrough        one recording agent per product   -> videos/round2/<repo>-raw.mp4 + chapters
 round 3  the cut                human notes -> ~3 min film         -> the submission video
```

The human judges at the end of rounds 1, 2 and 3. Don't move on to round 3 without their notes.

## Before you start

1. **List the products** and, for each one, its repo path, how to run it locally (dev server, local chain or
   fork, database) and which ports it uses. Give every worker its own port range so no two workers collide.
2. **Write the rules once.** Collect the event's rules (required proof, branding bans, compliance notices,
   deadline) into a few lines. Every brief quotes them.
3. **Put working files on persistent disk**, never in `/tmp` or a scratchpad. A power cut wiped five
   half-finished recordings in our run because they lived in a temp folder.
4. **Budget memory.** On a 16 GB laptop, run 3–4 heavy workers at once (each runs a chain fork, a dev server and
   a browser). Check free memory before starting the next one.

## Round 0: judge and fix everything except the UI

Brief: [briefs/round0-judge-fix.md](briefs/round0-judge-fix.md). Run it with a cheap coding model (we used the
Codex CLI) in two lanes of three repos each, sequentially inside a lane:

```bash
scripts/run-judge-lane.sh repo-a:8545 repo-b:8547 repo-c:8549 &
scripts/run-judge-lane.sh repo-d:8551 repo-e:8553 repo-f:8555 &
```

When each lane finishes, **review before committing**:
- Look for deleted or weakened tests (`git diff --diff-filter=D --name-only`, then the largest test diffs).
  Cheap models delete failing suites to get a green run.
- Look for gutted config or docs (a 300-line `.env.example` cut to 3 lines happened to us; restore it and
  append only the new variables).
- Check that no `.env` or key file is staged, then commit with a message that describes only that diff.

## Round 1: judge every screen, add art, fix, show a gallery

Brief: [briefs/round1-frontend.md](briefs/round1-frontend.md).

1. **Generate brand art first**, one art direction per product, matching each product's own palette:
   - **Set:** hero, 2–3 transparent objects to float, an empty state and an OG card.
   - **Tool:** the Codex CLI's built-in image tool on a ChatGPT plan works headless; see
     [scripts/assets-codex.sh](scripts/assets-codex.sh). Driving chatgpt.com through a browser also works, but it
     breaks whenever the browser bridge does.
   - **Check:** build a contact sheet (`scripts/contact-sheet.py`) and look at every image before using it.
2. **One design agent per product** (a strong model; cheap models produce slop UI). Each agent:
   - runs the product against real data;
   - judges every route at 1440 and 375 and writes a before score;
   - wires in the art with gentle motion that is switched off under `prefers-reduced-motion`;
   - fixes every finding;
   - takes full-page Playwright screenshots of every route at both widths;
   - writes the after score and commits.
3. **Check at five minutes that each agent is actually changing files.** One day every agent sat stuck behind a
   broken tool hook for hours. `git status --short | wc -l` in each repo is enough.
4. **Publish a gallery:**
   - Run `scripts/build-gallery.py` to turn the PNGs into web JPEGs plus a manifest.
   - Make one page with a tab per product, showing desktop and phone side by side and the before → after score.
   - Send the human the link; that page is their round-1 judging surface.

## Round 2: one raw walkthrough per product

Brief: [briefs/round2-raw-video.md](briefs/round2-raw-video.md). Raw means no narration, captions, music,
cuts or speed-ups: a real run of the real product, recorded at 1920×1080 with a visible cursor. The human
cuts it in round 3, so record more than needed (6–10 minutes) with the strongest feature first after a short
landing tour.

- **Run real flows.** Make real transactions through the UI: the core flow end to end, one refused action
  (a guard rail working), the token or fee mechanics with before/after numbers, the phone view, and the
  compliance notice.
- **Write chapters.** Each recording ships with `<repo>-raw.md`, a timestamped chapter list with every
  transaction hash, so the human can pick the cut.
- **Disclose off-camera steps.** Clock jumps, funding and admin calls go in the chapter file.
- **QA before sending.** Build a contact sheet (one frame every 20 s, `ffmpeg -vf fps=1/20,tile=4x4`) and look
  at it: no blank stretches, no dev-error overlays, nothing cut off.
- **Send phone copies.** Chat uploads cap around 30 MB, so re-encode at `-crf 27` without audio and send that
  copy, noting where the full-quality file lives.

## Round 3: the cut

Brief: [briefs/round3-cut.md](briefs/round3-cut.md). Wait for the human's notes on each raw video, then cut it
to about 3 minutes:
- **Open with the problem** in plain words (20–40 s).
- **Show real demos only**, strongest first.
- **Caption one line at a time** and add a focus zoom on whatever the narration names.
- **Badge every scene with its provenance** (`LIVE · local fork`, `REPLAY · <date>`).
- **Never edit a program's real output.** Redact only with a visible box.

## Rules that kept us out of trouble

- **Workers:**
  - Never let a worker push, open secret files, or touch processes or ports it didn't start.
  - Kill everything by PID when done.
  - Each worker reports in under 15 lines. Don't read a worker's full transcript; wait for its report.
- **Delivery:**
  - Deliver as results land, not in one batch at the end.
  - When the human asks for a narrow change ("remove the Japanese name from the header"), change only that.
- **Products in one event:** they must not look like one team made them. Each gets its own fonts, palette and
  layout, and at most one leans on a single cultural motif.
- **Honest numbers:** no mock data, no invented numbers, no fake success. A missing key shows "Setup required",
  and anything that can't be done without the human's account or money is marked BLOCKED with the exact
  action needed.
