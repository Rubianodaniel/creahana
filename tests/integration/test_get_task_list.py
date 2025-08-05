import pytest


@pytest.mark.asyncio
async def test_get_task_list_by_id(test_client):

    task_list_data = {
        "title": "Test Task List",
        "description": "Test description"
    }
    
    create_response = await test_client.post("/api/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    task_list_id = created_data["id"]
    
    get_response = await test_client.get(f"/api/task-lists/{task_list_id}")
    
    assert get_response.status_code == 200
    data = get_response.json()
    
    assert data["id"] == task_list_id
    assert data["title"] == "Test Task List"
    assert data["description"] == "Test description"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_task_list_not_found(test_client):
    response = await test_client.get("/api/task-lists/999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_task_lists(test_client):
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

    get_all_response = await test_client.get("/api/task-lists/")
    
    assert get_all_response.status_code == 200
    data = get_all_response.json()
    
    assert len(data) >= 3 

    # verify list tittles
    titles = [item["title"] for item in data]
    assert "List 1" in titles
    assert "List 2" in titles
    assert "List 3" in titles