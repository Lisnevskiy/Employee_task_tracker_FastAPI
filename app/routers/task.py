from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.task_crud import (
    create_task,
    get_tasks,
    get_task,
    partial_update_task,
    delete_task,
    get_important_tasks,
)
from app.database import get_db
from app.schemas.task_schemas import TaskSchema, TaskCreateSchema, TaskUpdateSchema, ImportantTasksShowSchema

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_new_task(task: TaskCreateSchema, db: Session = Depends(get_db)):
    """
    Создание новой задачи.
    Args:
        task (TaskCreateSchema): Данные для создания новой задачи.
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        TaskSchema: Информация о созданной задаче.
    """
    return create_task(db=db, task=task)


@router.get("/", response_model=list[TaskSchema])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка задач с пропуском и лимитом.
    Args:
        skip (int, optional): Количество пропускаемых элементов. По умолчанию 0.
        limit (int, optional): Количество извлекаемых элементов. По умолчанию 100.
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        List[TaskSchema]: Список задач.
    """
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks


@router.get("/important/", response_model=list[ImportantTasksShowSchema])
def read_important_tasks(db: Session = Depends(get_db)):
    """
    Получение списка важных задач.
    Важные задачи определяются согласно логике в функции get_important_tasks.
    Args:
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        List[ImportantTasksShowSchema]: Список важных задач.
    """
    tasks = get_important_tasks(db)
    return tasks


@router.get("/{task_id}", response_model=TaskSchema)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о задаче по её идентификатору.
    Args:
        task_id (int): Идентификатор задачи.
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        TaskSchema: Информация о задаче.
    """
    db_task = get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.put("/{task_id}", response_model=TaskSchema)
def put_task(task_id: int, task: TaskUpdateSchema, db: Session = Depends(get_db)):
    """
    Обновление информации о задаче по её идентификатору.
    Args:
        task_id (int): Идентификатор задачи.
        task (TaskUpdateSchema): Данные для обновления задачи.
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        TaskSchema: Обновленная информация о задаче.
    """
    db_task = partial_update_task(db=db, task_id=task_id, task=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.delete("/{task_id}", response_model=TaskSchema)
def del_task(task_id: int, db: Session = Depends(get_db)):
    """
    Удаление задачу по её идентификатору.
    Args:
        task_id (int): Идентификатор задачи.
        db (Session): Сессия базы данных SQLAlchemy.
    Returns:
        JSONResponse: Сообщение об успешном удалении задачи.
    """
    response = delete_task(db, task_id=task_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content={"message": "Task deleted"}, status_code=200)
