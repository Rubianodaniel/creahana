import pytest

from tests.helpers.auth_helper import create_test_user_and_get_headers


@pytest.mark.asyncio
async def test_create_task_success(test_client):
    """Test creating a task successfully."""
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 1)
    
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
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

    response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)

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
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 2)
    
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Create task with minimal data
    task_data = {"title": "Minimal Task", "task_list_id": task_list_id}

    response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)

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
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 3)
    
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Try to create task without title
    task_data = {"task_list_id": task_list_id, "description": "Task without title"}

    response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_task_short_title(test_client):
    """Test creating a task with title too short."""
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 4)
    
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Try to create task with short title (less than 4 characters)
    task_data = {"title": "abc", "task_list_id": task_list_id}  # Only 3 characters

    response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)

    assert response.status_code == 422 


@pytest.mark.asyncio
async def test_create_task_with_assigned_user(test_client):
    """Test creating a task with assigned user."""
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 5)
    
    # Create a user first
    user_data = {"username": "testuser", "email": "testuser@example.com", "full_name": "Test User"}
    user_response = await test_client.post("/api/users/", json=user_data, headers=auth_headers)
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    # Create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}
    list_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Create task with assigned user
    task_data = {
        "title": "Task with assigned user",
        "description": "This task is assigned to a user",
        "task_list_id": task_list_id,
        "assigned_user_id": user_id,
        "priority": "high"
    }

    response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Task with assigned user"
    assert data["description"] == "This task is assigned to a user"
    assert data["assigned_user_id"] == user_id
    assert data["priority"] == "high"
    assert data["task_list_id"] == task_list_id


@pytest.mark.asyncio
async def test_create_task_with_invalid_assigned_user(e2e_client):
    """Test creating a task with non-existent assigned user - End to End test."""
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(e2e_client, 6)
    
    # Create a valid user and task list first (using real commits)
    user_data = {"username": "validuser", "email": "validuser@example.com", "full_name": "Valid User"}  
    user_response = await e2e_client.post("/api/users/", json=user_data, headers=auth_headers)
    assert user_response.status_code == 201
    valid_user_id = user_response.json()["id"]

    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}
    list_response = await e2e_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # First confirm we can create task with valid user and list
    valid_task_data = {
        "title": "Valid task",
        "task_list_id": task_list_id,
        "assigned_user_id": valid_user_id
    }
    valid_response = await e2e_client.post("/api/tasks/", json=valid_task_data, headers=auth_headers)
    assert valid_response.status_code == 201


    task_data = {
        "title": "Task with invalid user",
        "task_list_id": task_list_id,
        "assigned_user_id": 99999  
    }

    response = await e2e_client.post("/api/tasks/", json=task_data, headers=auth_headers)
    

    assert response.status_code == 400
    response_detail = response.json()["detail"]
    assert ("User 99999 does not exist" in response_detail or 
            "Task list" in response_detail and "does not exist" in response_detail)
