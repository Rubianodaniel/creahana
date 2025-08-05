import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_graphql_create_task_list(test_client):

    query = """
    mutation {
        createTaskList(input: {
            title: "GraphQL Test List"
            description: "Created via GraphQL"
        }) {
            id
            title
            description
            isActive
        }
    }
    """
    
    response = await test_client.post("/graphql", json={"query": query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert "data" in data
    assert data["data"]["createTaskList"]["title"] == "GraphQL Test List"
    assert data["data"]["createTaskList"]["description"] == "Created via GraphQL"
    assert data["data"]["createTaskList"]["isActive"] is True
    assert data["data"]["createTaskList"]["id"] is not None


@pytest.mark.asyncio
async def test_graphql_get_task_list(test_client):

    # First create a task list
    create_query = """
    mutation {
        createTaskList(input: {
            title: "Test List for Query"
            description: "Test description"
        }) {
            id
        }
    }
    """
    
    create_response = await test_client.post("/graphql", json={"query": create_query})
    task_list_id = create_response.json()["data"]["createTaskList"]["id"]
    
    # Then query it
    get_query = f"""
    query {{
        taskList(id: {task_list_id}) {{
            id
            title
            description
            isActive
        }}
    }}
    """
    
    response = await test_client.post("/graphql", json={"query": get_query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["taskList"]["id"] == task_list_id
    assert data["data"]["taskList"]["title"] == "Test List for Query"


@pytest.mark.asyncio
async def test_graphql_get_all_task_lists(test_client):

    # Create multiple task lists
    task_lists = [
        {"title": "GraphQL List 1", "description": "First list"},
        {"title": "GraphQL List 2", "description": "Second list"}
    ]
    
    for task_list_data in task_lists:
        create_query = f"""
        mutation {{
            createTaskList(input: {{
                title: "{task_list_data['title']}"
                description: "{task_list_data['description']}"
            }}) {{
                id
            }}
        }}
        """
        await test_client.post("/graphql", json={"query": create_query})
    
    # Query all task lists
    query = """
    query {
        taskLists {
            id
            title
            description
        }
    }
    """
    
    response = await test_client.post("/graphql", json={"query": query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert len(data["data"]["taskLists"]) >= 2
    
    titles = [item["title"] for item in data["data"]["taskLists"]]
    assert "GraphQL List 1" in titles
    assert "GraphQL List 2" in titles


@pytest.mark.asyncio
async def test_graphql_update_task_list(test_client):

    # Create task list
    create_query = """
    mutation {
        createTaskList(input: {
            title: "Original Title"
            description: "Original description"
        }) {
            id
        }
    }
    """
    
    create_response = await test_client.post("/graphql", json={"query": create_query})
    task_list_id = create_response.json()["data"]["createTaskList"]["id"]
    
    # Update task list
    update_query = f"""
    mutation {{
        updateTaskList(id: {task_list_id}, input: {{
            title: "Updated Title"
            description: "Updated description"
        }}) {{
            id
            title
            description
        }}
    }}
    """
    
    response = await test_client.post("/graphql", json={"query": update_query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["updateTaskList"]["title"] == "Updated Title"
    assert data["data"]["updateTaskList"]["description"] == "Updated description"


@pytest.mark.asyncio
async def test_graphql_delete_task_list(test_client):

    # Create task list
    create_query = """
    mutation {
        createTaskList(input: {
            title: "To Delete"
            description: "Will be deleted"
        }) {
            id
        }
    }
    """
    
    create_response = await test_client.post("/graphql", json={"query": create_query})
    task_list_id = create_response.json()["data"]["createTaskList"]["id"]
    
    # Delete task list
    delete_query = f"""
    mutation {{
        deleteTaskList(id: {task_list_id})
    }}
    """
    
    response = await test_client.post("/graphql", json={"query": delete_query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["deleteTaskList"] is True
    
    # Verify it's deleted
    get_query = f"""
    query {{
        taskList(id: {task_list_id}) {{
            id
        }}
    }}
    """
    
    get_response = await test_client.post("/graphql", json={"query": get_query})
    get_data = get_response.json()
    
    assert get_data["data"]["taskList"] is None