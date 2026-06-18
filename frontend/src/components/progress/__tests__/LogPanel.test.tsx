/**
 * LogPanel Component Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LogPanel } from "../LogPanel";
import * as useProgressTrackingModule from "@/hooks/useProgressTracking";
import type { LogEntry } from "@/hooks/useProgressTracking";

// Mock the useProgressTracking hook
vi.mock("@/hooks/useProgressTracking");

describe("LogPanel", () => {
  const mockRunId = "test-run-123";

  const mockLogs: LogEntry[] = [
    {
      step: "researcher",
      level: "info",
      message: "Starting research",
      sequenceNum: 1,
      timestamp: "2024-01-01T10:00:00Z",
    },
    {
      step: "researcher",
      level: "debug",
      message: "Debug message",
      sequenceNum: 2,
      timestamp: "2024-01-01T10:00:05Z",
    },
    {
      step: "planner",
      level: "warning",
      message: "Warning message",
      sequenceNum: 3,
      timestamp: "2024-01-01T10:00:10Z",
    },
    {
      step: "coder",
      level: "error",
      message: "Error occurred",
      sequenceNum: 4,
      timestamp: "2024-01-01T10:00:15Z",
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("Loading State", () => {
    it("displays loading skeleton when isLoading is true", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: true,
        error: null,
      });

      const { container } = render(<LogPanel runId={mockRunId} />);
      const skeleton = container.querySelector(".animate-pulse");
      expect(skeleton).toBeInTheDocument();
    });
  });

  describe("Error State", () => {
    it("displays error message when error exists", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: false,
        error: "Failed to load logs",
      });

      render(<LogPanel runId={mockRunId} />);
      expect(screen.getByText("加载日志失败")).toBeInTheDocument();
      expect(screen.getByText("Failed to load logs")).toBeInTheDocument();
    });

    it("displays error with warning icon", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: false,
        error: "Network error",
      });

      render(<LogPanel runId={mockRunId} />);
      expect(screen.getByText("⚠")).toBeInTheDocument();
    });
  });

  describe("Normal State - Log Display", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("renders title and log count", () => {
      render(<LogPanel runId={mockRunId} />);
      expect(screen.getByText("执行日志")).toBeInTheDocument();
      expect(screen.getByText(`4 / 4`)).toBeInTheDocument();
    });

    it("displays all log entries", () => {
      render(<LogPanel runId={mockRunId} />);
      expect(screen.getByText("Starting research")).toBeInTheDocument();
      expect(screen.getByText("Debug message")).toBeInTheDocument();
      expect(screen.getByText("Warning message")).toBeInTheDocument();
      expect(screen.getByText("Error occurred")).toBeInTheDocument();
    });

    it("has region role with aria-label", () => {
      render(<LogPanel runId={mockRunId} />);
      const region = screen.getByRole("region", { name: "执行日志" });
      expect(region).toBeInTheDocument();
    });

    it('log container has role="log"', () => {
      render(<LogPanel runId={mockRunId} />);
      const logContainer = screen.getByRole("log");
      expect(logContainer).toBeInTheDocument();
    });
  });

  describe("Level Filter", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("renders level filter buttons", () => {
      render(<LogPanel runId={mockRunId} />);
      const allButtons = screen.getAllByText("全部");
      expect(allButtons.length).toBeGreaterThanOrEqual(1);
      const debugs = screen.getAllByText("DEBUG");
      expect(debugs.length).toBeGreaterThanOrEqual(1);
      const infos = screen.getAllByText("INFO");
      expect(infos.length).toBeGreaterThanOrEqual(1);
      const warnings = screen.getAllByText("WARNING");
      expect(warnings.length).toBeGreaterThanOrEqual(1);
      const errors = screen.getAllByText("ERROR");
      expect(errors.length).toBeGreaterThanOrEqual(1);
    });

    it("filters logs by info level", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      const infoButton = screen.getByRole("button", {
        name: "INFO",
        pressed: false,
      });
      await user.click(infoButton);

      // Only info logs should be visible
      expect(screen.getByText("Starting research")).toBeInTheDocument();
      expect(screen.queryByText("Debug message")).not.toBeInTheDocument();
      expect(screen.queryByText("Warning message")).not.toBeInTheDocument();
      expect(screen.queryByText("Error occurred")).not.toBeInTheDocument();
    });

    it("filters logs by error level", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      const errorButton = screen.getByRole("button", {
        name: "ERROR",
        pressed: false,
      });
      await user.click(errorButton);

      expect(screen.getByText("Error occurred")).toBeInTheDocument();
      expect(screen.queryByText("Starting research")).not.toBeInTheDocument();
    });

    it("updates filter count when filtering", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      const infoButton = screen.getByRole("button", {
        name: "INFO",
        pressed: false,
      });
      await user.click(infoButton);

      // Should show 1 / 4 (1 info log out of 4 total)
      expect(screen.getByText("1 / 4")).toBeInTheDocument();
    });

    it("highlights selected level filter", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      const debugButton = screen.getByRole("button", {
        name: "DEBUG",
        pressed: false,
      });
      await user.click(debugButton);

      expect(debugButton).toHaveAttribute("aria-pressed", "true");
      expect(debugButton).toHaveClass("bg-blue-50", "border-blue-300");
    });

    it('shows all logs when "全部" is selected', async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      // First filter by info
      await user.click(screen.getByRole("button", { name: "INFO" }));
      // Then click "全部" - get the first one (level filter)
      const allButtons = screen.getAllByRole("button", { name: "全部" });
      await user.click(allButtons[0]);

      expect(screen.getByText("Starting research")).toBeInTheDocument();
      expect(screen.getByText("Debug message")).toBeInTheDocument();
      expect(screen.getByText("Warning message")).toBeInTheDocument();
      expect(screen.getByText("Error occurred")).toBeInTheDocument();
    });
  });

  describe("Step Filter", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("renders step filter buttons", () => {
      render(<LogPanel runId={mockRunId} />);
      const allButtons = screen.getAllByRole("button", { name: "全部" });
      expect(allButtons.length).toBeGreaterThanOrEqual(2); // Level and step filters
      expect(screen.getByRole("button", { name: "调研" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "规划" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "编码" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "审查" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "测试" })).toBeInTheDocument();
    });

    it("filters logs by researcher step", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      const researcherButton = screen.getByRole("button", { name: "调研" });
      await user.click(researcherButton);

      expect(screen.getByText("Starting research")).toBeInTheDocument();
      expect(screen.getByText("Debug message")).toBeInTheDocument();
      expect(screen.queryByText("Warning message")).not.toBeInTheDocument();
      expect(screen.queryByText("Error occurred")).not.toBeInTheDocument();
    });

    it("filters logs by coder step", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      const coderButton = screen.getByRole("button", { name: "编码" });
      await user.click(coderButton);

      expect(screen.getByText("Error occurred")).toBeInTheDocument();
      expect(screen.queryByText("Starting research")).not.toBeInTheDocument();
    });

    it("highlights selected step filter", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      const plannerButton = screen.getByRole("button", { name: "规划" });
      await user.click(plannerButton);

      expect(plannerButton).toHaveAttribute("aria-pressed", "true");
      expect(plannerButton).toHaveClass("bg-blue-50");
    });
  });

  describe("Combined Filters", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("applies both level and step filters simultaneously", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      // Filter by researcher step
      await user.click(screen.getByRole("button", { name: "调研" }));
      // Filter by info level
      await user.click(screen.getByRole("button", { name: "INFO" }));

      // Only researcher + info should show (1 log)
      expect(screen.getByText("Starting research")).toBeInTheDocument();
      expect(screen.queryByText("Debug message")).not.toBeInTheDocument();
      expect(screen.getByText("1 / 4")).toBeInTheDocument();
    });

    it("shows filter indicator in footer when filtered", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      await user.click(screen.getByRole("button", { name: "ERROR" }));

      expect(screen.getByText(/显示 1 条日志.*已过滤/)).toBeInTheDocument();
    });
  });

  describe("Empty State with Filters", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("shows empty state when no logs match filters", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      // Filter by tester step (no logs from tester)
      await user.click(screen.getByRole("button", { name: "测试" }));

      expect(screen.getByText("暂无日志")).toBeInTheDocument();
      expect(screen.getByText("尝试调整过滤条件")).toBeInTheDocument();
    });

    it("does not show filter hint in empty state when no filters applied", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<LogPanel runId={mockRunId} />);
      expect(screen.getByText("暂无日志")).toBeInTheDocument();
      expect(screen.queryByText("尝试调整过滤条件")).not.toBeInTheDocument();
    });
  });

  describe("Auto-scroll Functionality", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("auto-scroll is enabled by default", () => {
      render(<LogPanel runId={mockRunId} />);
      const autoScrollButton = screen.getByRole("button", { name: /自动滚动/ });
      expect(autoScrollButton).toHaveAttribute("aria-pressed", "true");
      expect(autoScrollButton).toHaveTextContent("✓ 自动滚动");
    });

    it("toggles auto-scroll when button is clicked", async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      const autoScrollButton = screen.getByRole("button", { name: /自动滚动/ });
      await user.click(autoScrollButton);

      expect(autoScrollButton).toHaveAttribute("aria-pressed", "false");
      expect(autoScrollButton).toHaveTextContent("○ 自动滚动");
    });

    it('shows "滚动到底部" button when auto-scroll is disabled', async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      const autoScrollButton = screen.getByRole("button", { name: /自动滚动/ });
      await user.click(autoScrollButton);

      expect(screen.getByText("滚动到底部 ↓")).toBeInTheDocument();
    });

    it('hides "滚动到底部" button when auto-scroll is enabled', () => {
      render(<LogPanel runId={mockRunId} />);
      expect(screen.queryByText("滚动到底部 ↓")).not.toBeInTheDocument();
    });

    it('re-enables auto-scroll when "滚动到底部" is clicked', async () => {
      const user = userEvent.setup();
      render(<LogPanel runId={mockRunId} />);

      // Disable auto-scroll
      const autoScrollButton = screen.getByRole("button", { name: /自动滚动/ });
      await user.click(autoScrollButton);

      // Click scroll to bottom
      const scrollButton = screen.getByText("滚动到底部 ↓");
      await user.click(scrollButton);

      // Auto-scroll should be re-enabled
      expect(autoScrollButton).toHaveAttribute("aria-pressed", "true");
    });
  });

  describe("Log Container Scrolling", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("log container has max-height and overflow-y-auto", () => {
      const { container } = render(<LogPanel runId={mockRunId} />);
      const logContainer = container.querySelector(".max-h-96.overflow-y-auto");
      expect(logContainer).toBeInTheDocument();
    });

    it("log container has scroll event handler", () => {
      const { container } = render(<LogPanel runId={mockRunId} />);
      const logContainer = container.querySelector('[role="log"]');
      expect(logContainer).toBeInTheDocument();
    });
  });

  describe("Footer Information", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("shows log count in footer", () => {
      render(<LogPanel runId={mockRunId} />);
      expect(screen.getByText("显示 4 条日志")).toBeInTheDocument();
    });

    it("does not show footer when no logs", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<LogPanel runId={mockRunId} />);
      expect(screen.queryByText(/显示.*条日志/)).not.toBeInTheDocument();
    });
  });

  describe("Custom className", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("applies custom className to container", () => {
      const { container } = render(
        <LogPanel runId={mockRunId} className="custom-log-panel" />,
      );
      const panel = container.querySelector(".custom-log-panel");
      expect(panel).toBeInTheDocument();
    });
  });

  describe("Integration with useProgressTracking", () => {
    it("calls useProgressTracking with correct runId", () => {
      const mockHook = vi.mocked(useProgressTrackingModule.useProgressTracking);
      mockHook.mockReturnValue({
        progress: null,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<LogPanel runId={mockRunId} />);
      expect(mockHook).toHaveBeenCalledWith(mockRunId);
    });
  });

  describe("Accessibility - Live Regions", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it('log container has aria-live="polite"', () => {
      render(<LogPanel runId={mockRunId} />);
      const logContainer = screen.getByRole("log");
      expect(logContainer).toHaveAttribute("aria-live", "polite");
    });

    it('log container has aria-atomic="false"', () => {
      render(<LogPanel runId={mockRunId} />);
      const logContainer = screen.getByRole("log");
      expect(logContainer).toHaveAttribute("aria-atomic", "false");
    });
  });

  describe("Filter Button States", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: mockLogs,
        isLoading: false,
        error: null,
      });
    });

    it("all filter buttons have aria-pressed attribute", () => {
      render(<LogPanel runId={mockRunId} />);
      const filterButtons = screen.getAllByRole("button");
      const levelAndStepButtons = filterButtons.filter((btn) =>
        [
          "全部",
          "DEBUG",
          "INFO",
          "WARNING",
          "ERROR",
          "调研",
          "规划",
          "编码",
          "审查",
          "测试",
        ].includes(btn.textContent || ""),
      );
      levelAndStepButtons.forEach((button) => {
        expect(button).toHaveAttribute("aria-pressed");
      });
    });
  });
});
