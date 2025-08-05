import pytest


@pytest.mark.asyncio
async def test_delete_task_list_success(test_client):
    """Test deleting a task list successfully."""
    # First create a task list
    task_list_data = {
        "title": "Task List to Delete",
        "description": "This will be deleted"
    }
    
    create_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    task_list_id = created_data["id"]
    
    # Verify it exists
    get_response = await test_client.get(f"/api/task-lists/{task_list_id}")
    assert get_response.status_code == 200
    
    # Delete the task list
    delete_response = await test_client.delete(f"/api/task-lists/{task_list_id}")
    
    assert delete_response.status_code == 204  # No Content
    
    # Verify it no longer exists
    get_after_delete = await test_client.get(f"/api/task-lists/{task_list_id}")
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_list_not_found(test_client):
    """Test deleting a task list that doesn't exist."""
    response = await test_client.delete("/api/task-lists/999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_multiple_task_lists(test_client):
    """Test deleting multiple task lists."""
    # Create multiple task lists
    task_lists = [
        {"title": "List 1", "description": "Description 1"},
        {"title": "List 2", "description": "Description 2"},
        {"title": "List 3", "description": "Description 3"}
    ]
    
    created_ids = []
    for task_list_data in task_lists:
        response = await test_client.post("/api/task-lists/", json=task_list_data)
        assert response.status_code == 201
        created_ids.append(response.json()["id"])
    
    # Delete each task list
    for task_list_id in created_ids:
        delete_response = await test_client.delete(f"/api/task-lists/{task_list_id}")
        assert delete_response.status_code == 204
        
        # Verify deletion
        get_response = await test_client.get(f"/api/task-lists/{task_list_id}")
        assert get_response.status_code == 404