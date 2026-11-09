#!/usr/bin/env python3
"""orch.py - the /orchestrate run loop: a task graph per hackathon run, plus the Stop-hook gate.

A run lives in <work>/orchestrate/run.json and is rendered to <work>/STATE.md after every change.
The session that runs `init` or `resume` is bound to the run (~/.claude/orchestrate/sessions.json).
While that session has runnable tasks, the Stop hook (`orch.py stop-check`) refuses to let it end
its turn and tells it the next task. It may stop only when every open task is waiting on a background
worker or on the human.

  orch.py init   --work DIR --event NAME [--url URL] [--deadline 2026-11-10T17:00Z] [--products a,b]
                 [--template full|mini] [--mode autopilot|gated]
  orch.py resume --work DIR            bind this session to an existing run
  orch.py next   [--all]               the next runnable task, with its skill and done-criteria
  orch.py start  ID
  orch.py done   ID --evidence "commit abc123 / URL / path"   (evidence is required)
  orch.py block  ID --needs "WALRUS_ACCOUNT_ID from the Walrus dashboard" [--who human|external]
  orch.py unblock ID
  orch.py skip   ID --why "..."
  orch.py worker ID --pid PID [--log PATH]   the task waits on a background worker
  orch.py add    --product P --phase N --title "..." [--skill S] [--done-when "..."] [--after ID,~ID]
  orch.py status
  orch.py pause | unpause | finish
  orch.py stop-check                   (Stop hook; reads the hook JSON on stdin)

Deps: "ID" must be done or skipped; "~ID" (soft) is also satisfied when ID is blocked, so work routes
around a missing key instead of stopping.
"""
import argparse, datetime as dt, hashlib, json, os, re, sys

HOME_DIR = os.path.expanduser("~/.claude/orchestrate")
SESSIONS = os.path.join(HOME_DIR, "sessions.json")
MAX_IDLE_BLOCKS = 3  # Stop-hook blocks with no state change before we let the session stop

PHASES = {0: "intake", 1: "ideate", 2: "judge ideas", 3: "build", 4: "look", 5: "prove live",
          6: "judge + film", 7: "submit"}

# (key, phase, title, skill, done_when, deps, who)  - deps refer to keys; "E:" = event-level task
EVENT_TASKS = [
    ("rules", 0, "Read the event page live; fill RULES.md (deadline UTC + IST, rubric with weights, must-haves, entries per team, prize amounts copied, bans, built-in-window rule)",
     "browser", "RULES.md has every field filled from the live page, with the URL", [], "claude"),
    ("creds", 0, "Credential sweep: list every key, account, funded wallet, faucet and sign-in each entry needs; write CREDENTIALS.md and PushNotification the checklist to the human NOW",
     "PushNotification", "CREDENTIALS.md exists and the notification was sent; missing items become `block` tasks", ["rules"], "claude"),
    ("ideate", 1, "Ideate with /grok-ideation (skip with `skip` if the human already named the products)",
     "/grok-ideation", "IDEAS.md with verified survivors", ["rules"], "claude"),
    ("pick", 2, "Judge with /idea-judge and PICK. Autopilot: take your own recommendation, record why in STATE.md, tell the human, keep going",
     "/idea-judge", "the pick is written in STATE.md Decisions; `add`-ed product tasks exist (use `orch.py add-product`)", ["ideate"], "claude"),
]

