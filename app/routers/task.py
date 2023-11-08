from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.task_crud import create_task, get_tasks, get_task, partial_update_task, delete_task, get_important_tasks
from app.database import get_db
from app.schemas.task_schemas import TaskSchema, TaskCreateSchema, TaskUpdateSchema, ImportantTasksShowSchema

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_new_task(task: TaskCreateSchema, db: Session = Depends(get_db)):

    return create_task(db=db, task=task)


@router.get("/", response_model=list[TaskSchema])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    tasks = get_tasks(db, skip=skip, limit=limit)

    return tasks


@router.get("/important/", response_model=list[ImportantTasksShowSchema])
def read_important_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    tasks = get_important_tasks(db, skip=skip, limit=limit)

    return tasks


@router.get("/{task_id}", response_model=TaskSchema)
def read_task(task_id: int, db: Session = Depends(get_db)):

    db_task = get_task(db, task_id=task_id)

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task


@router.put("/{task_id}", response_model=TaskSchema)
def put_task(task_id: int, task: TaskUpdateSchema, db: Session = Depends(get_db)):

    db_task = partial_update_task(db=db, task_id=task_id, task=task)

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return db_task


@router.delete("/{task_id}", response_model=TaskSchema)
def del_task(task_id: int, db: Session = Depends(get_db)):

    response = delete_task(db, task_id=task_id)

    if response is False:
        raise HTTPException(status_code=404, detail="Task not found")

    return JSONResponse(content={"message": "Task deleted"}, status_code=200)
