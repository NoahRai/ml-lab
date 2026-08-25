from typing import Literal

from pydantic import BaseModel, Field


class ColumnSummary(BaseModel):
    name: str
    kind: Literal["numeric", "categorical", "datetime", "unknown"]
    missing_count: int
    unique_count: int
    sample_values: list[str]
    minimum: float | None = None
    mean: float | None = None
    maximum: float | None = None


class DatasetAnalysis(BaseModel):
    filename: str
    rows: int
    columns: int
    missing_cells: int
    missing_percentage: float
    numeric_columns: list[str]
    categorical_columns: list[str]
    potential_target_columns: list[str]
    column_summaries: list[ColumnSummary]
    preview: list[dict[str, str | int | float | bool | None]] = Field(max_length=15)
