from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.orm import relationship

from app.database import Base

metadata_employee = MetaData()


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False, index=True)
    position = Column(String)

    task = relationship("Task", back_populates="executor")

    metadata = metadata_employee
