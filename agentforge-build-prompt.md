# AgentForge Evolution — Claude Code Build Prompt

You are building out AgentForge, an AI agent orchestration platform. The repo is at https://github.com/AaronCx/AgentForge and currently has a basic Next.js 14 + FastAPI + LangChain + Supabase scaffold with agent builder, runner, templates, SSE streaming, and a dashboard.

Your job is to evolve this into a production-grade multi-agent orchestration platform inspired by https://github.com/jayminwest/overstory — but with BOTH a web GUI AND a CLI with a live terminal dashboard. Overstory is CLI-only. AgentForge's differentiator is being web-native AND CLI-capable.

## CRITICAL RULES

1. **Meaningful commits.** NEVER do giant monolithic commits. Commit after every logical unit of work with conventional commit messages (feat:, fix:, docs:, test:, refactor:, chore:). Each commit should be a coherent, reviewable change. Aim for 5-15 commits per phase minimum. Example commit flow for a feature:
   - `feat(backend): add agent_heartbeats table migration`
   - `feat(backend): add AgentState enum and heartbeat models`
   - `feat(backend): add heartbeat update logic to agent executor`
   - `feat(api): add GET /api/dashboard/agents endpoint`
   - `feat(api): add SSE stream for agent status updates`
   - `test(backend): add heartbeat service unit tests`
   - `feat(frontend): add AgentStatusCard component`
   - `feat(frontend): add real-time dashboard page with SSE`
   - `style(frontend): polish dashboard grid layout and animations`
   - `docs: update README with dashboard feature`

2. **Test as you go.** Write tests alongside features, not as an afterthought. Every new backend service gets unit tests. Every new API endpoint gets integration tests. Every new frontend component gets at least a render test.

3. **Don't break existing functionality.** The current agent builder, runner, templates, and SSE streaming must continue working throughout all phases. Run existing tests before and after major changes.

4. **Branch strategy.** Work on `main` with frequent commits. Tag releases at phase boundaries (v0.2.0, v0.3.0, etc.).

5. **Keep the README updated.** After each phase, update the README to reflect new features, updated architecture diagrams, and new screenshots/GIFs where applicable.

---

## EXISTING ARCHITECTURE (Do not break this)

```
agentforge/
├── frontend/          # Next.js 14 + TypeScript + Tailwind + shadcn/ui
│   ├── app/           # App Router pages (auth, dashboard, agents, runs, settings)
│   ├── components/    # UI components (agents, runner, dashboard)
│   └── lib/           # Supabase client, API client, utilities
├── backend/           # FastAPI + LangChain + OpenAI
│   ├── app/
│   │   ├── routers/   # API endpoints (agents, runs, auth, api_keys)
│   │   ├── services/  # Agent executor, tools, rate limiter, templates
│   │   └── models/    # Pydantic models
│   └── tests/         # Unit tests
├── supabase/          # Database migrations
├── .github/workflows/ # CI/CD pipelines
└── docker-compose.yml # Docker orchestration
```

Tech stack: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Python 3.12, FastAPI, LangChain, OpenAI API, PostgreSQL via Supabase, Supabase Auth, Vercel + Render deployment, GitHub Actions CI/CD.

---

## BUILD PHASES — Execute in this exact order

---

### PHASE 0: Repo Maturity (Tag: v0.2.0)

**Goal:** Make the repo look like a real maintained project before adding features.

