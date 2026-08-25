from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_healthy_status() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "ml-service"}


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
