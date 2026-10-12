# Step 1:

# اجلب لي اداة FastAPI من مكتبة fastapi
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_db
from models import TaskRow

DbSession = Annotated[Session, Depends(get_db)]

# "أنشئ لي تطبيق FastAPI جديد، واسمه الظاهر Tasks API."
app = FastAPI(title="Tasks API")


# "إذا جاء شخص إلى العنوان /hello باستخدام طريقة GET، أرسله إلى الوظيفة التي سأكتبها بعد قليل."
# Endpoint يعني انشأ
@app.get("/hello")

# define \ نقول انها سترجع قاموس من نوع  فقط
def hello() -> dict[str, str]:
    return {"message": "hello"}


# Step 3:
# "من مكتبة Pydantic، أعطني أداتين: BaseModel و Field."



# كلاس يرث شروط التحقق من ال BaseModel
class TaskCreate(BaseModel):
    # str يعني ان يكون نص داخل خاصية التايتل
    title: str = Field(min_length=1, max_length=200)
    # bool يعني ان يكون قيمة من نوع منطقي داخل الحقل
    done: bool = False


# ورثنا الكلاس واضفنا شيئ يميزه
class Task(TaskCreate):
    model_config = ConfigDict(from_attributes=True)
    
    # id عرفنا
    id: int


# step 6 p1 | للتعديل انه ممكن تعديل العنوان والحالة
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None



# Step 4:


# انشاء مهمة جديدة | 201 تعني انه تم انشاء شيئ جديد

# عرفنا دالة وتتوقع ان يصل لها البودي المذكور | body.title , body.done
@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate, db: DbSession) -> Task:
    row = TaskRow(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return Task.model_validate(row)


@app.get("/tasks")
def list_tasks(db: DbSession) -> list[Task]:
    rows = db.scalars(select(TaskRow).order_by(TaskRow.id))
    return [Task.model_validate(row) for row in rows]





# Step 5:


def find_task(db: Session, task_id: int) -> TaskRow:
    row = db.get(TaskRow, task_id)
    if row is None:
        raise HTTPException(status_code=404, detail="task not found")
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