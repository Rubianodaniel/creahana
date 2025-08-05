import pytest


@pytest.mark.asyncio
async def test_graphql_create_task_list_success(test_client):
    """Test successful task list creation with all fields"""

    create_query = """
    mutation {
        createTaskList(input: {
            title: "My New Task List"
            description: "A task list"
            userId: 42
        }) {
            id
            title
            description
            userId
            isActive
            createdAt
            updatedAt
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": create_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["createTaskList"] is not None

    task_list = data["data"]["createTaskList"]
    assert task_list["id"] is not None
    assert task_list["title"] == "My New Task List"
    assert task_list["description"] == "A task list"
    assert task_list["isActive"] is True
    assert task_list["createdAt"] is not None
    assert task_list["updatedAt"] is not None


@pytest.mark.asyncio
async def test_graphql_create_task_list_minimal_data(test_client):
    """Test task list creation with only required fields"""

    create_query = """
    mutation {
        createTaskList(input: {
            title: "Minimal Task List"
        }) {
            id
            title
            description
            userId
            isActive
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": create_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task_list = data["data"]["createTaskList"]

    assert task_list["id"] is not None
    assert task_list["title"] == "Minimal Task List"
    assert task_list["description"] is None
    assert task_list["userId"] is None
    assert task_list["isActive"] is True


@pytest.mark.asyncio
async def test_graphql_create_task_list_empty_title_should_fail(test_client):
    """Test that creating task list with empty title should fail"""

    create_query = """
    mutation {
        createTaskList(input: {
            title: ""
            description: "Task list with empty title"
        }) {
            id
            title
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": create_query})

    assert response.status_code == 200
    data = response.json()

    # Should contain errors due to validation failure
    assert "errors" in data


@pytest.mark.asyncio
async def test_graphql_create_task_list_long_title_should_fail(test_client):
    """Test that creating task list with very long title should fail"""

    long_title = "A" * 300

    create_query = f"""
    mutation {{
        createTaskList(input: {{
            title: "{long_title}"
            description: "Task list with very long title"
        }}) {{
            id
            title
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": create_query})

    assert response.status_code == 200
    data = response.json()

    # Should contain errors due to validation failure
    assert "errors" in data


@pytest.mark.asyncio
async def test_graphql_create_task_list_with_description_only(test_client):
    """Test task list creation with description but no user"""

    create_query = """
    mutation {
        createTaskList(input: {
            title: "Task List with Description"
            description: "This task list has a description but no assigned user"
        }) {
            id
            title
            description
            userId
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": create_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task_list = data["data"]["createTaskList"]

    assert task_list["title"] == "Task List with Description"
    assert task_list["description"] == "This task list has a description but no assigned user"
    assert task_list["userId"] is None


@pytest.mark.asyncio
async def test_graphql_create_multiple_task_lists(test_client):
    """Test creating multiple task lists in sequence"""

    task_lists_data = [
        {"title": "First Project", "description": "First project tasks", "userId": 1},
        {"title": "Second Project", "description": "Second project tasks", "userId": 2},
        {
            "title": "Personal Tasks",
            "description": "My personal task list",
            "userId": 1,
        },
    ]

    created_task_lists = []

    for tl_data in task_lists_data:
        create_query = f"""
        mutation {{
            createTaskList(input: {{
                title: "{tl_data['title']}"
                description: "{tl_data['description']}"
                userId: {tl_data['userId']}
            }}) {{
                id
                title
                description
                userId
            }}
        }}
        """

        response = await test_client.post("/graphql", json={"query": create_query})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data

        task_list = data["data"]["createTaskList"]
        created_task_lists.append(task_list)

        assert task_list["title"] == tl_data["title"]
        assert task_list["description"] == tl_data["description"]
        assert task_list["userId"] == tl_data["userId"]

    # Verify all task lists have unique IDs
    ids = [tl["id"] for tl in created_task_lists]
    assert len(ids) == len(set(ids))
    assert len(created_task_lists) == 3


@pytest.mark.asyncio
async def test_graphql_update_task_list_success(test_client):
    """Test successful task list update with all fields"""

    # First create a task list
    create_query = """
    mutation {
        createTaskList(input: {
            title: "Original Title"
            description: "Original description"
            userId: 100
        }) {
            id
        }
    }
    """

    create_response = await test_client.post("/graphql", json={"query": create_query})
    task_list_id = create_response.json()["data"]["createTaskList"]["id"]

    # Update the task list
    update_query = f"""
    mutation {{
        updateTaskList(id: {task_list_id}, input: {{
            title: "Updated Title"
            description: "Updated description"
            userId: 200
        }}) {{
            id
            title
            description
            userId
            isActive
            updatedAt
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": update_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["updateTaskList"] is not None

    task_list = data["data"]["updateTaskList"]
    assert task_list["id"] == task_list_id
    assert task_list["title"] == "Updated Title"
    assert task_list["description"] == "Updated description"
    assert task_list["userId"] == 200
    assert task_list["isActive"] is True
    assert task_list["updatedAt"] is not None


@pytest.mark.asyncio
async def test_graphql_update_task_list_partial_update(test_client):
    """Test updating only some fields of a task list"""

    # Create a task list
    create_query = """
    mutation {
        createTaskList(input: {
            title: "Original Title"
            description: "Original description"
            userId: 100
        }) {
            id
        }
    }
    """

    create_response = await test_client.post("/graphql", json={"query": create_query})
    task_list_id = create_response.json()["data"]["createTaskList"]["id"]

    # Update only the title
    update_query = f"""
    mutation {{
        updateTaskList(id: {task_list_id}, input: {{
            title: "Only Title Updated"
        }}) {{
            id
            title
            description
            userId
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": update_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task_list = data["data"]["updateTaskList"]

    assert task_list["title"] == "Only Title Updated"
    assert task_list["description"] == "Original description"
    assert task_list["userId"] == 100


@pytest.mark.asyncio
async def test_graphql_update_task_list_nonexistent(test_client):
    """Test updating a non-existent task list returns null"""

    update_query = """
    mutation {
        updateTaskList(id: 99999, input: {
            title: "Updated Title"
        }) {
            id
            title
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": update_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert data["data"]["updateTaskList"] is None


@pytest.mark.asyncio
async def test_graphql_delete_task_list_success(test_client):
    """Test successful task list deletion"""

    # First create a task list
    create_query = """
    mutation {
        createTaskList(input: {
            title: "Task List to Delete"
            description: "This will be deleted"
        }) {
            id
        }
    }
    """

    create_response = await test_client.post("/graphql", json={"query": create_query})
    task_list_id = create_response.json()["data"]["createTaskList"]["id"]

    # Delete the task list
    delete_query = f"""
    mutation {{
        deleteTaskList(id: {task_list_id})
    }}
    """

    response = await test_client.post("/graphql", json={"query": delete_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["deleteTaskList"] is True

    # Verify the task list is actually deleted by trying to get it
    get_query = f"""
    query {{
        taskList(id: {task_list_id}) {{
            id
            title
        }}
    }}
    """

    get_response = await test_client.post("/graphql", json={"query": get_query})
    get_data = get_response.json()

    assert get_data["data"]["taskList"] is None


@pytest.mark.asyncio
async def test_graphql_delete_task_list_nonexistent(test_client):
    """Test deleting a non-existent task list returns false"""

    delete_query = """
    mutation {
        deleteTaskList(id: 99999)
    }
    """

    response = await test_client.post("/graphql", json={"query": delete_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["deleteTaskList"] is False


@pytest.mark.asyncio
async def test_graphql_delete_task_list_negative_id(test_client):
    """Test deleting with negative ID returns false"""

    delete_query = """
    mutation {
        deleteTaskList(id: -1)
    }
    """

    response = await test_client.post("/graphql", json={"query": delete_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert data["data"]["deleteTaskList"] is False
