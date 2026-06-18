/**
 * StepPipeline Component Tests
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StepPipeline } from "../StepPipeline";
import type { StepState } from "@/hooks/useProgressTracking";

describe("StepPipeline", () => {
  const mockSteps: StepState[] = [
    {
      name: "researcher",
      status: "completed",
      startedAt: "2024-01-01T10:00:00Z",
      completedAt: "2024-01-01T10:05:00Z",
      durationMs: 300000,
      retryCount: 0,
      errorMessage: null,
    },
    {
      name: "planner",
      status: "running",
      startedAt: "2024-01-01T10:05:00Z",
      completedAt: null,
      durationMs: null,
      retryCount: 0,
      errorMessage: null,
    },
    {
      name: "coder",
      status: "pending",
      startedAt: null,
      completedAt: null,
      durationMs: null,
      retryCount: 0,
      errorMessage: null,
    },
    {
      name: "reviewer",
      status: "pending",
      startedAt: null,
      completedAt: null,
      durationMs: null,
      retryCount: 0,
      errorMessage: null,
    },
    {
      name: "tester",
      status: "pending",
      startedAt: null,
      completedAt: null,
      durationMs: null,
      retryCount: 0,
      errorMessage: null,
    },
  ];

  describe("Step Rendering", () => {
    it("renders all 5 steps", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      expect(screen.getByText("调研")).toBeInTheDocument();
      expect(screen.getByText("规划")).toBeInTheDocument();
      expect(screen.getByText("编码")).toBeInTheDocument();
      expect(screen.getByText("审查")).toBeInTheDocument();
      expect(screen.getByText("测试")).toBeInTheDocument();
    });

    it("renders step cards with correct aria-labels", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      expect(screen.getByLabelText("步骤: 调研")).toBeInTheDocument();
      expect(screen.getByLabelText("步骤: 规划")).toBeInTheDocument();
    });

    it("renders connectors between steps", () => {
      const { container } = render(
        <StepPipeline steps={mockSteps} currentStep="planner" />,
      );
      const connectors = container.querySelectorAll('[aria-hidden="true"]');
      // Icons are also aria-hidden, so we check for → specifically
      const arrows = Array.from(connectors).filter(
        (el) => el.textContent === "→",
      );
      expect(arrows.length).toBe(4); // 4 arrows for 5 steps
    });

    it("renders empty state when no steps", () => {
      render(<StepPipeline steps={[]} currentStep={null} />);
      expect(screen.getByText("暂无步骤数据")).toBeInTheDocument();
    });
  });

  describe("Current Step Highlighting", () => {
    it("highlights current step with blue styling", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const plannerCard = screen.getByLabelText("步骤: 规划").closest("div");
      expect(plannerCard).toHaveClass("border-blue-400", "bg-blue-50");
    });

    it("does not highlight non-current steps", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const researcherCard = screen.getByLabelText("步骤: 调研").closest("div");
      expect(researcherCard).not.toHaveClass("border-blue-400");
      expect(researcherCard).toHaveClass("border-gray-200", "bg-white");
    });

    it("sets aria-current on current step", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const plannerCard = screen.getByLabelText("步骤: 规划");
      expect(plannerCard).toHaveAttribute("aria-current", "step");
    });

    it("handles null currentStep", () => {
      render(<StepPipeline steps={mockSteps} currentStep={null} />);
      const cards = screen.getAllByRole("article");
      cards.forEach((card) => {
        expect(card).not.toHaveAttribute("aria-current");
      });
    });
  });

  describe("Status Icons", () => {
    it("displays correct icon for completed step", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const researcherCard = screen.getByLabelText("步骤: 调研");
      expect(researcherCard.textContent).toContain("✓");
    });

    it("displays correct icon for running step", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const plannerCard = screen.getByLabelText("步骤: 规划");
      expect(plannerCard.textContent).toContain("●");
    });

    it("displays correct icon for pending step", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const coderCard = screen.getByLabelText("步骤: 编码");
      expect(coderCard.textContent).toContain("○");
    });

    it("displays correct icon for failed step", () => {
      const failedSteps: StepState[] = [
        {
          name: "researcher",
          status: "failed",
          startedAt: "2024-01-01T10:00:00Z",
          completedAt: null,
          durationMs: null,
          retryCount: 2,
          errorMessage: "Connection timeout",
        },
      ];
      render(<StepPipeline steps={failedSteps} currentStep={null} />);
      const card = screen.getByLabelText("步骤: 调研");
      expect(card.textContent).toContain("✗");
    });
  });

  describe("Duration Display", () => {
    it("shows duration for completed step (5m format)", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      expect(screen.getByText(/耗时: 5m/)).toBeInTheDocument();
    });

    it('shows "进行中" for running step', () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const plannerCard = screen.getByLabelText("步骤: 规划");
      expect(plannerCard.textContent).toContain("进行中");
    });

    it('shows "—" for pending step', () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const coderCard = screen.getByLabelText("步骤: 编码");
      // Check for the dash in duration section
      expect(coderCard.textContent).toMatch(/—/);
    });

    it("formats duration in seconds (< 60s)", () => {
      const shortStep: StepState[] = [
        {
          name: "researcher",
          status: "completed",
          startedAt: "2024-01-01T10:00:00Z",
          completedAt: "2024-01-01T10:00:45Z",
          durationMs: 45000,
          retryCount: 0,
          errorMessage: null,
        },
      ];
      render(<StepPipeline steps={shortStep} currentStep={null} />);
      expect(screen.getByText(/耗时: 45s/)).toBeInTheDocument();
    });

    it("formats duration with minutes and seconds", () => {
      const mediumStep: StepState[] = [
        {
          name: "planner",
          status: "completed",
          startedAt: "2024-01-01T10:00:00Z",
          completedAt: "2024-01-01T10:02:30Z",
          durationMs: 150000,
          retryCount: 0,
          errorMessage: null,
        },
      ];
      render(<StepPipeline steps={mediumStep} currentStep={null} />);
      expect(screen.getByText(/耗时: 2m 30s/)).toBeInTheDocument();
    });
  });

  describe("Retry Count Badge", () => {
    it("displays retry count when > 0", () => {
      const retriedSteps: StepState[] = [
        {
          name: "coder",
          status: "retrying",
          startedAt: "2024-01-01T10:00:00Z",
          completedAt: null,
          durationMs: null,
          retryCount: 3,
          errorMessage: null,
        },
      ];
      render(<StepPipeline steps={retriedSteps} currentStep="coder" />);
      expect(screen.getByText("重试 3 次")).toBeInTheDocument();
    });

    it("does not display retry badge when count is 0", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      expect(screen.queryByText(/重试/)).not.toBeInTheDocument();
    });

    it("displays retry count with orange styling", () => {
      const retriedSteps: StepState[] = [
        {
          name: "coder",
          status: "retrying",
          startedAt: "2024-01-01T10:00:00Z",
          completedAt: null,
          durationMs: null,
          retryCount: 2,
          errorMessage: null,
        },
      ];
      render(<StepPipeline steps={retriedSteps} currentStep="coder" />);
      const retryBadge = screen.getByText("重试 2 次");
      expect(retryBadge).toHaveClass("text-orange-600");
    });
  });

  describe("Error Message Display", () => {
    it("displays error message for failed step", () => {
      const failedSteps: StepState[] = [
        {
          name: "tester",
          status: "failed",
          startedAt: "2024-01-01T10:00:00Z",
          completedAt: null,
          durationMs: null,
          retryCount: 0,
          errorMessage: "Test suite failed: 3 errors",
        },
      ];
      render(<StepPipeline steps={failedSteps} currentStep={null} />);
      expect(
        screen.getByText("Test suite failed: 3 errors"),
      ).toBeInTheDocument();
    });

    it("does not display error message for non-failed steps", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });

    it("truncates long error messages with title attribute", () => {
      const failedSteps: StepState[] = [
        {
          name: "coder",
          status: "failed",
          startedAt: "2024-01-01T10:00:00Z",
          completedAt: null,
          durationMs: null,
          retryCount: 0,
          errorMessage: "Very long error message that should be truncated",
        },
      ];
      render(<StepPipeline steps={failedSteps} currentStep={null} />);
      const errorMsg = screen.getByText(
        "Very long error message that should be truncated",
      );
      expect(errorMsg).toHaveClass("truncate");
      expect(errorMsg).toHaveAttribute(
        "title",
        "Very long error message that should be truncated",
      );
    });
  });

  describe("Accessibility", () => {
    it("has region role with aria-label", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const region = screen.getByRole("region", { name: "执行步骤管道" });
      expect(region).toBeInTheDocument();
    });

    it("each step card has article role", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      const cards = screen.getAllByRole("article");
      expect(cards).toHaveLength(5);
    });

    it("icons are hidden from screen readers", () => {
      const { container } = render(
        <StepPipeline steps={mockSteps} currentStep="planner" />,
      );
      const hiddenElements = container.querySelectorAll('[aria-hidden="true"]');
      expect(hiddenElements.length).toBeGreaterThan(0);
    });
  });

  describe("Custom className", () => {
    it("applies custom className to container", () => {
      const { container } = render(
        <StepPipeline
          steps={mockSteps}
          currentStep="planner"
          className="custom-pipeline"
        />,
      );
      const region = container.querySelector('[role="region"]');
      expect(region).toHaveClass("custom-pipeline");
    });
  });

  describe("Step Name Localization", () => {
    it("translates standard step names to Chinese", () => {
      render(<StepPipeline steps={mockSteps} currentStep="planner" />);
      expect(screen.getByText("调研")).toBeInTheDocument();
      expect(screen.getByText("规划")).toBeInTheDocument();
      expect(screen.getByText("编码")).toBeInTheDocument();
      expect(screen.getByText("审查")).toBeInTheDocument();
      expect(screen.getByText("测试")).toBeInTheDocument();
    });

    it("displays original name for unknown step names", () => {
      const customSteps: StepState[] = [
        {
          name: "CustomStep",
          status: "pending",
          startedAt: null,
          completedAt: null,
          durationMs: null,
          retryCount: 0,
          errorMessage: null,
        },
      ];
      render(<StepPipeline steps={customSteps} currentStep={null} />);
      expect(screen.getByText("CustomStep")).toBeInTheDocument();
    });
  });
});
