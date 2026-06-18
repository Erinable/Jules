/**
 * Task Service Tests
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { taskService } from "@/services/taskService";
import apiClient from "@/services/apiClient";

vi.mock("@/services/apiClient");

describe("taskService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getAll", () => {
    it("fetches all tasks without filters", async () => {
      const mockTasks = [
        {
          id: "1",
          project_id: "p1",
          title: "Task 1",
          status: "pending",
          priority: 5,
          created_at: "2024-01-01",
        },
      ];
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockTasks });

      const result = await taskService.getAll();

      expect(apiClient.get).toHaveBeenCalledWith("/tasks/", {
        params: undefined,
      });
      expect(result).toEqual(mockTasks);
    });

    it("fetches tasks with filters", async () => {
      const mockTasks = [];
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockTasks });

      await taskService.getAll({ status: "completed", priority: 10 });

      expect(apiClient.get).toHaveBeenCalledWith("/tasks/", {
        params: { status: "completed", priority: 10 },
      });
    });
  });

  describe("getById", () => {
    it("fetches a task by ID", async () => {
      const mockTask = {
        id: "1",
        project_id: "p1",
        title: "Task 1",
        status: "pending",
        priority: 5,
        created_at: "2024-01-01",
      };
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockTask });

      const result = await taskService.getById("1");

      expect(apiClient.get).toHaveBeenCalledWith("/tasks/1");
      expect(result).toEqual(mockTask);
    });
  });

  describe("create", () => {
    it("creates a new task", async () => {
      const newTask = { project_id: "p1", title: "New Task", priority: 5 };
      const createdTask = {
        id: "2",
        ...newTask,
        status: "pending",
        created_at: "2024-01-01",
      };
      vi.mocked(apiClient.post).mockResolvedValue({ data: createdTask });

      const result = await taskService.create(newTask);

      expect(apiClient.post).toHaveBeenCalledWith("/tasks/", newTask);
      expect(result).toEqual(createdTask);
    });
  });

  describe("update", () => {
    it("updates a task", async () => {
      const updateData = { title: "Updated Title" };
      const updatedTask = {
        id: "1",
        project_id: "p1",
        title: "Updated Title",
        status: "pending",
        priority: 5,
        created_at: "2024-01-01",
      };
      vi.mocked(apiClient.put).mockResolvedValue({ data: updatedTask });

      const result = await taskService.update("1", updateData);

      expect(apiClient.put).toHaveBeenCalledWith("/tasks/1", updateData);
      expect(result).toEqual(updatedTask);
    });
  });

  describe("updateStatus", () => {
    it("updates task status", async () => {
      const statusUpdate = { status: "completed" as const };
      const updatedTask = {
        id: "1",
        project_id: "p1",
        title: "Task",
        status: "completed" as const,
        priority: 5,
        created_at: "2024-01-01",
      };
      vi.mocked(apiClient.patch).mockResolvedValue({ data: updatedTask });

      const result = await taskService.updateStatus("1", statusUpdate);

      expect(apiClient.patch).toHaveBeenCalledWith(
        "/tasks/1/status",
        statusUpdate,
      );
      expect(result).toEqual(updatedTask);
    });
  });

  describe("delete", () => {
    it("deletes a task", async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: undefined });

      await taskService.delete("1");

      expect(apiClient.delete).toHaveBeenCalledWith("/tasks/1");
    });
  });
});
