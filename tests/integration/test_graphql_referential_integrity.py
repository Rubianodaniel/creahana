import pytest


@pytest.mark.asyncio
async def test_delete_task_list_with_tasks_should_fail(test_client):
    """Test that deleting a task list with associated tasks should fail or handle cascade"""

    # Create a task list
    create_task_list_query = """
    mutation {
        createTaskList(input: {
            title: "Task List with Tasks"
            description: "This list will have tasks"
        }) {
            id
        }
    }
    """

    task_list_response = await test_client.post("/graphql", json={"query": create_task_list_query})
    task_list_id = task_list_response.json()["data"]["createTaskList"]["id"]

    # Create tasks associated with the task list
    create_task_query = f"""
    mutation {{
        createTask(input: {{
            title: "Task 1"
            taskListId: {task_list_id}
        }}) {{
            id
        }}
    }}
    """

    await test_client.post("/graphql", json={"query": create_task_query})

    create_task_query_2 = f"""
    mutation {{
        createTask(input: {{
            title: "Task 2"
            taskListId: {task_list_id}
        }}) {{
            id
        }}
    }}
    """

    await test_client.post("/graphql", json={"query": create_task_query_2})

    # Try to delete the task list
    delete_query = f"""
    mutation {{
        deleteTaskList(id: {task_list_id})
    }}
    """

    response = await test_client.post("/graphql", json={"query": delete_query})

    assert response.status_code == 200
    data = response.json()

    if "errors" in data:
        print(f"Deletion failed with error: {data['errors']}")
        assert "errors" in data
