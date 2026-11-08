# nick-skills

Claude Code skills from a solo builder who ships to hackathons every week. They're the working loops behind six
hackathon entries judged, polished and filmed in one day, with the human approving each round from a phone.

## The pipeline

```
 /orchestrate        does it all: intake -> ideas -> judge -> build -> look -> live proof -> film -> submit
   /grok-ideation      Grok Expert (grok.com in your Chrome) generates; Claude kills, sharpens, re-judges: 5 rounds
   /idea-judge         honest self-judging against the event's real rubric, for ideas and finished builds
   /dribbble-frontend  UI built from randomly picked, studied Dribbble references; QA at 375 px and 1440 px
   /chatgpt-assets     brand art from ChatGPT images (chatgpt.com in your Chrome), downloaded as blobs
   /gemini-video       hero loops and film openers from Veo (gemini.google.com in your Chrome)
   /judge-skill        judge, polish and film a batch of products in rounds the human approves
```

| Skill | Use it for |
|---|---|
| [orchestrate](skills/orchestrate/SKILL.md) | One command for a whole entry. Keeps `STATE.md` so any session can resume; Codex workers write code ([scripts/codex-run.sh](skills/orchestrate/scripts/codex-run.sh), five-minute [check-workers.sh](skills/orchestrate/scripts/check-workers.sh)); stops only at the human's gates (pick, keys/money, film notes, submit). |
| [grok-ideation](skills/grok-ideation/SKILL.md) | Ideas in five rounds: fan-out across lenses, kill pass, sharpen, re-judge, pick. Grok never gives the final score. |
| [idea-judge](skills/idea-judge/SKILL.md) | Five-round honest judge: rubric and gates, prior-art kill check, evidence per criterion, improve the weakest, re-judge. |
| [dribbble-frontend](skills/dribbble-frontend/SKILL.md) | Seeded random picks from your own private reference library (`DRIBBBLE_LIB`), notes on what to take, distinct look per product. Library images are never shipped. |
| [chatgpt-assets](skills/chatgpt-assets/SKILL.md) | Art direction, the asset set, blob download, contact-sheet check, web sizes. |
| [gemini-video](skills/gemini-video/SKILL.md) | One careful Veo clip per day, blob download, web encode, keep the Gemini mark. |
| [judge-skill](skills/judge-skill/SKILL.md) | Rounds 0–3 for a batch: non-UI fixes, UI gallery, raw walkthrough, the cut. |

The browser skills drive **your real Chrome** through Claude in Chrome, because that is where your ChatGPT,
Gemini and Grok sign-ins live. They never sign in, create accounts or solve CAPTCHAs for you.

## /judge-skill

Judge, fix and film a whole batch of products in rounds that a human signs off one at a time.

```
 round 0  judge + fix (non-UI)   cheap coding model, two lanes    -> scorecards + commits
 round 1  UI judge + art + fix   one design agent per product      -> every screen at 1440 and 375, one gallery link
 round 2  raw walkthrough        one recording agent per product   -> a 6–10 min unedited take + chapter list
 round 3  the cut                the human's notes -> ~3 min film   -> the submission video
```

### Round 1: every screen judged, generated art wired in, then a gallery

![Six products after round 1, desktop](docs/images/round1-desktop.jpg)

The same pass at phone width:

![Phone screens after round 1](docs/images/round1-phones.jpg)

Each product gets its own art direction, generated headlessly with the Codex CLI's image tool:

![Generated brand art, six products](docs/images/generated-art.jpg)

### Round 2: one raw take per product

A real run of the real product, made through its UI, with a visible cursor. There's no narration and no cuts.
It ships with a chapter list of every transaction, so the human picks the cut.

![Frames from a raw walkthrough](docs/images/round2-raw-frames.jpg)

## Install

```bash
git clone https://github.com/nickthelegend/nick-skills
for s in nick-skills/skills/*/; do ln -sfn "$PWD/$s" ~/.claude/skills/$(basename "$s"); done
```

Then, in Claude Code: `/orchestrate <event url>`, or any single skill (`/grok-ideation`, `/judge-skill`, ...).
For `/dribbble-frontend`, set `DRIBBBLE_LIB` to your own reference folder and run
`python3 ~/.claude/skills/dribbble-frontend/scripts/pick.py write-categories` once.

Needs: Claude Code with Claude in Chrome (for Grok, ChatGPT and Gemini); the [Codex CLI](https://github.com/openai/codex) for coding workers and headless art; Playwright and ffmpeg
for screenshots and recordings; Python 3 with Pillow for the gallery and contact sheets.

## What's inside

| Path | What it is |
|---|---|
| [skills/judge-skill/SKILL.md](skills/judge-skill/SKILL.md) | The loop, round by round, with the rules that kept it safe |
| [skills/judge-skill/briefs/](skills/judge-skill/briefs/) | Worker briefs for rounds 0–3, with placeholders for your paths and event rules |
| [skills/judge-skill/scripts/](skills/judge-skill/scripts/) | Codex judge lanes, headless art generation, contact sheets, gallery builder |

## Lessons baked in

- **Check every worker at five minutes.** One day a broken tool hook left every agent stuck for hours and
  nobody noticed. A one-line `git status` per repo would have caught it.
- **Keep working files on persistent disk.** A power cut wiped five half-finished recordings that lived in a
  temp folder.
- **Review cheap-model diffs for deleted tests and gutted config.** It happened to us twice in one day.
- **Hold to 3–4 heavy workers on 16 GB.** Each runs a chain fork, a dev server and a browser.
- **Keep same-event products distinct.** They should never look like one team made them.
- **Do the credential sweep on day one.** Our losses came from entries stuck at "needs a key" or never submitted,
  not from weak ideas. Ask for every key, wallet and sign-in the hour you read the rules.
- **Grok generates; Claude judges.** Grok invented competitors, misstated APIs and renamed our own products as
  "new" ideas. Verify every claim before it reaches the human.

## License

MIT © 2026 Nivesh Gajengi
