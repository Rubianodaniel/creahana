import pytest


@pytest.mark.asyncio
async def test_graphql_create_task_success(test_client):
    """Test successful task creation with all fields"""

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
    create_query = f"""
    mutation {{
        createTask(input: {{
            title: "New Task"
            description: "new task"
            taskListId: {task_list_id}
            status: IN_PROGRESS
            priority: HIGH
            assignedUserId: 42
        }}) {{
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

    response = await test_client.post("/graphql", json={"query": create_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["createTask"] is not None

    task = data["data"]["createTask"]
    assert task["id"] is not None
    assert task["title"] == "New Task"
    assert task["description"] == "new task"
    assert task["taskListId"] == task_list_id
    assert task["status"] == "IN_PROGRESS"
    assert task["priority"] == "HIGH"
    assert task["assignedUserId"] == 42
    assert task["isActive"] is True
    assert task["createdAt"] is not None
    assert task["updatedAt"] is not None


@pytest.mark.asyncio
async def test_graphql_create_task_minimal_data(test_client):
    """Test task creation with only required fields"""

    # Create a task list
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Minimal Task List"
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    create_query = f"""
    mutation {{
        createTask(input: {{
            title: "Minimal Task"
            taskListId: {task_list_id}
        }}) {{
            id
            title
            description
            taskListId
            status
            priority
            assignedUserId
            isActive
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": create_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task = data["data"]["createTask"]

    assert task["id"] is not None
    assert task["title"] == "Minimal Task"
    assert task["description"] is None
    assert task["taskListId"] == task_list_id
    assert task["status"] == "PENDING"  # Default status
    assert task["priority"] == "MEDIUM"  # Default priority
    assert task["assignedUserId"] is None
    assert task["isActive"] is True


@pytest.mark.asyncio
async def test_graphql_create_task_with_description_only(test_client):
    """Test task creation with description but no assigned user"""

    # Create a task list
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Description Task List"
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    create_query = f"""
    mutation {{
        createTask(input: {{
            title: "Task with Description"
            description: "This task has a description but no assigned user"
            taskListId: {task_list_id}
            priority: LOW
        }}) {{
            id
            title
            description
            priority
            assignedUserId
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": create_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task = data["data"]["createTask"]

    assert task["title"] == "Task with Description"
    assert task["description"] == "This task has a description but no assigned user"
    assert task["priority"] == "LOW"
    assert task["assignedUserId"] is None


@pytest.mark.asyncio
async def test_graphql_create_multiple_tasks(test_client):
    """Test creating multiple tasks in sequence"""

    # Create a task list
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Multiple Tasks List"
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    tasks_data = [
        {
            "title": "First Task",
            "status": "PENDING",
            "priority": "HIGH",
            "assignedUserId": 1,
        },
        {
            "title": "Second Task",
            "status": "IN_PROGRESS",
            "priority": "MEDIUM",
            "assignedUserId": 2,
        },
        {
            "title": "Third Task",
            "status": "COMPLETED",
            "priority": "LOW",
            "assignedUserId": 1,
        },
    ]

    created_tasks = []

    for task_data in tasks_data:
        create_query = f"""
        mutation {{
            createTask(input: {{
                title: "{task_data['title']}"
                taskListId: {task_list_id}
                status: {task_data['status']}
                priority: {task_data['priority']}
                assignedUserId: {task_data['assignedUserId']}
            }}) {{
                id
                title
                status
                priority
                assignedUserId
            }}
        }}
        """

        response = await test_client.post("/graphql", json={"query": create_query})

        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data

        task = data["data"]["createTask"]
        created_tasks.append(task)

        assert task["title"] == task_data["title"]
        assert task["status"] == task_data["status"]
        assert task["priority"] == task_data["priority"]
        assert task["assignedUserId"] == task_data["assignedUserId"]

    # Verify all tasks have unique IDs
    ids = [task["id"] for task in created_tasks]
    assert len(ids) == len(set(ids))  # All IDs should be unique
    assert len(created_tasks) == 3


@pytest.mark.asyncio
async def test_graphql_delete_task_success(test_client):
    """Test successful task deletion"""

    # Create task list and task
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Delete Test List"
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
            title: "Task to Delete"
            description: "This will be deleted"
            taskListId: {task_list_id}
        }}) {{
            id
        }}
    }}
    """

    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]

    # Delete the task
    delete_query = f"""
    mutation {{
        deleteTask(id: {task_id})
    }}
    """

    response = await test_client.post("/graphql", json={"query": delete_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["deleteTask"] is True

    # Verify the task is actually deleted by trying to get it
    get_query = f"""
    query {{
        task(id: {task_id}) {{
            id
            title
        }}
    }}
    """

    get_response = await test_client.post("/graphql", json={"query": get_query})
    get_data = get_response.json()

    assert get_data["data"]["task"] is None


@pytest.mark.asyncio
async def test_graphql_delete_task_nonexistent(test_client):
    """Test deleting a non-existent task returns false"""

    delete_query = """
    mutation {
        deleteTask(id: 99999)
    }
    """

    response = await test_client.post("/graphql", json={"query": delete_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["deleteTask"] is False


@pytest.mark.asyncio
async def test_graphql_change_task_status_success(test_client):
    """Test successful task status change"""

    # Create task list and task
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Status Change List"
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
            title: "Status Change Task"
            taskListId: {task_list_id}
            status: PENDING
        }}) {{
            id
        }}
    }}
    """

    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]

    # Change status to IN_PROGRESS
    change_status_query = f"""
    mutation {{
        changeTaskStatus(id: {task_id}, input: {{
            status: IN_PROGRESS
        }}) {{
            id
            title
            status
            updatedAt
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": change_status_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["changeTaskStatus"] is not None

    task = data["data"]["changeTaskStatus"]
    assert task["id"] == task_id
    assert task["title"] == "Status Change Task"
    assert task["status"] == "IN_PROGRESS"
    assert task["updatedAt"] is not None


@pytest.mark.asyncio
async def test_graphql_change_task_status_to_completed(test_client):
    """Test changing task status to completed"""

    # Create task list and task
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Complete Status List"
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
            title: "Task to Complete"
            taskListId: {task_list_id}
            status: IN_PROGRESS
        }}) {{
            id
        }}
    }}
    """

    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]

    # Change status to COMPLETED
    change_status_query = f"""
    mutation {{
        changeTaskStatus(id: {task_id}, input: {{
            status: COMPLETED
        }}) {{
            id
            status
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": change_status_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task = data["data"]["changeTaskStatus"]
    assert task["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_graphql_change_task_status_nonexistent(test_client):
    """Test changing status of non-existent task returns null"""

    change_status_query = """
    mutation {
        changeTaskStatus(id: 99999, input: {
            status: COMPLETED
        }) {
            id
            status
        }
    }
    """

    response = await test_client.post("/graphql", json={"query": change_status_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert data["data"]["changeTaskStatus"] is None


@pytest.mark.asyncio
async def test_graphql_update_task_success(test_client):
    """Test successful task update with all fields"""

    # Create task list and task
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Update Task Test List"
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
            title: "Original Task"
            description: "Original description"
            taskListId: {task_list_id}
            status: PENDING
            priority: LOW
            assignedUserId: 100
        }}) {{
            id
        }}
    }}
    """

    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]

    # Update the task
    update_query = f"""
    mutation {{
        updateTask(id: {task_id}, input: {{
            title: "Updated Task"
            description: "Updated description"
            status: IN_PROGRESS
            priority: HIGH
            assignedUserId: 200
        }}) {{
            id
            title
            description
            status
            priority
            assignedUserId
            updatedAt
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": update_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    assert "data" in data
    assert data["data"]["updateTask"] is not None

    task = data["data"]["updateTask"]
    assert task["id"] == task_id
    assert task["title"] == "Updated Task"
    assert task["description"] == "Updated description"
    assert task["status"] == "IN_PROGRESS"
    assert task["priority"] == "HIGH"
    assert task["assignedUserId"] == 200
    assert task["updatedAt"] is not None


@pytest.mark.asyncio
async def test_graphql_update_task_partial_update(test_client):
    """Test updating only some fields of a task"""

    # Create task list and task
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Partial Update List"
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
            title: "Original Task"
            description: "Original description"
            taskListId: {task_list_id}
            priority: MEDIUM
            assignedUserId: 150
        }}) {{
            id
        }}
    }}
    """

    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]

    # Update only the title and priority
    update_query = f"""
    mutation {{
        updateTask(id: {task_id}, input: {{
            title: "Only Title Updated"
            priority: HIGH
        }}) {{
            id
            title
            description
            priority
            status
            assignedUserId
        }}
    }}
    """

    response = await test_client.post("/graphql", json={"query": update_query})

    assert response.status_code == 200
    data = response.json()

    assert "errors" not in data
    task = data["data"]["updateTask"]

    assert task["title"] == "Only Title Updated"
    assert task["priority"] == "HIGH"


@pytest.mark.asyncio
async def test_graphql_update_task_nonexistent(test_client):
    """Test updating a non-existent task returns null"""

    update_query = """
    mutation {
        updateTask(id: 99999, input: {
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
    assert data["data"]["updateTask"] is None
