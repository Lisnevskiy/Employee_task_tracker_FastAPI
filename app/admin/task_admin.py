from sqladmin import ModelView

from app.models.task import Task


class TaskAdmin(ModelView, model=Task):
    column_list = [Task.id, Task.title, Task.parent_task_id, Task.executor_id, Task.deadline, Task.is_active]
