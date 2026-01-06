from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os

app = FastAPI(title="Task Priority Prediction API")

# Download the model
MODEL_PATH = "task3/priority_model.pkl"
model = None

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✓ Model loaded successfully")
else:
    print("⚠ Model not found. Run train_model.py first.")

class TaskInput(BaseModel):
    task_description: str

class PredictionOutput(BaseModel):
    task_description: str
    predicted_priority: str
    confidence: str

@app.get("/")
def read_root():
    return {
        "message": "Task Priority Prediction API",
        "model_loaded": model is not None,
        "endpoint": "/predict"
    }

@app.post("/predict", response_model=PredictionOutput)
def predict_priority(task: TaskInput):
    """Predict the priority of a task"""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run train_model.py first."
        )
    
    try:
        prediction = model.predict([task.task_description])[0]
        
        return PredictionOutput(
            task_description=task.task_description,
            predicted_priority=prediction,
            confidence="estimated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)