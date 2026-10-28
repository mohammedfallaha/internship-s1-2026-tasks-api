from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session
from auth import create_token, password_hash
from db import get_db
from models import ProjectRow, TaskRow,UserRow

DbSession = Annotated[Session, Depends(get_db)]

app = FastAPI(title="Tasks API")


@app.get("/hello")
def hello() -> dict[str, str]:
    return {"message": "hello"}


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    done: bool = False
    project_id: int | None = None


class Task(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


@app.post("/projects", status_code=201)
def create_project(body: ProjectCreate, db: DbSession) -> Project:
    row = ProjectRow(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return Project.model_validate(row)


@app.get("/projects")
def list_projects(db: DbSession) -> list[Project]:
    rows = db.scalars(select(ProjectRow).order_by(ProjectRow.id))
    return [Project.model_validate(row) for row in rows]


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate, db: DbSession) -> Task:
    if body.project_id is not None:
        find_project(db, body.project_id)

    row = TaskRow(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return Task.model_validate(row)


@app.get("/tasks")
def list_tasks(
    db: DbSession, done: bool | None = None, q: str | None = None
) -> list[Task]:
    stmt = select(TaskRow).order_by(TaskRow.id)
    if done is not None:
        stmt = stmt.where(TaskRow.done == done)
    if q is not None:
        stmt = stmt.where(TaskRow.title.ilike(f"%{q}%"))
    return [Task.model_validate(row) for row in db.scalars(stmt)]


def find_task(db: Session, task_id: int) -> TaskRow:
    row = db.get(TaskRow, task_id)
    if row is None:
        raise HTTPException(status_code=404, detail="task not found")
    return row


def find_project(db: Session, project_id: int) -> ProjectRow:
    row = db.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    return row


@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: DbSession) -> Task:
    return Task.model_validate(find_task(db, task_id))


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate, db: DbSession) -> Task:
    row = find_task(db, task_id)
    for name, value in body.model_dump(exclude_unset=True).items():
        setattr(row, name, value)
    db.commit()
    db.refresh(row)
    return Task.model_validate(row)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: DbSession) -> None:
    db.delete(find_task(db, task_id))
    db.commit()


@app.get("/projects/{project_id}/tasks")
def list_project_tasks(project_id: int, db: DbSession) -> list[Task]:
    project = find_project(db, project_id)
    return [Task.model_validate(row) for row in project.tasks]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


@app.post("/auth/register", status_code=201)
def register(body: UserCreate, db: DbSession) -> UserRead:
    if db.scalar(select(UserRow).where(UserRow.email == body.email)) is not None:
        raise HTTPException(status_code=409, detail="email already registered")
    row = UserRow(email=body.email, password_hash=password_hash.hash(body.password))
    db.add(row)
    db.commit()
    db.refresh(row)
    return UserRead.model_validate(row)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/auth/login")
def login(body: LoginIn, db: DbSession) -> TokenOut:
    user = db.scalar(select(UserRow).where(UserRow.email == body.email))
    if user is None or not password_hash.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="wrong email or password")
    return TokenOut(access_token=create_token(user.id))