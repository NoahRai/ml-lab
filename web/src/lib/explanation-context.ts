import type { ExperimentResult } from "@/lib/datasets";

export function buildExperimentContext(result: ExperimentResult) {
  return {
    problem_type: result.problem_type,
    target_column: result.target_column,
    train_rows: result.training_rows,
    test_rows: result.testing_rows,
    best_model: result.best_model,
    primary_metric: {
      name: result.primary_metric_name,
      value: result.primary_metric_value,
    },
    models: result.models.map((model) => ({ name: model.name, metrics: model.metrics, training_time_ms: model.training_time_ms })),
    feature_importance: result.feature_importance.map((item) => ({ feature: item.feature, importance: item.importance })),
    error_count: result.error_analysis.length,
  };
}
