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