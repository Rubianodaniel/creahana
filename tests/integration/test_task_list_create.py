import pytest


@pytest.mark.asyncio
async def test_create_task_list_without_user_id(test_client):
    task_list_data = {"title": "Test Task List", "description": "Test description"}

    response = await test_client.post("/api/task-lists/", json=task_list_data)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test Task List"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_task_list_with_user_id(test_client):
    task_list_data = {
        "title": "Test Task List 2",
        "description": "Test description 2",
        "user_id": 123,
    }

    response = await test_client.post("/api/task-lists/", json=task_list_data)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test Task List 2"
    assert data["user_id"] == 123


@pytest.mark.asyncio
async def test_create_task_list_missing_title(test_client):
    task_list_data = {"description": "Test description"}

    response = await test_client.post("/api/task-lists/", json=task_list_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_list_empty_title(test_client):
    task_list_data = {"title": "", "description": "Test description"}

    response = await test_client.post("/api/task-lists/", json=task_list_data)

    assert response.status_code == 422
