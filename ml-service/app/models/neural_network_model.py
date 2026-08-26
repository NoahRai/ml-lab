from typing import Any

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch import Tensor, nn
from torch.utils.data import DataLoader, TensorDataset

from app.models.base_model import BaseMLModel


class TabularNeuralNetwork(nn.Module):
    """Two-hidden-layer network for preprocessed tabular features."""

    def __init__(self, input_size: int, output_size: int, hidden_size: int, dropout: float) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, output_size),
        )

    def forward(self, features: Tensor) -> Tensor:
        """Accept [batch_size, feature_count] tensors and return model outputs."""
        return self.layers(features)


class NeuralNetworkModel(BaseMLModel):
    """PyTorch training loop with validation monitoring and early stopping."""

    model_type = "neural_network"
    name = "Neural Network"

    def __init__(self, problem_type: str, config: dict[str, Any] | None = None) -> None:
        self.problem_type = problem_type
        self.training_history: list[dict[str, float]] = []
        self._classes: list[str] = []
        super().__init__(config)

    def _create_estimator(self) -> None:
        return None

    def train(self, features: Any, target: Any) -> None:
        config = {
            "hidden_size": 32,
            "dropout": 0.15,
            "learning_rate": 0.001,
            "epochs": 50,
            "batch_size": 32,
            "patience": 8,
        }
        config.update(self.config)
        torch.manual_seed(42)
        feature_array = np.asarray(features, dtype=np.float32)
        target_array = np.asarray(target)
        if self.problem_type == "classification":
            self._classes = sorted(str(value) for value in np.unique(target_array))
            class_indices = np.asarray([self._classes.index(str(value)) for value in target_array], dtype=np.int64)
            target_array = class_indices

        indices = np.arange(len(feature_array))
        train_indices, validation_indices = train_test_split(indices, test_size=0.15, random_state=42)
        train_x = torch.tensor(feature_array[train_indices], dtype=torch.float32)
        validation_x = torch.tensor(feature_array[validation_indices], dtype=torch.float32)
        if self.problem_type == "regression":
            train_y = torch.tensor(target_array[train_indices], dtype=torch.float32).view(-1, 1)
            validation_y = torch.tensor(target_array[validation_indices], dtype=torch.float32).view(-1, 1)
            output_size = 1
            criterion: nn.Module = nn.MSELoss()
        else:
            train_y = torch.tensor(target_array[train_indices], dtype=torch.long)
            validation_y = torch.tensor(target_array[validation_indices], dtype=torch.long)
            output_size = len(self._classes)
            criterion = nn.CrossEntropyLoss()

        self._estimator = TabularNeuralNetwork(
            input_size=feature_array.shape[1],
            output_size=output_size,
            hidden_size=int(config["hidden_size"]),
            dropout=float(config["dropout"]),
        )
        optimizer = torch.optim.Adam(self._estimator.parameters(), lr=float(config["learning_rate"]))
        loader = DataLoader(TensorDataset(train_x, train_y), batch_size=int(config["batch_size"]), shuffle=True)
        best_validation_loss = float("inf")
        best_state: dict[str, Tensor] | None = None
        stale_epochs = 0
        started_at = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        if started_at is not None:
            end_event = torch.cuda.Event(enable_timing=True)
            started_at.record()
        else:
            import time
            start_time = time.perf_counter()

        for epoch in range(1, int(config["epochs"]) + 1):
            self._estimator.train()
            total_loss = 0.0
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                predictions = self._estimator(batch_x)
                loss = criterion(predictions, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += float(loss.item()) * len(batch_x)
            training_loss = total_loss / len(train_x)
            self._estimator.eval()
            with torch.no_grad():
                validation_loss = float(criterion(self._estimator(validation_x), validation_y).item())
            self.training_history.append({"epoch": float(epoch), "training_loss": round(training_loss, 6), "validation_loss": round(validation_loss, 6)})
            if validation_loss < best_validation_loss:
                best_validation_loss = validation_loss
                best_state = {key: value.detach().clone() for key, value in self._estimator.state_dict().items()}
                stale_epochs = 0
            else:
                stale_epochs += 1
                if stale_epochs >= int(config["patience"]):
                    break
        if best_state is not None:
            self._estimator.load_state_dict(best_state)
        if started_at is not None:
            end_event.record()
            torch.cuda.synchronize()
            self.training_time_ms = round(float(started_at.elapsed_time(end_event)), 2)
        else:
            self.training_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

    def predict(self, features: Any) -> np.ndarray:
        if self._estimator is None:
            raise RuntimeError("NeuralNetworkModel must be trained before prediction.")
        self._estimator.eval()
        with torch.no_grad():
            outputs = self._estimator(torch.tensor(np.asarray(features), dtype=torch.float32))
        if self.problem_type == "regression":
            return outputs.squeeze(1).numpy()
        return np.asarray([self._classes[index] for index in outputs.argmax(dim=1).numpy()])

    def get_params(self) -> dict[str, Any]:
        return self.config
