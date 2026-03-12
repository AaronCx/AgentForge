CREATE TABLE IF NOT EXISTS token_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
  agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  step_number INTEGER NOT NULL DEFAULT 1,
  model TEXT NOT NULL DEFAULT 'gpt-4o-mini',
  input_tokens INTEGER NOT NULL DEFAULT 0,
  output_tokens INTEGER NOT NULL DEFAULT 0,
  cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_token_usage_run_id ON token_usage(run_id);
CREATE INDEX idx_token_usage_agent_id ON token_usage(agent_id);
CREATE INDEX idx_token_usage_user_id ON token_usage(user_id);
CREATE INDEX idx_token_usage_created_at ON token_usage(created_at DESC);
CREATE INDEX idx_token_usage_model ON token_usage(model);

-- RLS policies
ALTER TABLE token_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own token usage"
  ON token_usage FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage token usage"
  ON token_usage FOR ALL
  USING (true)
  WITH CHECK (true);
