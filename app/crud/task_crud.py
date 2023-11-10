from typing import Type, List

from sqlalchemy.orm import Session

from app.crud.employee_crud import (
    get_employees_with_min_workload,
    get_employees_without_tasks,
    get_employee,
    get_min_tasks_count,
)
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


def get_tasks_without_executor(db: Session) -> List[Type[Task]]:
    """
    Получение списка задач без исполнителя.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        List[Task]: Список задач без исполнителя.
    """
    return db.query(Task).filter(Task.executor_id == None).all()


def get_parent_tasks(db: Session, tasks) -> List[Type[Task]]:
    """
    Получение списка родительских задач для заданных задач.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
        tasks: Список задач.
    Returns:
        List[Task]: Список родительских задач.
    """
    parent_tasks = []

    for task in tasks:
        dependent_tasks = db.query(Task).filter(Task.parent_task_id == task.id).all()

        if dependent_tasks:
            parent_tasks.append(task)

    return parent_tasks


def get_important_tasks(db: Session):
    """
    Возвращает важные задачи с информацией о сотрудниках с минимальной загрузкой.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        Список важных задач с информацией о сотрудниках.
    """
    # Получаем задачи без исполнителя
    tasks_without_executor = get_tasks_without_executor(db)

    # Получаем родительские задачи
    tasks = get_parent_tasks(db, tasks_without_executor)

    # Получаем сотрудников без задач
    employees_with_min_workload = get_employees_without_tasks(db)

    # Если нет сотрудников без задач, получаем сотрудников с минимальной загрузкой
    if len(employees_with_min_workload) == 0:
        employees_with_min_workload = get_employees_with_min_workload(db)

    # Создаем пустой список для хранения важных задач
    important_tasks = []

    # Итерируем по списку задач
    for important_task in tasks:
        # Проверяем, является ли задача родительской (не имеет parent_task_id)
        if important_task.parent_task_id is None:
            # Создаем словарь с информацией о задаче и сотрудниках с минимальной загрузкой
            important_tasks.append({
                'title': important_task.title,
                'deadline': important_task.deadline,
                'employees': [employee.full_name for employee in employees_with_min_workload]
            })
        else:
            # Если задача имеет parent_task_id, находим ее родительскую задачу
            task = db.query(Task).filter(Task.id == important_task.parent_task_id).first()
            # Проверяем, есть ли у родительской задачи исполнитель
            if task.executor_id:
                # Если есть исполнитель, получаем информацию о сотруднике
                emp = get_employee(db, task.executor_id)
                # Проверяем, находится ли сотрудник на грани минимальной загрузки
                if len(emp.task) - get_min_tasks_count(db) <= 2:
                    # Если сотрудник на грани, обновляем список сотрудников с минимальной загрузкой
                    employees_with_min_workload = [emp]

                # Добавляем информацию о задаче и сотрудниках в список важных задач
                important_tasks.append({
                    'title': important_task.title,
                    'deadline': important_task.deadline,
                    'employees': [employee.full_name for employee in employees_with_min_workload]
                })

    # Возвращаем список важных задач
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
