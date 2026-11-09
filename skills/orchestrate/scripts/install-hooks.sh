#!/usr/bin/env bash
# Installs the /orchestrate Stop guard into ~/.claude/settings.json (idempotent; backs the file up first).
# The guard is a no-op for every session that hasn't run `orch.py init` or `orch.py resume`, so it's safe
# to keep installed. Remove it with: install-hooks.sh --remove
set -euo pipefail
settings=${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}
cmd='python3 "$HOME/.claude/skills/orchestrate/scripts/orch.py" stop-check'
mode=${1:-install}
[ -f "$settings" ] || echo '{}' > "$settings"
cp "$settings" "$settings.bak-orchestrate"
python3 - "$settings" "$cmd" "$mode" <<'PY'
import json, sys
path, cmd, mode = sys.argv[1:4]
d = json.load(open(path))
stop = d.setdefault("hooks", {}).setdefault("Stop", [])
stop[:] = [g for g in stop if not any("orchestrate/scripts/orch.py" in h.get("command", "") for h in g.get("hooks", []))]
if mode != "--remove":
    stop.append({"hooks": [{"type": "command", "command": cmd, "timeout": 10}]})
if not stop:
    d["hooks"].pop("Stop")
json.dump(d, open(path, "w"), indent=2)
print(("removed" if mode == "--remove" else "installed") + " the /orchestrate Stop guard in " + path)
PY
