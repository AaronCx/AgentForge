-- Blueprint System tables for AgentForge v1.1.0
-- Blueprints are DAG-based workflow definitions with deterministic and agent nodes.

-- Blueprints table
create table if not exists blueprints (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  description text not null default '',
  version integer not null default 1,
  is_template boolean not null default false,

  -- Full DAG definition: array of nodes with edges
  -- Each node: { id, type, label, config, dependencies[] }
  nodes jsonb not null default '[]'::jsonb,

  -- Blueprint-level configuration
  context_config jsonb not null default '{}'::jsonb,   -- urls to pre-fetch, accepted doc types, etc.
  tool_scope text[] not null default '{}',              -- which tools agent nodes can use
  retry_policy jsonb not null default '{"max_retries": 2}'::jsonb,
  output_schema jsonb,                                  -- expected output format

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Add blueprint_id FK to agents table (optional link)
alter table agents add column if not exists blueprint_id uuid references blueprints(id) on delete set null;

-- Blueprint runs table (execution traces)
create table if not exists blueprint_runs (
  id uuid primary key default gen_random_uuid(),
  blueprint_id uuid not null references blueprints(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  status text not null default 'pending',  -- pending, running, completed, failed
  input_payload jsonb not null default '{}'::jsonb,
  output jsonb,

  -- Full execution trace: per-node input/output/timing/tokens
  execution_trace jsonb not null default '[]'::jsonb,

  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now()
);

-- Indexes
create index if not exists idx_blueprints_user_id on blueprints(user_id);
create index if not exists idx_blueprints_is_template on blueprints(is_template);
create index if not exists idx_blueprint_runs_blueprint_id on blueprint_runs(blueprint_id);
create index if not exists idx_blueprint_runs_user_id on blueprint_runs(user_id);
create index if not exists idx_blueprint_runs_status on blueprint_runs(status);

-- RLS policies
alter table blueprints enable row level security;
alter table blueprint_runs enable row level security;

-- Users can see their own blueprints + templates
create policy "Users can view own blueprints and templates"
  on blueprints for select
  using (user_id = auth.uid() or is_template = true);

create policy "Users can insert own blueprints"
  on blueprints for insert
  with check (user_id = auth.uid());

create policy "Users can update own blueprints"
  on blueprints for update
  using (user_id = auth.uid());

create policy "Users can delete own blueprints"
  on blueprints for delete
  using (user_id = auth.uid());

-- Blueprint runs: users can only see/create their own
create policy "Users can view own blueprint runs"
  on blueprint_runs for select
  using (user_id = auth.uid());

create policy "Users can insert own blueprint runs"
  on blueprint_runs for insert
  with check (user_id = auth.uid());

create policy "Users can update own blueprint runs"
  on blueprint_runs for update
  using (user_id = auth.uid());

-- Updated_at trigger for blueprints
create or replace function update_blueprint_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger blueprints_updated_at
  before update on blueprints
  for each row execute function update_blueprint_updated_at();
