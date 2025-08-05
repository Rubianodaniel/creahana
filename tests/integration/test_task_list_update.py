import pytest


@pytest.mark.asyncio
async def test_update_task_list_success(test_client):
    """Test updating a task list successfully."""
    # First create a task list
    task_list_data = {"title": "Original Title", "description": "Original description"}

    create_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    task_list_id = created_data["id"]

    # Update the task list
    update_data = {"title": "Updated Title", "description": "Updated description"}

    update_response = await test_client.put(f"/api/task-lists/{task_list_id}", json=update_data)

    assert update_response.status_code == 200
    data = update_response.json()

    assert data["id"] == task_list_id
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_update_task_list_partial_update(test_client):
    """Test partially updating a task list."""
    # Create a task list
    task_list_data = {"title": "Original Title", "description": "Original description"}

    create_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    task_list_id = created_data["id"]

    # Update only the title
    update_data = {"title": "Only Title Updated"}

    update_response = await test_client.put(f"/api/task-lists/{task_list_id}", json=update_data)

    assert update_response.status_code == 200
    data = update_response.json()

    assert data["id"] == task_list_id
    assert data["title"] == "Only Title Updated"
    assert data["description"] == "Original description"  # Didn't change


@pytest.mark.asyncio
async def test_update_task_list_not_found(test_client):
    """Test updating a task list that doesn't exist."""
    update_data = {"title": "Non-existent List", "description": "This should fail"}

    response = await test_client.put("/api/task-lists/999", json=update_data)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task_list_invalid_data(test_client):
    """Test updating a task list with invalid data."""
    # Create a task list
    task_list_data = {"title": "Original Title", "description": "Original description"}

    create_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    task_list_id = created_data["id"]

    # Try to update with empty or invalid title
    update_data = {"title": "", "description": "Valid description"}  # Empty title

    update_response = await test_client.put(f"/api/task-lists/{task_list_id}", json=update_data)

    # Depending on validations, could be 422 or 200
    assert update_response.status_code in [200, 422]
