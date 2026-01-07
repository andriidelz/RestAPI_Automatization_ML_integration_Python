import requests
import csv
from datetime import datetime
from task2.celery_app import app

@app.task(name="task2.tasks.fetch_and_save_users")
def fetch_and_save_users():
    """Get users from API and save to CSV"""
    try:
        response = requests.get(
            "https://jsonplaceholder.typicode.com/users",
            timeout=10
        )
        response.raise_for_status()
        users = response.json()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"users_{timestamp}.csv"
        
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["id", "name", "email"])
            writer.writeheader()
            
            for user in users:
                writer.writerow({
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"]
                })
        
        print(f"✓ Saved {len(users)} users to {filename}")
        return {"status": "success", "file": filename, "count": len(users)}
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return {"status": "error", "message": str(e)}
    
ML_API_URL = "http://ml-api:8001/predict"

TASKS = [
    "Fix login bug on website",
    "Update user profile page",
    "Implement new API endpoint",
    "Refactor old code",
    "Write unit tests for API",
    "Clean up temporary files",
    "Optimize database queries",
    "Update documentation",
    "Security vulnerability fix",
    "Add new feature request",
    "Update library versions",
    "Design new UI component",
    "Critical production bug",
    "Code review comments",
    "Performance optimization",
    "Update README file"
]

@app.task(name="task2.tasks.generate_tasks_csv")
def generate_tasks_csv():
    """Call ML API for each task and save to CSV"""
    filename = f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["task_description", "priority"])
        
        for task in TASKS:
            try:
                r = requests.post(ML_API_URL, json={"task_description": task})
                r.raise_for_status()
                priority = r.json().get("predicted_priority", "unknown")
                writer.writerow([task, priority])
            except Exception as e:
                writer.writerow([task, "error"])
    
    print(f"✓ Saved {len(TASKS)} tasks to {filename}")
    return {"status": "success", "file": filename, "count": len(TASKS)}