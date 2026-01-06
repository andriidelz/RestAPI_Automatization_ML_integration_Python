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