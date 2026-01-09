import pytest
import requests
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from task1.main import app
from task1.database import Base
from task1.dependencies import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_task():
    response = client.post("/tasks", json= {         
        "title": "Test Task",
        "description": "Test Description",
        "completed": False
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data
    assert "created_at" in data

def test_get_tasks():
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})
    
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) >= 2

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
    
def test_create_task_with_ml_prediction_high():
    """Test ML API integration - high priority prediction"""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"predicted_priority": "high"}
        mock_post.return_value = mock_response
        
        response = client.post("/tasks", json={
            "title": "Critical Security Bug",
            "description": "Fix critical vulnerability"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "high"


def test_create_task_with_ml_prediction_low():
    """Test ML API integration - low priority prediction"""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"predicted_priority": "low"}
        mock_post.return_value = mock_response
        
        response = client.post("/tasks", json={
            "title": "Update docs",
            "description": "Update documentation"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "low"


def test_create_task_ml_api_failure():
    """Test task creation when ML API fails"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("ML API unavailable")
        
        response = client.post("/tasks", json={
            "title": "Task without ML",
            "description": "Should still work"
        })
        
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Task without ML"

def test_create_task_ml_invalid_priority():
    """Test ML API returns invalid priority"""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"predicted_priority": "invalid"}
        mock_post.return_value = mock_response
        
        response = client.post("/tasks", json={
            "title": "Test Task",
            "description": "Test"
        })

        assert response.status_code == 201

def test_get_db_dependency():
    """Test database dependency for coverage"""
    from task1.dependencies import get_db
    
    db_gen = get_db()
    db = next(db_gen)
    
    assert db is not None
    
    try:
        next(db_gen)
    except StopIteration:
        pass 