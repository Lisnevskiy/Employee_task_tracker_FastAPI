from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud.employee_crud import (
    get_employees,
    create_employee,
    get_employee,
    delete_employee,
    partial_update_employee,
    get_employees_tasks,
)
from app.database import get_db
from app.schemas.employee_schemas import (
    EmployeeSchema,
    EmployeeCreateSchema,
    EmployeeUpdateSchema,
    EmployeeTasksSchema,
)

router = APIRouter(
    prefix="/employees",
    tags=["employees"]
)


@router.post("/", response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
def create_new_employee(employee: EmployeeCreateSchema, db: Session = Depends(get_db)):
    """
    Создание нового сотрудника.
    Args:
        employee (EmployeeCreateSchema): Данные для создания нового сотрудника.
        db (Session, optional): Сессия базы данных. По умолчанию используется Depends(get_db).
    Returns:
        EmployeeSchema: Созданный сотрудник.
    """
    return create_employee(db=db, employee=employee)


@router.get("/", response_model=list[EmployeeSchema])
def read_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка сотрудников.
    Args:
        skip (int, optional): Количество пропускаемых элементов. По умолчанию 0.
        limit (int, optional): Количество извлекаемых элементов. По умолчанию 100.
        db (Session, optional): Сессия базы данных. По умолчанию используется Depends(get_db).
    Returns:
        List[EmployeeSchema]: Список сотрудников.
    """
    return get_employees(db, skip=skip, limit=limit)


@router.get("/tasks/", response_model=list[EmployeeTasksSchema])
def read_employees_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка сотрудников и их задач, отсортированного по количеству активных задач.
    Args:
        skip (int, optional): Количество пропускаемых элементов. По умолчанию 0.
        limit (int, optional): Количество извлекаемых элементов. По умолчанию 100.
        db (Session, optional): Сессия базы данных. По умолчанию используется Depends(get_db).
    Returns:
        List[EmployeeTasksSchema]: Список сотрудников с задачами.
    """
    return get_employees_tasks(db, skip=skip, limit=limit)


@router.get("/{employee_id}", response_model=EmployeeSchema)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о сотруднике по его идентификатору.
    Args:
        employee_id (int): Идентификатор сотрудника.
        db (Session, optional): Сессия базы данных. По умолчанию используется Depends(get_db).
    Returns:
        EmployeeSchema: Информация о сотруднике.
    """
    db_employee = get_employee(db, employee_id=employee_id)

    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return db_employee


@router.put("/{employee_id}", response_model=EmployeeSchema)
def put_employee(employee_id: int, employee: EmployeeUpdateSchema, db: Session = Depends(get_db)):
    """
    Обновление информации о сотруднике.
    Args:
        employee_id (int): Идентификатор сотрудника.
        employee (EmployeeUpdateSchema): Данные для обновления сотрудника.
        db (Session, optional): Сессия базы данных. По умолчанию используется Depends(get_db).
    Returns:
        EmployeeSchema: Обновленная информация о сотруднике.
    """
    db_employee = partial_update_employee(db=db, employee_id=employee_id, employee=employee)

    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return db_employee


@router.delete("/{employee_id}", response_model=EmployeeSchema)
def del_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    Удаление сотрудника.
    Args:
        employee_id (int): Идентификатор сотрудника.
        db (Session, optional): Сессия базы данных. По умолчанию используется Depends(get_db).
    Returns:
        JSONResponse: Сообщение об успешном удалении сотрудника.
    """
    response = delete_employee(db, employee_id=employee_id)

    if response is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return JSONResponse(content={"message": "Employee deleted"}, status_code=200)
