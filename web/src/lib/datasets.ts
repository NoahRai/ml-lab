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
}
