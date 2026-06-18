/**
 * Agents Page Tests
 */

import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import AgentsPage from "@/app/agents/page";
import { agentService } from "@/services";

vi.mock("@/services", () => ({
  agentService: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

describe("AgentsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the page title", () => {
    vi.mocked(agentService.getAll).mockResolvedValue([]);
    render(<AgentsPage />);
    expect(screen.getByText("Agents")).toBeInTheDocument();
  });

  it("loads and displays agents", async () => {
    const mockAgents = [
      {
        id: "1",
        name: "Test Agent",
        description: "Test Description",
        config: {},
        is_active: "true",
        created_at: "2024-01-01T00:00:00Z",
      },
    ];
    vi.mocked(agentService.getAll).mockResolvedValue(mockAgents);

    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText("Test Agent")).toBeInTheDocument();
      expect(screen.getByText("Test Description")).toBeInTheDocument();
    });
  });

  it("shows loading spinner while fetching", () => {
    vi.mocked(agentService.getAll).mockImplementation(
      () => new Promise(() => {}),
    );
    render(<AgentsPage />);
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("displays error message on fetch failure", async () => {
    vi.mocked(agentService.getAll).mockRejectedValue(new Error("API Error"));
    render(<AgentsPage />);

    await waitFor(() => {
      expect(screen.getByText("Failed to load agents")).toBeInTheDocument();
    });
  });

  it("shows create form when button is clicked", async () => {
    vi.mocked(agentService.getAll).mockResolvedValue([]);
    render(<AgentsPage />);

    await waitFor(() => screen.getByText("Create Agent"));
    fireEvent.click(screen.getByText("Create Agent"));
    expect(screen.getByText("Create New Agent")).toBeInTheDocument();
  });

  it("creates a new agent when form is submitted", async () => {
    vi.mocked(agentService.getAll).mockResolvedValue([]);
    vi.mocked(agentService.create).mockResolvedValue({
      id: "1",
      name: "New Agent",
      description: "Description",
      config: {},
      is_active: "true",
      created_at: "2024-01-01T00:00:00Z",
    });

    render(<AgentsPage />);
    await waitFor(() => screen.getByText("Create Agent"));
    fireEvent.click(screen.getByText("Create Agent"));

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "New Agent" },
    });
    fireEvent.click(screen.getByText("Create"));

    await waitFor(() => {
      expect(agentService.create).toHaveBeenCalled();
    });
  });

  it("toggles agent active status", async () => {
    const mockAgents = [
      {
        id: "1",
        name: "Test Agent",
        description: "Test",
        config: {},
        is_active: "true",
        created_at: "2024-01-01T00:00:00Z",
      },
    ];
    vi.mocked(agentService.getAll).mockResolvedValue(mockAgents);
    vi.mocked(agentService.update).mockResolvedValue(mockAgents[0]);

    render(<AgentsPage />);
    await waitFor(() => screen.getByText("Active"));

    fireEvent.click(screen.getByText("Active"));

    await waitFor(() => {
      expect(agentService.update).toHaveBeenCalledWith("1", {
        is_active: "false",
      });
    });
  });

  it("deletes an agent when delete button is clicked and confirmed", async () => {
    const mockAgents = [
      {
        id: "1",
        name: "Test Agent",
        description: "Test",
        config: {},
        is_active: "true",
        created_at: "2024-01-01T00:00:00Z",
      },
    ];
    vi.mocked(agentService.getAll).mockResolvedValue(mockAgents);
    vi.mocked(agentService.delete).mockResolvedValue();
    global.confirm = vi.fn(() => true);

    render(<AgentsPage />);
    await waitFor(() => screen.getByText("Test Agent"));

    fireEvent.click(screen.getByText("Delete"));

    await waitFor(() => {
      expect(agentService.delete).toHaveBeenCalledWith("1");
    });
  });
});
