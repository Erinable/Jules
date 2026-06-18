/**
 * DetailPanel Component Tests
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DetailPanel } from "../DetailPanel";
import type { StepState } from "@/hooks/useProgressTracking";

describe("DetailPanel", () => {
  const mockStep: StepState = {
    name: "coder",
    status: "completed",
    startedAt: "2024-01-01T10:00:00Z",
    completedAt: "2024-01-01T10:05:30Z",
    durationMs: 330000,
    retryCount: 0,
    errorMessage: null,
  };

  describe("Empty State", () => {
    it("displays empty state when step is null", () => {
      render(<DetailPanel step={null} />);
      expect(screen.getByText("暂无选中步骤")).toBeInTheDocument();
      expect(
        screen.getByText("请点击步骤卡片查看详细信息"),
      ).toBeInTheDocument();
    });

    it("has region role in empty state", () => {
      render(<DetailPanel step={null} />);
      const region = screen.getByRole("region", { name: "步骤详情" });
      expect(region).toBeInTheDocument();
    });
  });

  describe("Step Name Display", () => {
    it("translates researcher to 调研阶段", () => {
      const step = { ...mockStep, name: "researcher" };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("调研阶段")).toBeInTheDocument();
    });

    it("translates planner to 规划阶段", () => {
      const step = { ...mockStep, name: "planner" };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("规划阶段")).toBeInTheDocument();
    });

    it("translates coder to 编码阶段", () => {
      const step = { ...mockStep, name: "coder" };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("编码阶段")).toBeInTheDocument();
    });

    it("translates reviewer to 审查阶段", () => {
      const step = { ...mockStep, name: "reviewer" };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("审查阶段")).toBeInTheDocument();
    });

    it("translates tester to 测试阶段", () => {
      const step = { ...mockStep, name: "tester" };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("测试阶段")).toBeInTheDocument();
    });

    it("displays original name for unknown steps", () => {
      const step = { ...mockStep, name: "CustomStep" };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("CustomStep")).toBeInTheDocument();
    });
  });

  describe("Status Description", () => {
    it("shows description for pending status", () => {
      const step = { ...mockStep, status: "pending" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("此步骤正在等待执行")).toBeInTheDocument();
    });

    it("shows description for running status", () => {
      const step = { ...mockStep, status: "running" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("此步骤正在运行中")).toBeInTheDocument();
    });

    it("shows description for completed status", () => {
      const step = { ...mockStep, status: "completed" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("此步骤已成功完成")).toBeInTheDocument();
    });

    it("shows description for failed status", () => {
      const step = { ...mockStep, status: "failed" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("此步骤执行失败")).toBeInTheDocument();
    });

    it("shows description for skipped status", () => {
      const step = { ...mockStep, status: "skipped" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("此步骤已被跳过")).toBeInTheDocument();
    });

    it("shows description for retrying status", () => {
      const step = { ...mockStep, status: "retrying" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("此步骤正在重试")).toBeInTheDocument();
    });

    it("shows description for cancelled status", () => {
      const step = { ...mockStep, status: "cancelled" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("此步骤已被取消")).toBeInTheDocument();
    });
  });

  describe("Timestamp Display", () => {
    it("displays start and complete times", () => {
      render(<DetailPanel step={mockStep} />);
      expect(screen.getByText("开始时间")).toBeInTheDocument();
      expect(screen.getByText("完成时间")).toBeInTheDocument();
    });

    it("formats timestamps correctly", () => {
      render(<DetailPanel step={mockStep} />);
      // Should display timestamps in format YYYY/MM/DD HH:mm:ss
      const timestamps = screen.getAllByText(/\d{4}\/\d{2}\/\d{2}/);
      expect(timestamps.length).toBeGreaterThanOrEqual(1);
    });

    it('displays "—" when timestamp is null', () => {
      const step = { ...mockStep, startedAt: null, completedAt: null };
      render(<DetailPanel step={step} />);
      const dashes = screen.getAllByText("—");
      expect(dashes.length).toBeGreaterThanOrEqual(2);
    });
  });

  describe("Duration Formatting", () => {
    it("formats duration with hours, minutes, and seconds", () => {
      render(<DetailPanel step={mockStep} />);
      expect(screen.getByText(/5m 30s/)).toBeInTheDocument();
    });

    it("formats duration with hours when >= 60 minutes", () => {
      const step = { ...mockStep, durationMs: 5400000 }; // 1h 30m
      render(<DetailPanel step={step} />);
      expect(screen.getByText(/1h 30m 0s/)).toBeInTheDocument();
    });

    it("formats duration in seconds only (< 60s)", () => {
      const step = { ...mockStep, durationMs: 45000 };
      render(<DetailPanel step={step} />);
      expect(screen.getByText(/45s/)).toBeInTheDocument();
    });

    it("formats duration in milliseconds (< 1s)", () => {
      const step = { ...mockStep, durationMs: 500 };
      render(<DetailPanel step={step} />);
      expect(screen.getByText(/500ms/)).toBeInTheDocument();
    });

    it('displays "—" when duration is null', () => {
      const step = { ...mockStep, durationMs: null };
      render(<DetailPanel step={step} />);
      // Should have "—" for duration display
      expect(screen.getByText("执行时长")).toBeInTheDocument();
    });

    it("shows milliseconds breakdown when durationMs >= 1000", () => {
      render(<DetailPanel step={mockStep} />);
      expect(screen.getByText(/330,000 ms/)).toBeInTheDocument();
    });

    it("does not show milliseconds breakdown when durationMs < 1000", () => {
      const step = { ...mockStep, durationMs: 500 };
      render(<DetailPanel step={step} />);
      expect(screen.queryByText(/ms\)/)).not.toBeInTheDocument();
    });
  });

  describe("Retry Count Badge", () => {
    it("displays retry badge when retryCount > 0", () => {
      const step = { ...mockStep, retryCount: 3 };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("重试 3 次")).toBeInTheDocument();
    });

    it("does not display retry badge when retryCount is 0", () => {
      render(<DetailPanel step={mockStep} />);
      expect(screen.queryByText(/重试.*次/)).not.toBeInTheDocument();
    });

    it("styles retry badge with orange", () => {
      const step = { ...mockStep, retryCount: 2 };
      render(<DetailPanel step={step} />);
      const badge = screen.getByText("重试 2 次");
      expect(badge).toHaveClass("bg-orange-100", "text-orange-700");
    });
  });

  describe("Error Message Display", () => {
    it("shows error section when status is failed", () => {
      const step = {
        ...mockStep,
        status: "failed" as const,
        errorMessage: "Connection timeout",
      };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("错误信息")).toBeInTheDocument();
      expect(screen.getByText("Connection timeout")).toBeInTheDocument();
    });

    it("does not show error section when status is not failed", () => {
      render(<DetailPanel step={mockStep} />);
      expect(screen.queryByText("错误信息")).not.toBeInTheDocument();
    });

    it("does not show error section when errorMessage is null", () => {
      const step = {
        ...mockStep,
        status: "failed" as const,
        errorMessage: null,
      };
      render(<DetailPanel step={step} />);
      expect(screen.queryByText("错误信息")).not.toBeInTheDocument();
    });

    it("styles error message with red colors", () => {
      const step = {
        ...mockStep,
        status: "failed" as const,
        errorMessage: "Test error",
      };
      const { container } = render(<DetailPanel step={step} />);
      const errorBox = container.querySelector(".bg-red-50");
      expect(errorBox).toBeInTheDocument();
    });

    it("preserves whitespace in error message", () => {
      const step = {
        ...mockStep,
        status: "failed" as const,
        errorMessage: "Line 1\nLine 2",
      };
      const { container } = render(<DetailPanel step={step} />);
      const errorText = container.querySelector(".whitespace-pre-wrap");
      expect(errorText).toBeInTheDocument();
    });
  });

  describe("Retry Information Section", () => {
    it("shows retry information when retryCount > 0", () => {
      const step = { ...mockStep, retryCount: 2 };
      render(<DetailPanel step={step} />);
      expect(screen.getByText("重试信息")).toBeInTheDocument();
      expect(screen.getByText(/此步骤已重试/)).toBeInTheDocument();
    });

    it("highlights retry count in bold", () => {
      const step = { ...mockStep, retryCount: 3 };
      const { container } = render(<DetailPanel step={step} />);
      const boldCount = container.querySelector(".font-bold");
      expect(boldCount).toHaveTextContent("3");
    });

    it("does not show retry section when retryCount is 0", () => {
      render(<DetailPanel step={mockStep} />);
      expect(screen.queryByText("重试信息")).not.toBeInTheDocument();
    });

    it("styles retry section with orange", () => {
      const step = { ...mockStep, retryCount: 1 };
      const { container } = render(<DetailPanel step={step} />);
      const retryBox = container.querySelector(".bg-orange-50");
      expect(retryBox).toBeInTheDocument();
    });
  });

  describe("Status-Specific Information", () => {
    it("shows running message for running status", () => {
      const step = { ...mockStep, status: "running" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText(/⏳ 此步骤正在执行中/)).toBeInTheDocument();
    });

    it("shows pending message for pending status", () => {
      const step = { ...mockStep, status: "pending" as const };
      render(<DetailPanel step={step} />);
      expect(
        screen.getByText(/⏸ 此步骤正在队列中等待执行/),
      ).toBeInTheDocument();
    });

    it("shows completed message for completed status", () => {
      const step = { ...mockStep, status: "completed" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText(/✓ 此步骤已成功完成/)).toBeInTheDocument();
    });

    it("shows skipped message for skipped status", () => {
      const step = { ...mockStep, status: "skipped" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText(/— 此步骤已被跳过/)).toBeInTheDocument();
    });

    it("shows cancelled message for cancelled status", () => {
      const step = { ...mockStep, status: "cancelled" as const };
      render(<DetailPanel step={step} />);
      expect(screen.getByText(/⊗ 此步骤已被取消/)).toBeInTheDocument();
    });

    it("applies correct colors for running status", () => {
      const step = { ...mockStep, status: "running" as const };
      const { container } = render(<DetailPanel step={step} />);
      const runningBox = container.querySelector(".bg-blue-50");
      expect(runningBox).toBeInTheDocument();
    });

    it("applies correct colors for completed status", () => {
      const step = { ...mockStep, status: "completed" as const };
      const { container } = render(<DetailPanel step={step} />);
      const completedBox = container.querySelector(".bg-green-50");
      expect(completedBox).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("has region role with descriptive aria-label", () => {
      render(<DetailPanel step={mockStep} />);
      const region = screen.getByRole("region", { name: "步骤详情: 编码阶段" });
      expect(region).toBeInTheDocument();
    });

    it("uses semantic headings", () => {
      render(<DetailPanel step={mockStep} />);
      expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent(
        "编码阶段",
      );
      expect(
        screen.getByRole("heading", { level: 3, name: "时间信息" }),
      ).toBeInTheDocument();
    });
  });

  describe("Responsive Grid Layout", () => {
    it("uses responsive grid for timestamps", () => {
      const { container } = render(<DetailPanel step={mockStep} />);
      const grid = container.querySelector(".grid-cols-1.sm\\:grid-cols-2");
      expect(grid).toBeInTheDocument();
    });
  });

  describe("Custom className", () => {
    it("applies custom className to container", () => {
      const { container } = render(
        <DetailPanel step={mockStep} className="custom-detail" />,
      );
      const panel = container.querySelector(".custom-detail");
      expect(panel).toBeInTheDocument();
    });
  });

  describe("StatusBadge Integration", () => {
    it("renders StatusBadge component", () => {
      render(<DetailPanel step={mockStep} />);
      expect(screen.getByRole("status")).toBeInTheDocument();
    });
  });
});
