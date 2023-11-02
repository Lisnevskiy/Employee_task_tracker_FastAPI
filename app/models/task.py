from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, MetaData
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.employee import Employee

metadata_task = MetaData()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"))
    executor_id = Column(Integer, ForeignKey(Employee.id))
    deadline = Column(DateTime)
    status = Column(Boolean, default=False)

    executor = relationship("Employee", back_populates="tasks")

    metadata = metadata_task
