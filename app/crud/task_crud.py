from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.employee_crud import get_employees_with_min_workload, get_employees_without_tasks, get_employee, \
    get_min_tasks_count
from app.models.employee import Employee
from app.models.task import Task
from app.schemas.task_schemas import TaskCreateSchema, TaskUpdateSchema


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).offset(skip).limit(limit).all()


def get_important_tasks(db: Session, skip: int = 0, limit: int = 100):
    tasks_without_executor = db.query(Task).filter(Task.executor_id == None).all()

    tasks = []

    for task in tasks_without_executor:
        # Проверяем, есть ли зависимые задачи
        dependent_tasks = db.query(Task).filter(Task.parent_task_id == task.id).all()

        if dependent_tasks:
            # Если есть зависимые задачи, то это родительская задача
            tasks.append(task)

    employees_with_min_workload = get_employees_without_tasks(db)

    if len(employees_with_min_workload) == 0:
        employees_with_min_workload = get_employees_with_min_workload(db)

    important_tasks = []

    for important_task in tasks:
        if important_task.parent_task_id is None:
            important_tasks.append({
                'title': important_task.title,
                'deadline': important_task.deadline,
                'employees': [employee.full_name for employee in employees_with_min_workload]
            })

        else:
            task = db.query(Task).filter(Task.id == important_task.parent_task_id).first()
            if task.executor_id:
                emp = get_employee(db, task.executor_id)
                if len(emp.task) - get_min_tasks_count(db) <= 2:
                    employees_with_min_workload = [emp]

                important_tasks.append({
                    'title': important_task.title,
                    'deadline': important_task.deadline,
                    'employees': [employee.full_name for employee in employees_with_min_workload]
                })

    print(important_tasks)
    # print(get_employees_without_tasks(db))

    # print(get_employees_with_min_workload(db))

    return important_tasks


def create_task(db: Session, task: TaskCreateSchema):
    db_task = Task(
        title=task.title,
        parent_task_id=task.parent_task_id,
        executor_id=task.executor_id,
        deadline=task.deadline,
        is_active=task.is_active,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def partial_update_task(db: Session, task_id: int, task: TaskUpdateSchema):
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if db_task:
        if task.title:
            db_task.title = task.title
        if task.parent_task_id:
            db_task.parent_task_id = task.parent_task_id
        if task.executor_id:
            db_task.executor_id = task.executor_id
        if task.deadline:
            db_task.deadline = task.deadline
        if task.is_active:
            db_task.is_active = task.is_active
        db.commit()
        db.refresh(db_task)
        return db_task

    return None


def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if db_task:
        db.delete(db_task)
        db.commit()
        return db_task
    return False
