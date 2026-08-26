from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_healthy_status() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "ml-service"}


def test_iris_demo_dataset_is_a_valid_csv() -> None:
    response = TestClient(app).get("/dataset/demo/iris")

    assert response.status_code == 200
    assert "species" in response.text.splitlines()[0]
    assert len(response.text.splitlines()) == 151


def test_dataset_analysis_returns_preview_and_column_types() -> None:
    content = "study_hours,attendance,final_grade\n2,80,71\n3,83,74\n4,85,77\n5,88,81\n6,90,83\n7,92,86\n8,94,89\n9,95,91\n10,96,93\n11,98,96\n"
    response = TestClient(app).post(
        "/dataset/analyze", files={"file": ("students.csv", content, "text/csv")}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == 10
    assert body["numeric_columns"] == ["study_hours", "attendance", "final_grade"]
    assert body["preview"][0]["final_grade"] == 71
    assert body["column_summaries"][0]["mean"] == 6.5


def test_dataset_analysis_rejects_duplicate_headers() -> None:
    content = "score,score\n1,2\n3,4\n5,6\n7,8\n9,10\n11,12\n13,14\n15,16\n17,18\n19,20\n"
    response = TestClient(app).post(
        "/dataset/analyze", files={"file": ("duplicate.csv", content, "text/csv")}
    )

    assert response.status_code == 422
    assert "duplicate column headers" in response.json()["detail"]


def test_regression_experiment_returns_real_metrics() -> None:
    rows = ["hours,attendance,grade"]
    rows.extend(f"{hour},{70 + hour},{50 + hour * 4}" for hour in range(1, 31))
    response = TestClient(app).post(
        "/experiment/run",
        files={"file": ("grades.csv", "\n".join(rows), "text/csv")},
        data={"target_column": "grade", "problem_type": "regression"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["best_model"] == "Linear Regression"
    assert body["models"][0]["metrics"]["r2"] > 0.99
    assert body["training_rows"] == 24
    assert body["testing_rows"] == 6
    assert len(body["prediction_points"]) == 6
    assert body["feature_importance"]


def test_experiment_compares_requested_models_on_same_split() -> None:
    rows = ["hours,attendance,grade"]
    rows.extend(f"{hour},{70 + hour},{50 + hour * 4}" for hour in range(1, 31))
    response = TestClient(app).post(
        "/experiment/run",
        files={"file": ("grades.csv", "\n".join(rows), "text/csv")},
        data={
            "target_column": "grade",
            "problem_type": "regression",
            "model_types": ["linear", "random_forest", "gradient_boosting"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert [model["name"] for model in body["models"]] == [
        "Linear Regression",
        "Random Forest",
        "Gradient Boosting",
    ]


def test_classification_experiment_returns_real_metrics() -> None:
    rows = ["hours,attendance,passed"]
    rows.extend(f"{hour},{65 + hour},{'yes' if hour > 15 else 'no'}" for hour in range(1, 31))
    response = TestClient(app).post(
        "/experiment/run",
        files={"file": ("outcomes.csv", "\n".join(rows), "text/csv")},
        data={"target_column": "passed", "problem_type": "classification"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["best_model"] == "Logistic Regression"
    assert body["models"][0]["metrics"]["accuracy"] > 0.9
    assert body["confusion_matrix"]["labels"] == ["no", "yes"]
