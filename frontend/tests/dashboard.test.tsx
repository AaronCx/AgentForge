import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

// Mock supabase
vi.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
      getUser: vi.fn().mockResolvedValue({ data: { user: null } }),
    },
  },
}));

// Mock next/navigation
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
  useRouter: () => ({ push: vi.fn() }),
}));

// Mock next/link
vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe("MetricsBar", () => {
  it("renders metrics values", async () => {
    const { MetricsBar } = await import(
      "@/components/dashboard/MetricsBar"
    );

    render(
      <MetricsBar
        metrics={{
          active_runs: 3,
          total_agents: 10,
          tokens_today: 5000,
          cost_today: 0.42,
        }}
      />
    );

    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("5,000")).toBeInTheDocument();
    expect(screen.getByText("$0.4200")).toBeInTheDocument();
  });

  it("renders zero metrics", async () => {
    const { MetricsBar } = await import(
      "@/components/dashboard/MetricsBar"
    );

    render(
      <MetricsBar
        metrics={{
          active_runs: 0,
          total_agents: 0,
          tokens_today: 0,
          cost_today: 0,
        }}
      />
    );

    const zeros = screen.getAllByText("0");
    expect(zeros.length).toBeGreaterThanOrEqual(2);
  });
});

describe("AgentStatusGrid", () => {
  it("renders agents with state badges", async () => {
    const { AgentStatusGrid } = await import(
      "@/components/dashboard/AgentStatusGrid"
    );

    const agents = [
      {
        id: "hb1",
        agent_id: "a1",
        state: "running",
        current_step: 2,
        total_steps: 5,
        tokens_used: 100,
        cost_estimate: 0.01,
        output_preview: "Processing...",
        agents: { name: "TestAgent", description: "A test agent", tools: [] },
      },
    ];

    render(<AgentStatusGrid agents={agents} />);

    expect(screen.getByText("TestAgent")).toBeInTheDocument();
    expect(screen.getByText("running")).toBeInTheDocument();
  });

  it("renders empty state", async () => {
    const { AgentStatusGrid } = await import(
      "@/components/dashboard/AgentStatusGrid"
    );

    render(<AgentStatusGrid agents={[]} />);

    expect(screen.getByText(/No active agents/)).toBeInTheDocument();
  });
});

describe("EventTimeline", () => {
  it("renders events with severity colors", async () => {
    const { EventTimeline } = await import(
      "@/components/dashboard/EventTimeline"
    );

    const events = [
      {
        id: "e1",
        agent_name: "Agent Alpha",
        state: "completed",
        severity: "success",
        current_step: 3,
        total_steps: 3,
        tokens_used: 200,
        cost_estimate: 0.01,
        updated_at: "2026-03-12T10:00:00Z",
      },
      {
        id: "e2",
        agent_name: "Agent Beta",
        state: "failed",
        severity: "error",
        current_step: 1,
        total_steps: 3,
        tokens_used: 50,
        cost_estimate: 0.005,
        updated_at: "2026-03-12T09:00:00Z",
      },
    ];

    render(<EventTimeline events={events} />);

    expect(screen.getAllByText("Agent Alpha").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Agent Beta").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("completed")).toBeInTheDocument();
    expect(screen.getByText("failed")).toBeInTheDocument();
  });

  it("renders empty state", async () => {
    const { EventTimeline } = await import(
      "@/components/dashboard/EventTimeline"
    );

    render(<EventTimeline events={[]} />);

    expect(screen.getByText("No events yet.")).toBeInTheDocument();
  });
});
