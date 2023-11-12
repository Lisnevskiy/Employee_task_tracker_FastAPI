from tests.conftest import client


def test_create_new_task():
    new_task_data = {
        "title": "Test_title",
        "deadline": "3024-11-09T06:46:48",
        "parent_task_id": 2
    }

    response = client.post("/tasks/", json=new_task_data)

    assert response.status_code == 201

    created_task = response.json()

    assert created_task["id"] == 3
    assert created_task["title"] == "Test_title"
    assert created_task["parent_task_id"] == 2
    assert created_task["executor_id"] is None
    assert created_task["deadline"] == "3024-11-09T06:46:48"
    assert created_task["is_active"] is False


def test_read_tasks():
    response = client.get("/tasks/")

    assert response.status_code == 200

    task = response.json()
    assert len(task) == 3


def test_read_important_tasks():
    response = client.get("/tasks/important/")
    assert response.status_code == 200

    important_tasks = response.json()

    assert len(important_tasks) == 1


def test_read_task():
    task_id = 1
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200

    non_existing_task_id = 999
    response = client.get(f"/tasks/{non_existing_task_id}")

    assert response.status_code == 404
    error_message = response.json()
    assert error_message["detail"] == "Task not found"


def test_put_task():
    new_task_data = {
        "title": "Test_put",
        "executor_id": 1,
        "deadline": "2024-11-09T06:46:48",
        "is_active": True
    }

    task_id = 1

    response = client.put(f"/tasks/{task_id}", json=new_task_data)

    assert response.status_code == 200

    updated_task = response.json()

    assert updated_task["id"] == 1
    assert updated_task["title"] == "Test_put"
    assert updated_task["parent_task_id"] is None
    assert updated_task["executor_id"] == 1
    assert updated_task["deadline"] == "2024-11-09T06:46:48"
    assert updated_task["is_active"] is True

    non_existing_task_id = 999
    response = client.put(f"/tasks/{non_existing_task_id}", json=new_task_data)

    assert response.status_code == 404
    error_message = response.json()
    assert error_message["detail"] == "Task not found"


def test_del_task():
    task_id = 1

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 200

    non_existing_task_id = 999
    response = client.delete(f"/tasks/{non_existing_task_id}")

    assert response.status_code == 404
    error_message = response.json()
    assert error_message["detail"] == "Task not found"
