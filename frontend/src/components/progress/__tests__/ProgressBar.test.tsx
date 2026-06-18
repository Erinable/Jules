/**
 * ProgressBar Component Tests
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ProgressBar } from "../ProgressBar";

describe("ProgressBar", () => {
  describe("Percentage Display", () => {
    it("renders percentage correctly", () => {
      render(<ProgressBar percentage={45.5} eta={null} />);
      expect(screen.getByText("45.5%")).toBeInTheDocument();
    });

    it("clamps percentage to 0-100 range (below 0)", () => {
      render(<ProgressBar percentage={-10} eta={null} />);
      expect(screen.getByText("0.0%")).toBeInTheDocument();
    });

    it("clamps percentage to 0-100 range (above 100)", () => {
      render(<ProgressBar percentage={120} eta={null} />);
      expect(screen.getByText("100.0%")).toBeInTheDocument();
    });

    it("handles zero percentage", () => {
      render(<ProgressBar percentage={0} eta={null} />);
      expect(screen.getByText("0.0%")).toBeInTheDocument();
    });

    it("handles 100% completion", () => {
      render(<ProgressBar percentage={100} eta={null} />);
      expect(screen.getByText("100.0%")).toBeInTheDocument();
    });

    it("formats decimal places correctly", () => {
      render(<ProgressBar percentage={33.333} eta={null} />);
      expect(screen.getByText("33.3%")).toBeInTheDocument();
    });
  });

  describe("ETA Display", () => {
    it("displays ETA for seconds (< 60s)", () => {
      render(<ProgressBar percentage={50} eta={45} />);
      expect(screen.getByText(/预计剩余: 45s/)).toBeInTheDocument();
    });

    it("displays ETA for minutes (60-3600s)", () => {
      render(<ProgressBar percentage={50} eta={150} />);
      expect(screen.getByText(/预计剩余: 2m 30s/)).toBeInTheDocument();
    });

    it("displays ETA for minutes without seconds (exact)", () => {
      render(<ProgressBar percentage={50} eta={120} />);
      expect(screen.getByText(/预计剩余: 2m/)).toBeInTheDocument();
    });

    it("displays ETA for hours (> 3600s)", () => {
      render(<ProgressBar percentage={50} eta={4500} />);
      expect(screen.getByText(/预计剩余: 1h 15m/)).toBeInTheDocument();
    });

    it("displays ETA for hours without minutes (exact)", () => {
      render(<ProgressBar percentage={50} eta={7200} />);
      expect(screen.getByText(/预计剩余: 2h/)).toBeInTheDocument();
    });

    it("hides ETA when null", () => {
      render(<ProgressBar percentage={50} eta={null} />);
      expect(screen.queryByText(/预计剩余/)).not.toBeInTheDocument();
    });

    it("hides ETA when zero", () => {
      render(<ProgressBar percentage={50} eta={0} />);
      expect(screen.queryByText(/预计剩余/)).not.toBeInTheDocument();
    });

    it("hides ETA when negative", () => {
      render(<ProgressBar percentage={50} eta={-10} />);
      expect(screen.queryByText(/预计剩余/)).not.toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("has correct role attribute", () => {
      render(<ProgressBar percentage={50} eta={null} />);
      const progressbar = screen.getByRole("progressbar");
      expect(progressbar).toBeInTheDocument();
    });

    it("has correct aria-valuenow attribute", () => {
      render(<ProgressBar percentage={75.5} eta={null} />);
      const progressbar = screen.getByRole("progressbar");
      expect(progressbar).toHaveAttribute("aria-valuenow", "75.5");
    });

    it("has correct aria-valuemin attribute", () => {
      render(<ProgressBar percentage={50} eta={null} />);
      const progressbar = screen.getByRole("progressbar");
      expect(progressbar).toHaveAttribute("aria-valuemin", "0");
    });

    it("has correct aria-valuemax attribute", () => {
      render(<ProgressBar percentage={50} eta={null} />);
      const progressbar = screen.getByRole("progressbar");
      expect(progressbar).toHaveAttribute("aria-valuemax", "100");
    });

    it("clamps aria-valuenow when percentage exceeds bounds", () => {
      render(<ProgressBar percentage={150} eta={null} />);
      const progressbar = screen.getByRole("progressbar");
      expect(progressbar).toHaveAttribute("aria-valuenow", "100");
    });
  });

  describe("Visual Progress Bar", () => {
    it("renders progress bar with correct width style", () => {
      render(<ProgressBar percentage={60} eta={null} />);
      const progressbar = screen.getByRole("progressbar");
      expect(progressbar).toHaveStyle({ width: "60%" });
    });

    it("renders 0% width for negative percentage", () => {
      render(<ProgressBar percentage={-20} eta={null} />);
      const progressbar = screen.getByRole("progressbar");
      expect(progressbar).toHaveStyle({ width: "0%" });
    });

    it("renders 100% width for over-100 percentage", () => {
      render(<ProgressBar percentage={200} eta={null} />);
      const progressbar = screen.getByRole("progressbar");
      expect(progressbar).toHaveStyle({ width: "100%" });
    });
  });

  describe("Custom className", () => {
    it("applies custom className to container", () => {
      const { container } = render(
        <ProgressBar percentage={50} eta={null} className="custom-class" />,
      );
      const outerDiv = container.firstChild as HTMLElement;
      expect(outerDiv).toHaveClass("custom-class");
    });

    it("preserves default classes with custom className", () => {
      const { container } = render(
        <ProgressBar percentage={50} eta={null} className="my-custom" />,
      );
      const outerDiv = container.firstChild as HTMLElement;
      expect(outerDiv).toHaveClass("w-full");
      expect(outerDiv).toHaveClass("my-custom");
    });
  });
});
