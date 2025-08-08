import pytest
from tests.helpers.auth_helper import create_test_user_and_get_headers


@pytest.mark.asyncio
async def test_delete_task_success(test_client):
    auth_headers = await create_test_user_and_get_headers(test_client, 101)
    """Test deleting a task successfully."""
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Create a task
    task_data = {
        "title": "Task to Delete",
        "description": "This will be deleted",
        "task_list_id": task_list_id,
    }

    create_response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Verify it exists
    get_response = await test_client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 200

    # Delete the task
    delete_response = await test_client.delete(f"/api/tasks/{task_id}", headers=auth_headers)

    assert delete_response.status_code == 204  # No Content

    # Verify it no longer exists
    get_after_delete = await test_client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_not_found(test_client):
    auth_headers = await create_test_user_and_get_headers(test_client, 102)
    """Test deleting a task that doesn't exist."""
    response = await test_client.delete("/api/tasks/999", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_multiple_tasks(test_client):
    auth_headers = await create_test_user_and_get_headers(test_client, 103)
    """Test deleting multiple tasks."""
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Create multiple tasks
    tasks = [
        {
            "title": "Task 1",
            "description": "Description 1",
            "task_list_id": task_list_id,
        },
        {
            "title": "Task 2",
            "description": "Description 2",
            "task_list_id": task_list_id,
        },
        {
            "title": "Task 3",
            "description": "Description 3",
            "task_list_id": task_list_id,
        },
    ]

    created_ids = []
    for task_data in tasks:
        response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        created_ids.append(response.json()["id"])

    # Delete each task
    for task_id in created_ids:
        delete_response = await test_client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
        assert delete_response.status_code == 204

        # Verify deletion
        get_response = await test_client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_from_task_list(test_client):
    auth_headers = await create_test_user_and_get_headers(test_client, 104)
    """Test that deleting a task doesn't affect the parent task list."""
    # First create a task list
    task_list_data = {"title": "Parent Task List", "description": "List for tasks"}

    list_response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)
    assert list_response.status_code == 201
    task_list_id = list_response.json()["id"]

    # Create a task
    task_data = {
        "title": "Task to Delete",
        "description": "This will be deleted",
        "task_list_id": task_list_id,
    }

    create_response = await test_client.post("/api/tasks/", json=task_data, headers=auth_headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Delete the task
    delete_response = await test_client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    # Verify the task list still exists
    list_get_response = await test_client.get(f"/api/task-lists/{task_list_id}", headers=auth_headers)
    assert list_get_response.status_code == 200
    list_data = list_get_response.json()
    assert list_data["title"] == "Parent Task List"
