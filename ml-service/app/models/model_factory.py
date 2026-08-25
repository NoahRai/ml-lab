from typing import Any

from app.models.base_model import BaseMLModel
from app.models.gradient_boosting_model import GradientBoostingModel
from app.models.linear_model import LinearModel
from app.models.random_forest_model import RandomForestModel


class ModelFactory:
    """Creates model implementations without exposing construction details to experiments."""

    _model_classes = {
        "linear": LinearModel,
        "random_forest": RandomForestModel,
        "gradient_boosting": GradientBoostingModel,
    }

    @classmethod
    def create_model(cls, model_type: str, problem_type: str, config: dict[str, Any] | None = None) -> BaseMLModel:
        try:
            return cls._model_classes[model_type](problem_type, config)
        except KeyError as error:
            supported = ", ".join(cls._model_classes)
            raise ValueError(f"Unsupported model '{model_type}'. Choose one of: {supported}.") from error
