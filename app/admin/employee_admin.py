from sqladmin import ModelView

from app.models.employee import Employee


class EmployeeAdmin(ModelView, model=Employee):
    column_list = [Employee.id, Employee.full_name]