PRODUCT_TASKS = [
    ("spec", 3, "Write specs/<slug>.md: pitch, 2-min demo beat sheet, architecture, what must be live", "", "spec file exists", ["E:pick"], "claude"),
    ("repo", 3, "Repo: monorepo packages/*, MIT (Copyright (c) 2026 Nivesh Gajengi), .env.example, gitignored .env, private GitHub remote, first push", "gh", "repo path + remote URL", ["spec"], "claude"),
    ("brief", 3, "Split the build into Codex briefs from templates/codex-brief.md (one per slice, own ports)", "", "brief files listed", ["repo"], "claude"),
    ("code", 3, "Launch Codex workers with scripts/codex-run.sh using Bash run_in_background:true (so you are woken when each ends); `orch.py worker` each", "codex", "every brief's worker finished", ["brief"], "claude"),
    ("review", 3, "Review every worker diff (deleted tests, gutted docs, secrets, fake data), run the tests, commit per diff, push", "", "commits pushed; test command output green", ["code"], "claude"),
    ("ui", 4, "Build the UI yourself with /dribbble-frontend (seeded picks, own palette/type, live data or Setup-required states only)", "/dribbble-frontend", "picks logged; app runs", ["repo"], "claude"),
    ("art", 4, "Generate the art set with /chatgpt-assets (docs/ART.md first) and wire it in", "/chatgpt-assets", "files in public/art + contact sheet checked", ["spec"], "claude"),
    ("clip", 4, "One hero clip with /gemini-video if the landing earns it (skip otherwise, with why)", "/gemini-video", "hero.mp4/webm/jpg wired in, Gemini mark kept", ["art"], "claude"),
    ("qa", 4, "QA at 375px and 1440px next to the references; fix overflow, focus, empty/error states", "/dribbble-frontend", "screenshots + QA note in picks log", ["ui", "~art", "review"], "claude"),
    ("live", 5, "Deploy where the rules demand; real tx hashes + explorer links in the README deployment table (mainnet spend = block for the human's yes with an amount)", "", "deployment table with links", ["review"], "claude"),
    ("testing", 5, "TESTING.md from real runs: counts, dates, skipped and why", "", "TESTING.md committed", ["review"], "claude"),
    ("judge", 6, "Judge the BUILD with /idea-judge round 3-5 on what runs today; fix the weakest criterion", "/idea-judge", "judging/<repo>.md with scores and fixes committed", ["qa", "~live"], "claude"),
    ("gallery", 6, "/judge-skill round 1: UI gallery (desktop + phone) published", "/judge-skill", "gallery link", ["judge"], "claude"),
    ("walk", 6, "/judge-skill round 2: raw live walkthrough recording of the real product", "/judge-skill", "recording path", ["gallery", "~live"], "claude"),
    ("film", 6, "Cut the ~3 min film (problem first, live demos, captions, explorer proof) with /hyperframes; send it", "/hyperframes", "film path sent with SendUserFile", ["walk"], "claude"),
    ("pack", 7, "HACKATHON_SUBMISSION_FORM.md, README (try-it, deployment table, AI disclosure, film link), post text", "", "files committed and pushed", ["film", "testing"], "claude"),
    ("public", 7, "Secret scan; then make the repo public (ask the human once, via block, if not pre-approved)", "gh", "repo URL public", ["pack"], "claude"),
    ("submit", 7, "HUMAN: submit the form, sign in, post. Hand them a 3-line checklist with links and the deadline in IST", "PushNotification", "human confirms submitted", ["public"], "human"),
]

MINI_EVENT = [("rules", 0, "Write RULES.md with one line", "", "RULES.md exists", [], "claude")]
MINI_PRODUCT = [
    ("spec", 3, "Write spec.txt", "", "spec.txt exists", ["E:rules"], "claude"),
    ("code", 3, "Write code.txt", "", "code.txt exists", ["spec"], "claude"),
    ("ship", 7, "Write ship.txt", "", "ship.txt exists", ["code"], "claude"),
]


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "x"


def session_id():
    return os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID") or ""


def load_json(p, default):
    try:
        with open(p) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=1)
    os.replace(tmp, p)


def run_path(work):
    return os.path.join(work, "orchestrate", "run.json")


def find_work(arg):
    if arg:
        return os.path.abspath(arg)
    if os.environ.get("ORCH_WORK"):
        return os.path.abspath(os.environ["ORCH_WORK"])
    sid = session_id()
    w = load_json(SESSIONS, {}).get(sid, {}).get("work") if sid else None
    if w:
        return w
    d = os.getcwd()
    while d != "/":
        if os.path.exists(run_path(d)):
            return d
        d = os.path.dirname(d)
    sys.exit("orch: no run found. Pass --work DIR, set ORCH_WORK, or run `orch.py init`.")


