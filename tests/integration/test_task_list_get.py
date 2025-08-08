import pytest

from tests.helpers.auth_helper import create_test_user_and_get_headers


@pytest.mark.asyncio
async def test_get_task_list_with_tasks_no_filters(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 1)
    
    task_list_data = {"title": "Test Task List", "description": "Test description"}

    create_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert create_response.status_code == 201
    task_list_id = create_response.json()["id"]

    # Create 3 tasks with different statuses
    tasks_data = [
        {
            "title": "Task 1",
            "description": "Pending task",
            "task_list_id": task_list_id,
            "status": "pending",
            "priority": "high",
        },
        {
            "title": "Task 2",
            "description": "Completed task",
            "task_list_id": task_list_id,
            "status": "completed",
            "priority": "medium",
        },
        {
            "title": "Task 3",
            "description": "Pending task",
            "task_list_id": task_list_id,
            "status": "pending",
            "priority": "low",
        },
    ]

    for task_data in tasks_data:
        task_response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)
        assert task_response.status_code == 201

    response = await test_client.get(f"/api/task-lists/{task_list_id}/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert "tasks" in data
    assert "completion_percentage" in data
    assert "total_tasks" in data
    assert "completed_tasks" in data
    assert "id" in data

    assert data["id"] == task_list_id
    assert data["total_tasks"] == 3
    assert data["completed_tasks"] == 1
    assert data["completion_percentage"] == 33.33
    assert len(data["tasks"]) == 3


@pytest.mark.asyncio
async def test_get_task_list_by_id(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 2)
    
    task_list_data = {"title": "Test Task List", "description": "Test description"}

    create_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert create_response.status_code == 201
    created_data = create_response.json()
    task_list_id = created_data["id"]

    get_response = await test_client.get(f"/api/task-lists/{task_list_id}", headers=auth_headers)

    assert get_response.status_code == 200
    data = get_response.json()

    assert data["id"] == task_list_id
    assert data["title"] == "Test Task List"
    assert data["description"] == "Test description"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_task_list_not_found(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 3)
    
    response = await test_client.get("/api/task-lists/999", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_task_lists(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 4)
    
    task_lists = [
        {"title": "List 1", "description": "Description 1"},
        {"title": "List 2", "description": "Description 2"},
        {"title": "List 3", "description": "Description 3"},
    ]

    created_ids = []
    for task_list_data in task_lists:
        response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
        assert response.status_code == 201
        created_ids.append(response.json()["id"])

    get_all_response = await test_client.get("/api/task-lists/", headers=auth_headers)

    assert get_all_response.status_code == 200
    data = get_all_response.json()

    assert len(data) >= 3

    # verify list tittles
    titles = [item["title"] for item in data]
    assert "List 1" in titles
    assert "List 2" in titles
    assert "List 3" in titles


@pytest.mark.asyncio
async def test_get_task_list_with_tasks_filter_by_status(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 5)
    
    task_list_data = {"title": "Test Task List", "description": "Test description"}

    create_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert create_response.status_code == 201
    task_list_id = create_response.json()["id"]

    # Create tasks with different statuses
    tasks_data = [
        {
            "title": "Task 1",
            "task_list_id": task_list_id,
            "status": "pending",
            "priority": "high",
        },
        {
            "title": "Task 2",
            "task_list_id": task_list_id,
            "status": "completed",
            "priority": "medium",
        },
    ]

    for task_data in tasks_data:
        task_response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)
        assert task_response.status_code == 201

    response = await test_client.get(f"/api/task-lists/{task_list_id}/tasks?status=pending", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_tasks"] == 2
    assert data["completed_tasks"] == 1
    assert data["completion_percentage"] == 50.0

    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["status"] == "pending"


@pytest.mark.asyncio
async def test_get_task_list_with_tasks_filter_by_priority(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 6)
    
    task_list_data = {"title": "Test Task List", "description": "Test description"}

    create_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert create_response.status_code == 201
    task_list_id = create_response.json()["id"]

    # Create tasks with different priorities
    tasks_data = [
        {
            "title": "High Priority Task",
            "task_list_id": task_list_id,
            "status": "pending",
            "priority": "high",
        },
        {
            "title": "Medium Priority Task",
            "task_list_id": task_list_id,
            "status": "pending",
            "priority": "medium",
        },
    ]

    for task_data in tasks_data:
        task_response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)
        assert task_response.status_code == 201

    response = await test_client.get(f"/api/task-lists/{task_list_id}/tasks?priority=high", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_tasks"] == 2
    assert data["completed_tasks"] == 0
    assert data["completion_percentage"] == 0.0

    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["priority"] == "high"


@pytest.mark.asyncio
async def test_get_task_list_with_tasks_not_found(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 7)
    
    response = await test_client.get("/api/task-lists/99999/tasks", headers=auth_headers)

    assert response.status_code == 404
    assert "Task list not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_task_list_with_tasks_no_tasks(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 8)
    
    task_list_data = {"title": "Empty Task List", "description": "No tasks here"}

    create_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert create_response.status_code == 201
    task_list_id = create_response.json()["id"]

    response = await test_client.get(f"/api/task-lists/{task_list_id}/tasks", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == task_list_id
    assert data["total_tasks"] == 0
    assert data["completed_tasks"] == 0
    assert data["completion_percentage"] == 0.0
    assert len(data["tasks"]) == 0
