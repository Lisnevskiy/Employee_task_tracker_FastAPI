from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.task import Task
from app.schemas.employee_schemas import EmployeeCreateSchema, EmployeeUpdateSchema


def get_employee(db: Session, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Employee).offset(skip).limit(limit).all()


def get_employees_tasks(db: Session, skip: int = 0, limit: int = 100):
    employees = db.query(Employee).join(Employee.task).filter(Task.is_active == True)
    employees = employees.group_by(Employee.id).order_by(func.count(Task.id).desc())
    employees = employees.offset(skip).limit(limit).all()

    return employees


def get_employees_without_tasks(db: Session):
    return db.query(Employee).filter(Employee.task == None).all()


def get_min_tasks_count(db: Session):
    emp_min_tasks = db.query(Employee).join(Employee.task).group_by(Employee.id).order_by(func.count(Task.id)).first()

    return len(emp_min_tasks.task)


def get_employees_with_min_workload(db: Session):

    min_tasks_count = get_min_tasks_count(db)

    employees = db.query(Employee).join(Employee.task).group_by(Employee.id).all()

    employees_with_min_workload = [employee for employee in employees if len(employee.task) == min_tasks_count]

    return employees_with_min_workload


def create_employee(db: Session, employee: EmployeeCreateSchema):
    db_employee = Employee(
        full_name=employee.full_name,
        position=employee.position
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee


def partial_update_employee(db: Session, employee_id: int, employee: EmployeeUpdateSchema):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if db_employee:
        if employee.full_name:
            db_employee.full_name = employee.full_name
        if employee.position:
            db_employee.position = employee.position
        db.commit()
        db.refresh(db_employee)
        return db_employee

    return None


def delete_employee(db: Session, employee_id: int):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True

    return False