def bind(work, sid):
    if not sid:
        print("orch: warning - no CLAUDE_CODE_SESSION_ID; the Stop guard can't bind this session.", file=sys.stderr)
        return
    s = load_json(SESSIONS, {})
    s[sid] = {"work": work, "bound": now(), "idle_blocks": 0, "last_hash": ""}
    save_json(SESSIONS, s)


def unbind_all(work):
    s = load_json(SESSIONS, {})
    s = {k: v for k, v in s.items() if v.get("work") != work}
    save_json(SESSIONS, s)


def mk(tid, product, phase, title, skill, done_when, deps, who):
    t = {"id": tid, "product": product, "phase": phase, "title": title, "skill": skill,
         "done_when": done_when, "deps": deps, "who": who, "status": "todo", "notes": []}
    if who == "human":
        t["status"] = "blocked"
        t["needs"] = "the human does this step"
    return t


def product_tasks(run, product, template):
    p = slugify(product)
    for key, ph, title, skill, dw, deps, who in template:
        d2 = []
        for d in deps:
            soft = d.startswith("~")
            d = d.lstrip("~")
            ref = d[2:] if d.startswith("E:") else f"{p}.{d}"
            d2.append(("~" if soft else "") + ref)
        run["tasks"].append(mk(f"{p}.{key}", p, ph, title.replace("<slug>", p), skill, dw, d2, who))
    if p not in run["products"]:
        run["products"].append(p)


def load(work):
    r = load_json(run_path(work), None)
    if r is None:
        sys.exit(f"orch: no run at {run_path(work)}")
    return r


def by_id(run, tid):
    for t in run["tasks"]:
        if t["id"] == tid:
            return t
    sys.exit(f"orch: no task {tid}. Ids: " + ", ".join(t["id"] for t in run["tasks"]))


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (ProcessLookupError, ValueError, TypeError):
        return False
    except PermissionError:
        return True


def deps_ok(run, t):
    st = {x["id"]: x["status"] for x in run["tasks"]}
    for d in t["deps"]:
        soft = d.startswith("~")
        s = st.get(d.lstrip("~"), "done")
        if s in ("done", "skipped") or (soft and s == "blocked"):
            continue
        return False
    return True


def classify(run):
    """runnable: Claude can act now. waiting: a live background worker. human: blocked on someone else."""
    runnable, waiting, human, dead = [], [], [], []
    for t in run["tasks"]:
        s = t["status"]
        if s in ("done", "skipped"):
            continue
        if s == "blocked":
            human.append(t)
        elif s == "waiting":
            (waiting if pid_alive(t.get("pid")) else dead).append(t)
        elif s == "doing" or (s == "todo" and deps_ok(run, t)):
            runnable.append(t)
    runnable.sort(key=lambda t: (t["status"] != "doing", t["phase"], run["tasks"].index(t)))
    return runnable, waiting, human, dead


def render(work, run):
    runnable, waiting, human, dead = classify(run)
    L = [f"# Orchestrate state: {run['event']}  (read me first when resuming)", "",
         f"Deadline: {run.get('deadline') or 'unknown - fill from RULES.md'}. Mode: {run['mode']}"
         f"{' (PAUSED)' if run.get('paused') else ''}. Updated: {now()}.",
         f"Event page: {run.get('url') or '-'}", "",
         "Loop: `orch.py next` -> do it -> `orch.py done ID --evidence ...` (or `block`). The Stop hook won't let",
         "the bound session end its turn while a task is runnable.", ""]
    total = len(run["tasks"])
    fin = sum(t["status"] in ("done", "skipped") for t in run["tasks"])
    L += [f"Progress: {fin}/{total} done. Runnable now: {len(runnable)}. Waiting on workers: {len(waiting)}."
          f" Waiting on the human: {len(human)}.", ""]
    if dead:
        L += ["**Worker finished - review it:** " + ", ".join(t["id"] for t in dead), ""]
    L += ["| Task | Phase | Status | What | Evidence / blocked on |", "|---|---|---|---|---|"]
    for t in run["tasks"]:
        ev = t.get("evidence") or (("NEEDS: " + t["needs"]) if t["status"] == "blocked" else "") or t.get("why", "")
        if t["status"] == "waiting":
            ev = f"worker pid {t.get('pid')} log {t.get('log', '-')}"
        title = t["title"] if len(t["title"]) < 90 else t["title"][:87] + "..."
        L.append(f"| {t['id']} | {t['phase']} {PHASES.get(t['phase'], '')} | {t['status']} | {title} | {ev} |")
    if human:
        L += ["", "## Asked the human (waiting)"] + [f"- {t['id']}: {t.get('needs')}" for t in human]
    L += ["", "## Decisions"] + ([f"- {d}" for d in run.get("decisions", [])] or ["- none yet"])
    with open(os.path.join(work, "STATE.md"), "w") as f:
        f.write("\n".join(L) + "\n")


