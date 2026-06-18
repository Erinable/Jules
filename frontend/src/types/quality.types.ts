/**
 * Quality Metric type definitions based on backend Pydantic schemas
 */

export interface QualityMetric {
  id: string;
  project_id: string;
  avg_complexity: number;
  maintainability_index: number;
  security_issues: number;
  test_coverage: number;
  measured_at: string;
  [key: string]: unknown;
}

export interface QualityMetricCreate {
  project_id: string;
  avg_complexity: number;
  maintainability_index?: number;
  security_issues?: number;
  test_coverage?: number;
}

export interface QualityMetricResponse extends QualityMetric {}
