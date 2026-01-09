import requests
import csv
from datetime import UTC, datetime
from task2.celery_app import app

from task1.database import SessionLocal
from task1.models import Task

ML_API_URL = "http://keymakr-ml-api:8001/predict"

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
        
        filename = f"users_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.csv"
        
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
    
@app.task(name="task2.tasks.generate_tasks_csv")
def generate_tasks_csv():
    """Call ML API for each task and save to CSV"""
    db = SessionLocal()

    try:
        tasks = (
            db.query(Task)
            .filter(Task.deleted_at.is_(None))
            .all()
        )

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"tasks_{timestamp}.csv"
        
        if not tasks:
            print("No tasks in database, generating sample data...")
            sample_data = [
                ("Fix login bug on website", "high"),
                ("Update user profile page", "low"),
                ("Implement new API endpoint", "high"),
                ("Refactor old code", "low"),
                ("Write unit tests for API", "high"),
                ("Clean up temporary files", "low"),
                ("Optimize database queries", "high"),
                ("Update documentation", "low"),
                ("Security vulnerability fix", "high"),
                ("Add new feature request", "high"),
                ("Update library versions", "low"),
                ("Design new UI component", "low"),
                ("Critical production bug", "high"),
                ("Code review comments", "low"),
                ("Performance optimization", "high"),
                ("Update README file", "low"),
            ]

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["task_description", "priority"])
                writer.writerows(sample_data)
            
            print(f"✓ Generated {len(sample_data)} sample tasks to {filename}")
            return {
                "status": "success",
                "file": filename,
                "count": len(sample_data),
                "source": "sample_data"
            }

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["task_description", "priority"])

            for task in tasks:
                description = task.description or task.title

                try:
                    r = requests.post(
                        ML_API_URL,
                        json={"task_description": description},
                        timeout=5
                    )
                    r.raise_for_status()
                    priority = r.json().get("predicted_priority", "unknown")
                except Exception as e:
                    print(f"ML API error for '{description}': {e}")
                    priority = getattr(task, 'priority', 'medium')

                writer.writerow([description, priority])

        print(f"✓ Exported {len(tasks)} tasks to {filename}")
        return {
            "status": "success",
            "file": filename,
            "count": len(tasks),
            "source": "database"
        }
    
    except Exception as e:
        print(f"✗ Error generating tasks CSV: {str(e)}")
        return {"status": "error", "message": str(e)}

    finally:
        db.close()
        
@app.task(name="task2.tasks.train_ml_model")
def train_ml_model():
    """Generate CSV and train ML model using existing train_model.py"""
    try:
        print("Step 1: Generating tasks CSV...")
        csv_result = generate_tasks_csv()
        
        if csv_result["status"] != "success":
            return {"status": "error", "message": "Failed to generate CSV"}
        
        csv_file = csv_result["file"]
        print(f"✓ CSV generated: {csv_file}")
        
        import shutil
        shutil.copy(csv_file, "tasks.csv")
        print("✓ CSV copied to tasks.csv")
        
        print("Step 2: Training ML model...")
        from task3.train_model import train_model
        
        train_model()
        
        print(f"✓ ML model trained successfully using {csv_file}")
        return {
            "status": "success",
            "message": "ML model trained successfully",
            "csv_file": csv_file,
            "tasks_count": csv_result["count"],
            "source": csv_result.get("source", "database")
        }
        
    except Exception as e:
        print(f"✗ Error training ML model: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}