def save(work, run):
    save_json(run_path(work), run)
    render(work, run)


def show(t, full=True):
    s = f"{t['id']}  [phase {t['phase']} {PHASES.get(t['phase'], '')}]  {t['title']}"
    if full:
        if t.get("skill"):
            s += f"\n  use: {t['skill']}"
        s += f"\n  done when: {t['done_when']}"
        if t.get("notes"):
            s += "\n  notes: " + " | ".join(t["notes"][-3:])
    return s


def cmd_init(a):
    work = os.path.abspath(a.work)
    if os.path.exists(run_path(work)) and not a.force:
        sys.exit(f"orch: a run already exists at {work}. Use `resume`, or --force to start over.")
    os.makedirs(os.path.join(work, "orchestrate"), exist_ok=True)
    run = {"event": a.event, "url": a.url, "deadline": a.deadline, "mode": a.mode, "created": now(),
           "products": [], "tasks": [], "decisions": [], "template": a.template}
    ev, pr = (MINI_EVENT, MINI_PRODUCT) if a.template == "mini" else (EVENT_TASKS, PRODUCT_TASKS)
    for key, ph, title, skill, dw, deps, who in ev:
        run["tasks"].append(mk(key, "event", ph, title, skill, dw, deps, who))
    products = [p for p in (a.products or "").split(",") if p.strip()]
    for p in products:
        product_tasks(run, p.strip(), pr)
    if products and a.template != "mini":
        for t in run["tasks"]:
            if t["id"] in ("ideate", "pick"):
                t["status"] = "skipped"
                t["why"] = "products named at init: " + ", ".join(products)
    save(work, run)
    bind(work, session_id())
    print(f"orch: run '{a.event}' at {work} ({len(run['tasks'])} tasks), bound to session {session_id() or '?'}")
    cmd_next(argparse.Namespace(work=work, all=False))


def cmd_resume(a):
    work = find_work(a.work)
    run = load(work)
    bind(work, session_id())
    run.pop("paused", None)
    save(work, run)
    print(f"orch: resumed '{run['event']}' at {work}, bound to session {session_id() or '?'}")
    cmd_next(argparse.Namespace(work=work, all=False))


def cmd_next(a):
    work = find_work(a.work)
    run = load(work)
    runnable, waiting, human, dead = classify(run)
    for t in dead:
        print(f"REVIEW: worker for {t['id']} has exited -> read {t.get('log', 'its log')}, review the diff, then `done`/`block`.")
    if runnable:
        print("NEXT: " + show(runnable[0]))
        if a.all and len(runnable) > 1:
            print("\nalso runnable (do in parallel via subagents/workers where independent):")
            for t in runnable[1:]:
                print("  - " + show(t, False))
    elif dead:
        pass
    elif waiting:
        print("WAIT: only background workers are running (" + ", ".join(t["id"] for t in waiting) +
              "). You may end the turn; their exit wakes you.")
    elif human:
        print("HUMAN: everything left waits on the human:")
        for t in human:
            print(f"  - {t['id']}: {t.get('needs')}")
        print("Make sure each ask was sent (PushNotification), then report and end the turn.")
    else:
        print("DONE: every task is done or skipped. Run `orch.py finish`.")


