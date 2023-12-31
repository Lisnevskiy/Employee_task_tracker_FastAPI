from datetime import datetime

import pytz
from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class TaskBaseSchema(BaseModel):
    """
    Базовая схема для данных о задаче.
    Attributes:
        title (str): Название задачи.
        parent_task_id (int | None): Идентификатор родительской задачи или None.
        executor_id (int | None): Идентификатор исполнителя или None.
        deadline (datetime | None): Срок выполнения задачи или None.
        is_active (bool | None): Флаг активности задачи или None.
    """
    title: str
    parent_task_id: int | None = None
    executor_id: int | None = None
    deadline: datetime | None = None
    is_active: bool | None = False

    @field_validator("is_active")
    def validate_is_active(cls, is_active, info: FieldValidationInfo):
        """
        Валидатор для проверки, что задача не может быть активной без назначенного исполнителя.
        """
        if "executor_id" in info.data and is_active and info.data["executor_id"] is None:
            raise ValueError("Task cannot be active without an assigned executor")

        return is_active


class TaskCreateSchema(TaskBaseSchema):
    """
    Схема данных для создания новой задачи, на основе базовой схемы.
    """
    @field_validator("deadline")
    def validate_deadline(cls, deadline):
        """
        Валидатор для проверки, что срок выполнения не может быть в прошлом.
        """
        utc = pytz.UTC

        if deadline and deadline.replace(tzinfo=utc) < datetime.now().replace(tzinfo=utc):
            raise ValueError("Deadline cannot be set in the past")

        return deadline


class TaskSchema(TaskBaseSchema):
    """
    Схема данных для отображения информации о задаче.
    Attributes:
        id (int): Идентификатор задачи.
    Config:
        from_attributes (bool): Флаг для использования атрибутов класса при создании схемы.
    """
    id: int

    class Config:
        from_attributes = True


class TaskUpdateSchema(TaskCreateSchema):
    """
       Схема данных для частичного обновления информации о задаче.
       Attributes:
           title (str | None): Новое название задачи или None, если не обновляется.
       """
    title: str | None = None


class ImportantTasksShowSchema(BaseModel):
    """
    Схема данных для отображения важных задач.
    Attributes:
        title (str): Название задачи.
        deadline (datetime | None): Срок выполнения задачи или None.
        employees (List[str]): Список сотрудников.
    """
    title: str
    deadline: datetime | None = None
    employees: list = []
