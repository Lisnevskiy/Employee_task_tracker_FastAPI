from pydantic import BaseModel
from app.schemas.task_schemas import TaskSchema


class EmployeeBaseSchema(BaseModel):
    """
    Базовая схема для данных о сотруднике.
    Attributes:
        full_name (str): Полное имя сотрудника.
        position (str): Должность сотрудника.
    """
    full_name: str
    position: str


class EmployeeCreateSchema(EmployeeBaseSchema):
    """Схема данных для создания нового сотрудника, на основе базовой схемы."""
    pass


class EmployeeSchema(EmployeeBaseSchema):
    """
    Схема данных для отображения информации о сотруднике.
    Attributes:
        id (int): Идентификатор сотрудника.
    Config:
        from_attributes (bool): Флаг для использования атрибутов класса при создании схемы.
    """
    id: int

    class Config:
        from_attributes = True


class EmployeeUpdateSchema(EmployeeBaseSchema):
    """
    Схема данных для частичного обновления информации о сотруднике.
    Attributes:
        full_name (str | None): Новое полное имя сотрудника или None, если не обновляется.
        position (str | None): Новая должность сотрудника или None, если не обновляется.
    """
    full_name: str | None = None
    position: str | None = None


class EmployeeTasksSchema(EmployeeBaseSchema):
    """
    Схема данных для отображения информации о сотруднике вместе с его задачами.
    Attributes:
        id (int): Идентификатор сотрудника.
        task (list[TaskSchema]): Список задач, связанных с сотрудником.
    """
    id: int
    task: list[TaskSchema] = []
