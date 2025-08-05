import pytest


@pytest.mark.asyncio
async def test_graphql_create_task(test_client):

    # First create a task list
    task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Test List"
            description: "For task creation"
        }) {
            id
        }
    }
    """
    
    task_list_response = await test_client.post("/graphql", json={"query": task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]
    
    # Create task
    create_task_query = f"""
    mutation {{
        createTask(input: {{
            title: "GraphQL Task"
            description: "Created via GraphQL"
            taskListId: {task_list_id}
            status: PENDING
            priority: HIGH
        }}) {{
            id
            title
            description
            taskListId
            status
            priority
            isActive
        }}
    }}
    """
    
    response = await test_client.post("/graphql", json={"query": create_task_query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["createTask"]["title"] == "GraphQL Task"
    assert data["data"]["createTask"]["description"] == "Created via GraphQL"
    assert data["data"]["createTask"]["taskListId"] == task_list_id
    assert data["data"]["createTask"]["status"] == "PENDING"
    assert data["data"]["createTask"]["priority"] == "HIGH"
    assert data["data"]["createTask"]["isActive"] is True


@pytest.mark.asyncio
async def test_graphql_get_task(test_client):

    # Create task list and task
    task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Test List"
        }) {
            id
        }
    }
    """
    
    task_list_response = await test_client.post("/graphql", json={"query": task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]
    
    create_task_query = f"""
    mutation {{
        createTask(input: {{
            title: "Task to Query"
            taskListId: {task_list_id}
        }}) {{
            id
        }}
    }}
    """
    
    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]
    
    # Query the task
    get_query = f"""
    query {{
        task(id: {task_id}) {{
            id
            title
            taskListId
            status
            priority
        }}
    }}
    """
    
    response = await test_client.post("/graphql", json={"query": get_query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["task"]["id"] == task_id
    assert data["data"]["task"]["title"] == "Task to Query"
    assert data["data"]["task"]["taskListId"] == task_list_id


@pytest.mark.asyncio
async def test_graphql_change_task_status(test_client):

    # Create task list and task
    task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Status Test List"
        }) {
            id
        }
    }
    """
    
    task_list_response = await test_client.post("/graphql", json={"query": task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]
    
    create_task_query = f"""
    mutation {{
        createTask(input: {{
            title: "Task for Status Change"
            taskListId: {task_list_id}
            status: PENDING
        }}) {{
            id
        }}
    }}
    """
    
    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]
    
    # Change status to completed
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
    assert data["data"]["changeTaskStatus"]["id"] == task_id
    assert data["data"]["changeTaskStatus"]["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_graphql_get_all_tasks(test_client):

    # Create task list
    task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Tasks List"
        }) {
            id
        }
    }
    """
    
    task_list_response = await test_client.post("/graphql", json={"query": task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]
    
    # Create multiple tasks
    tasks_data = [
        {"title": "GraphQL Task 1", "priority": "HIGH"},
        {"title": "GraphQL Task 2", "priority": "MEDIUM"}
    ]
    
    for task_data in tasks_data:
        create_query = f"""
        mutation {{
            createTask(input: {{
                title: "{task_data['title']}"
                taskListId: {task_list_id}
                priority: {task_data['priority']}
            }}) {{
                id
            }}
        }}
        """
        await test_client.post("/graphql", json={"query": create_query})
    
    # Query all tasks
    query = """
    query {
        tasks {
            id
            title
            priority
        }
    }
    """
    
    response = await test_client.post("/graphql", json={"query": query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert len(data["data"]["tasks"]) >= 2
    
    titles = [task["title"] for task in data["data"]["tasks"]]
    assert "GraphQL Task 1" in titles
    assert "GraphQL Task 2" in titles


@pytest.mark.asyncio
async def test_graphql_update_task(test_client):

    # Create task list and task
    task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Update Test List"
        }) {
            id
        }
    }
    """
    
    task_list_response = await test_client.post("/graphql", json={"query": task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]
    
    create_task_query = f"""
    mutation {{
        createTask(input: {{
            title: "Original Task"
            taskListId: {task_list_id}
            priority: LOW
        }}) {{
            id
        }}
    }}
    """
    
    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]
    
    # Update task
    update_query = f"""
    mutation {{
        updateTask(id: {task_id}, input: {{
            title: "Updated Task"
            priority: HIGH
            status: IN_PROGRESS
        }}) {{
            id
            title
            priority
            status
        }}
    }}
    """
    
    response = await test_client.post("/graphql", json={"query": update_query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["updateTask"]["title"] == "Updated Task"
    assert data["data"]["updateTask"]["priority"] == "HIGH"
    assert data["data"]["updateTask"]["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_graphql_delete_task(test_client):

    # Create task list and task
    task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Delete Test List"
        }) {
            id
        }
    }
    """
    
    task_list_response = await test_client.post("/graphql", json={"query": task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]
    
    create_task_query = f"""
    mutation {{
        createTask(input: {{
            title: "Task to Delete"
            taskListId: {task_list_id}
        }}) {{
            id
        }}
    }}
    """
    
    create_response = await test_client.post("/graphql", json={"query": create_task_query})
    task_id = create_response.json()["data"]["createTask"]["id"]
    
    # Delete task
    delete_query = f"""
    mutation {{
        deleteTask(id: {task_id})
    }}
    """
    
    response = await test_client.post("/graphql", json={"query": delete_query})
    
    assert response.status_code == 200
    data = response.json()
    
    assert "errors" not in data
    assert data["data"]["deleteTask"] is True
    
    # Verify it's deleted
    get_query = f"""
    query {{
        task(id: {task_id}) {{
            id
        }}
    }}
    """
    
    get_response = await test_client.post("/graphql", json={"query": get_query})
    get_data = get_response.json()
    
    assert get_data["data"]["task"] is None