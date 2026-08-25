from typing import Any

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from app.models.base_model import BaseMLModel


class RandomForestModel(BaseMLModel):
    model_type = "random_forest"
    name = "Random Forest"

    def __init__(self, problem_type: str, config: dict[str, Any] | None = None) -> None:
        self.problem_type = problem_type
        super().__init__(config)

    def _create_estimator(self) -> RandomForestClassifier | RandomForestRegressor:
        defaults = {"n_estimators": 150, "random_state": 42, "n_jobs": -1}
        defaults.update(self.config)
        if self.problem_type == "regression":
            return RandomForestRegressor(**defaults)
        return RandomForestClassifier(**defaults)
