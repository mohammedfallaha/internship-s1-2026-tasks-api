#اجلب لي اداة FastAPI من مكتبة fastapi
from fastapi import FastAPI 

#"أنشئ لي تطبيق FastAPI جديد، واسمه الظاهر Tasks API."
app = FastAPI(title="Tasks API")


#"إذا جاء شخص إلى العنوان /hello باستخدام طريقة GET، أرسله إلى الوظيفة التي سأكتبها بعد قليل."
#Endpoint يعني انشأ
@app.get("/hello")

#define \ نقول انها سترجع قاموس من نوع  فقط
def hello() -> dict[str, str]:
    return {"message": "hello"}


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


@app.get("/tasks")
def list_tasks() -> list[Task]:
    return list(tasks.values())