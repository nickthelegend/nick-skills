---
name: idea-judge
description: Judge hackathon ideas or finished builds honestly yourself, in five rounds, against the event's real rubric. Round 1 captures the rubric, round 2 runs the prior-art kill check, round 3 scores each criterion with evidence, round 4 improves each idea at its weakest criterion, and round 5 re-judges and picks. Never hands judging to another model. Use it inside /grok-ideation's rounds 2 and 4, on finished builds, when someone asks "score this", "which should we build", "is this a 9", or types /idea-judge.
---

# /idea-judge

You are the judge. Not Grok, not a cheaper model, not the idea's own author. The user said it directly:
"judge honestly by yourself." Score low when it's low. A 6 the user hears today beats a loss they learn about
next week.

Write everything to `judging/<event>-ideas.md` (or `judging/<repo>.md` for a build), round by round, so the
user can see how each score moved.

## Round 1: the real rubric
- Copy the event's judging criteria and their **weights**, word for word, from the event page (read it live;
  pages change). If the event gives none, use: impact/need, technical depth, originality, sponsor fit,
  demo/presentation, feasibility before the deadline.
- Add the **gates** that zero an entry no matter how good the idea is:
  - must-haves (mainnet writes, public repo, video, blog post, N on-chain proofs);
  - eligibility (built in the window, entries per team, banned names or countries);
  - one chain only;
  - no re-skin of the team's past builds;
  - not a past winner.
- Write the **credential sweep**: every account, key, faucet, funded wallet and sign-in each idea needs before
  it can run live. Losing streaks in our history came from entries that stayed "BLOCKED: needs a key" until the
  deadline, not from bad ideas.

## Round 2: kill check
For each idea:
- **Prior art.** `gh search repos` with 3–5 phrasings, the event series' showcase, and X. Paste the links. "Not
  found" is recorded as not found, never as "nobody is building this" unless the search was thorough.
- **Platform reality.** Does the SDK, API or chain feature actually work today, on the network the event
  requires, at the price the team can pay? Make one real call or read the docs page.
- **Gates.** Fail any gate and the idea dies here, with the reason.

## Round 3: score each criterion with evidence
One table per idea: criterion | weight | score 0–10 | the evidence | the gap that costs points.
- Score the **idea as it would ship by the deadline**, not as it could be with a month.
- "Technical quality" can't exceed 7 for anything not yet built, unless the hard part is already proven.
- "Presentation" scores the 2-minute demo moment: what a non-technical judge *sees change* on screen, live.
- Weighted total to one decimal. Don't round up.

## Round 4: improve
For each surviving idea, attack its **weakest criterion**:
- low need → find who complains about it (links);
- low originality → the twist that no prior-art hit has;
- weak sponsor fit → make the sponsor load-bearing;
- weak demo → design the moment the product visibly changes, on real data;
- feasibility → cut scope to one loop that works live.

Write the improved version as a new row; never edit the round-3 row.

## Round 5: re-judge and pick
- Re-score the improved versions with the same rubric, in a fresh pass. Assume you are a judge who has seen 100 entries today.
- Rank them. For the top pick, write:
  - the one-line pitch;
  - the demo beat sheet (≤ 2 minutes);
  - the build plan by hour;
  - the credential sweep;
  - the single biggest risk and its fallback.
- Show the user the before → after scores and your recommendation. If nothing reaches 7.5, say so, and say what would get one there.

## Honesty rules
- Nobody can promise a 9 on every criterion before it's built and filmed; say that instead of inflating.
- Name the weakness first. The user asked to be told plainly when an idea is bad ("if I'm wrong, hurt me").
- Never present a competitor, a number, a prize amount or a platform claim you didn't verify.
- When judging a finished build, run it: judge what is on screen and on chain today, not the README.
