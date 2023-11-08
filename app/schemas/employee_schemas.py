from pydantic import BaseModel

from app.schemas.task_schemas import TaskSchema


# Базовая модель для сотрудника без идентификатора.
class EmployeeBaseSchema(BaseModel):
    full_name: str  # Полное имя сотрудника
    position: str    # Должность сотрудника


# Модель для создания сотрудника (наследует поля из базовой модели).
class EmployeeCreateSchema(EmployeeBaseSchema):
    pass


# Модель сотрудника для вывода (включает идентификатор сотрудника).
class EmployeeSchema(EmployeeBaseSchema):
    id: int

    class Config:
        orm_mode = True


class EmployeeUpdateSchema(EmployeeBaseSchema):
    full_name: str | None = None
    position: str | None = None


class EmployeeTasksSchema(EmployeeBaseSchema):
    id: int
    task: list[TaskSchema] = []
