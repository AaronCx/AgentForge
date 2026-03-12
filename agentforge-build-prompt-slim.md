# AgentForge Build Plan

You are evolving AgentForge into a production-grade multi-agent orchestration platform. Reference repo for inspiration: https://github.com/jayminwest/overstory (CLI-only, 412 stars, 434 commits). AgentForge's differentiator: BOTH web GUI AND CLI with live terminal dashboard.

## Commit Rules

Make small, meaningful commits after every logical unit of work. Use conventional commits (feat:, fix:, docs:, test:, refactor:, chore:). Never do monolithic commits. Aim for 5-15 commits per phase. Write tests alongside features.

## Phase 0: Repo Maturity → tag v0.2.0

Create these root files:
- CHANGELOG.md (keepachangelog.com format, document existing features under 0.1.0)
- CONTRIBUTING.md (setup guide, PR process, conventional commits)
- SECURITY.md (vulnerability reporting policy)
- CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- Verify LICENSE exists

Set up code quality:
- ruff.toml for Python linting
- mypy config for Python type checking  
- biome.json or ESLint config for frontend
- Update CI workflow to run lint + typecheck + tests for both frontend and backend

Set up testing:
- Backend: pytest + pytest-asyncio + pytest-cov, write baseline tests for existing routes (min 10 tests)
- Frontend: vitest + testing-library/react, write render tests for existing components (min 5 tests)

Tag existing state as v0.1.0, then tag Phase 0 completion as v0.2.0.

## Phase 1: Live Dashboard + CLI → tag v0.3.0

### Backend
Add an agent_heartbeats table (agent_id, run_id, state enum, current_step, total_steps, tokens_used, cost_estimate, output_preview, updated_at). Integrate heartbeat updates into the existing agent executor so it reports progress at each workflow step. Add stalled detection (no update for 30s).

New dashboard API routes: GET active agents with heartbeats, SSE stream for agent updates, aggregate metrics (total agents, active runs, tokens today, cost today), event timeline, health check endpoint.

### Frontend  
Build a real-time monitoring dashboard page with:
- Metrics bar at top (stat cards with sparklines using Recharts)
- Agent status card grid (name, role, state color-coded, progress bar, tokens, cost, pulse animation on activity)
- Event timeline at bottom (scrolling feed, color-coded by severity, filterable by agent)
- All powered by SSE for real-time updates

### CLI
Create a cli/ directory with a Python CLI using typer + rich + httpx. The CLI is a client that talks to the FastAPI backend via API keys (already exist).

Config: reads from ~/.agentforge/config.toml (api_url, api_key) or env vars.

Commands:
- agentforge status — Rich table of active agents
- agentforge dashboard — Live-updating TUI using rich.live.Live that polls the dashboard API. Show agent table with states, progress, tokens, cost + event log panel. Press q to quit. --interval flag for refresh rate.
- agentforge agents list/run/create — manage agents from terminal
- Add pyproject.toml with entry point, install instructions in README

Write tests for all new backend endpoints and CLI commands.

## Phase 2: Cost & Token Tracking → tag v0.4.0

### Backend
Add a token_usage table (run_id, agent_id, user_id, step_number, model, input_tokens, output_tokens, cost_usd, created_at). Create a token tracking service that hooks into LangChain callbacks to capture token counts per LLM call. Store model pricing in a config dict. Add cost API endpoints: summary by period, breakdown by agent/model/day, per-run step-by-step usage, monthly projection.

### Frontend
Build an analytics page with: summary cards (spend today/week/month with trends), daily stacked bar chart (input vs output tokens), agent cost table (sortable), model breakdown pie chart, cost projection, and per-run detail view.

### CLI
Add: agentforge costs (summary table), agentforge costs --breakdown agent/model, agentforge costs --live (live counter for active runs).

Write tests for all new endpoints and commands.

## Phase 3: Agent Hierarchy & Orchestration → tag v0.5.0

### Backend
Add hierarchy columns to agents table (parent_agent_id, agent_role, depth). Create task_groups and task_group_members tables for batch coordination.

Agent roles: coordinator (decomposes objectives), supervisor (manages workers), worker/builder (executes tasks), scout (research/read-only), reviewer (validation).

Build an orchestrator service that: takes a high-level objective, uses an LLM call to decompose it into sub-tasks with dependencies, dispatches worker agents for each task, runs independent tasks concurrently via FastAPI background tasks, monitors progress via heartbeats, and aggregates results with a final LLM synthesis call.

New orchestration API routes: POST objective (starts orchestration), GET group status, SSE stream of orchestration progress, GET final result, GET history.

### Frontend
Build an orchestration page with: objective input area, tool selection, decomposition view showing the task plan, interactive agent tree visualization using React Flow (nodes = agents styled by role, edges = parent/child, click node for details), live updates via SSE as workers spawn and progress, result panel for aggregated output.

Update the dashboard to show agent hierarchy with role badges.

### CLI
Add: agentforge orchestrate "objective" (submit and stream progress with Rich tree), agentforge orchestrate status/result. Update the TUI dashboard to show agent roles and hierarchy.

Write tests for orchestrator logic, endpoints, and CLI commands.

## Phase 4: Inter-Agent Messaging → tag v0.6.0

### Backend
Add agent_messages table (from_agent_id, to_agent_id, group_id, thread_id, message_type enum, subject, body jsonb, priority enum, read_at, created_at). Message types: dispatch, worker_done, escalation, nudge, status_update, question, result.

Build a messaging service with send, get_inbox, get_thread, mark_read, broadcast. Integrate into the orchestrator so agents coordinate via messages instead of direct calls.

New message API routes: send, inbox, thread, mark read, SSE stream of messages, stats.

### Frontend
Build a message feed component: real-time scrolling feed styled by message type (color-coded), expandable threads, filterable by agent/type/priority. Integrate into dashboard and orchestration pages.

### CLI
Add: agentforge mail list/inbox/thread commands. Add message feed panel to the TUI dashboard.

Write tests for messaging service, endpoints, and CLI commands.

## Phase 5: Testing Push → tag v0.7.0

Audit all services and routes for missing tests. Add edge case tests (auth failures, rate limiting, invalid inputs, concurrency). Target 70%+ backend coverage. Add Playwright E2E tests for key flows (login, create agent, run, view dashboard). Test all CLI commands. Add coverage badges to README.

## Phase 6: Polish & Ship → tag v1.0.0

Build a landing page at / (hero with screenshot, feature cards, architecture diagram, tech badges, CTAs).

CRITICAL: Add demo mode at /demo with pre-seeded mock data so visitors see the app working without API keys. Include sample agents, completed orchestration, messages, and cost data.

Add documentation (API reference via FastAPI /docs, user guide, architecture deep-dive).

Final deployment: frontend on Vercel, backend on Render, Supabase with all migrations. Update README with hero screenshot, feature list, quick start for web + CLI, architecture diagram, live demo link.

Create GitHub Release for v1.0.0 with full release notes.
