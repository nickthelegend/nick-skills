---
name: orchestrate
description: Run a whole hackathon entry end to end as an agentic harness. Steps: read the event; sweep for credentials on day one; ideate with /grok-ideation; judge with /idea-judge; hand coding to Codex workers; build the UI with /dribbble-frontend; generate art with /chatgpt-assets and clips with /gemini-video; judge, polish and film with /judge-skill; package the submission. State lives in a file so any session can resume. Use it when someone says "do it all", "run the pipeline", names a hackathon and wants an entry, or types /orchestrate.
---

# /orchestrate

You are the conductor. The workers do the heavy lifting:
- **Codex** writes code.
- **You** do the design, film, copy and review.
- **Grok** scouts ideas.
- **ChatGPT and Gemini** make art.

Your job:
- keep `STATE.md` true;
- launch and check workers;
- review every diff;
- deliver results the moment they land;
- stop only at the gates that belong to the human.

```
 phase 0  intake           event page -> RULES.md, credential sweep (ask the human for keys NOW)
 phase 1  ideate           /grok-ideation rounds + lenses -> IDEAS.md (verified)
 phase 2  judge ideas      /idea-judge 5 rounds -> pick           [GATE: human picks, unless "no stops"]
 phase 3  build            spec -> Codex briefs -> workers -> review -> commit -> push
 phase 4  look             /dribbble-frontend (you, never Codex) + /chatgpt-assets + /gemini-video
 phase 5  prove live       testnet/mainnet runs, real tx links, TESTING.md counts   [GATE: keys/money]
 phase 6  judge + film     /judge-skill rounds 0-3 -> the ~3 min film           [GATE: human notes]
 phase 7  submit pack      SUBMISSION.md, README, repo public, post text        [GATE: human submits]
```

## Phase 0: intake (never skip; this is where we kept losing)
1. Read the event page live in a browser. Pages are often JS-rendered and dates move. Fill
   [templates/RULES.md](templates/RULES.md) with:
   - the deadline in UTC **and** the user's time zone;
   - the rubric with its weights;
   - the must-haves;
   - entries per team;
   - prize amounts copied exactly (never guess);
   - bans (names, logos, countries);
   - "built in window" rules.
2. **Credential sweep, the same hour.** List every account, API key, funded wallet, faucet, sign-in and
   public-repo approval the entry will need before it can run live. Send that list to the human
   immediately, as one short checklist with links.
   - Our losing streak came from entries stuck at "BLOCKED: needs a key" or "never submitted", not from weak
     ideas.
   - Keys go in gitignored `.env` files by variable name. Never print, copy or open them.
3. Create [templates/STATE.md](templates/STATE.md) in the work folder. Update it at every phase change. A new session resumes by reading `STATE.md` first.

## Phase 1–2: ideas
- Run **/grok-ideation**, then **/idea-judge**. Present the top 3 with honest before → after scores, and recommend one.
- **Gate:** the human picks, unless they said "no stops" (then take your recommendation and say so).
- If they reject the batch, change the lens, not the wording.
- Respect the standing constraints:
  - one chain per project;
  - no re-skins of past builds;
  - a product that won on one chain stays there;
  - several products in one event must not look like one team made them.

## Phase 3: build with Codex workers
1. Write `specs/<slug>.md` with:
   - the one-line pitch;
   - the demo beat sheet;
   - the architecture;
   - the gates (what must be live).
2. Split coding into worker briefs from [templates/codex-brief.md](templates/codex-brief.md). Each brief carries the
   hard rules: no push, no secrets, no mainnet, no mocks of external APIs, fail loudly with "Setup required",
   kill processes by PID, its own ports, and "don't restyle the UI".
3. Launch with [scripts/codex-run.sh](scripts/codex-run.sh) `<repo> <brief.md>`. It runs in the background,
   logs to `<work>/codex/logs/`, and uses `-m gpt-6-sol`.
   - Run at most 2–3 heavy workers at once on a 16 GB laptop.
   - Codex may refuse security-flavoured work (attack tests); do those yourself.
4. **Five-minute check:** `scripts/check-workers.sh <repo>…` shows changed-file counts and the last log lines.
   A worker with no changes at five minutes is stuck. Kill it and re-brief it.
5. **Review before every commit:**
   - deleted or weakened tests (`git diff --diff-filter=D --name-only`);
   - gutted `.env.example` or docs;
   - staged secrets;
   - fake data.
   Then commit with a message that describes only that diff, and push right away if the repo has a remote
   (a laptop shutdown once cost work). Don't ask again; the human approved pushing for their own repos.
6. Give every product a brandable name (Japanese, Greek or Korean; never descriptive) and an MIT license under the
   human's name.

## Phase 4: make it look like a real product
- Build the UI yourself with **/dribbble-frontend**: references picked at random, its own archetype, fonts
  and palette, QA at 375 px and 1440 px, and only live data, empty states or "Setup required".
- Generate the art with **/chatgpt-assets**, plus one **/gemini-video** clip if the landing earns it. Credit both tools.
- Agents are chat-driven: a real tool-calling model with visible tool calls and guardrails that refuse on
  camera, never a "do the thing" button.

## Phase 5: prove it live
- Deploy where the rules demand it. Prefer local chains for development, then the required network for the proof.
- **Gate:** real money or mainnet spend needs the human's explicit yes, with an amount.
- Record every transaction hash with an explorer link in the README's deployment table.
- Write `TESTING.md` from real runs: counts, dates, what's skipped and why.
- Anything still impossible becomes `BLOCKED.md`, naming the exact credential or action needed and who must do it.

## Phase 6: judge and film
Run **/judge-skill**:
- Round 0: non-UI fixes.
- Round 1: UI gallery.
- Round 2: a raw walkthrough of the live product.
- Round 3: the cut, using the human's notes.

The film's format:
- the problem in plain words first (20–40 s), then only live demos, strongest first;
- full-width app screens;
- one-line captions;
- speed badges on sped-up footage;
- explorer proof for anything on chain.

Never edit a program's real output; redact with a visible box.

## Phase 7: submit pack
- `HACKATHON_SUBMISSION_FORM.md`: every field the form asks, filled from facts.
- README: what it is, try-it steps, the live deployment table, AI and library disclosure, a link to the film.
- Run a secret scan, then make the repo public. Some events need a topic or an invited judge account.
- Write the post text for X or LinkedIn if the event rewards it.
- **Gate:** the human submits, signs in and posts. Hand them a 3-line checklist with links and the deadline in their time zone.
- After submitting: never delete a submitted video. Upload a new version of the same file so the link stays.

## Delivery rules
- Deliver each result as it lands (a gallery link, a film, a live URL), not in one batch at the end.
- Report in plain words: what's done, what's live (with links), what only the human can do, and by when.
- Give honest pushback. If an entry won't be live by the deadline, say so early and propose the cut that makes it live.
