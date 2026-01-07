from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, UTC

app = FastAPI(title="To-Do List API")

# In-memory storage
tasks_db = {}
task_id_counter = {"value": 1}


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False
    priority: Optional[str] = Field(None, description="low | medium | high")
    assigned_to: Optional[int] = None
    project_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    
    completed: bool = False
    status: str = "todo"          

    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    project_id: Optional[int] = None

    created_at: str
    deleted_at: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "To-Do List API", "endpoints": ["/tasks", "/tasks/{id}", "/health"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    """Get the list of all tasks"""
    return [
        task for task in tasks_db.values()
        if task.deleted_at is None
    ]

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    """Create a new task"""
    task_id = task_id_counter["value"]
    task_id_counter["value"] += 1
    
    status = "done" if task.completed else "todo"
    
    new_task = Task(
        id=task_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        status=status,
        priority=task.priority,
        assigned_to=task.assigned_to,
        project_id=task.project_id,
        created_at=datetime.now(UTC).isoformat(),
    )
    
    tasks_db[task_id] = new_task
    return new_task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = tasks_db.get(task_id)
    """Get a task by ID"""
    if not task or task.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    task = tasks_db.get(task_id)
    """Renew a task"""
    if not task or task.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.model_dump(exclude_unset=True)    
    
    if "completed" in update_data:
        update_data["status"] = "done" if update_data["completed"] else "todo"
    
    updated_task = task.model_copy(update=update_data)

    tasks_db[task_id] = updated_task
    return updated_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = tasks_db.get(task_id)
    """Delete a task"""
    if not task or task.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.deleted_at = datetime.now(UTC).isoformat()
    tasks_db[task_id] = task
    return None