from app.models.gradient_boosting_model import GradientBoostingModel
from app.models.linear_model import LinearModel
from app.models.model_factory import ModelFactory
from app.models.random_forest_model import RandomForestModel
from app.models.neural_network_model import NeuralNetworkModel
import numpy as np


def test_model_factory_creates_random_forest() -> None:
    model = ModelFactory.create_model("random_forest", "regression")

    assert isinstance(model, RandomForestModel)
    assert model.name == "Random Forest"


def test_model_factory_creates_task_appropriate_linear_model() -> None:
    model = ModelFactory.create_model("linear", "classification")

    assert isinstance(model, LinearModel)
    assert model.name == "Logistic Regression"


def test_model_factory_creates_gradient_boosting() -> None:
    model = ModelFactory.create_model("gradient_boosting", "regression")

    assert isinstance(model, GradientBoostingModel)


def test_model_factory_creates_neural_network() -> None:
    model = ModelFactory.create_model("neural_network", "regression", {"epochs": 2})

    assert isinstance(model, NeuralNetworkModel)


def test_neural_network_trains_and_records_validation_history() -> None:
    features = np.asarray([[float(index), float(index % 3)] for index in range(20)])
    target = np.asarray([float(index * 2) for index in range(20)])
    model = NeuralNetworkModel("regression", {"epochs": 3, "patience": 3, "batch_size": 8})

    model.train(features, target)

    assert len(model.training_history) == 3
    assert model.training_time_ms is not None
    assert len(model.predict(features[:2])) == 2
