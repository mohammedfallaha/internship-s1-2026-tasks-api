from fastapi import FastAPI

app = FastAPI(title="Tasks API")


@app.get("/hello")
def hello() -> dict[str, str]:
    return {"message": "hello"}