import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apps.integrations.hello_world import get_hello_message
from apps.integrations.oracle_utilization import start_utilization_tasks
# from fastapi.responses import FileResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs on startup
    start_utilization_tasks()
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

if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
