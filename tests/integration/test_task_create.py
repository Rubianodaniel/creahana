import pytest


@pytest.mark.asyncio
async def test_create_task_success(test_client):
    """Test creating a task successfully."""
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Create a task
    task_data = {
        "title": "Test Task",
        "description": "Test task description",
        "task_list_id": task_list_id,
        "status": "pending",
        "priority": "medium",
    }

    response = await test_client.post("/api/tasks/", json=task_data)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test Task"
    assert data["description"] == "Test task description"
    assert data["task_list_id"] == task_list_id
    assert data["status"] == "pending"
    assert data["priority"] == "medium"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_task_minimal_data(test_client):
    """Test creating a task with minimal required data."""
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Create task with minimal data
    task_data = {"title": "Minimal Task", "task_list_id": task_list_id}

    response = await test_client.post("/api/tasks/", json=task_data)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Minimal Task"
    assert data["task_list_id"] == task_list_id
    assert data["status"] == "pending"  # Default value
    assert data["priority"] == "medium"  # Default value
    assert data["description"] is None


@pytest.mark.asyncio
async def test_create_task_missing_title(test_client):
    """Test creating a task without required title."""
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Try to create task without title
    task_data = {"task_list_id": task_list_id, "description": "Task without title"}

    response = await test_client.post("/api/tasks/", json=task_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_task_short_title(test_client):
    """Test creating a task with title too short."""
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Try to create task with short title (less than 4 characters)
    task_data = {"title": "abc", "task_list_id": task_list_id}  # Only 3 characters

    response = await test_client.post("/api/tasks/", json=task_data)

    assert response.status_code == 422  # Validation error