def cmd_start(a):
    work = find_work(a.work); run = load(work); t = by_id(run, a.id)
    t["status"] = "doing"; t["started"] = now(); save(work, run); print("orch: doing " + show(t, False))


def cmd_done(a):
    work = find_work(a.work); run = load(work); t = by_id(run, a.id)
    ev = (a.evidence or "").strip()
    if len(ev) < 4:
        sys.exit("orch: `done` needs --evidence (a commit hash, URL, file path or command output line).")
    t.update(status="done", evidence=ev, finished=now()); t.pop("pid", None)
    save(work, run); print("orch: done " + t["id"]); cmd_next(argparse.Namespace(work=work, all=False))


def cmd_block(a):
    work = find_work(a.work); run = load(work); t = by_id(run, a.id)
    t.update(status="blocked", needs=a.needs, who=a.who, blocked_at=now())
    save(work, run)
    print(f"orch: blocked {t['id']} on: {a.needs}. Tell the human (PushNotification) if you haven't, then continue:")
    cmd_next(argparse.Namespace(work=work, all=False))


def cmd_unblock(a):
    work = find_work(a.work); run = load(work); t = by_id(run, a.id)
    t["status"] = "todo"; t["who"] = "claude"; t.pop("needs", None); save(work, run); print("orch: unblocked " + t["id"])


def cmd_skip(a):
    work = find_work(a.work); run = load(work); t = by_id(run, a.id)
    t.update(status="skipped", why=a.why); save(work, run); print("orch: skipped " + t["id"])
    cmd_next(argparse.Namespace(work=work, all=False))


def cmd_worker(a):
    work = find_work(a.work); run = load(work); t = by_id(run, a.id)
    t.update(status="waiting", pid=a.pid, log=a.log, worker_started=now()); save(work, run)
    print(f"orch: {t['id']} waits on pid {a.pid}")


def cmd_note(a):
    work = find_work(a.work); run = load(work); t = by_id(run, a.id)
    t["notes"].append(f"{now()} {a.text}"); save(work, run)


def cmd_decide(a):
    work = find_work(a.work); run = load(work)
    run["decisions"].append(f"{now()}: {a.text}"); save(work, run)


def cmd_add(a):
    work = find_work(a.work); run = load(work)
    p = slugify(a.product); tid = a.id or f"{p}.{slugify(a.title)[:24]}"
    if any(t["id"] == tid for t in run["tasks"]):
        sys.exit(f"orch: {tid} exists")
    deps = [d.strip() for d in (a.after or "").split(",") if d.strip()]
    run["tasks"].append(mk(tid, p, a.phase, a.title, a.skill or "", a.done_when or "evidence recorded", deps, a.who))
    save(work, run); print("orch: added " + tid)


def cmd_add_product(a):
    work = find_work(a.work); run = load(work)
    tpl = MINI_PRODUCT if run.get("template") == "mini" else PRODUCT_TASKS
    for p in a.names.split(","):
        if slugify(p) in run["products"]:
            print(f"orch: {p} already present"); continue
        product_tasks(run, p.strip(), tpl); print(f"orch: added product {slugify(p)}")
    save(work, run)


def cmd_status(a):
    work = find_work(a.work); run = load(work); render(work, run)
    print(open(os.path.join(work, "STATE.md")).read())


def cmd_pause(a, val=True):
    work = find_work(a.work); run = load(work)
    if val:
        run["paused"] = True
    else:
        run.pop("paused", None)
    save(work, run); print("orch: " + ("paused (the Stop guard is off)" if val else "unpaused"))


def cmd_finish(a):
    work = find_work(a.work); run = load(work); run["finished"] = now(); save(work, run); unbind_all(work)
    print("orch: finished; sessions unbound")


