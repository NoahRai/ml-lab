from abc import ABC, abstractmethod
from time import perf_counter
from typing import Any

import numpy as np


class BaseMLModel(ABC):
    """Common interface and timing behavior for tabular ML estimators."""

    model_type: str
    name: str

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.training_time_ms: float | None = None
        self._estimator = self._create_estimator()

    @abstractmethod
    def _create_estimator(self) -> Any:
        """Create the underlying sklearn estimator for this model family."""

    def train(self, features: Any, target: Any) -> None:
        started_at = perf_counter()
        self._estimator.fit(features, target)
        self.training_time_ms = round((perf_counter() - started_at) * 1000, 2)

    def predict(self, features: Any) -> Any:
        return self._estimator.predict(features)

    def get_params(self) -> dict[str, Any]:
        return self._estimator.get_params(deep=False)

    def get_feature_importance(self, feature_names: list[str]) -> list[tuple[str, float]]:
        """Return normalized model importance only for models that expose it."""
        raw_importance = getattr(self._estimator, "feature_importances_", None)
        if raw_importance is None and hasattr(self._estimator, "coef_"):
            coefficients = np.asarray(self._estimator.coef_)
            raw_importance = np.abs(coefficients).mean(axis=0) if coefficients.ndim > 1 else np.abs(coefficients)
        if raw_importance is None:
            return []
        total = float(np.sum(raw_importance))
        if total == 0:
            return []
        pairs = zip(feature_names, raw_importance, strict=False)
        return sorted(((name, round(float(value / total), 6)) for name, value in pairs), key=lambda item: item[1], reverse=True)
