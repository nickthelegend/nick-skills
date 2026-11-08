# Codex brief: <product> / <slice>

Repo: `<absolute path>`. Work on `main`. <Either: "Commit after each working step; message describes only its
diff and ends with `Co-Authored-By: ...`" or "Do not commit; leave changes in the working tree".> Never push.

## Goal (one paragraph)
<what this slice must do, and how we'll know it works>

## Hard rules
- No mocks of external APIs and no fake data. Tests that touch a chain or API use the real one. Pure logic may
  use fixtures saved from real responses (with their IDs).
- Fail loudly: a missing key shows "Setup required: <VAR>" in the API and the UI. Never pretend success.
- Never print, copy or open secrets. Read keys from `.env` by variable name only.
- No mainnet transactions and no real money. Local chain or testnet only.
- Use only ports <range>. Kill every process you start, by PID, before you finish.
- Don't restyle the UI (the orchestrator owns design); keep structure in components, CSS minimal.
- Don't delete or weaken tests to get green. If a test is wrong, say why in the report.
- One chain: <chain>. Don't add a second one.

## Interfaces to honour
<types, endpoints, contract ABIs, env var names>

## Done means
<commands that must pass>, plus a report of 15 lines or fewer: what works live, what's blocked and on what, and the test counts.
