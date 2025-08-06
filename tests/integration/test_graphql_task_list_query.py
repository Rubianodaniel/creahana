import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_graphql_task_list_get_existing(test_client):
    """Test getting an existing task list by ID"""

    # First create a task list
    create_query = """
    mutation {
        createTaskList(input: {
            title: "Test Task List"
            description: "A test task list for GraphQL"
        }) {
            id
            title
            description
        }
    }
    """

    create_response = await test_client.post("/graphql", json={"query": create_query})
    assert create_response.status_code == 200

    create_data = create_response.json()
    task_list_id = create_data["data"]["createTaskList"]["id"]

    # Query the task list
    get_query = f"""
    query {{
        taskList(id: {task_list_id}) {{
            id
            title
            description
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
    assert data["data"]["taskList"] is not None
    assert data["data"]["taskList"]["id"] == task_list_id
    assert data["data"]["taskList"]["title"] == "Test Task List"
    assert data["data"]["taskList"]["description"] == "A test task list for GraphQL"
    assert data["data"]["taskList"]["isActive"] is True
    assert data["data"]["taskList"]["createdAt"] is not None


@pytest.mark.asyncio
async def test_graphql_task_list_not_found(test_client):
    """Test getting a non-existent task list returns null"""

    get_query = """
    query {
        taskList(id: 99999) {
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
    assert data["data"]["taskList"] is None


@pytest.mark.asyncio
async def test_graphql_task_list_invalid_id_zero(test_client):
    """Test getting task list with ID 0 returns null (validation error)"""

    get_query = """
    query {
        taskList(id: 0) {
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
    assert data["data"]["taskList"] is None


@pytest.mark.asyncio
async def test_graphql_task_list_invalid_id_negative(test_client):
    """Test getting task list with negative ID returns null (validation error)"""

    get_query = """
    query {
        taskList(id: -5) {
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
    assert data["data"]["taskList"] is None


@pytest.mark.asyncio
async def test_graphql_task_list_with_all_fields(test_client):
    """Test getting task list requesting all available fields"""


    # Create a task list with all possible data
    create_query = f"""
    mutation {{
        createTaskList(input: {{
            title: "Complete Task List"
            description: "Task list with all fields populated"
        }}) {{
            id
        }}
    }}
    """

    create_response = await test_client.post("/graphql", json={"query": create_query})
    task_list_id = create_response.json()["data"]["createTaskList"]["id"]

    # Query with all possible fields
    get_query = f"""
    query {{
        taskList(id: {task_list_id}) {{
            id
            title
            description
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
    assert data["data"]["taskList"] is not None

    task_list = data["data"]["taskList"]
    assert task_list["id"] == task_list_id
    assert task_list["title"] == "Complete Task List"
    assert task_list["description"] == "Task list with all fields populated"
    assert task_list["isActive"] is True
    assert task_list["createdAt"] is not None
    assert task_list["updatedAt"] is not None


@pytest.mark.asyncio
async def test_graphql_task_list_minimal_fields(test_client):
    """Test getting task list with minimal field selection"""

    # Create a task list
    create_query = """
    mutation {
        createTaskList(input: {
            title: "Minimal Field Test"
        }) {
            id
        }
    }
    """

    create_response = await test_client.post("/graphql", json={"query": create_query})
    task_list_id = create_response.json()["data"]["createTaskList"]["id"]

    # Query with only required fields
    get_query = f"""
    query {{
        taskList(id: {task_list_id}) {{
            id
            title
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": get_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task_list = data["data"]["taskList"]
    assert task_list["id"] == task_list_id
    assert task_list["title"] == "Minimal Field Test"
    # Should only contain the requested fields
    assert len(task_list.keys()) == 2


@pytest.mark.asyncio
async def test_graphql_task_lists_get_all(test_client):
    """Test getting all task lists"""

    # Create multiple task lists
    task_lists_data = [
        {"title": "First List", "description": "First description"},
        {"title": "Second List", "description": "Second description"},
        {"title": "Third List", "description": "Third description"},
    ]

    created_ids = []
    for task_list_data in task_lists_data:
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

        create_response = await test_client.post("/graphql", json={"query": create_query})
        assert create_response.status_code == 200
        created_ids.append(create_response.json()["data"]["createTaskList"]["id"])

    # Query all task lists
    get_all_query = """
    query {
        taskLists {
            id
            title
            description
            isActive
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": get_all_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["taskLists"] is not None

    returned_ids = [tl["id"] for tl in data["data"]["taskLists"]]
    returned_titles = [tl["title"] for tl in data["data"]["taskLists"]]

    for created_id in created_ids:
        assert created_id in returned_ids

    assert "First List" in returned_titles
    assert "Second List" in returned_titles
    assert "Third List" in returned_titles


@pytest.mark.asyncio
async def test_graphql_task_lists_empty_result(test_client):
    """Test getting task lists when there might be none (edge case)"""

    # Query all task lists without creating any new ones
    get_all_query = """
    query {
        taskLists {
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
    assert data["data"]["taskLists"] is not None
    assert isinstance(data["data"]["taskLists"], list)


@pytest.mark.asyncio
async def test_graphql_task_list_with_tasks(test_client):
    """Test getting task list with its tasks and completion stats"""

    # First create a task list
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Task List with Tasks"
            description: "Testing with tasks"
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    # Create some tasks with different statuses
    tasks_data = [
        {"title": "Task 1", "status": "PENDING", "priority": "HIGH"},
        {"title": "Task 2", "status": "IN_PROGRESS", "priority": "MEDIUM"},
        {"title": "Task 3", "status": "COMPLETED", "priority": "LOW"},
    ]

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

        await test_client.post("/graphql", json={"query": create_task_query})

    # Query task list with tasks
    get_with_tasks_query = f"""
    query {{
        taskListWithTasks(id: {task_list_id}) {{
            id
            title
            description
            tasks {{
                id
                title
                status
                priority
            }}
            completionPercentage
            totalTasks
            completedTasks
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": get_with_tasks_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["taskListWithTasks"] is not None

    task_list_with_tasks = data["data"]["taskListWithTasks"]
    assert task_list_with_tasks["id"] == task_list_id
    assert task_list_with_tasks["title"] == "Task List with Tasks"
    assert task_list_with_tasks["totalTasks"] == 3
    assert task_list_with_tasks["completedTasks"] == 1
    assert abs(task_list_with_tasks["completionPercentage"] - 33.33) < 0.1  # ~33.33%

    # Verify tasks are present
    tasks = task_list_with_tasks["tasks"]
    assert len(tasks) == 3

    task_titles = [task["title"] for task in tasks]
    assert "Task 1" in task_titles
    assert "Task 2" in task_titles
    assert "Task 3" in task_titles


@pytest.mark.asyncio
async def test_graphql_task_list_with_tasks_filtered_by_status(test_client):
    """Test getting task list with tasks filtered by status"""

    # Create task list and tasks (same setup as above)
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Filtered Task List"
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    # Create tasks with different statuses
    tasks_data = [
        {"title": "Pending Task 1", "status": "PENDING"},
        {"title": "Pending Task 2", "status": "PENDING"},
        {"title": "Completed Task", "status": "COMPLETED"},
    ]

    for task_data in tasks_data:
        create_task_query = f"""
        mutation {{
            createTask(input: {{
                title: "{task_data['title']}"
                taskListId: {task_list_id}
                status: {task_data['status']}
            }}) {{
                id
            }}
        }}
        """

        await test_client.post("/graphql", json={"query": create_task_query})

    # Query with status filter
    get_filtered_query = f"""
    query {{
        taskListWithTasks(id: {task_list_id}, status: "pending") {{
            id
            tasks {{
                title
                status
            }}
            totalTasks
            completedTasks
            completionPercentage
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": get_filtered_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task_list_with_tasks = data["data"]["taskListWithTasks"]

    # Should only return pending tasks
    tasks = task_list_with_tasks["tasks"]
    for task in tasks:
        assert task["status"] == "PENDING"

    # Should still show total stats
    assert abs(task_list_with_tasks["completionPercentage"] - 33.33) < 0.1  # ~33.33%
    assert task_list_with_tasks["totalTasks"] == 3
    assert task_list_with_tasks["completedTasks"] == 1
