from tests.conftest import client


def test_create_new_employee():
    new_employee_data = [
        {"full_name": "Test_2",
         "position": "Developer_2"}
    ]

    for employee in new_employee_data:

        response = client.post("/employees/", json=employee)

        assert response.status_code == 201
        created_employee = response.json()
        assert created_employee["full_name"] == employee["full_name"]
        assert created_employee["position"] == employee["position"]


def test_read_employees():
    response = client.get("/employees/")

    assert response.status_code == 200

    employees = response.json()
    assert len(employees) == 3


def test_read_employee():
    employee_id = 1
    response = client.get(f"/employees/{employee_id}")
    assert response.status_code == 200

    non_existing_employee_id = 999
    response = client.get(f"/employees/{non_existing_employee_id}")

    assert response.status_code == 404
    error_message = response.json()
    assert error_message["detail"] == "Employee not found"


def test_put_employee():
    new_employee_data = {
        "full_name": "Test_put",
        "position": "Test_position_put",
    }

    employee_id = 2

    response = client.put(f"/employees/{employee_id}", json=new_employee_data)

    assert response.status_code == 200

    updated_employee = response.json()

    assert updated_employee["id"] == 2
    assert updated_employee["full_name"] == "Test_put"
    assert updated_employee["position"] == "Test_position_put"

    non_existing_employee_id = 999
    response = client.put(f"/employees/{non_existing_employee_id}", json=new_employee_data)

    assert response.status_code == 404
    error_message = response.json()
    assert error_message["detail"] == "Employee not found"


def test_del_employee():
    employee_id = 2

    response = client.delete(f"/employees/{employee_id}")

    assert response.status_code == 200

    non_existing_employee_id = 999
    response = client.delete(f"/employees/{non_existing_employee_id}")

    assert response.status_code == 404
    error_message = response.json()
    assert error_message["detail"] == "Employee not found"


def test_read_employees_tasks():

    response = client.get("/employees/tasks/")
    assert response.status_code == 200

    employees = response.json()
    assert len(employees) == 1
