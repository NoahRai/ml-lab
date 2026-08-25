from typing import Literal

from pydantic import BaseModel, Field


ProblemType = Literal["regression", "classification"]


class ModelResult(BaseModel):
    name: str
    metrics: dict[str, float]
    training_time_ms: float


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
