from typing import List, Type

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.task import Task
from app.schemas.employee_schemas import EmployeeCreateSchema, EmployeeUpdateSchema


def get_employee(db: Session, employee_id: int) -> Type[Employee]:
    """
    Получение информации о сотруднике по его идентификатору.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        employee_id (int): Идентификатор сотрудника.
    Returns:
        Employee: Объект с информацией о сотруднике.
    """
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Type[Employee]]:
    """
    Получение списка сотрудников с возможностью пагинации.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        skip (int): Количество записей, которые следует пропустить (по умолчанию 0).
        limit (int): Максимальное количество записей для возврата (по умолчанию 100).
    Returns:
        List[Employee]: Список сотрудников.
    """
    return db.query(Employee).offset(skip).limit(limit).all()


def get_employees_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Type[Employee]]:
    """
    Получение списка сотрудников с числом активных задач, отсортированных по убыванию количества задач.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        skip (int): Количество записей, которые следует пропустить (по умолчанию 0).
        limit (int): Максимальное количество записей для возврата (по умолчанию 100).
    Returns:
        List[Employee]: Список сотрудников с числом активных задач.
    """
    employees = db.query(Employee).join(Employee.task).filter(Task.is_active.is_(True))
    employees = employees.group_by(Employee.id).order_by(func.count(Task.id).desc())
    employees = employees.offset(skip).limit(limit).all()

    return employees


def get_min_loaded_employees(db: Session, min_tasks_count: int) -> List[Type[Employee]]:
    """
    Получает список сотрудников с минимальной нагрузкой задач.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        min_tasks_count (int): Минимальное количество задач.
    Returns:
        List[Employee]: Список сотрудников с минимальной нагрузкой.
    """
    min_loaded_employees = (
        db.query(Employee)
        .outerjoin(Employee.task)
        .group_by(Employee.id)
        .having(func.count(Task.id) == min_tasks_count)
        .all()
    )

    return min_loaded_employees


def create_employee(db: Session, employee: EmployeeCreateSchema) -> Employee:
    """
    Создание нового сотрудника.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        employee (EmployeeCreateSchema): Данные для создания нового сотрудника.
    Returns:
        Employee: Созданный сотрудник.
    """
    db_employee = Employee(
        full_name=employee.full_name,
        position=employee.position
    )

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee


def partial_update_employee(db: Session, employee_id: int, employee: EmployeeUpdateSchema) -> Type[Employee]:
    """
    Частичное обновление данных о сотруднике.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        employee_id (int): Идентификатор сотрудника, данные которого обновляются.
        employee (EmployeeUpdateSchema): Данные для частичного обновления сотрудника.
    Returns:
        Employee: Обновленный сотрудник или None, если сотрудник не найден.
    """
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if db_employee:

        if employee.full_name:
            db_employee.full_name = employee.full_name

        if employee.position:
            db_employee.position = employee.position

        db.commit()
        db.refresh(db_employee)

    return db_employee


def delete_employee(db: Session, employee_id: int) -> Type[Employee]:
    """
    Удаление сотрудника.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        employee_id (int): Идентификатор сотрудника, которого следует удалить.
    Returns:
        Employee: Удаленный сотрудник или None, если сотрудник не найден.
    """
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if db_employee:
        db.delete(db_employee)
        db.commit()

    return db_employee
