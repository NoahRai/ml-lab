export type ColumnKind = "numeric" | "categorical" | "datetime" | "unknown";

export interface ColumnSummary {
  name: string;
  kind: ColumnKind;
  missing_count: number;
  unique_count: number;
  sample_values: string[];
  minimum: number | null;
  mean: number | null;
  maximum: number | null;
}

export interface DatasetAnalysis {
  filename: string;
  rows: number;
  columns: number;
  missing_cells: number;
  missing_percentage: number;
  numeric_columns: string[];
  categorical_columns: string[];
  potential_target_columns: string[];
  column_summaries: ColumnSummary[];
  preview: Array<Record<string, string | number | boolean | null>>;
}

export interface DatasetApiError {
  detail: string;
}

export type ProblemType = "classification" | "regression";

export interface ExperimentModelResult {
  name: string;
  metrics: Record<string, number>;
  training_time_ms: number;
  training_history: Array<{ epoch: number; training_loss: number; validation_loss: number }>;
}

export interface ExperimentResult {
  dataset_name: string;
  target_column: string;
  problem_type: ProblemType;
  training_rows: number;
  testing_rows: number;
  models: ExperimentModelResult[];
  best_model: string;
  primary_metric_name: string;
  primary_metric_value: number;
  notes: string[];
  feature_importance: Array<{ feature: string; importance: number }>;
  prediction_points: Array<{ actual: number | string; predicted: number | string; residual: number | null }>;
  error_analysis: Array<{
    actual: number | string;
    predicted: number | string;
    error: number | null;
    feature_values: Record<string, string | number | boolean | null>;
  }>;
  confusion_matrix: { labels: string[]; matrix: number[][] } | null;
}
