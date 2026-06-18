/**
 * Code Files Page Tests
 */

import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import CodeFilesPage from "@/app/code-files/page";
import { codeFileService } from "@/services";

vi.mock("@/services", () => ({
  codeFileService: {
    getByProject: vi.fn(),
  },
}));

describe("CodeFilesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the page title", () => {
    render(<CodeFilesPage />);
    expect(screen.getByText("Code Files")).toBeInTheDocument();
  });

  it("loads code files when project ID is submitted", async () => {
    const mockFiles = [
      {
        id: "1",
        project_id: "proj-1",
        path: "/src/test.ts",
        content: 'console.log("test")',
        hash: "abc123",
        updated_at: "2024-01-01T00:00:00Z",
      },
    ];
    vi.mocked(codeFileService.getByProject).mockResolvedValue(mockFiles);

    render(<CodeFilesPage />);

    fireEvent.change(screen.getByPlaceholderText("Project ID"), {
      target: { value: "proj-1" },
    });
    fireEvent.click(screen.getByText("Load Files"));

    await waitFor(() => {
      expect(screen.getByText("/src/test.ts")).toBeInTheDocument();
    });
  });

  it("displays file content when view button is clicked", async () => {
    const mockFiles = [
      {
        id: "1",
        project_id: "proj-1",
        path: "/src/test.ts",
        content: 'console.log("test")',
        hash: "abc123",
        updated_at: "2024-01-01T00:00:00Z",
      },
    ];
    vi.mocked(codeFileService.getByProject).mockResolvedValue(mockFiles);

    render(<CodeFilesPage />);

    fireEvent.change(screen.getByPlaceholderText("Project ID"), {
      target: { value: "proj-1" },
    });
    fireEvent.click(screen.getByText("Load Files"));

    await waitFor(() => screen.getByText("View"));
    fireEvent.click(screen.getByText("View"));

    await waitFor(() => {
      expect(screen.getByText('console.log("test")')).toBeInTheDocument();
    });
  });

  it("closes file viewer when close button is clicked", async () => {
    const mockFiles = [
      {
        id: "1",
        project_id: "proj-1",
        path: "/src/test.ts",
        content: "test content",
        hash: "abc123",
        updated_at: "2024-01-01T00:00:00Z",
      },
    ];
    vi.mocked(codeFileService.getByProject).mockResolvedValue(mockFiles);

    render(<CodeFilesPage />);

    fireEvent.change(screen.getByPlaceholderText("Project ID"), {
      target: { value: "proj-1" },
    });
    fireEvent.click(screen.getByText("Load Files"));

    await waitFor(() => screen.getByText("View"));
    fireEvent.click(screen.getByText("View"));

    await waitFor(() => screen.getByText("Close"));
    fireEvent.click(screen.getByText("Close"));

    expect(screen.queryByText("test content")).not.toBeInTheDocument();
  });

  it("disables load button when project ID is empty", () => {
    render(<CodeFilesPage />);
    expect(screen.getByText("Load Files")).toBeDisabled();
  });

  it("displays error message on fetch failure", async () => {
    vi.mocked(codeFileService.getByProject).mockRejectedValue(
      new Error("API Error"),
    );

    render(<CodeFilesPage />);

    fireEvent.change(screen.getByPlaceholderText("Project ID"), {
      target: { value: "proj-1" },
    });
    fireEvent.click(screen.getByText("Load Files"));

    await waitFor(() => {
      expect(screen.getByText("Failed to load code files")).toBeInTheDocument();
    });
  });
});
