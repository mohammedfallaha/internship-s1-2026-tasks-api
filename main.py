#Step 1: 

#اجلب لي اداة FastAPI من مكتبة fastapi
from fastapi import FastAPI , HTTPException

#"أنشئ لي تطبيق FastAPI جديد، واسمه الظاهر Tasks API."
app = FastAPI(title="Tasks API")


#"إذا جاء شخص إلى العنوان /hello باستخدام طريقة GET، أرسله إلى الوظيفة التي سأكتبها بعد قليل."
#Endpoint يعني انشأ
@app.get("/hello")

#define \ نقول انها سترجع قاموس من نوع  فقط
def hello() -> dict[str, str]:
    return {"message": "hello"}






#Step 3:
#"من مكتبة Pydantic، أعطني أداتين: BaseModel و Field."

from pydantic import BaseModel, Field

#كلاس يرث شروط التحقق من ال BaseModel
class TaskCreate(BaseModel):
    #str يعني ان يكون نص داخل خاصية التايتل
    title: str = Field(min_length=1, max_length=200)
    #bool يعني ان يكون قيمة من نوع منطقي داخل الحقل
    done: bool = False

# ورثنا الكلاس واضفنا شيئ يميزه
class Task(TaskCreate):
    #id عرفنا
    id: int

#step 6 p1 | للتعديل انه ممكن تعديل العنوان والحالة 
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None



# انشأ ديكشيناري ليخزن البيانات 
tasks: dict[int, Task] = {}
next_id = 1



# tasks = {
#     1: {
#         "id": 1,
#         "title": "Study Python",
#         "done": False
#     },
#     2: {
#         "id": 2,
#         "title": "Build API",
#         "done": False
#     }
# }






#Step 4:

#انشاء مهمة جديدة | 201 تعني انه تم انشاء شيئ جديد
@app.post("/tasks", status_code=201)

# عرفنا دالة وتتوقع ان يصل لها البودي المذكور | body.title , body.done
def create_task(body: TaskCreate) -> Task:

    #glnal = this لخارج الدالة
    global next_id

    # **body.model.dump() يحول الخصائص الاتية من المستخدم عند انشاء المهمة الى قاموس ويترجمه 
    task = Task(id=next_id, **body.model_dump())

    #شرحها تحتها
    tasks[task.id] = task
    #tasks[1] = Task(
    # id=1,
    #  title="Learn Python",
    #done=False)

    next_id += 1
    return task

#اذا اجاك جيت شغل الدالة الي تحت هاي
@app.get("/tasks")
def list_tasks() -> list[Task]: 

#list[Task]=
#[Task(id=1, title="Learn Python", done=False),Task(id=2, title="Learn FastAPI", done=True)]

    # رجعلي القيم الموجودة في الديكشنري
    return list(tasks.values())
    #tasks = { 
    #1: Task1,
    #2: Task2,
    #3: Task3}





#Step 5:

@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> Task:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


#Step 6 p2: انشاء ايند بوينت
@app.patch("/tasks/{task_id}")

#تاخذ رقم المهمة من الرابط وما يريد المستخدم تغييره
def update_task(task_id: int, body: TaskUpdate) -> Task:

    #جلب المهمة من خلال رقمها 
    task = get_task(task_id)

    # تطبيق التغييرات على المهمة
    changes = body.model_dump(exclude_unset=True)
    #exclude_unset=True --> تعطي الحقول المرسلة فقط بدون None
    #Changes = {"title": None,"done": True} X
    #Changes = {"title": "Master FastAPI",done": True}

    #انسخ التاسك ومن ثم طبق التعديلات على التاسك المنسوخ
    tasks[task_id] = task.model_copy(update=changes)
    return tasks[task_id]


#Step 7: انشاء ايند بوينت لحذف المهمة
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    get_task(task_id)
    del tasks[task_id]