**0.1 — Project files.** Create these in the repo root:
- `CHANGELOG.md` — Use Keep a Changelog format (https://keepachangelog.com). Start with `## [0.1.0] - YYYY-MM-DD` documenting the existing scaffold features under Added.
- `CONTRIBUTING.md` — Setup instructions (prerequisites, clone, env setup for both frontend and backend), PR process, commit message conventions (conventional commits), code style guidelines.
- `SECURITY.md` — Standard security policy. How to report vulnerabilities (email), supported versions, response timeline.
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1.
- Verify `LICENSE` exists and says MIT with current year.

Commit: `docs: add CHANGELOG, CONTRIBUTING, SECURITY, and CODE_OF_CONDUCT`

**0.2 — CI/CD pipeline.** Update `.github/workflows/` to include:
- Backend: lint with ruff, type check with mypy, test with pytest, coverage report
- Frontend: lint with ESLint, type check with tsc --noEmit, test with vitest, build check with next build
- Run on push to main and on PRs

Commit: `ci: add comprehensive CI pipeline with lint, typecheck, and test jobs`

**0.3 — Testing foundation.**
- Backend: set up pytest + pytest-asyncio + pytest-cov. Write baseline tests for existing routes (agents CRUD, runs, auth). Minimum 10 tests.
- Frontend: set up vitest + @testing-library/react. Write render tests for existing components. Minimum 5 tests.

Commit: `test(backend): add pytest setup and baseline route tests`
Commit: `test(frontend): add vitest setup and component render tests`

**0.4 — Code quality config.**
- Add `ruff.toml` for Python linting
- Add `biome.json` or update `.eslintrc` for frontend
- Add `mypy.ini` or `pyproject.toml` section for type checking

Commit: `chore: add ruff, mypy, and biome config for code quality`

**0.5 — Tag and release.**
- Tag current state as `v0.1.0` with release notes describing the original scaffold
- After all Phase 0 work, tag as `v0.2.0`

Commit: `chore: tag v0.2.0 — repo maturity milestone`

---

### PHASE 1: Live Monitoring Dashboard + CLI (Tag: v0.3.0)

**Goal:** Real-time agent monitoring through BOTH a web dashboard AND a terminal TUI dashboard.

#### Backend Work

**1.1 — Heartbeat system.**

New Supabase migration `005_agent_heartbeats.sql`:
```sql
CREATE TYPE agent_state AS ENUM ('idle', 'running', 'waiting', 'completed', 'failed', 'stalled');

CREATE TABLE agent_heartbeats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
    state agent_state NOT NULL DEFAULT 'idle',
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 1,
    tokens_used INTEGER DEFAULT 0,
    cost_estimate DECIMAL(10, 6) DEFAULT 0,
    output_preview TEXT DEFAULT '',
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_heartbeats_agent ON agent_heartbeats(agent_id);
CREATE INDEX idx_heartbeats_run ON agent_heartbeats(run_id);
```

Commit: `feat(db): add agent_heartbeats table migration`

**1.2 — Heartbeat models and service.**

New file `app/models/heartbeat.py` with Pydantic models for AgentState, AgentHeartbeat, HeartbeatUpdate.

New file `app/services/heartbeat.py` with:
- `update_heartbeat(agent_id, run_id, state, step, tokens, output_preview)`
- `get_active_agents()` — returns all agents with state != completed/failed
- `detect_stalled(threshold_seconds=30)` — marks agents stalled if no update
- `get_agent_timeline(limit=50)` — recent events across all agents

Commit: `feat(backend): add heartbeat models and service`

**1.3 — Integrate heartbeats into agent executor.**

Modify the existing agent executor service to emit heartbeat updates at each workflow step. At step start: update state to running, increment step. At step end: update tokens used, output preview. On completion/failure: update final state.

Commit: `feat(backend): integrate heartbeat updates into agent executor`

**1.4 — Dashboard API routes.**

New file `app/routers/dashboard.py`:
- `GET /api/dashboard/agents` — all active agents with heartbeat data
- `GET /api/dashboard/agents/{id}/stream` — SSE stream for single agent updates (push heartbeat changes)
- `GET /api/dashboard/metrics` — aggregate: total agents, active runs, tokens today, cost today
- `GET /api/dashboard/timeline` — last 50 events across all agents
- `GET /api/dashboard/health` — system-wide health check (stalled agents, error rates)

Commit: `feat(api): add dashboard endpoints for agent monitoring`

**1.5 — Dashboard endpoint tests.**

Test each endpoint with valid auth, invalid auth, empty state, and populated state.

Commit: `test(api): add dashboard endpoint tests`

#### Frontend Work

**1.6 — Agent status card component.**

New component `components/dashboard/AgentStatusCard.tsx`:
- Shows agent name, role badge, state with color coding (running=blue, completed=green, failed=red, stalled=yellow)
- Progress bar showing current_step / total_steps
- Elapsed time counter
- Token count and cost estimate
- Pulse animation when state changes
- Click to expand full execution log

Commit: `feat(frontend): add AgentStatusCard component`

**1.7 — Metrics bar component.**

New component `components/dashboard/MetricsBar.tsx`:
- Four stat cards: Total Agents | Active Runs | Tokens Today | Cost Today
- Each with a sparkline chart (use Recharts) showing trend over last 24h
- Auto-refreshes via polling or SSE

Commit: `feat(frontend): add MetricsBar component with sparklines`

**1.8 — Event timeline component.**

New component `components/dashboard/EventTimeline.tsx`:
- Scrolling feed of timestamped events
- Color-coded by type: info (gray), success (green), warning (yellow), error (red)
- Filterable by agent name
- Auto-scrolls to latest, with "pause" button to stop scroll

Commit: `feat(frontend): add EventTimeline component`

**1.9 — Dashboard page.**

New or updated page at `app/dashboard/page.tsx`:
- Layout: MetricsBar at top, AgentStatusCard grid in middle, EventTimeline at bottom
- SSE connection for real-time updates
- Responsive: cards stack on mobile, grid on desktop
- Empty state with helpful message when no agents are running

Commit: `feat(frontend): build real-time monitoring dashboard page`

**1.10 — Dashboard tests.**

- Render tests for AgentStatusCard, MetricsBar, EventTimeline
- Test with various agent states (empty, running, mixed)

Commit: `test(frontend): add dashboard component tests`

#### CLI Work

**1.11 — CLI foundation.**

Create a new top-level directory `cli/` with a Python CLI using `click` or `typer`:

```
cli/
├── __init__.py
├── __main__.py          # Entry point
├── main.py              # CLI app with command groups
├── commands/
│   ├── __init__.py
│   ├── status.py        # agentforge status
│   ├── dashboard.py     # agentforge dashboard (live TUI)
│   ├── agents.py        # agentforge agents list/create/run
│   └── costs.py         # agentforge costs
├── tui/
│   ├── __init__.py
│   └── dashboard.py     # Rich Live TUI dashboard
├── api_client.py        # HTTP client for the AgentForge backend API
└── config.py            # CLI config (API URL, auth token)
```

Use `typer` for CLI framework and `rich` for terminal output and TUI.

The CLI is a **client** that talks to the same FastAPI backend — it does NOT run agents locally. It uses the API endpoints. Auth via API key (already exists in the backend).

Commit: `feat(cli): scaffold CLI with typer and rich`

**1.12 — CLI config and API client.**

`cli/config.py`: Load config from `~/.agentforge/config.toml` or env vars:
- `api_url` — backend URL (default http://localhost:8000)
- `api_key` — API key for auth (the af_... keys from the settings page)

`cli/api_client.py`: Thin HTTP client wrapping `httpx`:
- Auth header injection
- Methods for all API endpoints
- SSE stream support

Commit: `feat(cli): add config loader and API client`

**1.13 — CLI status command.**

`agentforge status` — Shows a Rich table of all active agents with state, progress, tokens, cost. Similar to `overstory status`. Quick snapshot, not live-updating.

Commit: `feat(cli): add status command with rich table output`

**1.14 — CLI live TUI dashboard.**

`agentforge dashboard` — Live-updating terminal dashboard using `rich.live.Live`:

Layout (inspired by Overstory's TUI):
```
┌─ AgentForge Dashboard ──────────────────────────────────┐
│ Agents: 3 active  │  Tokens: 12,450  │  Cost: $0.0234   │
├──────────────────────────────────────────────────────────┤
│ AGENT            │ STATE    │ PROGRESS │ TOKENS │ COST   │
│ doc-analyzer-1   │ ●RUNNING │ ███░░ 3/5│  4,200 │ $0.008 │
│ research-scout   │ ●RUNNING │ ██░░░ 2/5│  3,100 │ $0.006 │
│ code-reviewer    │ ✓DONE    │ █████ 5/5│  5,150 │ $0.010 │
├──────────────────────────────────────────────────────────┤
│ EVENT LOG                                                │
│ 14:23:01 [doc-analyzer-1] Started step 3: Extract data   │
│ 14:22:58 [research-scout] Completed web search            │
│ 14:22:45 [code-reviewer] ✓ Completed all steps            │
└──────────────────────────────────────────────────────────┘
```

- Polls `/api/dashboard/agents` and `/api/dashboard/timeline` on an interval (default 2s)
- Color-coded states matching the web dashboard
- Press `q` to quit
- `--interval` flag to set refresh rate

Commit: `feat(cli): add live TUI dashboard with rich`

**1.15 — CLI agent commands.**

- `agentforge agents list` — list all agents (table format)
- `agentforge agents run <agent-id> --input "text"` — trigger a run, stream SSE output to terminal in real-time
- `agentforge agents create --name "X" --template research` — create from template

Commit: `feat(cli): add agents list, run, and create commands`

**1.16 — CLI setup and packaging.**

- Add `pyproject.toml` in `cli/` with entry point `agentforge = "cli.main:app"`
- Add install instructions to README
- `pip install -e ./cli` for local dev

Commit: `feat(cli): add pyproject.toml and install configuration`

**1.17 — CLI tests.**

Test CLI commands with mocked API responses using `pytest` + `httpx` mocking.

Commit: `test(cli): add CLI command tests with mocked API`

**Phase 1 wrap-up:**

- Update README with dashboard screenshots (web + CLI)
- Update CHANGELOG with v0.3.0 entry
- Tag `v0.3.0`

Commit: `docs: update README with dashboard feature and screenshots`
Commit: `chore: release v0.3.0 — live monitoring dashboard`

---

### PHASE 2: Cost & Token Tracking (Tag: v0.4.0)

**Goal:** Full token instrumentation and cost analytics, visible in web, CLI, and API.

**2.1 — Token usage table.**

New migration `006_token_usage.sql`:
```sql
CREATE TABLE token_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    step_number INTEGER,
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_token_usage_run ON token_usage(run_id);
CREATE INDEX idx_token_usage_agent ON token_usage(agent_id);
CREATE INDEX idx_token_usage_user ON token_usage(user_id);
CREATE INDEX idx_token_usage_created ON token_usage(created_at);
```

Commit: `feat(db): add token_usage table migration`

**2.2 — Token tracking service.**

New file `app/services/token_tracker.py`:
- `record_usage(run_id, agent_id, user_id, step, model, input_tokens, output_tokens)`
- Automatically calculates cost_usd based on model pricing config
- `get_summary(user_id, period)` — aggregates for today/week/month/all
- `get_breakdown(user_id, group_by)` — group by agent, model, or day
- `get_run_usage(run_id)` — per-step breakdown for a specific run

Model pricing config stored in `app/config/pricing.py`:
```python
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # per 1k tokens
    "gpt-4o": {"input": 0.005, "output": 0.015},
    # Add more as needed
}
```

Commit: `feat(backend): add token tracking service with cost calculation`

**2.3 — Integrate token tracking into agent executor.**

Hook into LangChain callbacks to capture token counts after each LLM call. Record via token_tracker service.

Commit: `feat(backend): integrate token tracking into agent executor`

**2.4 — Cost API endpoints.**

New file `app/routers/costs.py`:
- `GET /api/costs` — summary (today, this week, this month, all time)
- `GET /api/costs/breakdown?group_by=agent|model|day` — grouped breakdown
- `GET /api/costs/run/{run_id}` — per-step usage for a run
- `GET /api/costs/projection` — estimated monthly cost based on trailing 7-day average

Commit: `feat(api): add cost and token usage endpoints`

**2.5 — Cost endpoint tests.**

Commit: `test(api): add cost endpoint tests`

**2.6 — Analytics page (frontend).**

New page `app/analytics/page.tsx` or new tab on dashboard:
- **Summary cards:** Total spend today / week / month with trend arrows (up/down vs previous period)
- **Daily token chart:** Stacked bar chart (Recharts) — input vs output tokens by day, last 14 days
- **Agent cost table:** Sortable table — agent name, total runs, total tokens, total cost, avg cost/run
- **Model breakdown:** Pie/donut chart of spend by model
- **Cost projection card:** "At current usage, estimated $X.XX / month"
- **Run detail view:** Click a run → see per-step token breakdown

Commit: `feat(frontend): add analytics page with cost charts`
Commit: `style(frontend): polish analytics page layout`

**2.7 — CLI costs command.**

`agentforge costs` — Rich table showing cost summary
`agentforge costs --breakdown agent` — breakdown by agent
`agentforge costs --breakdown model` — breakdown by model
`agentforge costs --live` — live-updating cost counter for active runs

Commit: `feat(cli): add costs command with breakdown options`

**2.8 — Tests and release.**

Commit: `test: add analytics component and cost CLI tests`
Commit: `docs: update CHANGELOG and README for v0.4.0`
Commit: `chore: release v0.4.0 — cost and token analytics`

---

### PHASE 3: Agent Hierarchy & Orchestration (Tag: v0.5.0)

**Goal:** Multi-agent orchestration with coordinator → supervisor → worker hierarchy, visible as an interactive graph in the web UI and a tree in the CLI.

**3.1 — Database changes.**

New migration `007_agent_hierarchy.sql`:
```sql
ALTER TABLE agents ADD COLUMN parent_agent_id UUID REFERENCES agents(id);
ALTER TABLE agents ADD COLUMN agent_role TEXT DEFAULT 'worker'
    CHECK (agent_role IN ('coordinator', 'supervisor', 'worker', 'scout', 'reviewer'));
ALTER TABLE agents ADD COLUMN depth INTEGER DEFAULT 0;

CREATE TABLE task_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    objective TEXT,
    coordinator_id UUID REFERENCES agents(id),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed')),
    user_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE task_group_members (
    group_id UUID REFERENCES task_groups(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    task_description TEXT,
    status TEXT DEFAULT 'pending',
    PRIMARY KEY (group_id, agent_id)
);

CREATE INDEX idx_agents_parent ON agents(parent_agent_id);
CREATE INDEX idx_task_groups_user ON task_groups(user_id);
```

Commit: `feat(db): add agent hierarchy and task groups migrations`

**3.2 — Orchestrator service.**

New file `app/services/orchestrator.py`:

This is the brain. It takes a high-level objective and:

1. **Decompose:** Calls the LLM (as a Coordinator agent) with the objective. The LLM returns a structured task plan as JSON: list of sub-tasks, each with a description, required tools, dependencies (which tasks must complete first), and suggested role (scout/builder/reviewer).

2. **Dispatch:** Creates a task_group, then for each sub-task:
   - Creates a child agent with appropriate role and tools
   - Sets parent_agent_id to the coordinator
   - Respects dependencies — tasks with deps wait until deps complete

3. **Execute:** Runs agents as FastAPI background tasks. Independent tasks run concurrently. Dependent tasks queue.

4. **Monitor:** Polls heartbeats. If a worker stalls, notifies the coordinator. If a worker fails, coordinator can retry or reassign.

5. **Aggregate:** When all workers in a task group complete, the coordinator agent makes a final LLM call to synthesize all worker outputs into a cohesive result.

Key methods:
- `orchestrate(user_id, objective, tools_available)` — full pipeline
- `decompose_objective(objective)` — LLM call for task planning
- `dispatch_workers(task_plan, group_id)` — spawn workers
- `check_dependencies(task_id)` — can this task start?
- `aggregate_results(group_id)` — final synthesis

Commit: `feat(backend): add orchestrator service with task decomposition`
Commit: `feat(backend): add worker dispatch and dependency resolution`
Commit: `feat(backend): add result aggregation in orchestrator`

**3.3 — Orchestration API routes.**

New file `app/routers/orchestrate.py`:
- `POST /api/orchestrate` — submit an objective, returns group_id, starts orchestration
- `GET /api/orchestrate/{group_id}` — get task group status, all member agents and their states
- `GET /api/orchestrate/{group_id}/stream` — SSE stream of orchestration progress
- `GET /api/orchestrate/{group_id}/result` — final aggregated result
- `GET /api/orchestrate/history` — list past orchestration runs

Commit: `feat(api): add orchestration endpoints`

**3.4 — Orchestration tests.**

Unit test the orchestrator with mocked LLM responses. Integration test the full flow.

Commit: `test(backend): add orchestrator unit tests`
Commit: `test(api): add orchestration endpoint tests`

**3.5 — Agent tree visualization (frontend).**

New component `components/orchestrate/AgentTree.tsx`:
- Interactive tree/graph using React Flow (already familiar from SupaViz)
- Nodes = agents, styled by role (coordinator=purple, supervisor=blue, worker=green, scout=teal, reviewer=orange)
- Each node shows: agent name, role badge, state indicator, progress
- Edges = parent/child relationships, animated when data is flowing
- Click a node → side panel with agent details, output, logs
- Auto-layouts as new workers spawn

Commit: `feat(frontend): add AgentTree visualization with React Flow`

**3.6 — Orchestration page (frontend).**

New page `app/orchestrate/page.tsx`:
- **Input section:** Large text area for objective, tool selection checkboxes, "Orchestrate" button
- **Decomposition view:** After submitting, shows the coordinator's task plan as a structured list before dispatching
- **Live execution:** AgentTree renders and updates in real-time via SSE as workers spawn and progress
- **Result panel:** When complete, shows the aggregated final output
- **History sidebar:** Past orchestration runs, click to review

Commit: `feat(frontend): build orchestration page with objective input`
Commit: `feat(frontend): add live agent tree updates via SSE`
Commit: `feat(frontend): add result panel and orchestration history`

**3.7 — CLI orchestrate commands.**

- `agentforge orchestrate "Research competitor pricing and generate a report"` — submits objective, streams progress to terminal
- Shows a Rich tree that updates live as agents spawn:
  ```
  🎯 Coordinator: competitor-research
  ├── 🔍 Scout: web-search-pricing [●RUNNING 2/3]
  ├── 🔍 Scout: web-search-features [✓DONE 3/3]
  ├── 🔨 Builder: report-generator [◌WAITING]
  └── 📋 Reviewer: report-reviewer [◌PENDING]
  ```
- `agentforge orchestrate status <group-id>` — check status
- `agentforge orchestrate result <group-id>` — print final result

Commit: `feat(cli): add orchestrate command with live tree output`

**3.8 — Update dashboard.**

Both web and CLI dashboards should now show agent hierarchy. The web dashboard's AgentStatusCards should show role badges and parent agent. The CLI dashboard should show a tree column.

Commit: `feat(frontend): update dashboard to show agent hierarchy`
Commit: `feat(cli): update dashboard to show agent roles and tree`

**3.9 — Release.**

Commit: `docs: update README with orchestration feature and agent tree screenshot`
Commit: `chore: release v0.5.0 — multi-agent orchestration`

---

### PHASE 4: Inter-Agent Messaging (Tag: v0.6.0)

**Goal:** Typed message protocol between agents, visible in both web and CLI.

**4.1 — Messages table.**

New migration `008_agent_messages.sql`:
```sql
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    to_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    group_id UUID REFERENCES task_groups(id) ON DELETE CASCADE,
    thread_id UUID,
    message_type TEXT NOT NULL
        CHECK (message_type IN ('dispatch', 'worker_done', 'escalation', 'nudge',
               'merge_ready', 'status_update', 'question', 'result')),
    subject TEXT,
    body JSONB NOT NULL,
    priority TEXT DEFAULT 'normal'
        CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_messages_to ON agent_messages(to_agent_id, read_at);
CREATE INDEX idx_messages_group ON agent_messages(group_id);
CREATE INDEX idx_messages_thread ON agent_messages(thread_id);
CREATE INDEX idx_messages_type ON agent_messages(message_type);
```

Commit: `feat(db): add agent_messages table migration`

**4.2 — Messaging service.**

New file `app/services/messenger.py`:
- `send(from_id, to_id, type, subject, body, priority, group_id, thread_id)`
- `get_inbox(agent_id, unread_only=True)` 
- `get_thread(thread_id)`
- `mark_read(message_id)`
- `broadcast(from_id, group_id, type, subject, body)` — send to all agents in a group

Commit: `feat(backend): add inter-agent messaging service`

**4.3 — Integrate messaging into orchestrator.**

The orchestrator should use messages instead of direct function calls for coordination:
- Coordinator sends `dispatch` messages to workers
- Workers send `worker_done` messages on completion
- Workers send `escalation` messages on failure
- Coordinator sends `nudge` messages to stalled workers
- Reviewer sends `result` messages with review feedback

Commit: `feat(backend): integrate messaging into orchestration flow`

**4.4 — Message API endpoints.**

New file `app/routers/messages.py`:
- `POST /api/messages` — send a message
- `GET /api/messages/inbox/{agent_id}` — unread messages
- `GET /api/messages/thread/{thread_id}` — full thread
- `PUT /api/messages/{id}/read` — mark read
- `GET /api/messages/stream` — SSE of all messages for a group (for dashboard)
- `GET /api/messages/stats` — message volume stats

Commit: `feat(api): add messaging endpoints`

**4.5 — Message tests.**

Commit: `test(backend): add messaging service tests`
Commit: `test(api): add messaging endpoint tests`

**4.6 — Message feed component (frontend).**

New component `components/dashboard/MessageFeed.tsx`:
- Real-time scrolling feed of inter-agent messages
- Messages styled by type: dispatch=blue, worker_done=green, escalation=red, nudge=yellow, result=purple
- Each message shows: timestamp, from→to, type badge, subject, preview of body
- Click to expand full message body and thread
- Filter by type, agent, or priority
- Optional: overlay message flow arrows on the AgentTree

Commit: `feat(frontend): add MessageFeed component`
Commit: `feat(frontend): integrate MessageFeed into dashboard and orchestrate pages`

**4.7 — CLI mail commands.**

- `agentforge mail list` — show recent messages (Rich table)
- `agentforge mail inbox <agent-name>` — unread messages for an agent
- `agentforge mail thread <thread-id>` — show conversation thread
- Add message feed to the CLI live dashboard as a bottom panel

Commit: `feat(cli): add mail commands and integrate into dashboard`

**4.8 — Release.**

Commit: `docs: update README with messaging feature`
Commit: `chore: release v0.6.0 — inter-agent messaging`

---

### PHASE 5: Testing Push & Quality (Tag: v0.7.0)

**Goal:** Get test coverage to a respectable level. Fill gaps from earlier phases.

**5.1 — Backend coverage push.**
- Audit all services and routes for missing tests
- Add edge case tests: auth failures, rate limiting, invalid inputs, concurrent operations
- Target: 70%+ coverage
- Add coverage badge to README

Commit: `test(backend): add edge case tests for agent executor`
Commit: `test(backend): add orchestrator integration tests`
Commit: `test(backend): add messaging and heartbeat edge case tests`
(Multiple commits as you work through different areas)

**5.2 — Frontend coverage push.**
- Test all dashboard components with various data states
- Test orchestration page interaction flow
- Test analytics charts with mock data
- Add E2E tests with Playwright for key flows: login → create agent → run → view dashboard

Commit: `test(frontend): add dashboard interaction tests`
Commit: `test(frontend): add orchestration page tests`
Commit: `test(e2e): add Playwright tests for core user flows`

**5.3 — CLI test coverage.**
- Test all commands with mocked API responses
- Test TUI dashboard rendering
- Test error handling (API down, auth failed, etc.)

Commit: `test(cli): comprehensive CLI command tests`

**5.4 — Release.**

Commit: `chore: release v0.7.0 — comprehensive test suite`

---

### PHASE 6: Polish & Ship (Tag: v1.0.0)

**Goal:** Make it portfolio-ready with a landing page, demo mode, and clean deployment.

**6.1 — Landing page.**

Update the root `/` page (when not logged in) to be a marketing/landing page:
- Hero section: project name, one-line description, screenshot/GIF of dashboard
- Feature cards: Agent Builder, Live Dashboard, Multi-Agent Orchestration, Inter-Agent Messaging, Cost Analytics, CLI + Web
- Architecture diagram (real image, not just mermaid)
- Tech stack badges
- "Get Started" and "View Demo" CTAs

Commit: `feat(frontend): add landing page with feature showcase`

**6.2 — Demo mode.**

CRITICAL for portfolio. Visitors must see the app working without API keys.

- Add a `/demo` route that loads a pre-seeded demo environment
- Mock data: 3-4 agents with realistic run histories, a completed orchestration with agent tree, message thread, cost data
- No OpenAI key required — all data is pre-recorded
- Banner at top: "You're viewing a demo — Sign up to create your own agents"
- Landing page links to this

Commit: `feat(frontend): add demo mode with pre-seeded data`
Commit: `feat(backend): add demo data seeding endpoint`

**6.3 — Documentation.**

- Add `/docs` page or comprehensive GitHub Wiki
- API reference (link to FastAPI's auto-generated /docs)
- User guide: Getting started, Creating agents, Running orchestrations, Using the CLI
- Architecture deep-dive with diagrams

Commit: `docs: add user guide and architecture documentation`

**6.4 — Final deployment.**

- Frontend on Vercel with proper env vars
- Backend on Render with proper env vars  
- Supabase project with all migrations run
- CLI published to PyPI (optional but impressive): `pip install agentforge-cli`
- Verify live demo URL works and is in repo About section
- Add deployment badges to README

Commit: `chore: finalize deployment configuration`

**6.5 — README final pass.**

- Hero GIF/screenshot at the very top
- Clean feature list with screenshots
- Quick start for both web and CLI
- Architecture diagram
- Links to live demo
- Contributing, license, etc.

Commit: `docs: final README polish with screenshots and demo link`

**6.6 — Release v1.0.0.**

Commit: `chore: release v1.0.0 — production ready`

Create a GitHub Release with full release notes covering everything from v0.1.0 to v1.0.0.

---

## SUMMARY

| Phase | Tag | Key Deliverables |
|-------|-----|-----------------|
| 0 | v0.2.0 | CHANGELOG, CONTRIBUTING, SECURITY, CI/CD, test foundation |
| 1 | v0.3.0 | Live web dashboard + CLI TUI dashboard + heartbeat system |
| 2 | v0.4.0 | Token tracking, cost analytics page, CLI costs command |
| 3 | v0.5.0 | Multi-agent orchestration, agent tree viz, task groups |
| 4 | v0.6.0 | Inter-agent messaging, message feed, CLI mail commands |
| 5 | v0.7.0 | Comprehensive test suite, E2E tests, coverage badges |
| 6 | v1.0.0 | Landing page, demo mode, docs, deployment, final polish |

Total expected commits: 80-120+ meaningful, atomic commits building a real commit history.
