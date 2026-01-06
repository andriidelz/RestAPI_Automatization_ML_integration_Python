from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="To-Do List API")

# In-memory storage
tasks_db = {}
task_id_counter = {"value": 1}


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: str


@app.get("/")
def read_root():
    return {"message": "To-Do List API", "endpoints": ["/tasks", "/tasks/{id}"]}


@app.get("/tasks", response_model=List[Task])
def get_tasks():
    """Get the list of all tasks"""
    return list(tasks_db.values())


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    """Create a new task"""
    task_id = task_id_counter["value"]
    task_id_counter["value"] += 1
    
    new_task = Task(
        id=task_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=datetime.now().isoformat()
    )
    
    tasks_db[task_id] = new_task
    return new_task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    """Get a task by ID"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    """Renew a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    existing_task = tasks_db[task_id]
    update_data = task_update.model_dump(exclude_unset=True)
    
    updated_task = existing_task.model_copy(update=update_data)
    tasks_db[task_id] = updated_task
    
    return updated_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """Delete a task"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks_db[task_id]
    return None