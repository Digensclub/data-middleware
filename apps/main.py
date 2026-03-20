import uvicorn
from fastapi import FastAPI
import os
from contextlib import asynccontextmanager
from apps.integrations.hello_world import get_hello_message
from apps.integrations.oracle_utilization import manage_utilization
# from fastapi.responses import FileResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs on startup
    if os.getenv("KEEP_ALIVE", "true").lower() == "true":
        manage_utilization(active=True)
    yield
    # Clean up (if any) on shutdown

app = FastAPI(title="Data-Middleware-Prod", lifespan=lifespan)

@app.get('/')
async def root():
    return {
        "status": "online",
        "message": "Middleware is running on OCI ARM64",
        "resources": "4 OCPUs / 24GB RAM"
    }

@app.get('/hello')
async def hello():
    message = get_hello_message()
    return {"status": "success", "data": message}

@app.post("/utilization/toggle")
async def toggle_utilization(status: bool, ram_size: int = 40_000_000):
    # Note: In Gunicorn, this only affects the worker hitting this specific request.
    # To affect ALL workers, you'd usually use a shared file or Redis.
    manage_utilization(active=status, ram_count=ram_size)
    return {"status": "updated", "is_active": status, "ram_size": ram_size}

if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
