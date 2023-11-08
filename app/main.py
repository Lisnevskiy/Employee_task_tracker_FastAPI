from fastapi import FastAPI
from sqladmin import Admin

from app.admin.employee_admin import EmployeeAdmin
from app.admin.task_admin import TaskAdmin
from app.database import engine
from app.routers import employee, task

app = FastAPI()

admin = Admin(app, engine)

app.include_router(employee.router)
app.include_router(task.router)

admin.add_view(EmployeeAdmin)
admin.add_view(TaskAdmin)
