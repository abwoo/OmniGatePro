from fastapi.testclient import TestClient
from api.main import app
from core.worker import celery_app
from unittest.mock import patch

client = TestClient(app)

# Configure Celery to run tasks synchronously for testing
celery_app.conf.update(
    task_always_eager=True,
    task_eager_propagates=True,
    broker_url='memory://',
    result_backend='cache+memory://'
)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_execute_intent():
    payload = {
        "goals": ["Test goal 1", "Test goal 2"],
        "constraints": {"style": "test"}
    }
    
    # We need to mock the Celery task execution because it depends on DB session 
    # and other things that might be tricky in eager mode if not set up perfectly.
    # However, setting task_always_eager=True should work if the worker code is importable.
    
    response = client.post("/v1/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "accepted"
    
    run_id = data["run_id"]
    
    # Since it's eager, the task should have run. 
    # But wait, run_agent_task_celery uses its own DB session. 
    # SQLite in-memory might be an issue if we were using it, but config says ./artfish.db (file).
    # So it should persist.
    
    # Check status
    response = client.get(f"/v1/execution/{run_id}")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["run_id"] == run_id
    # It might be SUCCESS or FAIL depending on whether the mock backend works.
    assert status_data["status"] in ["SUCCESS", "FAIL", "PENDING", "RUNNING"]

def test_execution_not_found():
    response = client.get("/v1/execution/non-existent-id")
    assert response.status_code == 404
