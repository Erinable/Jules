/**
 * LogEntry Component Tests
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { LogEntry } from "../LogEntry";
import type { LogEntry as LogEntryType } from "@/hooks/useProgressTracking";

describe("LogEntry", () => {
  const mockLog: LogEntryType = {
    step: "coder",
    level: "info",
    message: "Test log message",
    sequenceNum: 42,
    timestamp: "2024-01-01T10:30:45.123Z",
  };

  describe("Log Level Rendering", () => {
    it("renders debug level with gray styling", () => {
      const debugLog = { ...mockLog, level: "debug" as const };
      render(<LogEntry log={debugLog} />);

      expect(screen.getByText("🔍")).toBeInTheDocument();
      expect(screen.getByText("DEBUG")).toBeInTheDocument();
      expect(screen.getByText("DEBUG")).toHaveClass(
        "bg-gray-200",
        "text-gray-700",
      );
    });

    it("renders info level with blue styling", () => {
      const infoLog = { ...mockLog, level: "info" as const };
      render(<LogEntry log={infoLog} />);

      expect(screen.getByText("ℹ️")).toBeInTheDocument();
      expect(screen.getByText("INFO")).toBeInTheDocument();
      expect(screen.getByText("INFO")).toHaveClass(
        "bg-blue-200",
        "text-blue-700",
      );
    });

    it("renders warning level with yellow styling", () => {
      const warningLog = { ...mockLog, level: "warning" as const };
      render(<LogEntry log={warningLog} />);

      expect(screen.getByText("⚠️")).toBeInTheDocument();
      expect(screen.getByText("WARNING")).toBeInTheDocument();
      expect(screen.getByText("WARNING")).toHaveClass(
        "bg-yellow-200",
        "text-yellow-700",
      );
    });

    it("renders error level with red styling", () => {
      const errorLog = { ...mockLog, level: "error" as const };
      render(<LogEntry log={errorLog} />);

      expect(screen.getByText("❌")).toBeInTheDocument();
      expect(screen.getByText("ERROR")).toBeInTheDocument();
      expect(screen.getByText("ERROR")).toHaveClass(
        "bg-red-200",
        "text-red-700",
      );
    });
  });

  describe("Message Display", () => {
    it("displays log message correctly", () => {
      render(<LogEntry log={mockLog} />);
      expect(screen.getByText("Test log message")).toBeInTheDocument();
    });

    it("handles long messages with word break", () => {
      const longLog = {
        ...mockLog,
        message:
          "This is a very long log message that should wrap correctly when displayed in the UI",
      };
      const { container } = render(<LogEntry log={longLog} />);
      const messageElement = container.querySelector(".break-words");
      expect(messageElement).toBeInTheDocument();
    });

    it("displays empty message", () => {
      const emptyLog = { ...mockLog, message: "" };
      const { container } = render(<LogEntry log={emptyLog} />);
      expect(container.querySelector(".text-sm")).toBeInTheDocument();
    });
  });

  describe("Timestamp Formatting", () => {
    it("formats timestamp to HH:mm:ss format", () => {
      render(<LogEntry log={mockLog} />);
      // The timestamp should be formatted to local time (HH:mm:ss)
      const timeElement = screen.getByText(/\d{2}:\d{2}:\d{2}/);
      expect(timeElement).toBeInTheDocument();
    });

    it("has correct datetime attribute", () => {
      render(<LogEntry log={mockLog} />);
      const timeElement = screen.getByText(/\d{2}:\d{2}:\d{2}/);
      expect(timeElement.tagName).toBe("TIME");
      expect(timeElement).toHaveAttribute("datetime", mockLog.timestamp);
    });

    it("uses font-mono for timestamp", () => {
      render(<LogEntry log={mockLog} />);
      const timeElement = screen.getByText(/\d{2}:\d{2}:\d{2}/);
      expect(timeElement).toHaveClass("font-mono");
    });
  });

  describe("Step Name Display", () => {
    it("translates researcher to 调研", () => {
      const log = { ...mockLog, step: "researcher" };
      render(<LogEntry log={log} />);
      expect(screen.getByText("调研")).toBeInTheDocument();
    });

    it("translates planner to 规划", () => {
      const log = { ...mockLog, step: "planner" };
      render(<LogEntry log={log} />);
      expect(screen.getByText("规划")).toBeInTheDocument();
    });

    it("translates coder to 编码", () => {
      const log = { ...mockLog, step: "coder" };
      render(<LogEntry log={log} />);
      expect(screen.getByText("编码")).toBeInTheDocument();
    });

    it("translates reviewer to 审查", () => {
      const log = { ...mockLog, step: "reviewer" };
      render(<LogEntry log={log} />);
      expect(screen.getByText("审查")).toBeInTheDocument();
    });

    it("translates tester to 测试", () => {
      const log = { ...mockLog, step: "tester" };
      render(<LogEntry log={log} />);
      expect(screen.getByText("测试")).toBeInTheDocument();
    });

    it("displays original name for unknown step", () => {
      const log = { ...mockLog, step: "CustomStep" };
      render(<LogEntry log={log} />);
      expect(screen.getByText("CustomStep")).toBeInTheDocument();
    });
  });

  describe("Sequence Number Display", () => {
    it("displays sequence number with # prefix", () => {
      render(<LogEntry log={mockLog} />);
      expect(screen.getByText("#42")).toBeInTheDocument();
    });

    it("displays sequence number with gray styling", () => {
      render(<LogEntry log={mockLog} />);
      const seqElement = screen.getByText("#42");
      expect(seqElement).toHaveClass("text-gray-400");
    });

    it("handles sequence number 0", () => {
      const log = { ...mockLog, sequenceNum: 0 };
      render(<LogEntry log={log} />);
      expect(screen.getByText("#0")).toBeInTheDocument();
    });

    it("handles large sequence numbers", () => {
      const log = { ...mockLog, sequenceNum: 9999 };
      render(<LogEntry log={log} />);
      expect(screen.getByText("#9999")).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it('has role="article"', () => {
      render(<LogEntry log={mockLog} />);
      const article = screen.getByRole("article");
      expect(article).toBeInTheDocument();
    });

    it("has descriptive aria-label", () => {
      render(<LogEntry log={mockLog} />);
      const article = screen.getByRole("article");
      expect(article).toHaveAttribute("aria-label", "日志: Test log message");
    });

    it("level icon has aria-label", () => {
      const { container } = render(<LogEntry log={mockLog} />);
      const icon = container.querySelector('[aria-label="info"]');
      expect(icon).toBeInTheDocument();
    });
  });

  describe("Hover Effect", () => {
    it("has hover transition classes", () => {
      const { container } = render(<LogEntry log={mockLog} />);
      const logEntry = container.querySelector('[role="article"]');
      expect(logEntry).toHaveClass("transition-colors");
    });

    it("includes hover background class", () => {
      const { container } = render(<LogEntry log={mockLog} />);
      const logEntry = container.querySelector('[role="article"]');
      // Check that the className includes hover: prefix (Tailwind hover classes)
      expect(logEntry?.className).toMatch(/hover:/);
    });
  });

  describe("Custom className", () => {
    it("applies custom className to container", () => {
      const { container } = render(
        <LogEntry log={mockLog} className="custom-log" />,
      );
      const article = container.querySelector('[role="article"]');
      expect(article).toHaveClass("custom-log");
    });

    it("preserves default classes with custom className", () => {
      const { container } = render(
        <LogEntry log={mockLog} className="extra-class" />,
      );
      const article = container.querySelector('[role="article"]');
      expect(article).toHaveClass("flex", "items-start");
      expect(article).toHaveClass("extra-class");
    });
  });

  describe("Layout Structure", () => {
    it("renders with flex layout", () => {
      const { container } = render(<LogEntry log={mockLog} />);
      const article = container.querySelector('[role="article"]');
      expect(article).toHaveClass("flex", "items-start");
    });

    it("includes proper spacing classes", () => {
      const { container } = render(<LogEntry log={mockLog} />);
      const article = container.querySelector('[role="article"]');
      expect(article).toHaveClass("gap-3", "px-3", "py-2");
    });

    it("icon is flex-shrink-0", () => {
      const { container } = render(<LogEntry log={mockLog} />);
      const icon = container.querySelector(".flex-shrink-0");
      expect(icon).toBeInTheDocument();
    });

    it("content area is flex-1 with min-w-0", () => {
      const { container } = render(<LogEntry log={mockLog} />);
      const content = container.querySelector(".flex-1");
      expect(content).toHaveClass("min-w-0");
    });
  });

  describe("Color Coding by Level", () => {
    it("applies correct text color for debug messages", () => {
      const debugLog = { ...mockLog, level: "debug" as const };
      render(<LogEntry log={debugLog} />);
      const message = screen.getByText("Test log message");
      expect(message).toHaveClass("text-gray-600");
    });

    it("applies correct text color for info messages", () => {
      const infoLog = { ...mockLog, level: "info" as const };
      render(<LogEntry log={infoLog} />);
      const message = screen.getByText("Test log message");
      expect(message).toHaveClass("text-blue-700");
    });

    it("applies correct text color for warning messages", () => {
      const warningLog = { ...mockLog, level: "warning" as const };
      render(<LogEntry log={warningLog} />);
      const message = screen.getByText("Test log message");
      expect(message).toHaveClass("text-yellow-700");
    });

    it("applies correct text color for error messages", () => {
      const errorLog = { ...mockLog, level: "error" as const };
      render(<LogEntry log={errorLog} />);
      const message = screen.getByText("Test log message");
      expect(message).toHaveClass("text-red-700");
    });
  });
});
