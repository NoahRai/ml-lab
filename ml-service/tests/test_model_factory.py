from app.models.gradient_boosting_model import GradientBoostingModel
from app.models.linear_model import LinearModel
from app.models.model_factory import ModelFactory
from app.models.random_forest_model import RandomForestModel


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
