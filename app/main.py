from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    return {"status": "ok", "message": "Hello from FastAPI"}


@app.get("/healthz")
def health_check() -> dict:
    return {"status": "healthy"}
