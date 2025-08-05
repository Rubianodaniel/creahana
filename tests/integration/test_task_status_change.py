import pytest


@pytest.mark.asyncio
async def test_change_task_status_to_completed(test_client):

    task_list_data = {
        "title": "Test Task List",
        "description": "Test description"
    }
    
    create_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    task_list_id = create_response.json()["id"]
    
    task_data = {
        "title": "Test Task",
        "description": "Task to change status",
        "task_list_id": task_list_id,
        "status": "pending",
        "priority": "medium"
    }
    
    create_task_response = await test_client.post("/api/tasks/", json=task_data)
    assert create_task_response.status_code == 201
    task_id = create_task_response.json()["id"]
    
    status_data = {"status": "completed"}
    
    response = await test_client.patch(f"/api/tasks/{task_id}/status", json=status_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == task_id
    assert data["status"] == "completed"
    assert data["title"] == "Test Task"


@pytest.mark.asyncio
async def test_change_task_status_to_in_progress(test_client):

    task_list_data = {
        "title": "Test Task List",
        "description": "Test description"
    }
    
    create_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    task_list_id = create_response.json()["id"]
    
    task_data = {
        "title": "Test Task",
        "task_list_id": task_list_id,
        "status": "pending",
        "priority": "high"
    }
    
    create_task_response = await test_client.post("/api/tasks/", json=task_data)
    assert create_task_response.status_code == 201
    task_id = create_task_response.json()["id"]
    
    status_data = {"status": "in_progress"}
    
    response = await test_client.patch(f"/api/tasks/{task_id}/status", json=status_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == task_id
    assert data["status"] == "in_progress"


@pytest.mark.asyncio
async def test_change_task_status_invalid_status(test_client):

    task_list_data = {
        "title": "Test Task List",
        "description": "Test description"
    }
    
    create_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    task_list_id = create_response.json()["id"]
    
    task_data = {
        "title": "Test Task",
        "task_list_id": task_list_id,
        "status": "pending",
        "priority": "low"
    }
    
    create_task_response = await test_client.post("/api/tasks/", json=task_data)
    assert create_task_response.status_code == 201
    task_id = create_task_response.json()["id"]
    
    status_data = {"status": "invalid_status"}
    
    response = await test_client.patch(f"/api/tasks/{task_id}/status", json=status_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_change_task_status_task_not_found(test_client):

    status_data = {"status": "completed"}
    
    response = await test_client.patch("/api/tasks/99999/status", json=status_data)
    
    assert response.status_code == 404
    assert "Task with id 99999 not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_change_task_status_affects_completion_percentage(test_client):

    task_list_data = {
        "title": "Test Task List",
        "description": "Test description"
    }
    
    create_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    task_list_id = create_response.json()["id"]
    
    # Create 2 tasks
    task1_data = {
        "title": "Task 1",
        "task_list_id": task_list_id,
        "status": "pending",
        "priority": "medium"
    }
    
    task2_data = {
        "title": "Task 2",
        "task_list_id": task_list_id,
        "status": "pending",
        "priority": "medium"
    }
    
    task1_response = await test_client.post("/api/tasks/", json=task1_data)
    task2_response = await test_client.post("/api/tasks/", json=task2_data)
    
    task1_id = task1_response.json()["id"]
    task2_id = task2_response.json()["id"]
    
    # Check initial completion percentage (0%)
    initial_response = await test_client.get(f"/api/task-lists/{task_list_id}/tasks")
    assert initial_response.json()["completion_percentage"] == 0.0
    
    # Change first task to completed
    status_data = {"status": "completed"}
    await test_client.patch(f"/api/tasks/{task1_id}/status", json=status_data)
    
    # Check completion percentage (50%)
    after_one_response = await test_client.get(f"/api/task-lists/{task_list_id}/tasks")
    assert after_one_response.json()["completion_percentage"] == 50.0
    
    # Change second task to completed
    await test_client.patch(f"/api/tasks/{task2_id}/status", json=status_data)
    
    # Check completion percentage (100%)
    final_response = await test_client.get(f"/api/task-lists/{task_list_id}/tasks")
    assert final_response.json()["completion_percentage"] == 100.0