# RestAPI_Automatization_ML_integration_Python APP

## Quick start

## 1. Local launch (without Docker)

```bash
pip install -r requirements.txt

# Launch Redis (required for task 2)
# on Ubuntu/Debian:
sudo apt-get install redis-server
redis-server

# On macOS:
brew install redis
redis-server

# Launch Task 1 API
uvicorn task1.main:app --reload --port 8000

# In another terminal: make tests Task 1
pytest task1/test_main.py -v

# Launch Task 2 Celery worker
celery -A task2.celery_app worker --loglevel=info

# In another terminal: launch Celery beat (automatic tasks)
celery -A task2.celery_app beat --loglevel=info

# Launch Task 3: first of all to train model
python task3/train_model.py

# The launch ML API
python task3/ml_api.py
```

### 2. Launch via Docker

```bash
docker-compose up --build

# API will be accessed on http://localhost:8000
# Redis on port 6379
```

### Before task check

Delete this cache files (optionally)

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

Check all files to be on a correct

```bash
ls -la task1/ task2/ task3/
```

Final launching and test

```bash
docker-compose up --build
pytest task1/test_main.py -v
```

## Testing

### Task 1: REST API

```bash
pytest task1/test_main.py -v
pytest task1/test_main.py --cov

cd task1
pytest test_main.py -v

pytest task1/test_main.py --cov=task1 --cov-report=html
pytest task1/test_main.py --cov=task1 --cov-report=html --cov-report=term
open htmlcov/index.html

# Manual testing via curl:
# Create task 
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "Description"}'

# Get all tasks
curl "http://localhost:8000/tasks"

# Renew task
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete task
curl -X DELETE "http://localhost:8000/tasks/1"
```

### Task 2: Celery

```bash
# Check worker status
celery -A task2.celery_app inspect active
docker exec -it keymakr-celery-worker celery -A task2.celery_app inspect active

# Lauch task manually in Python:
python -c "from task2.tasks import fetch_and_save_users; fetch_and_save_users.delay()"
docker exec -it keymakr-api python -c \
"from task2.tasks import fetch_and_save_users; fetch_and_save_users.delay()"
or
docker exec -it keymakr-api python -c "from task2.tasks import generate_tasks_csv; generate_tasks_csv.delay()"

# Check corollaries - file users_*.csv will be created
```

### Task 3: ML API

```bash
# Testing via curl:
curl -X POST "http://localhost:8001/predict" \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Fix critical security bug"}'

# Expected result:
# {"task_description":"Fix critical security bug","predicted_priority":"high","confidence":"estimated"}
```

## API Documentation

### Task 1 Endpoints

- `GET /tasks` - Get all tasks
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get task for ID
- `PUT /tasks/{id}` - Renew task
- `DELETE /tasks/{id}` - Delete task

Swagger UI: <http://localhost:8000/docs>

### Task 3 Endpoints

- `POST /predict` - Predict task priority

Swagger UI: <http://localhost:8001/docs>

## Technologies

- __FastAPI__ - REST API framework
- __Pydantic__ - data's validation
- __Celery__ - asynchrony tasks
- __Redis__ - report broker
- __Docker__ - containerization
- __Pytest__ - testing
- __Scikit-learn__ - machine learning
- __Pandas__ - data's calculation

## Remarks

- Task 1: Datas keep in memory (vanish after relaunch)
- Task 2: Celery beat launches the task automatically every 5 minutes
- Task 3:  The model is simple and ready for demonstration, not for production

## Makefile commands

make test-cov
make docker-up
make clean

## Migration

```bash
docker exec -it keymakr-api alembic upgrade head
alembic revision --autogenerate -m "create tasks table"
alembic upgrade head
```

## API endpoints

- To-Do API: <http://localhost:8000/tasks>
- Docs: <http://localhost:8000/docs>
- ML Predict: <http://localhost:8001/predict>

## Documentation

- API Docs: <http://localhost:8000/docs>
- ML Docs: <http://localhost:8001/docs>

## Author

Andrii Zaliubovskyi
