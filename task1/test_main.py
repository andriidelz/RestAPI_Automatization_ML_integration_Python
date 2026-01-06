import pytest
from fastapi.testclient import TestClient
from task1.main import app, tasks_db, task_id_counter

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    """Clear the database before each test"""
    tasks_db.clear()
    task_id_counter["value"] = 1
    yield

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_task():
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False
    }
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["id"] == 1
    assert "created_at" in data

def test_get_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks():
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})
    
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_task_by_id():
    create_response = client.post("/tasks", json={"title": "Test Task"})
    task_id = create_response.json()["id"]
    
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"

def test_get_task_not_found():
    response = client.get("/tasks/999")
    assert response.status_code == 404

def test_update_task():
    create_response = client.post("/tasks", json={"title": "Old Title"})
    task_id = create_response.json()["id"]
    
    update_data = {"title": "New Title", "completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["completed"] is True

def test_update_task_not_found():
    response = client.put("/tasks/999", json={"title": "New Title"})
    assert response.status_code == 404

def test_delete_task():
    create_response = client.post("/tasks", json={"title": "To Delete"})
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404

def test_delete_task_not_found():
    response = client.delete("/tasks/999")
    assert response.status_code == 404

def test_create_task_validation():
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422