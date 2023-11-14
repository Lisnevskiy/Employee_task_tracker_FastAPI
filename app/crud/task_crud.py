from typing import Type, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.employee_crud import get_employee, get_min_loaded_employees
from app.models.employee import Employee
from app.models.task import Task
from app.schemas.task_schemas import TaskCreateSchema, TaskUpdateSchema


def get_task(db: Session, task_id: int) -> Type[Task]:
    """
    Получение информации о задаче по её идентификатору.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        task_id (int): Идентификатор задачи.
    Returns:
        Task: Информация о задаче.
    """
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Type[Task]]:
    """
    Получение списка задач с пропуском и лимитом.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        skip (int, optional): Количество пропускаемых элементов. По умолчанию 0.
        limit (int, optional): Количество извлекаемых элементов. По умолчанию 100.
    Returns:
        List[Task]: Список задач.
    """
    return db.query(Task).offset(skip).limit(limit).all()


def get_min_task_count(db: Session) -> int:
    """
    Получение минимального количества задач у сотрудников.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        int: Минимальное количество задач.
    """
    min_tasks_count = (
        db.query(Employee.id, func.count(Task.id).label('task_count'))
        .outerjoin(Employee.task)
        .group_by(Employee.id)
    ).order_by(func.count(Task.id)).first().task_count

    return min_tasks_count


def get_unassigned_parent_tasks(db: Session) -> List[Type[Task]]:
    """
    Получение списка задач, не взятых в работу, и от которых зависят другие задачи.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        List[Task]: Список родительских задач без исполнителя.
    """
    unassigned_parent_tasks = (
        db.query(Task)
        .filter(Task.id.in_(db.query(Task.parent_task_id)))
        .filter(Task.executor_id.is_(None))
        .all()
    )

    return unassigned_parent_tasks


def get_important_tasks(db: Session):
    """
    Получает список важных задач.

    Важные задачи определяются следующим образом:
    1. Выбираются невыполненные родительские задачи, у которых не указан исполнитель.
    2. Находится минимальное количество задач, выполненных сотрудниками.
    3. Выбираются сотрудники, у которых количество задач равно минимальному количеству.

    Если родительская задача имеет исполнителя, то проверяется его нагрузка:
    - Если у исполнителя родительской задачи задач меньше или равно (минимальное количество задач + 2),
      то его добавляем в список исполнителей важной задачи.

    Args:
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        List[dict]: Список словарей с информацией о важных задачах.
            Каждый словарь содержит:
            - 'title': Название задачи.
            - 'deadline': Срок выполнения задачи.
            - 'employees': Список ФИО сотрудников, способных взять важную задачу.
    """
    # Получаем родительских задач без исполнителя
    tasks = get_unassigned_parent_tasks(db)

    # Получаем минимальное количество задач у сотрудников
    min_tasks_count = get_min_task_count(db)

    # Получаем сотрудников с минимальным количеством задач
    min_loaded_employees = get_min_loaded_employees(db, min_tasks_count)

    # Извлекаем ФИО сотрудников из результата запроса
    min_loaded_employees = [employee.full_name for employee in min_loaded_employees]

    important_tasks = []

    # Обрабатываем каждую задачу
    for task in tasks:
        title = task.title
        deadline = task.deadline
        employees = min_loaded_employees

        # Если задача имеет родительскую задачу
        if task.parent_task_id is not None:
            parent_task = get_task(db, task.parent_task_id)

            # Если у родительской задачи есть исполнитель
            if parent_task.executor_id:
                emp = get_employee(db, parent_task.executor_id)

                # Если нагрузка исполнителя удовлетворяет условиям
                if len(emp.task) - min_tasks_count <= 2:
                    employees = [emp.full_name]

        # Добавляем информацию о важной задаче в список
        important_tasks.append({
            'title': title,
            'deadline': deadline,
            'employees': employees
        })

    return important_tasks


def create_task(db: Session, task: TaskCreateSchema) -> Task:
    """
    Создание новой задачи.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        task (TaskCreateSchema): Данные для создания новой задачи.
    Returns:
        Task: Созданная задача.
    """
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


def partial_update_task(db: Session, task_id: int, task: TaskUpdateSchema) -> Type[Task]:
    """
    Частичное обновление задачи.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        task_id (int): Идентификатор задачи.
        task (TaskUpdateSchema): Данные для частичного обновления задачи.
    Returns:
        Task: Обновленная задача.
    """
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


def delete_task(db: Session, task_id: int) -> Type[Task]:
    """
    Удаление задачи.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        task_id (int): Идентификатор задачи.
    Returns:
        Task: Удаленная задача.
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if db_task:
        db.delete(db_task)
        db.commit()

    return db_task
