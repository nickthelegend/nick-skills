---
name: grok-ideation
description: Generate and judge hackathon ideas in five rounds using Grok (grok.com, Expert mode, driven in the user's real Chrome) as the idea engine and Claude as the harsh judge. Round 1 fans one shared brief out across 5–10 "lenses" (one Grok chat each); round 2 kills ideas that are fake, taken or off-rules; round 3 sends the survivors back to Grok to sharpen; round 4 re-scores them against the event's real rubric; round 5 picks the winners with a build plan. Use it when someone wants hackathon ideas, asks "what should we build for <event>", wants Grok to brainstorm, or types /grok-ideation.
---

# /grok-ideation

Grok is fast, searches the web, and produces a lot of ideas. It is also generous with its own scores, it invents
competitors, and it renames ideas you already have. So split the roles:

- **Grok generates.**
- **Claude verifies and judges.**
- **The human picks.**

Never hand the final score to Grok.

```
 round 1  fan-out     one shared brief + one lens per Grok chat     -> 5 ideas per lens
 round 2  kill pass   Claude checks facts, rules, prior art          -> survivors + a kill list with reasons
 round 3  sharpen     survivors go back to Grok as a single chat     -> tighter demo, prize fit, risk
 round 4  re-judge    Claude scores each criterion of the rubric     -> scorecard, gaps, fixes
 round 5  pick        the top 1–3, each with a one-page build plan   -> the human approves
```

## Before round 1: write the shared brief

Use [templates/brief.md](templates/brief.md). Fill it **only from the event's own pages**: open them in a
browser (most hackathon sites are JS-rendered; a plain fetch returns an empty shell). It must contain:

- **Deadline, in UTC and in the team's time zone,** with the hours left.
- **Prizes and tracks, with exact amounts from the event page.** Never guess an amount.
- **The rubric, word for word,** plus any submission requirements (mainnet, public repo, video, blog, number of
  on-chain writes, which form fields need which account).
- **The team's hard rules.** Defaults for this user:
  - one chain per project; sponsors must live on that chain;
  - no re-skins of past builds (list them);
  - a product that won on one chain is never ported to another;
  - no mocks, no fake data, real transactions;
  - name every product in Japanese, Greek or Korean.
- **Crowded lanes to avoid,** and the past winners of this event series. Pull these from the event's showcase or
  gallery (see the bottom of the template).
- **The output format:**
  - a name and a 5-second one-liner;
  - which track and prize it targets, and why it qualifies;
  - the demo beat by beat, with the single WOW moment;
  - the nearest prior art, with links;
  - the hardest technical risk;
  - an honest score out of 10.

## Round 1: fan-out across lenses

Write 5–10 lenses (a lens is one angle that forces different ideas). Examples are in
[templates/lenses-example.md](templates/lenses-example.md):
- max prize stacking on one chain;
- one hard verifiable thing;
- a consumer app for a named city;
- a new agent primitive;
- new market types;
- what the sponsor's newest feature makes newly possible.

Send **one Grok chat per lens**, each with the full shared brief plus that one lens line. Use the user's real
Chrome, where they are signed in to grok.com. The in-app browser is logged out.

1. Load the Chrome tools in one ToolSearch call (`tabs_context_mcp`, `tabs_create_mcp`, `navigate`, `computer`,
   `javascript_tool`, `get_page_text`, `tabs_close_mcp`, `browser_batch`).
2. Open `https://grok.com/` in a new tab and check that the mode selector says **Expert**.
3. Insert the prompt with JS. Typing 4,000 characters key by key is slow and breaks on newlines. The full
   call, including the JSON-encoding of the prompt, is in [scripts/grok-insert.md](scripts/grok-insert.md). The same code
   is ready to paste in [scripts/grok-insert.js](scripts/grok-insert.js) (replace `__PROMPT__`), and
   [scripts/grok-read.js](scripts/grok-read.js) reads back only the answer.
4. Press Return. Open the next lens in a new tab while this one works. Grok Expert takes about 20 s to 3 min.
5. Read each answer with `get_page_text`. Save it **verbatim** to `research/<event>/grok-<lens>.md`, together with
   the chat URL. Close your tabs when done.

The `grok` CLI also has a headless mode (`grok --prompt-file brief.md`), but it needs its own login
(`grok login`). If it says "Not signed in", use grok.com.

## Round 2: kill pass (Claude, no Grok)

Check every idea. Kill it, with a one-line reason, if:
- **It's taken.** Search GitHub (`gh search repos "<terms>"`, several phrasings), the event's project gallery,
  the series' past winners and X.
- **It renames an idea you already have.** Grok often hands back the team's own entries with new names.
  Compare against the list of past builds.
- **It breaks a hard rule:** two chains, a re-skin, a sponsor that isn't on that chain, or a demo that needs fake
  data.
- **It rests on a false fact.** Verify every load-bearing claim Grok made: an API that exists, a contract
  address, a competitor's name. Grok has invented competitor projects and stated wrong API facts in our runs.
  Mark anything you couldn't verify as *unverified*.
- **It can't be built in the time left** by this team with AI coding agents.

Write the survivors and the kill list to `research/<event>/IDEAS.md`.

## Round 3: sharpen (Grok)

Send the survivors back to Grok in **one** chat. Include your kill reasons, so it learns what fails. Ask it to
make each survivor's demo moment sharper, tie it harder to the rubric's heaviest criterion, and cut scope to what
ships in the time left. Save the answer verbatim.

## Round 4: re-judge (Claude)

The full honest-judging method (rubric capture, gates, credential sweep, evidence per criterion) is
[/idea-judge](../idea-judge/SKILL.md). Use it here, and on finished builds.

Score each sharpened idea on **each criterion of the event's real rubric**, with the weights. For example
Total Recall: 30% integration, 30% technical, 20% creativity, 20% presentation.

| Idea | Criterion 1 (weight) | Criterion 2 | … | Weighted | Biggest gap | Fix |
|---|---|---|---|---|---|---|

Rules for honest scoring:
- **Score what will exist at the deadline, not the pitch.** Technical and presentation scores assume it ships
  live. If shipping needs keys, money or accounts the team doesn't have yet, say so in the gap column.
- **Don't round up.** A 9 needs evidence: no prior art found, a demo that works live on camera, and an
  integration that is the product, not a bolt-on. Most ideas are 6–7, and saying so is the job.
- **Note what blocks the team.** If the team keeps losing because entries aren't finished (nothing live, never
  submitted), say that plainly. A better idea won't fix an unfinished build.

## Round 5: pick

Present the top 1–3. For each one:
- a one-line pitch a non-crypto judge gets;
- the track and prizes;
- the demo moment;
- the weighted score;
- the build plan: packages, what Codex builds, what Claude designs, and the keys or accounts needed and from whom;
- hours to done.

**Stop and let the human choose.** If they reject everything, don't defend the list. Ask what felt wrong (too
safe? too niche? not fun?), write that into a new lens, and run rounds 1–5 again on it alone.

## Hand-off
The approved idea goes to `/orchestrate` (build, design, assets, judge rounds, film, submit) or straight to a
spec in `specs/<slug>.md`.
