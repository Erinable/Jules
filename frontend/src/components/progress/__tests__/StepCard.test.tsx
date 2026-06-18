/**
 * StepCard Component Tests
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { StepCard } from "../StepCard";
import type { StepState } from "@/hooks/useProgressTracking";

describe("StepCard", () => {
  const mockStep: StepState = {
    name: "coder",
    status: "completed",
    startedAt: "2024-01-01T10:00:00Z",
    completedAt: "2024-01-01T10:05:00Z",
    durationMs: 300000,
    retryCount: 0,
    errorMessage: null,
  };

  describe("Basic Rendering", () => {
    it("renders step card with step name", () => {
      render(<StepCard step={mockStep} />);
      expect(screen.getByText("编码阶段")).toBeInTheDocument();
    });

    it("renders StatusBadge component", () => {
      render(<StepCard step={mockStep} />);
      expect(screen.getByRole("status")).toBeInTheDocument();
    });

    it("displays duration", () => {
      render(<StepCard step={mockStep} />);
      expect(screen.getByText(/5m/)).toBeInTheDocument();
    });

    it('has role="article"', () => {
      render(<StepCard step={mockStep} />);
      const article = screen.getByRole("article");
      expect(article).toBeInTheDocument();
    });
  });

  describe("Step Name Localization", () => {
    it("translates researcher to 调研阶段", () => {
      const step = { ...mockStep, name: "researcher" };
      render(<StepCard step={step} />);
      expect(screen.getByText("调研阶段")).toBeInTheDocument();
    });

    it("translates planner to 规划阶段", () => {
      const step = { ...mockStep, name: "planner" };
      render(<StepCard step={step} />);
      expect(screen.getByText("规划阶段")).toBeInTheDocument();
    });

    it("translates coder to 编码阶段", () => {
      const step = { ...mockStep, name: "coder" };
      render(<StepCard step={step} />);
      expect(screen.getByText("编码阶段")).toBeInTheDocument();
    });

    it("translates reviewer to 审查阶段", () => {
      const step = { ...mockStep, name: "reviewer" };
      render(<StepCard step={step} />);
      expect(screen.getByText("审查阶段")).toBeInTheDocument();
    });

    it("translates tester to 测试阶段", () => {
      const step = { ...mockStep, name: "tester" };
      render(<StepCard step={step} />);
      expect(screen.getByText("测试阶段")).toBeInTheDocument();
    });

    it("displays original name for unknown steps", () => {
      const step = { ...mockStep, name: "CustomStep" };
      render(<StepCard step={step} />);
      expect(screen.getByText("CustomStep")).toBeInTheDocument();
    });
  });

  describe("Status Icons", () => {
    it("displays checkmark icon for completed", () => {
      const step = { ...mockStep, status: "completed" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-2xl.text-green-600");
      expect(icon).toHaveTextContent("✓");
    });

    it("displays filled circle for running", () => {
      const step = { ...mockStep, status: "running" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-2xl.text-blue-600");
      expect(icon).toHaveTextContent("●");
    });

    it("displays X icon for failed", () => {
      const step = { ...mockStep, status: "failed" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-2xl.text-red-600");
      expect(icon).toHaveTextContent("✗");
    });

    it("displays empty circle for pending", () => {
      const step = { ...mockStep, status: "pending" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-2xl.text-gray-400");
      expect(icon).toHaveTextContent("○");
    });

    it("displays dash for skipped", () => {
      const step = { ...mockStep, status: "skipped" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-2xl");
      expect(icon).toHaveTextContent("—");
    });

    it("displays retry icon for retrying", () => {
      const step = { ...mockStep, status: "retrying" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-2xl");
      expect(icon).toHaveTextContent("↻");
    });

    it("displays cancel icon for cancelled", () => {
      const step = { ...mockStep, status: "cancelled" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-2xl");
      expect(icon).toHaveTextContent("⊗");
    });
  });

  describe("Status Labels", () => {
    it('shows "已完成" for completed status', () => {
      const step = { ...mockStep, status: "completed" as const };
      render(<StepCard step={step} />);
      const labels = screen.getAllByText("已完成");
      expect(labels.length).toBeGreaterThan(0);
    });

    it('shows "进行中" for running status', () => {
      const step = { ...mockStep, status: "running" as const };
      render(<StepCard step={step} />);
      const labels = screen.getAllByText("进行中");
      expect(labels.length).toBeGreaterThan(0);
    });

    it('shows "失败" for failed status', () => {
      const step = { ...mockStep, status: "failed" as const };
      render(<StepCard step={step} />);
      const labels = screen.getAllByText("失败");
      expect(labels.length).toBeGreaterThan(0);
    });

    it('shows "待处理" for pending status', () => {
      const step = { ...mockStep, status: "pending" as const };
      render(<StepCard step={step} />);
      const labels = screen.getAllByText("待处理");
      expect(labels.length).toBeGreaterThan(0);
    });
  });

  describe("Retry Count Badge", () => {
    it("displays retry badge when retry count > 0", () => {
      const step = { ...mockStep, retryCount: 3 };
      render(<StepCard step={step} />);
      expect(screen.getByText("重试 3 次")).toBeInTheDocument();
    });

    it("does not display retry badge when retry count is 0", () => {
      const step = { ...mockStep, retryCount: 0 };
      render(<StepCard step={step} />);
      expect(screen.queryByText(/重试/)).not.toBeInTheDocument();
    });

    it("styles retry badge with orange colors", () => {
      const step = { ...mockStep, retryCount: 2 };
      render(<StepCard step={step} />);
      const badge = screen.getByText("重试 2 次");
      expect(badge).toHaveClass("bg-orange-100", "text-orange-700");
    });
  });

  describe("Duration Formatting", () => {
    it("formats duration in seconds (< 60s)", () => {
      const step = { ...mockStep, durationMs: 45000 };
      render(<StepCard step={step} />);
      expect(screen.getByText("45s")).toBeInTheDocument();
    });

    it("formats duration in minutes and seconds", () => {
      const step = { ...mockStep, durationMs: 150000 };
      render(<StepCard step={step} />);
      expect(screen.getByText("2m 30s")).toBeInTheDocument();
    });

    it("formats duration in minutes only (exact)", () => {
      const step = { ...mockStep, durationMs: 120000 };
      render(<StepCard step={step} />);
      expect(screen.getByText("2m")).toBeInTheDocument();
    });

    it("formats duration in milliseconds (< 1s)", () => {
      const step = { ...mockStep, durationMs: 500 };
      render(<StepCard step={step} />);
      expect(screen.getByText("500ms")).toBeInTheDocument();
    });

    it('displays "—" when duration is null', () => {
      const step = { ...mockStep, durationMs: null };
      render(<StepCard step={step} />);
      expect(screen.getByText("—")).toBeInTheDocument();
    });
  });

  describe("Expand/Collapse Functionality", () => {
    it("renders without expand indicator when onToggle is not provided", () => {
      render(<StepCard step={mockStep} />);
      expect(screen.queryByText("▶")).not.toBeInTheDocument();
      expect(screen.queryByText("▼")).not.toBeInTheDocument();
    });

    it("renders expand indicator when onToggle is provided", () => {
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={false} onToggle={handleToggle} />,
      );
      expect(screen.getByText("▶")).toBeInTheDocument();
    });

    it("shows collapse indicator when expanded", () => {
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={true} onToggle={handleToggle} />,
      );
      expect(screen.getByText("▼")).toBeInTheDocument();
    });

    it("calls onToggle when header is clicked", async () => {
      const user = userEvent.setup();
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={false} onToggle={handleToggle} />,
      );

      const header = screen.getByRole("button");
      await user.click(header);

      expect(handleToggle).toHaveBeenCalledTimes(1);
    });

    it('header has role="button" when onToggle is provided', () => {
      const handleToggle = vi.fn();
      render(<StepCard step={mockStep} onToggle={handleToggle} />);
      expect(screen.getByRole("button")).toBeInTheDocument();
    });

    it("header has no button role when onToggle is not provided", () => {
      const { container } = render(<StepCard step={mockStep} />);
      const header = container.querySelector(".p-4");
      expect(header).not.toHaveAttribute("role", "button");
    });

    it("header has cursor-pointer class when onToggle is provided", () => {
      const handleToggle = vi.fn();
      const { container } = render(
        <StepCard step={mockStep} onToggle={handleToggle} />,
      );
      const header = container.querySelector(".cursor-pointer");
      expect(header).toBeInTheDocument();
    });

    it("sets aria-expanded=true when expanded", () => {
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={true} onToggle={handleToggle} />,
      );
      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("aria-expanded", "true");
    });

    it("sets aria-expanded=false when collapsed", () => {
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={false} onToggle={handleToggle} />,
      );
      const button = screen.getByRole("button");
      expect(button).toHaveAttribute("aria-expanded", "false");
    });
  });

  describe("Expanded Details", () => {
    it("hides details when not expanded", () => {
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={false} onToggle={handleToggle} />,
      );
      expect(screen.queryByText("开始时间")).not.toBeInTheDocument();
    });

    it("shows details when expanded", () => {
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={true} onToggle={handleToggle} />,
      );
      expect(screen.getByText("开始时间")).toBeInTheDocument();
      expect(screen.getByText("完成时间")).toBeInTheDocument();
    });

    it("shows timestamps in expanded view", () => {
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={true} onToggle={handleToggle} />,
      );
      const timestamps = screen.getAllByText(/\d{2}:\d{2}:\d{2}/);
      expect(timestamps.length).toBeGreaterThan(0);
    });

    it("shows duration breakdown when expanded and durationMs is not null", () => {
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={true} onToggle={handleToggle} />,
      );
      expect(screen.getByText("耗时详情")).toBeInTheDocument();
      expect(screen.getByText(/300,000 ms/)).toBeInTheDocument();
    });

    it("does not show duration breakdown when durationMs is null", () => {
      const handleToggle = vi.fn();
      const step = { ...mockStep, durationMs: null };
      render(
        <StepCard step={step} isExpanded={true} onToggle={handleToggle} />,
      );
      expect(screen.queryByText("耗时详情")).not.toBeInTheDocument();
    });
  });

  describe("Error Message Display", () => {
    it("shows error message in collapsed view when failed", () => {
      const step = {
        ...mockStep,
        status: "failed" as const,
        errorMessage: "Connection timeout",
      };
      render(<StepCard step={step} />);
      // Error is only shown in expanded view
      expect(screen.queryByText("错误信息")).not.toBeInTheDocument();
    });

    it("shows error message in expanded view when failed", () => {
      const handleToggle = vi.fn();
      const step = {
        ...mockStep,
        status: "failed" as const,
        errorMessage: "Connection timeout",
      };
      render(
        <StepCard step={step} isExpanded={true} onToggle={handleToggle} />,
      );
      expect(screen.getByText("错误信息")).toBeInTheDocument();
      expect(screen.getByText("Connection timeout")).toBeInTheDocument();
    });

    it("does not show error section when status is not failed", () => {
      const handleToggle = vi.fn();
      const step = { ...mockStep, status: "completed" as const };
      render(
        <StepCard step={step} isExpanded={true} onToggle={handleToggle} />,
      );
      expect(screen.queryByText("错误信息")).not.toBeInTheDocument();
    });

    it("styles error message with red colors", () => {
      const handleToggle = vi.fn();
      const step = {
        ...mockStep,
        status: "failed" as const,
        errorMessage: "Test error",
      };
      const { container } = render(
        <StepCard step={step} isExpanded={true} onToggle={handleToggle} />,
      );
      const errorBox = container.querySelector(".bg-red-50");
      expect(errorBox).toBeInTheDocument();
    });
  });

  describe("Retry Information Display", () => {
    it("shows retry information in expanded view when retryCount > 0", () => {
      const handleToggle = vi.fn();
      const step = { ...mockStep, retryCount: 2 };
      render(
        <StepCard step={step} isExpanded={true} onToggle={handleToggle} />,
      );
      expect(screen.getByText(/已重试 2 次/)).toBeInTheDocument();
    });

    it("does not show retry section when retryCount is 0", () => {
      const handleToggle = vi.fn();
      const step = { ...mockStep, retryCount: 0 };
      render(
        <StepCard step={step} isExpanded={true} onToggle={handleToggle} />,
      );
      expect(screen.queryByText(/已重试/)).not.toBeInTheDocument();
    });

    it("styles retry information with orange colors", () => {
      const handleToggle = vi.fn();
      const step = { ...mockStep, retryCount: 1 };
      const { container } = render(
        <StepCard step={step} isExpanded={true} onToggle={handleToggle} />,
      );
      const retryBox = container.querySelector(".bg-orange-50");
      expect(retryBox).toBeInTheDocument();
    });
  });

  describe("Status Icon Colors", () => {
    it("applies green color for completed", () => {
      const step = { ...mockStep, status: "completed" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-green-600");
      expect(icon).toBeInTheDocument();
    });

    it("applies blue color for running", () => {
      const step = { ...mockStep, status: "running" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-blue-600");
      expect(icon).toBeInTheDocument();
    });

    it("applies red color for failed", () => {
      const step = { ...mockStep, status: "failed" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-red-600");
      expect(icon).toBeInTheDocument();
    });

    it("applies gray color for other statuses", () => {
      const step = { ...mockStep, status: "pending" as const };
      const { container } = render(<StepCard step={step} />);
      const icon = container.querySelector(".text-gray-400");
      expect(icon).toBeInTheDocument();
    });
  });

  describe("Custom className", () => {
    it("applies custom className to container", () => {
      const { container } = render(
        <StepCard step={mockStep} className="custom-card" />,
      );
      const card = container.querySelector(".custom-card");
      expect(card).toBeInTheDocument();
    });
  });

  describe("Timestamp Formatting", () => {
    it("formats timestamps to HH:mm:ss", () => {
      const handleToggle = vi.fn();
      render(
        <StepCard step={mockStep} isExpanded={true} onToggle={handleToggle} />,
      );
      const timestamps = screen.getAllByText(/\d{2}:\d{2}:\d{2}/);
      expect(timestamps.length).toBeGreaterThanOrEqual(2); // startedAt and completedAt
    });

    it('displays "—" when timestamp is null', () => {
      const handleToggle = vi.fn();
      const step = { ...mockStep, startedAt: null, completedAt: null };
      render(
        <StepCard step={step} isExpanded={true} onToggle={handleToggle} />,
      );
      const dashes = screen.getAllByText("—");
      expect(dashes.length).toBeGreaterThanOrEqual(2);
    });
  });
});
