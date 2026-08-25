from abc import ABC, abstractmethod
from time import perf_counter
from typing import Any


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
