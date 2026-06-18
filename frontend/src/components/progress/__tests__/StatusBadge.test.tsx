/**
 * StatusBadge Component Tests
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusBadge } from "../StatusBadge";

describe("StatusBadge", () => {
  describe("Status Rendering", () => {
    it("renders pending status", () => {
      render(<StatusBadge status="pending" />);
      expect(screen.getByText("待处理")).toBeInTheDocument();
      expect(screen.getByRole("status")).toHaveAttribute(
        "aria-label",
        "待处理",
      );
    });

    it("renders running status", () => {
      render(<StatusBadge status="running" />);
      expect(screen.getByText("运行中")).toBeInTheDocument();
      expect(screen.getByRole("status")).toHaveAttribute(
        "aria-label",
        "运行中",
      );
    });

    it("renders completed status", () => {
      render(<StatusBadge status="completed" />);
      expect(screen.getByText("已完成")).toBeInTheDocument();
      expect(screen.getByRole("status")).toHaveAttribute(
        "aria-label",
        "已完成",
      );
    });

    it("renders failed status", () => {
      render(<StatusBadge status="failed" />);
      expect(screen.getByText("失败")).toBeInTheDocument();
      expect(screen.getByRole("status")).toHaveAttribute("aria-label", "失败");
    });

    it("renders skipped status", () => {
      render(<StatusBadge status="skipped" />);
      expect(screen.getByText("跳过")).toBeInTheDocument();
      expect(screen.getByRole("status")).toHaveAttribute("aria-label", "跳过");
    });

    it("renders retrying status", () => {
      render(<StatusBadge status="retrying" />);
      expect(screen.getByText("重试中")).toBeInTheDocument();
      expect(screen.getByRole("status")).toHaveAttribute(
        "aria-label",
        "重试中",
      );
    });

    it("renders cancelled status", () => {
      render(<StatusBadge status="cancelled" />);
      expect(screen.getByText("已取消")).toBeInTheDocument();
      expect(screen.getByRole("status")).toHaveAttribute(
        "aria-label",
        "已取消",
      );
    });
  });

  describe("Color Coding", () => {
    it("applies gray color for pending", () => {
      render(<StatusBadge status="pending" />);
      const badge = screen.getByRole("status");
      expect(badge).toHaveClass(
        "bg-gray-100",
        "text-gray-700",
        "border-gray-300",
      );
    });

    it("applies yellow color for running", () => {
      render(<StatusBadge status="running" />);
      const badge = screen.getByRole("status");
      expect(badge).toHaveClass(
        "bg-yellow-100",
        "text-yellow-700",
        "border-yellow-300",
      );
    });

    it("applies green color for completed", () => {
      render(<StatusBadge status="completed" />);
      const badge = screen.getByRole("status");
      expect(badge).toHaveClass(
        "bg-green-100",
        "text-green-700",
        "border-green-300",
      );
    });

    it("applies red color for failed", () => {
      render(<StatusBadge status="failed" />);
      const badge = screen.getByRole("status");
      expect(badge).toHaveClass("bg-red-100", "text-red-700", "border-red-300");
    });

    it("applies gray color for skipped", () => {
      render(<StatusBadge status="skipped" />);
      const badge = screen.getByRole("status");
      expect(badge).toHaveClass(
        "bg-gray-100",
        "text-gray-500",
        "border-gray-200",
      );
    });

    it("applies orange color for retrying", () => {
      render(<StatusBadge status="retrying" />);
      const badge = screen.getByRole("status");
      expect(badge).toHaveClass(
        "bg-orange-100",
        "text-orange-700",
        "border-orange-300",
      );
    });

    it("applies gray color for cancelled", () => {
      render(<StatusBadge status="cancelled" />);
      const badge = screen.getByRole("status");
      expect(badge).toHaveClass(
        "bg-gray-200",
        "text-gray-600",
        "border-gray-400",
      );
    });
  });

  describe("Status Icons", () => {
    it("displays correct icon for pending", () => {
      render(<StatusBadge status="pending" />);
      expect(screen.getByText("○")).toBeInTheDocument();
    });

    it("displays correct icon for running", () => {
      render(<StatusBadge status="running" />);
      expect(screen.getByText("●")).toBeInTheDocument();
    });

    it("displays correct icon for completed", () => {
      render(<StatusBadge status="completed" />);
      expect(screen.getByText("✓")).toBeInTheDocument();
    });

    it("displays correct icon for failed", () => {
      render(<StatusBadge status="failed" />);
      expect(screen.getByText("✗")).toBeInTheDocument();
    });

    it("displays correct icon for skipped", () => {
      render(<StatusBadge status="skipped" />);
      expect(screen.getByText("—")).toBeInTheDocument();
    });

    it("displays correct icon for retrying", () => {
      render(<StatusBadge status="retrying" />);
      expect(screen.getByText("↻")).toBeInTheDocument();
    });

    it("displays correct icon for cancelled", () => {
      render(<StatusBadge status="cancelled" />);
      expect(screen.getByText("⊗")).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it('has role="status"', () => {
      render(<StatusBadge status="running" />);
      expect(screen.getByRole("status")).toBeInTheDocument();
    });

    it("icon is hidden from screen readers", () => {
      const { container } = render(<StatusBadge status="completed" />);
      const icon = container.querySelector('[aria-hidden="true"]');
      expect(icon).toBeInTheDocument();
      expect(icon).toHaveTextContent("✓");
    });

    it("has descriptive aria-label", () => {
      render(<StatusBadge status="failed" />);
      expect(screen.getByRole("status")).toHaveAttribute("aria-label", "失败");
    });
  });

  describe("Custom className", () => {
    it("applies custom className to badge", () => {
      render(<StatusBadge status="completed" className="my-custom-class" />);
      const badge = screen.getByRole("status");
      expect(badge).toHaveClass("my-custom-class");
    });

    it("preserves default classes with custom className", () => {
      render(<StatusBadge status="running" className="extra-class" />);
      const badge = screen.getByRole("status");
      expect(badge).toHaveClass("inline-flex", "items-center", "rounded-full");
      expect(badge).toHaveClass("extra-class");
    });
  });

  describe("Badge Structure", () => {
    it("renders as a span element", () => {
      const { container } = render(<StatusBadge status="completed" />);
      expect(
        container.querySelector('span[role="status"]'),
      ).toBeInTheDocument();
    });

    it("contains icon and label in correct order", () => {
      const { container } = render(<StatusBadge status="completed" />);
      const badge = container.querySelector('span[role="status"]');
      const children = badge?.children;
      expect(children).toHaveLength(2);
      expect(children?.[0]).toHaveTextContent("✓");
      expect(children?.[1]).toHaveTextContent("已完成");
    });
  });
});
