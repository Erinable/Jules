/**
 * Code File API service
 */

import apiClient from "./apiClient";
import type {
  CodeFile,
  CodeFileCreate,
  CodeFileUpdate,
  CodeFileResponse,
  CodeVersion,
} from "@/types";

export const codeFileService = {
  /**
   * Get all code files for a project
   */
  async getByProject(projectId: string): Promise<CodeFile[]> {
    const response = await apiClient.get<CodeFile[]>(
      `/code-files/project/${projectId}`,
    );
    return response.data;
  },

  /**
   * Get code file by ID
   */
  async getById(fileId: string): Promise<CodeFile> {
    const response = await apiClient.get<CodeFile>(`/code-files/${fileId}`);
    return response.data;
  },

  /**
   * Create new code file
   */
  async create(file: CodeFileCreate): Promise<CodeFileResponse> {
    const response = await apiClient.post<CodeFileResponse>(
      "/code-files/",
      file,
    );
    return response.data;
  },

  /**
   * Update code file
   */
  async update(
    fileId: string,
    file: CodeFileUpdate,
  ): Promise<CodeFileResponse> {
    const response = await apiClient.put<CodeFileResponse>(
      `/code-files/${fileId}`,
      file,
    );
    return response.data;
  },

  /**
   * Delete code file
   */
  async delete(fileId: string): Promise<void> {
    await apiClient.delete(`/code-files/${fileId}`);
  },

  /**
   * Get version history for a code file
   */
  async getVersions(fileId: string): Promise<CodeVersion[]> {
    const response = await apiClient.get<CodeVersion[]>(
      `/code-files/${fileId}/versions`,
    );
    return response.data;
  },
};
