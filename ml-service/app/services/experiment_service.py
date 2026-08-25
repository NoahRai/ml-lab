from time import perf_counter

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.schemas.experiment import ExperimentResult, ModelResult, ProblemType
from app.services.dataset_service import DatasetValidationError, UploadedDataset


class ExperimentService:
    """Runs the first reproducible baseline for a validated tabular dataset."""

    def run(
        self,
        upload: UploadedDataset,
        target_column: str,
        problem_type: ProblemType,
        train_split: float = 0.8,
        random_state: int = 42,
    ) -> ExperimentResult:
        dataframe = self._load_dataframe(upload)
        if target_column not in dataframe.columns:
            raise DatasetValidationError(f"The target column '{target_column}' was not found in this dataset.")
        if not 0.5 <= train_split < 1:
            raise DatasetValidationError("Train split must be between 0.5 and 0.99.")

        features, target = self._prepare_target(dataframe, target_column, problem_type)
        x_train, x_test, y_train, y_test = self._split(features, target, problem_type, train_split, random_state)
        pipeline = self._build_pipeline(x_train, problem_type)

        started_at = perf_counter()
        pipeline.fit(x_train, y_train)
        training_time_ms = round((perf_counter() - started_at) * 1000, 2)
        predictions = pipeline.predict(x_test)
        metrics = self._evaluate(y_test, predictions, problem_type)
        model_name = "Linear Regression" if problem_type == "regression" else "Logistic Regression"
        primary_metric_name = "r2" if problem_type == "regression" else "accuracy"
        notes = [
            "Preprocessing was fit on training data only; test data was held out until evaluation.",
            "This is a baseline result. Compare it with additional model families in the next phase.",
        ]
        return ExperimentResult(
            dataset_name=upload.filename,
            target_column=target_column,
            problem_type=problem_type,
            training_rows=len(x_train),
            testing_rows=len(x_test),
            models=[ModelResult(name=model_name, metrics=metrics, training_time_ms=training_time_ms)],
            best_model=model_name,
            primary_metric_name=primary_metric_name,
            primary_metric_value=metrics[primary_metric_name],
            notes=notes,
        )

    @staticmethod
    def _load_dataframe(upload: UploadedDataset) -> pd.DataFrame:
        from app.services.dataset_service import DatasetInspectionService

        inspector = DatasetInspectionService()
        inspector._validate_filename(upload.filename)
        inspector._validate_size(upload.content)
        text = inspector._decode(upload.content)
        inspector._read_headers(text)
        dataframe = inspector._read_dataframe(text)
        inspector._validate_dimensions(dataframe)
        return dataframe

    @staticmethod
    def _prepare_target(
        dataframe: pd.DataFrame, target_column: str, problem_type: ProblemType
    ) -> tuple[pd.DataFrame, pd.Series]:
        usable = dataframe.dropna(subset=[target_column]).copy()
        if len(usable) < 10:
            raise DatasetValidationError("Fewer than 10 rows have a target value. Choose a more complete target column.")
        target = usable.pop(target_column)
        features = usable.dropna(axis=1, how="all")
        if features.empty:
            raise DatasetValidationError("No usable feature columns remain after removing the target.")
        if problem_type == "regression":
            numeric_target = pd.to_numeric(target, errors="coerce")
            if numeric_target.isna().any():
                raise DatasetValidationError("Regression requires a target column containing numeric values.")
            return features, numeric_target
        if target.nunique() < 2:
            raise DatasetValidationError(
                "The selected target column contains only one unique class. Classification requires at least two classes."
            )
        return features, target.astype(str)

    @staticmethod
    def _split(
        features: pd.DataFrame,
        target: pd.Series,
        problem_type: ProblemType,
        train_split: float,
        random_state: int,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        test_size = 1 - train_split
        stratify = None
        if problem_type == "classification" and target.value_counts().min() >= 2:
            stratify = target
        try:
            return train_test_split(
                features, target, test_size=test_size, random_state=random_state, stratify=stratify
            )
        except ValueError as error:
            raise DatasetValidationError(
                "We couldn't create a reliable train/test split. Add more rows or reduce the number of target classes."
            ) from error

    @staticmethod
    def _build_pipeline(features: pd.DataFrame, problem_type: ProblemType) -> Pipeline:
        numeric_columns = features.select_dtypes(include="number").columns.tolist()
        categorical_columns = [column for column in features.columns if column not in numeric_columns]
        transformers = []
        if numeric_columns:
            transformers.append(
                ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_columns)
            )
        if categorical_columns:
            transformers.append(
                (
                    "categorical",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("encoder", OneHotEncoder(handle_unknown="ignore")),
                        ]
                    ),
                    categorical_columns,
                )
            )
        preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
        estimator = LinearRegression() if problem_type == "regression" else LogisticRegression(max_iter=1_000)
        return Pipeline([("preprocessor", preprocessor), ("model", estimator)])

    @staticmethod
    def _evaluate(target: pd.Series, predictions: object, problem_type: ProblemType) -> dict[str, float]:
        if problem_type == "regression":
            return {
                "r2": round(float(r2_score(target, predictions)), 4),
                "rmse": round(float(mean_squared_error(target, predictions) ** 0.5), 4),
                "mae": round(float(mean_absolute_error(target, predictions)), 4),
                "mse": round(float(mean_squared_error(target, predictions)), 4),
            }
        return {
            "accuracy": round(float(accuracy_score(target, predictions)), 4),
            "precision": round(float(precision_score(target, predictions, average="weighted", zero_division=0)), 4),
            "recall": round(float(recall_score(target, predictions, average="weighted", zero_division=0)), 4),
            "f1": round(float(f1_score(target, predictions, average="weighted", zero_division=0)), 4),
        }
