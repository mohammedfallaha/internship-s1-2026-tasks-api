from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_then_get() -> None:
    r = client.post("/tasks", json={"title": "Learn FastAPI"})
    assert r.status_code == 201
    task_id = r.json()["id"]
    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Learn FastAPI"


def test_get_missing_is_404() -> None:
    assert client.get("/tasks/999").status_code == 404
