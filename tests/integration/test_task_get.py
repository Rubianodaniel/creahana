import pytest


@pytest.mark.asyncio
async def test_get_task_by_id(test_client):
    """Test getting a task by ID."""
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
        "priority": "high",
    }

    create_response = await test_client.post("/api/tasks/", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Get the task
    get_response = await test_client.get(f"/api/tasks/{task_id}")

    assert get_response.status_code == 200
    data = get_response.json()

    assert data["id"] == task_id
    assert data["title"] == "Test Task"
    assert data["description"] == "Test task description"
    assert data["task_list_id"] == task_list_id
    assert data["status"] == "pending"
    assert data["priority"] == "high"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_task_not_found(test_client):
    """Test getting a task that doesn't exist."""
    response = await test_client.get("/api/tasks/999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_tasks(test_client):
    """Test getting all tasks."""
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Create multiple tasks
    tasks = [
        {
            "title": "Task 1",
            "description": "Description 1",
            "task_list_id": task_list_id,
            "priority": "low",
        },
        {
            "title": "Task 2",
            "description": "Description 2",
            "task_list_id": task_list_id,
            "priority": "medium",
        },
        {
            "title": "Task 3",
            "description": "Description 3",
            "task_list_id": task_list_id,
            "priority": "high",
        },
    ]

    created_ids = []
    for task_data in tasks:
        response = await test_client.post("/api/tasks/", json=task_data)
        assert response.status_code == 201
        created_ids.append(response.json()["id"])

    # Get all tasks
    get_all_response = await test_client.get("/api/tasks/")

    assert get_all_response.status_code == 200
    data = get_all_response.json()

    assert len(data) >= 3  # At least the 3 we created

    # Verify our tasks are in the response
    titles = [item["title"] for item in data]
    assert "Task 1" in titles
    assert "Task 2" in titles
    assert "Task 3" in titles
