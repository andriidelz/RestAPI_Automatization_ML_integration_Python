from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi import status

import requests
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from task1 import models, dependencies
from task1.schemas import TaskCreate, TaskUpdate, TaskOut

app = FastAPI(title="To-Do List API")

@app.get("/")
def root():
    return {"message": "OK"}

# models.Base.metadata.create_all(bind=database.engine)

@app.get("/tasks", response_model=List[TaskOut])
def get_tasks(db: Session = Depends(dependencies.get_db)):
    return db.query(models.Task).filter(models.Task.deleted_at == None).all()

@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(dependencies.get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.deleted_at == None).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(dependencies.get_db)):
    new_task = models.Task(
        title=task.title,
        description=task.description,
        completed=task.completed or False
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    description = new_task.description or new_task.title
    try:
        ml_response = requests.post(
            "http://keymakr-ml-api:8001/predict",  
            json={"task_description": description},
            timeout=5
        )
        if ml_response.status_code == 200:
            predicted_priority = ml_response.json().get("predicted_priority")
            if predicted_priority in ["high", "low"]:
                new_task.priority = predicted_priority
                db.commit()
                db.refresh(new_task)
                print(f"Predicted priority '{predicted_priority}' for task '{new_task.title}'")
    except requests.RequestException as e:
        print(f"ML prediction failed: {e} (priority remains null)")
    
    return new_task

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(dependencies.get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.deleted_at == None).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    if task.completed:
        task.status = "done"
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(dependencies.get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.deleted_at = datetime.now(timezone.utc)
    db.commit()