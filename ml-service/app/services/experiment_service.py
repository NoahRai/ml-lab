import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

from app.models.model_factory import ModelFactory
from app.preprocessing.preprocessor import DataPreprocessor
from app.schemas.experiment import (
    ConfusionMatrix,
    ErrorAnalysisRow,
    ExperimentResult,
    FeatureImportance,
    ModelResult,
    PredictionPoint,
    ProblemType,
)
from app.services.dataset_service import DatasetValidationError, UploadedDataset


class ExperimentService:
    """Runs reproducible comparisons using one shared train/test split."""

    def run(
        self,
        upload: UploadedDataset,
        target_column: str,
        problem_type: ProblemType,
        model_types: list[str] | None = None,
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
        selected_models = model_types or ["linear"]
        self._validate_models(selected_models)
        preprocessor = DataPreprocessor()
        processed_train = preprocessor.fit_transform(x_train)
        processed_test = preprocessor.transform(x_test)
        model_results = []
        completed_models = []
        for model_type in selected_models:
            try:
                model = ModelFactory.create_model(model_type, problem_type)
            except ValueError as error:
                raise DatasetValidationError(str(error)) from error
            model.train(processed_train, y_train)
            predictions = model.predict(processed_test)
            completed_models.append((model, predictions))
            model_results.append(
                ModelResult(
                    name=model.name,
                    metrics=self._evaluate(y_test, predictions, problem_type),
                    training_time_ms=model.training_time_ms or 0,
                    training_history=getattr(model, "training_history", []),
                )
            )
        primary_metric_name = "r2" if problem_type == "regression" else "accuracy"
        best_result = max(model_results, key=lambda result: result.metrics[primary_metric_name])
        best_index = model_results.index(best_result)
        best_model, best_predictions = completed_models[best_index]
        notes = [
            "Preprocessing was fit on training data only; test data was held out until evaluation.",
            "All models used the same split so their results are directly comparable.",
        ]
        return ExperimentResult(
            dataset_name=upload.filename,
            target_column=target_column,
            problem_type=problem_type,
            training_rows=len(x_train),
            testing_rows=len(x_test),
            models=model_results,
            best_model=best_result.name,
            primary_metric_name=primary_metric_name,
            primary_metric_value=best_result.metrics[primary_metric_name],
            notes=notes,
            feature_importance=[
                FeatureImportance(feature=feature, importance=importance)
                for feature, importance in best_model.get_feature_importance(preprocessor.get_feature_names())[:10]
            ],
            prediction_points=self._prediction_points(y_test, best_predictions, problem_type),
            error_analysis=self._error_analysis(x_test, y_test, best_predictions, problem_type),
            confusion_matrix=self._confusion_matrix(y_test, best_predictions, problem_type),
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
    def _validate_models(model_types: list[str]) -> None:
        if not model_types:
            raise DatasetValidationError("Select at least one model to run.")
        if len(model_types) > 4:
            raise DatasetValidationError("You can compare up to four models in one experiment.")
        if len(set(model_types)) != len(model_types):
            raise DatasetValidationError("Select each model only once.")

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

    @staticmethod
    def _prediction_points(target: pd.Series, predictions: object, problem_type: ProblemType) -> list[PredictionPoint]:
        points = []
        for actual, predicted in zip(target.tolist(), predictions, strict=False):
            if problem_type == "regression":
                actual_value = float(actual)
                predicted_value = float(predicted)
                points.append(PredictionPoint(actual=actual_value, predicted=predicted_value, residual=round(actual_value - predicted_value, 4)))
            else:
                points.append(PredictionPoint(actual=str(actual), predicted=str(predicted)))
        return points

    @staticmethod
    def _error_analysis(
        features: pd.DataFrame, target: pd.Series, predictions: object, problem_type: ProblemType
    ) -> list[ErrorAnalysisRow]:
        rows = []
        for (_, feature_row), actual, predicted in zip(features.iterrows(), target.tolist(), predictions, strict=False):
            serialized_features = {
                column: None if pd.isna(value) else value.item() if hasattr(value, "item") else value
                for column, value in feature_row.items()
            }
            if problem_type == "regression":
                error = abs(float(actual) - float(predicted))
                rows.append(ErrorAnalysisRow(actual=float(actual), predicted=float(predicted), error=round(error, 4), feature_values=serialized_features))
            elif actual != predicted:
                rows.append(ErrorAnalysisRow(actual=str(actual), predicted=str(predicted), feature_values=serialized_features))
        if problem_type == "regression":
            rows.sort(key=lambda row: row.error or 0, reverse=True)
        return rows[:10]

    @staticmethod
    def _confusion_matrix(target: pd.Series, predictions: object, problem_type: ProblemType) -> ConfusionMatrix | None:
        if problem_type != "classification":
            return None
        labels = sorted(set(target.astype(str)).union(str(value) for value in predictions))
        matrix = confusion_matrix(target.astype(str), [str(value) for value in predictions], labels=labels)
        return ConfusionMatrix(labels=labels, matrix=matrix.tolist())