def cmd_stop_check(a):
    """Stop hook. Print a block decision while the bound session has runnable work; else stay silent."""
    try:
        hook = json.load(sys.stdin)
    except Exception:
        hook = {}
    sid = hook.get("session_id") or session_id()
    sessions = load_json(SESSIONS, {})
    ent = sessions.get(sid)
    if not ent:
        return 0
    work = ent["work"]
    run = load_json(run_path(work), None)
    if not run or run.get("paused") or run.get("finished"):
        return 0
    runnable, waiting, human, dead = classify(run)
    if not runnable and not dead:
        ent["idle_blocks"] = 0; save_json(SESSIONS, sessions)
        return 0
    h = hashlib.sha1(json.dumps(run["tasks"], sort_keys=True).encode()).hexdigest()
    if h == ent.get("last_hash"):
        ent["idle_blocks"] = ent.get("idle_blocks", 0) + 1
    else:
        ent["idle_blocks"] = 0
    ent["last_hash"] = h
    save_json(SESSIONS, sessions)
    if ent["idle_blocks"] >= MAX_IDLE_BLOCKS:
        # Three stops in a row without touching the task graph: let it stop, but leave a trace.
        run.setdefault("decisions", []).append(f"{now()}: Stop guard released after {MAX_IDLE_BLOCKS} idle stops")
        save(work, run); ent["idle_blocks"] = 0; save_json(SESSIONS, sessions)
        return 0
    if dead:
        nxt = f"worker for {dead[0]['id']} has exited: read {dead[0].get('log', 'its log')}, review the diff, then mark it done or blocked."
    else:
        nxt = show(runnable[0])
    reason = (f"/orchestrate run '{run['event']}' is not finished: {len(runnable) + len(dead)} task(s) need you now and "
              f"nothing here needs the human. Do not end the turn and do not ask 'should I continue' - keep working.\n"
              f"NEXT: {nxt}\n"
              f"Record progress with `python3 ~/.claude/skills/orchestrate/scripts/orch.py done|block|skip ID ...` "
              f"(STATE.md: {work}/STATE.md). If a task truly needs the human, `block` it with the exact ask and move to the next one. "
              f"If Nick told you to stop, run `orch.py pause`.")
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def sp(name, fn, *args):
        p = sub.add_parser(name); p.add_argument("--work"); p.set_defaults(fn=fn)
        for x in args:
            p.add_argument(x)
        return p

    p = sp("init", cmd_init); p.add_argument("--event", required=True); p.add_argument("--url")
    p.add_argument("--deadline"); p.add_argument("--products"); p.add_argument("--force", action="store_true")
    p.add_argument("--template", default="full", choices=["full", "mini"])
    p.add_argument("--mode", default="autopilot", choices=["autopilot", "gated"])
    p.set_defaults(work=None)
    sp("resume", cmd_resume)
    p = sp("next", cmd_next); p.add_argument("--all", action="store_true")
    sp("start", cmd_start, "id")
    p = sp("done", cmd_done, "id"); p.add_argument("--evidence")
    p = sp("block", cmd_block, "id"); p.add_argument("--needs", required=True)
    p.add_argument("--who", default="human", choices=["human", "external"])
    sp("unblock", cmd_unblock, "id")
    p = sp("skip", cmd_skip, "id"); p.add_argument("--why", required=True)
    p = sp("worker", cmd_worker, "id"); p.add_argument("--pid", required=True); p.add_argument("--log")
    p = sp("note", cmd_note, "id", "text")
    sp("decide", cmd_decide, "text")
    p = sp("add", cmd_add); p.add_argument("--product", required=True); p.add_argument("--phase", type=int, required=True)
    p.add_argument("--title", required=True); p.add_argument("--id"); p.add_argument("--skill")
    p.add_argument("--done-when"); p.add_argument("--after"); p.add_argument("--who", default="claude")
    sp("add-product", cmd_add_product, "names")
    sp("status", cmd_status)
    sp("pause", lambda a: cmd_pause(a, True)); sp("unpause", lambda a: cmd_pause(a, False))
    sp("finish", cmd_finish)
    sub.add_parser("stop-check").set_defaults(fn=cmd_stop_check, work=None)
    a = ap.parse_args()
    if a.cmd == "init" and not a.work:
        ap.error("init needs --work DIR")
    sys.exit(a.fn(a) or 0)


if __name__ == "__main__":
    main()
