import csv
import io
from dataclasses import dataclass

import pandas as pd

from app.schemas.dataset import ColumnSummary, DatasetAnalysis


MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_ROWS = 50_000
MAX_COLUMNS = 100
MIN_ROWS = 10
PREVIEW_ROWS = 15


class DatasetValidationError(ValueError):
    """A user-safe validation failure for an uploaded dataset."""


@dataclass(frozen=True)
class UploadedDataset:
    filename: str
    content: bytes


class DatasetInspectionService:
    """Validates CSV uploads and produces safe metadata for experiment setup."""

    def analyze(self, upload: UploadedDataset) -> DatasetAnalysis:
        self._validate_filename(upload.filename)
        self._validate_size(upload.content)
        text = self._decode(upload.content)
        headers = self._read_headers(text)
        dataframe = self._read_dataframe(text)
        self._validate_dimensions(dataframe)

        missing_cells = int(dataframe.isna().sum().sum())
        total_cells = dataframe.shape[0] * dataframe.shape[1]
        summaries = [self._summarize_column(dataframe, column) for column in dataframe.columns]
        numeric = [summary.name for summary in summaries if summary.kind == "numeric"]
        categorical = [summary.name for summary in summaries if summary.kind == "categorical"]
        preview = self._preview(dataframe)

        return DatasetAnalysis(
            filename=upload.filename,
            rows=int(dataframe.shape[0]),
            columns=len(headers),
            missing_cells=missing_cells,
            missing_percentage=round((missing_cells / total_cells) * 100, 2) if total_cells else 0,
            numeric_columns=numeric,
            categorical_columns=categorical,
            potential_target_columns=self._potential_targets(summaries),
            column_summaries=summaries,
            preview=preview,
        )

    @staticmethod
    def _validate_filename(filename: str) -> None:
        if not filename.lower().endswith(".csv"):
            raise DatasetValidationError("Please upload a CSV file with a .csv extension.")

    @staticmethod
    def _validate_size(content: bytes) -> None:
        if not content:
            raise DatasetValidationError("The uploaded file is empty.")
        if len(content) > MAX_FILE_BYTES:
            raise DatasetValidationError("This file is larger than the 10 MB upload limit.")

    @staticmethod
    def _decode(content: bytes) -> str:
        try:
            return content.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise DatasetValidationError("We couldn't read this CSV. Save it as a UTF-8 encoded file and try again.") from error

    @staticmethod
    def _read_headers(text: str) -> list[str]:
        try:
            headers = next(csv.reader(io.StringIO(text)))
        except StopIteration as error:
            raise DatasetValidationError("The uploaded file is empty.") from error
        normalized = [header.strip() for header in headers]
        if not normalized or all(not header for header in normalized):
            raise DatasetValidationError("The CSV needs a header row with at least one column name.")
        if any(not header for header in normalized):
            raise DatasetValidationError("CSV column names cannot be blank.")
        if len(set(normalized)) != len(normalized):
            raise DatasetValidationError("The CSV contains duplicate column headers. Rename them and try again.")
        if len(normalized) > MAX_COLUMNS:
            raise DatasetValidationError(f"This dataset has more than the {MAX_COLUMNS}-column limit.")
        return normalized

    @staticmethod
    def _read_dataframe(text: str) -> pd.DataFrame:
        try:
            dataframe = pd.read_csv(io.StringIO(text))
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeError) as error:
            raise DatasetValidationError("We couldn't parse this file as a CSV. Check its delimiter and header row.") from error
        if dataframe.empty:
            raise DatasetValidationError("This dataset has no data rows.")
        return dataframe

    @staticmethod
    def _validate_dimensions(dataframe: pd.DataFrame) -> None:
        if len(dataframe) < MIN_ROWS:
            raise DatasetValidationError(
                f"This dataset has only {len(dataframe)} rows. Upload at least {MIN_ROWS} rows to run an experiment."
            )
        if len(dataframe) > MAX_ROWS:
            raise DatasetValidationError(f"This dataset has more than the {MAX_ROWS:,}-row limit.")

    @staticmethod
    def _summarize_column(dataframe: pd.DataFrame, column: str) -> ColumnSummary:
        values = dataframe[column]
        minimum: float | None = None
        mean: float | None = None
        maximum: float | None = None
        if pd.api.types.is_numeric_dtype(values):
            kind: str = "numeric"
            numeric_values = values.dropna()
            if not numeric_values.empty:
                minimum = float(numeric_values.min())
                mean = round(float(numeric_values.mean()), 4)
                maximum = float(numeric_values.max())
        elif pd.api.types.is_datetime64_any_dtype(values):
            kind = "datetime"
        elif pd.api.types.is_object_dtype(values) or pd.api.types.is_string_dtype(values):
            kind = "categorical"
        else:
            kind = "unknown"
        sample_values = [str(value) for value in values.dropna().drop_duplicates().head(3).tolist()]
        return ColumnSummary(
            name=column,
            kind=kind,
            missing_count=int(values.isna().sum()),
            unique_count=int(values.nunique(dropna=True)),
            sample_values=sample_values,
            minimum=minimum,
            mean=mean,
            maximum=maximum,
        )

    @staticmethod
    def _potential_targets(summaries: list[ColumnSummary]) -> list[str]:
        return [
            summary.name
            for summary in summaries
            if summary.unique_count > 1 and summary.unique_count < MAX_ROWS
        ]

    @staticmethod
    def _preview(dataframe: pd.DataFrame) -> list[dict[str, str | int | float | bool | None]]:
        sanitized = dataframe.head(PREVIEW_ROWS).where(pd.notna(dataframe), None)
        return sanitized.to_dict(orient="records")
