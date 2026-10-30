# Round 0 brief: judge and fix one product (everything except the UI)

You are working in ONE repo (the current directory), an entry for **<EVENT>**. Deadline: <DEADLINE>.

## The rules judges apply
<PASTE THE EVENT RULES: required proof (testnet/mainnet txs, video, repo), banned names/logos, required
notices, what the sponsor wants to see used.>

## Step 1: judge first, in writing
Read the README, docs, contracts, server, tests and scripts. Run every test suite and record the counts. Write
`<JUDGING_DIR>/<repo>.md` (outside the repo) with:
- a strict score out of 10 and one line per criterion;
- every finding that costs points, most severe first: bugs; security holes (reentrancy, front-running,
  approvals, oracle or price manipulation, rounding, access control, griefing, DoS); broken or missing tests;
  README claims the code doesn't back up; rule violations; a missing production path;
- for each finding: file:line, the failure scenario and the fix.

## Step 2: fix every non-UI finding
- Fix contracts, server, SDK, scripts, tests and docs, adding a regression test for each bug.
- **Never delete or weaken a test** to get a green run. Report test counts before and after; after must be at
  least before.
- Don't restyle the UI. If a UI file has a logic bug, fix only the logic.
- Tests that touch a chain use real contracts on a local fork. No mocked clients.

## Step 3: production readiness (don't broadcast)
- Add a deploy script that reads its key from an env var in a gitignored `.env`, checks the chain id, prints
  the balances it needs, and dry-runs on a local fork unless an explicit flag says go.
- Add a proof script that performs the transactions the demo video needs and writes every tx hash to
  `deployments/<network>.json`. Dry-run it on a fork now.
- Write a runbook: funding, commands in order, and what each transaction proves.
- The README gets an honest "Live deployments" table ("pending") and a test-count table that matches reality.

## Hard rules
- Don't commit, push or touch `.git`; the orchestrator reviews and commits.
- Never print, open or copy secrets, seeds or `.env` files.
- Use only your assigned ports, and kill everything you start by PID.
- Finish with: score before, findings fixed, findings left and why, test counts before and after, and the
  dry-run tx hashes.
