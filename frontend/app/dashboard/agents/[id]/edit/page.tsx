"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { api, Agent } from "@/lib/api";
import { isDemoMode, DEMO_AGENTS } from "@/lib/demo-data";
import { AgentBuilder } from "@/components/agents/AgentBuilder";

export default function EditAgentPage() {
  const params = useParams();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isDemoMode()) {
      const demo = DEMO_AGENTS.find((a) => a.id === params.id) as Agent | undefined;
      setAgent(demo || null);
      if (!demo) setError("Agent not found");
      setLoading(false);
      return;
    }

    async function load() {
      const { data } = await supabase.auth.getSession();
      if (!data.session) return;

      try {
        const a = await api.agents.get(params.id as string, data.session.access_token);
        setAgent(a);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load agent");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [params.id]);

  if (loading) return <p className="text-muted-foreground">Loading agent...</p>;
  if (error) return <p className="text-destructive">{error}</p>;
  if (!agent) return <p className="text-destructive">Agent not found</p>;

  return (
    <div>
      <h1 className="text-3xl font-bold">Edit Agent</h1>
      <p className="mt-1 text-muted-foreground">Update {agent.name}</p>
      <div className="mt-8">
        <AgentBuilder
          mode="edit"
          initialData={{
            id: agent.id,
            name: agent.name,
            description: agent.description,
            system_prompt: agent.system_prompt,
            tools: agent.tools,
            workflow_steps: agent.workflow_steps,
          }}
        />
      </div>
    </div>
  );
}
