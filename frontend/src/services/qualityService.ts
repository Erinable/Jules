/**
 * Quality Metric API service
 */

import apiClient from "./apiClient";
import type {
  QualityMetric,
  QualityMetricCreate,
  QualityMetricResponse,
  PaginationParams,
} from "@/types";

export const qualityService = {
  /**
   * Get quality metric by ID
   */
  async getById(metricId: string): Promise<QualityMetric> {
    const response = await apiClient.get<QualityMetric>(`/quality/${metricId}`);
    return response.data;
  },

  /**
   * Create new quality metric
   */
  async create(metric: QualityMetricCreate): Promise<QualityMetricResponse> {
    const response = await apiClient.post<QualityMetricResponse>(
      "/quality/",
      metric,
    );
    return response.data;
  },

  /**
   * Get latest quality metric for a project
   */
  async getLatest(projectId: string): Promise<QualityMetric> {
    const response = await apiClient.get<QualityMetric>(
      `/quality/project/${projectId}/latest`,
    );
    return response.data;
  },

  /**
   * Get quality metric history for a project
   */
  async getHistory(
    projectId: string,
    params?: PaginationParams,
  ): Promise<QualityMetric[]> {
    const response = await apiClient.get<QualityMetric[]>(
      `/quality/project/${projectId}/history`,
      { params },
    );
    return response.data;
  },

  /**
   * Delete quality metric
   */
  async delete(metricId: string): Promise<void> {
    await apiClient.delete(`/quality/${metricId}`);
  },
};
