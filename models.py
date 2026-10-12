from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class TaskRow(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    done: Mapped[bool] = mapped_column(default=False)

    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", name="fk_tasks_project"),
        index=True,
    )
    project: Mapped["ProjectRow | None"] = relationship(
        back_populates="tasks"
    )


class ProjectRow(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    tasks: Mapped[list["TaskRow"]] = relationship(
        back_populates="project"
    )
