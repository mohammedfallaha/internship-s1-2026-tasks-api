import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from db import SessionLocal
from main import app
from models import ProjectRow, TaskRow

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_tables() -> None:
    with SessionLocal() as db:
        db.execute(delete(TaskRow))
        db.execute(delete(ProjectRow))
        db.commit()


def test_create_then_get() -> None:
    r = client.post("/tasks", json={"title": "Learn FastAPI"})
    assert r.status_code == 201
    task_id = r.json()["id"]
    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Learn FastAPI"
    assert len(client.get("/tasks").json()) == 1


def test_get_missing_is_404() -> None:
    assert client.get("/tasks/999").status_code == 404


def test_project_lists_only_its_tasks() -> None:
    project_id = client.post("/projects", json={"name": "Home"}).json()["id"]
    client.post("/tasks", json={"title": "Buy milk", "project_id": project_id})
    client.post("/tasks", json={"title": "No project"})
    r = client.get(f"/projects/{project_id}/tasks")
    assert [t["title"] for t in r.json()] == ["Buy milk"]


def test_filter_by_done() -> None:
    client.post("/tasks", json={"title": "Done one", "done": True})
    client.post("/tasks", json={"title": "Open one"})
    r = client.get("/tasks", params={"done": True})
    assert [t["title"] for t in r.json()] == ["Done one"]
