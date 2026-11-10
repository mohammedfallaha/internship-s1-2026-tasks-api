
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from db import SessionLocal
from main import app
from models import ProjectRow, TaskRow, UserRow

client = TestClient(app)
PASSWORD = "correct horse battery"


@pytest.fixture(autouse=True)
def clean_tables() -> None:
    with SessionLocal() as db:
        db.execute(delete(TaskRow))
        db.execute(delete(ProjectRow))
        db.execute(delete(UserRow))
        db.commit()


def login(client: TestClient, email: str) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={"email": email, "password": PASSWORD},
    )
    r = client.post(
        "/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_create_then_get() -> None:
    h = login(client, "ann@example.com")
    r = client.post(
        "/tasks",
        json={"title": "Learn FastAPI"},
        headers=h,
    )
    assert r.status_code == 201
    task_id = r.json()["id"]

    r = client.get(f"/tasks/{task_id}", headers=h)
    assert r.status_code == 200
    assert r.json()["title"] == "Learn FastAPI"

    assert len(client.get("/tasks", headers=h).json()) == 1


def test_get_missing_is_404() -> None:
    h = login(client, "ann@example.com")
    assert client.get("/tasks/999", headers=h).status_code == 404


def test_project_lists_only_its_tasks() -> None:
    h = login(client, "ann@example.com")

    project_id = client.post(
        "/projects",
        json={"name": "Home"},
        headers=h,
    ).json()["id"]

    client.post(
        "/tasks",
        json={"title": "Buy milk", "project_id": project_id},
        headers=h,
    )
    client.post(
        "/tasks",
        json={"title": "No project"},
        headers=h,
    )

    r = client.get(f"/projects/{project_id}/tasks", headers=h)
    assert [t["title"] for t in r.json()] == ["Buy milk"]


def test_filter_by_done() -> None:
    h = login(client, "ann@example.com")

    client.post(
        "/tasks",
        json={"title": "Done one", "done": True},
        headers=h,
    )
    client.post(
        "/tasks",
        json={"title": "Open one"},
        headers=h,
    )

    r = client.get("/tasks", params={"done": True}, headers=h)
    assert [t["title"] for t in r.json()] == ["Done one"]


def test_register_twice_is_409() -> None:
    body = {"email": "ann@example.com", "password": PASSWORD}

    assert client.post("/auth/register", json=body).status_code == 201
    assert client.post("/auth/register", json=body).status_code == 409


def test_wrong_password_is_401() -> None:
    login(client, "ann@example.com")

    body = {"email": "ann@example.com", "password": "wrong"}
    assert client.post("/auth/login", json=body).status_code == 401


def test_no_token_is_401() -> None:
    assert client.get("/tasks").status_code == 401


def test_me_returns_email() -> None:
    r = client.get(
        "/auth/me",
        headers=login(client, "ann@example.com"),
    )

    assert r.status_code == 200
    assert r.json()["email"] == "ann@example.com"


def test_other_users_task_is_404() -> None:
    ann = login(client, "ann@example.com")
    bob = login(client, "bob@example.com")

    task_id = client.post(
        "/tasks",
        json={"title": "Ann's"},
        headers=ann,
    ).json()["id"]

    assert client.get(f"/tasks/{task_id}", headers=bob).status_code == 404
    assert client.get("/tasks", headers=bob).json() == []
