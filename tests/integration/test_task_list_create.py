import pytest

from tests.helpers.auth_helper import create_test_user_and_get_headers


@pytest.mark.asyncio
async def test_create_task_list_without_user_id(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 1)
    
    task_list_data = {"title": "Test Task List", "description": "Test description"}

    response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test Task List"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_task_list_with_user_id(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 2)
    
    # First create a user
    user_data = {"email": "taskowner@example.com", "username": "taskowner"}
    user_response = await test_client.post("/api/users/", json=user_data, headers=auth_headers)
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]
    
    # Now create task_list with the actual user_id
    task_list_data = {
        "title": "Test Task List 2",
        "description": "Test description 2",
        "user_id": user_id,
    }

    response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test Task List 2"
    assert data["user_id"] == user_id


@pytest.mark.asyncio
async def test_create_task_list_missing_title(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 3)
    
    task_list_data = {"description": "Test description"}

    response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_list_empty_title(test_client):
    # Get auth headers
    auth_headers = await create_test_user_and_get_headers(test_client, 4)
    
    task_list_data = {"title": "", "description": "Test description"}

    response = await test_client.post("/api/task-lists/", json=task_list_data, headers=auth_headers)

    assert response.status_code == 422
