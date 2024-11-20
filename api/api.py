from worker import celery_client
from typing import Any, Dict
# from loguru import logger

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body

# configuration
DEBUG = True
app = FastAPI()
# enable CORS
app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # Allows all origins
allow_credentials=True,
allow_methods=["*"], # Allows all methods
allow_headers=["*"], # Allows all headers
)

# ----------------------------
# Single task
# ----------------------------

@app.post("/chai/")
async def chai_task(request: Dict[str, Any] = Body(..., embed=True)):
    task = celery_client.send_task("chai", args=[request], queue="queue_chai")
    return {"task_id": task.id}

@app.post("/alphafold3/")
async def alphafold3_task(request: Dict[str, Any] = Body(..., embed=True)):
    task = celery_client.send_task("alphafold3", args=[request], queue="queue_alphafold3")
    return {"task_id": task.id}


