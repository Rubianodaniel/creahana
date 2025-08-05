import pytest


@pytest.mark.asyncio
async def test_update_task_success(test_client):
    """Test updating a task successfully."""
    # First create a task list
    task_list_data = {
        "title": "Parent Task List",
        "description": "List for tasks"
    }
    
    list_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]
    
    # Create a task
    task_data = {
        "title": "Original Task",
        "description": "Original description",
        "task_list_id": task_list_id,
        "status": "pending",
        "priority": "low"
    }
    
    create_response = await test_client.post("/api/tasks/", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Update the task
    update_data = {
        "title": "Updated Task",
        "description": "Updated description",
        "status": "in_progress",
        "priority": "high"
    }
    
    update_response = await test_client.put(f"/api/tasks/{task_id}", json=update_data)
    
    assert update_response.status_code == 200
    data = update_response.json()
    
    assert data["id"] == task_id
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated description"
    assert data["status"] == "in_progress"
    assert data["priority"] == "high"
    assert data["task_list_id"] == task_list_id  # Should remain unchanged


@pytest.mark.asyncio
async def test_update_task_partial_update(test_client):
    """Test partially updating a task."""
    # First create a task list
    task_list_data = {
        "title": "Parent Task List",
        "description": "List for tasks"
    }
    
    list_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]
    
    # Create a task
    task_data = {
        "title": "Original Task",
        "description": "Original description",
        "task_list_id": task_list_id,
        "status": "pending",
        "priority": "medium"
    }
    
    create_response = await test_client.post("/api/tasks/", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Update only the status
    update_data = {
        "status": "completed"
    }
    
    update_response = await test_client.put(f"/api/tasks/{task_id}", json=update_data)
    
    assert update_response.status_code == 200
    data = update_response.json()
    
    assert data["id"] == task_id
    assert data["title"] == "Original Task"  # Didn't change
    assert data["description"] == "Original description"  # Didn't change
    assert data["status"] == "completed"  # Changed
    assert data["priority"] == "medium"  # Didn't change


@pytest.mark.asyncio
async def test_update_task_not_found(test_client):
    """Test updating a task that doesn't exist."""
    update_data = {
        "title": "Non-existent Task",
        "description": "This should fail"
    }
    
    response = await test_client.put("/api/tasks/999", json=update_data)
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task_change_task_list(test_client):
    """Test moving a task to a different task list."""
    # Create two task lists
    task_list_data_1 = {
        "title": "Task List 1",
        "description": "First list"
    }
    
    list_response_1 = await test_client.post("/api/task-lists/", json=task_list_data_1)
    assert list_response_1.status_code == 201
    task_list_id_1 = list_response_1.json()["id"]
    
    task_list_data_2 = {
        "title": "Task List 2",
        "description": "Second list"
    }
    
    list_response_2 = await test_client.post("/api/task-lists/", json=task_list_data_2)
    assert list_response_2.status_code == 201
    task_list_id_2 = list_response_2.json()["id"]
    
    # Create a task in the first list
    task_data = {
        "title": "Movable Task",
        "description": "This task will move",
        "task_list_id": task_list_id_1
    }
    
    create_response = await test_client.post("/api/tasks/", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    # Move the task to the second list
    update_data = {
        "task_list_id": task_list_id_2
    }
    
    update_response = await test_client.put(f"/api/tasks/{task_id}", json=update_data)
    
    assert update_response.status_code == 200
    data = update_response.json()
    
    assert data["id"] == task_id
    assert data["task_list_id"] == task_list_id_2  # Moved to second list
    assert data["title"] == "Movable Task"  # Title unchanged