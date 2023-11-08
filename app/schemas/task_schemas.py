from datetime import datetime

from pydantic import BaseModel

# from app.schemas.employee_schemas import EmployeeBaseSchema


class TaskBaseSchema(BaseModel):
    title: str
    parent_task_id: int | None = None
    executor_id: int | None = None
    deadline: datetime | None = None
    is_active: bool | None = False


class TaskCreateSchema(TaskBaseSchema):
    pass


class TaskSchema(TaskBaseSchema):
    id: int

    class Config:
        from_attributes = True


class TaskUpdateSchema(TaskBaseSchema):
    title: str | None = None


class ImportantTasksShowSchema(BaseModel):
    title: str
    deadline: datetime
    employees: list = []
