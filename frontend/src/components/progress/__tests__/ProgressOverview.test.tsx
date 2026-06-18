/**
 * ProgressOverview Component Tests
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { ProgressOverview } from "../ProgressOverview";
import * as useProgressTrackingModule from "@/hooks/useProgressTracking";

// Mock the useProgressTracking hook
vi.mock("@/hooks/useProgressTracking");

describe("ProgressOverview", () => {
  const mockRunId = "test-run-123";

  const mockProgressData = {
    runId: mockRunId,
    status: "running",
    steps: [
      {
        name: "researcher",
        status: "completed" as const,
        startedAt: "2024-01-01T10:00:00Z",
        completedAt: "2024-01-01T10:05:00Z",
        durationMs: 300000,
        retryCount: 0,
        errorMessage: null,
      },
      {
        name: "planner",
        status: "running" as const,
        startedAt: "2024-01-01T10:05:00Z",
        completedAt: null,
        durationMs: null,
        retryCount: 0,
        errorMessage: null,
      },
      {
        name: "coder",
        status: "pending" as const,
        startedAt: null,
        completedAt: null,
        durationMs: null,
        retryCount: 0,
        errorMessage: null,
      },
    ],
    currentStep: "planner",
    overallPercentage: 45.5,
    etaSeconds: 300,
    startedAt: "2024-01-01T10:00:00Z",
    updatedAt: "2024-01-01T10:05:30Z",
    completedAt: null,
  };

  beforeEach(() => {
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

      const { container } = render(<ProgressOverview runId={mockRunId} />);
      const skeleton = container.querySelector(".animate-pulse");
      expect(skeleton).toBeInTheDocument();
    });

    it("displays loading skeleton with correct structure", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: true,
        error: null,
      });

      const { container } = render(<ProgressOverview runId={mockRunId} />);
      const skeletonBars = container.querySelectorAll(".bg-gray-200");
      expect(skeletonBars.length).toBeGreaterThan(0);
    });
  });

  describe("Error State", () => {
    it("displays error message when error exists", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: false,
        error: "Failed to fetch progress data",
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("加载进度失败")).toBeInTheDocument();
      expect(
        screen.getByText("Failed to fetch progress data"),
      ).toBeInTheDocument();
    });

    it("displays error with warning icon", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: false,
        error: "Network error",
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("⚠")).toBeInTheDocument();
    });

    it("applies error styling", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: false,
        error: "Test error",
      });

      const { container } = render(<ProgressOverview runId={mockRunId} />);
      const errorContainer = container.querySelector(".border-red-200");
      expect(errorContainer).toBeInTheDocument();
    });
  });

  describe("No Data State", () => {
    it('displays "no data" message when progress is null', () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: null,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("暂无进度数据")).toBeInTheDocument();
    });
  });

  describe("Normal State - Progress Display", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: mockProgressData,
        logs: [],
        isLoading: false,
        error: null,
      });
    });

    it("renders progress overview with title", () => {
      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("执行进度")).toBeInTheDocument();
    });

    it("displays status badge", () => {
      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("运行中")).toBeInTheDocument();
    });

    it("renders ProgressBar component with correct props", () => {
      render(<ProgressOverview runId={mockRunId} />);
      // ProgressBar displays percentage
      expect(screen.getByText("45.5%")).toBeInTheDocument();
    });

    it("displays current step", () => {
      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("planner")).toBeInTheDocument();
    });

    it("displays step progress (completed/total)", () => {
      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("1/3")).toBeInTheDocument();
    });

    it("displays run ID", () => {
      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText(`Run ID: ${mockRunId}`)).toBeInTheDocument();
    });
  });

  describe("Status Badge Mapping", () => {
    it('displays "运行中" for running status', () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: { ...mockProgressData, status: "running" },
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("运行中")).toBeInTheDocument();
    });

    it('displays "已完成" for completed status', () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: { ...mockProgressData, status: "completed" },
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("已完成")).toBeInTheDocument();
    });

    it('displays "失败" for failed status', () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: { ...mockProgressData, status: "failed" },
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("失败")).toBeInTheDocument();
    });

    it('displays "排队中" for queued status', () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: { ...mockProgressData, status: "queued" },
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("排队中")).toBeInTheDocument();
    });

    it('displays "已暂停" for paused status', () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: { ...mockProgressData, status: "paused" },
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("已暂停")).toBeInTheDocument();
    });

    it('displays "已取消" for cancelled status', () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: { ...mockProgressData, status: "cancelled" },
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("已取消")).toBeInTheDocument();
    });

    it('displays "超时" for timeout status', () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: { ...mockProgressData, status: "timeout" },
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("超时")).toBeInTheDocument();
    });
  });

  describe("Duration Calculation", () => {
    it("calculates total duration correctly (< 1 hour)", () => {
      const progress = {
        ...mockProgressData,
        startedAt: "2024-01-01T10:00:00Z",
        completedAt: null,
      };

      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress,
        logs: [],
        isLoading: false,
        error: null,
      });

      // Mock Date.now() to control current time
      const mockNow = new Date("2024-01-01T10:05:30Z").getTime();
      vi.spyOn(Date, "now").mockReturnValue(mockNow);

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText(/5m 30s/)).toBeInTheDocument();

      vi.restoreAllMocks();
    });

    it("calculates total duration with hours", () => {
      const progress = {
        ...mockProgressData,
        startedAt: "2024-01-01T10:00:00Z",
        completedAt: null,
      };

      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress,
        logs: [],
        isLoading: false,
        error: null,
      });

      const mockNow = new Date("2024-01-01T11:15:00Z").getTime();
      vi.spyOn(Date, "now").mockReturnValue(mockNow);

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText(/1h 15m/)).toBeInTheDocument();

      vi.restoreAllMocks();
    });

    it("uses completedAt when run is finished", () => {
      const progress = {
        ...mockProgressData,
        status: "completed",
        startedAt: "2024-01-01T10:00:00Z",
        completedAt: "2024-01-01T10:10:00Z",
      };

      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText(/10m/)).toBeInTheDocument();
    });
  });

  describe("Completed Steps Count", () => {
    it("counts completed steps correctly", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: mockProgressData,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("1/3")).toBeInTheDocument();
    });

    it("handles all steps completed", () => {
      const allCompleted = {
        ...mockProgressData,
        steps: mockProgressData.steps.map((s) => ({
          ...s,
          status: "completed" as const,
        })),
      };

      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: allCompleted,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("3/3")).toBeInTheDocument();
    });

    it("handles no completed steps", () => {
      const noneCompleted = {
        ...mockProgressData,
        steps: mockProgressData.steps.map((s) => ({
          ...s,
          status: "pending" as const,
        })),
      };

      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: noneCompleted,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("0/3")).toBeInTheDocument();
    });
  });

  describe("Current Step Display", () => {
    it("displays current step name when set", () => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: mockProgressData,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("planner")).toBeInTheDocument();
    });

    it('displays "准备中" when currentStep is null', () => {
      const progressWithoutStep = {
        ...mockProgressData,
        currentStep: null,
      };

      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: progressWithoutStep,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(screen.getByText("准备中")).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: mockProgressData,
        logs: [],
        isLoading: false,
        error: null,
      });
    });

    it("has region role with aria-label", () => {
      render(<ProgressOverview runId={mockRunId} />);
      const region = screen.getByRole("region", { name: "执行进度概览" });
      expect(region).toBeInTheDocument();
    });

    it('status badge has role="status"', () => {
      render(<ProgressOverview runId={mockRunId} />);
      const statusBadge = screen.getByRole("status");
      expect(statusBadge).toBeInTheDocument();
    });
  });

  describe("Responsive Layout", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: mockProgressData,
        logs: [],
        isLoading: false,
        error: null,
      });
    });

    it("uses responsive grid classes", () => {
      const { container } = render(<ProgressOverview runId={mockRunId} />);
      const grid = container.querySelector(".grid-cols-2");
      expect(grid).toBeInTheDocument();
      expect(grid).toHaveClass("sm:grid-cols-3");
    });
  });

  describe("Custom className", () => {
    beforeEach(() => {
      vi.mocked(useProgressTrackingModule.useProgressTracking).mockReturnValue({
        progress: mockProgressData,
        logs: [],
        isLoading: false,
        error: null,
      });
    });

    it("applies custom className to container", () => {
      const { container } = render(
        <ProgressOverview runId={mockRunId} className="custom-overview" />,
      );
      const region = container.querySelector('[role="region"]');
      expect(region).toHaveClass("custom-overview");
    });
  });

  describe("Integration with useProgressTracking Hook", () => {
    it("calls useProgressTracking with correct runId", () => {
      const mockHook = vi.mocked(useProgressTrackingModule.useProgressTracking);
      mockHook.mockReturnValue({
        progress: mockProgressData,
        logs: [],
        isLoading: false,
        error: null,
      });

      render(<ProgressOverview runId={mockRunId} />);
      expect(mockHook).toHaveBeenCalledWith(mockRunId);
    });
  });
});
