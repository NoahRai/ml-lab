from typing import Literal

from pydantic import BaseModel, Field


ProblemType = Literal["regression", "classification"]


class ModelResult(BaseModel):
    name: str
    metrics: dict[str, float]
    training_time_ms: float
    training_history: list[dict[str, float]] = Field(default_factory=list)


class FeatureImportance(BaseModel):
    feature: str
    importance: float


class PredictionPoint(BaseModel):
    actual: float | str
    predicted: float | str
    residual: float | None = None


class ErrorAnalysisRow(BaseModel):
    actual: float | str
    predicted: float | str
    error: float | None = None
    feature_values: dict[str, str | int | float | bool | None]


class ConfusionMatrix(BaseModel):
    labels: list[str]
    matrix: list[list[int]]


class ExperimentResult(BaseModel):
    dataset_name: str
    target_column: str
    problem_type: ProblemType
    training_rows: int
    testing_rows: int
    models: list[ModelResult]
    best_model: str
    primary_metric_name: str
    primary_metric_value: float
    notes: list[str] = Field(default_factory=list)
    feature_importance: list[FeatureImportance] = Field(default_factory=list)
    prediction_points: list[PredictionPoint] = Field(default_factory=list)
    error_analysis: list[ErrorAnalysisRow] = Field(default_factory=list)
    confusion_matrix: ConfusionMatrix | None = None
