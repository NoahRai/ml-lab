from typing import Any

from sklearn.linear_model import LinearRegression, LogisticRegression

from app.models.base_model import BaseMLModel


class LinearModel(BaseMLModel):
    model_type = "linear"
    name = "Linear Regression"

    def __init__(self, problem_type: str, config: dict[str, Any] | None = None) -> None:
        self.problem_type = problem_type
        if problem_type == "classification":
            self.name = "Logistic Regression"
        super().__init__(config)

    def _create_estimator(self) -> LinearRegression | LogisticRegression:
        if self.problem_type == "regression":
            return LinearRegression(**self.config)
        return LogisticRegression(max_iter=1_000, **self.config)
