import pytest


@pytest.mark.asyncio
async def test_graphql_task_get_existing(test_client):
    """Test getting an existing task by ID"""

    # First create a task list
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Test Task List"
            description: "For task testing"
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    # Create a task
    create_task_query = f"""
    mutation {{
        createTask(input: {{
            title: "Test Task"
            description: "A test task for GraphQL"
            taskListId: {task_list_id}
            status: PENDING
            priority: HIGH
        }}) {{
            id
        }}
    }}
    """

    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    assert create_response.status_code == 200

    create_data = create_response.json()
    task_id = create_data["data"]["createTask"]["id"]

    # Query the task
    get_query = f"""
    query {{
        task(id: {task_id}) {{
            id
            title
            description
            taskListId
            status
            priority
            isActive
            createdAt
            updatedAt
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": get_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["task"] is not None
    assert data["data"]["task"]["id"] == task_id
    assert data["data"]["task"]["title"] == "Test Task"
    assert data["data"]["task"]["description"] == "A test task for GraphQL"
    assert data["data"]["task"]["taskListId"] == task_list_id
    assert data["data"]["task"]["status"] == "PENDING"
    assert data["data"]["task"]["priority"] == "HIGH"
    assert data["data"]["task"]["isActive"] is True
    assert data["data"]["task"]["createdAt"] is not None


@pytest.mark.asyncio
async def test_graphql_task_not_found(test_client):
    """Test getting a non-existent task returns null"""

    get_query = """
    query {
        task(id: 99999) {
            id
            title
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": get_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["task"] is None


@pytest.mark.asyncio
async def test_graphql_task_invalid_id_zero(test_client):
    """Test getting task with ID 0 returns null (validation error)"""

    get_query = """
    query {
        task(id: 0) {
            id
            title
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": get_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["task"] is None


@pytest.mark.asyncio
async def test_graphql_task_invalid_id_negative(test_client):
    """Test getting task with negative ID returns null (validation error)"""

    get_query = """
    query {
        task(id: -5) {
            id
            title
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": get_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["task"] is None


@pytest.mark.asyncio
async def test_graphql_task_with_all_fields(test_client):
    """Test getting task requesting all available fields"""

    # Create a task list
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Complete Task List"
            userId: 123
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    # Create a task with all possible data
    create_task_query = f"""
    mutation {{
        createTask(input: {{
            title: "Complete Task"
            description: "Task with all fields populated"
            taskListId: {task_list_id}
            status: IN_PROGRESS
            priority: MEDIUM
            assignedUserId: 456
        }}) {{
            id
        }}
    }}
    """

    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]

    # Query with all possible fields
    get_query = f"""
    query {{
        task(id: {task_id}) {{
            id
            title
            description
            taskListId
            status
            priority
            assignedUserId
            isActive
            createdAt
            updatedAt
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": get_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["task"] is not None

    task = data["data"]["task"]
    assert task["id"] == task_id
    assert task["title"] == "Complete Task"
    assert task["description"] == "Task with all fields populated"
    assert task["taskListId"] == task_list_id
    assert task["status"] == "IN_PROGRESS"
    assert task["priority"] == "MEDIUM"
    assert task["assignedUserId"] == 456
    assert task["isActive"] is True
    assert task["createdAt"] is not None
    assert task["updatedAt"] is not None


@pytest.mark.asyncio
async def test_graphql_task_minimal_fields(test_client):
    """Test getting task with minimal field selection"""

    # Create task list and task
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Minimal Field Test"
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    create_task_query = f"""
    mutation {{
        createTask(input: {{
            title: "Minimal Task"
            taskListId: {task_list_id}
        }}) {{
            id
        }}
    }}
    """

    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]

    # Query with only required fields
    get_query = f"""
    query {{
        task(id: {task_id}) {{
            id
            title
            status
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": get_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task = data["data"]["task"]
    assert task["id"] == task_id
    assert task["title"] == "Minimal Task"
    assert task["status"] == "PENDING"  # Default status
    # Should only contain the requested fields
    assert len(task.keys()) == 3


@pytest.mark.asyncio
async def test_graphql_tasks_get_all(test_client):
    """Test getting all tasks"""

    # Create a task list
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Tasks List"
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    # Create multiple tasks
    tasks_data = [
        {"title": "First Task", "status": "PENDING", "priority": "HIGH"},
        {"title": "Second Task", "status": "IN_PROGRESS", "priority": "MEDIUM"},
        {"title": "Third Task", "status": "COMPLETED", "priority": "LOW"},
    ]

    created_ids = []
    for task_data in tasks_data:
        create_task_query = f"""
        mutation {{
            createTask(input: {{
                title: "{task_data['title']}"
                taskListId: {task_list_id}
                status: {task_data['status']}
                priority: {task_data['priority']}
            }}) {{
                id
            }}
        }}
        """

        create_response = await test_client.post("/graphql", json={"query": create_task_query})
        assert create_response.status_code == 200
        created_ids.append(create_response.json()["data"]["createTask"]["id"])

    # Query all tasks
    get_all_query = """
    query {
        tasks {
            id
            title
            status
            priority
            isActive
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": get_all_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["tasks"] is not None

    returned_ids = [task["id"] for task in data["data"]["tasks"]]
    returned_titles = [task["title"] for task in data["data"]["tasks"]]

    for created_id in created_ids:
        assert created_id in returned_ids

    assert "First Task" in returned_titles
    assert "Second Task" in returned_titles
    assert "Third Task" in returned_titles


@pytest.mark.asyncio
async def test_graphql_tasks_empty_result(test_client):
    """Test getting tasks when there might be none (edge case)"""

    # Query all tasks without creating any new ones
    get_all_query = """
    query {
        tasks {
            id
            title
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": get_all_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["tasks"] is not None
    assert isinstance(data["data"]["tasks"], list)
