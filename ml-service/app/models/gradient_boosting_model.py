from typing import Any

from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor

from app.models.base_model import BaseMLModel


class GradientBoostingModel(BaseMLModel):
    model_type = "gradient_boosting"
    name = "Gradient Boosting"

    def __init__(self, problem_type: str, config: dict[str, Any] | None = None) -> None:
        self.problem_type = problem_type
        super().__init__(config)

    def _create_estimator(self) -> GradientBoostingClassifier | GradientBoostingRegressor:
        defaults = {"n_estimators": 100, "random_state": 42}
        defaults.update(self.config)
        if self.problem_type == "regression":
            return GradientBoostingRegressor(**defaults)
        return GradientBoostingClassifier(**defaults)
