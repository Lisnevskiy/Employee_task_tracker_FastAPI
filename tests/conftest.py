import os
from contextlib import closing
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, drop_database

from app.database import Base, get_db
from app.main import app
from app.models.employee import Employee
from app.models.task import Task
from tests.fixtures import new_employee_data, new_task_data

# URL тестовой базы данных из переменной окружения.
SQLALCHEMY_DATABASE_URL = os.getenv("TEST_POSTGRESQL_DATABASE_URL")

# Создание тестовой БД.
create_database(SQLALCHEMY_DATABASE_URL)

# Создание SQLAlchemy engine с использованием StaticPool для тестовой БД.
engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=StaticPool)

# Создание TestingSessionLocal, который будет использоваться в тестах.
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблицы для модели Employee.
Base.metadata.create_all(bind=engine, tables=[Employee.__table__])

# Создание таблицы для модели Task.
Base.metadata.create_all(bind=engine, tables=[Task.__table__])


def bulk_insert_data(session, model, data):
    """Массовая вставка данных в таблицу через bulk_insert_mappings.
    Args:
        session (sqlalchemy.orm.Session): Сессия SQLAlchemy для взаимодействия с базой данных.
        model (sqlalchemy.ext.declarative.DeclarativeMeta): Модель SQLAlchemy.
        data (list[dict]): Список словарей, представляющих данные для вставки.
    Returns:
        None
    """
    # Используется bulk_insert_mappings для эффективной массовой вставки данных.
    session.bulk_insert_mappings(model, data)
    # Сохранение изменений в БД.
    session.commit()


def override_get_db():
    """Переопределенная зависимость get_db для тестовых целей.
    Returns:
        sqlalchemy.orm.Session: Сессия SQLAlchemy для взаимодействия с базой данных.
    """
    with closing(TestingSessionLocal()) as db:
        yield db


# Переопределение зависимости get_db в приложении для использования TestingSessionLocal.
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def cleanup_database():
    """Фикстура для очистки базы данных после завершения всех тестов.
    Yields:
        None
    """
    # Создание сессии для взаимодействия с БД.
    with closing(TestingSessionLocal()) as db:
        # Массовая вставка данных в таблицу Employee.
        bulk_insert_data(db, Employee, new_employee_data)
        # Массовая вставка данных в таблицу Task.
        bulk_insert_data(db, Task, new_task_data)

    yield

    # Удаление БД.
    drop_database(SQLALCHEMY_DATABASE_URL)


# Создание тестового клиента для взаимодействия с FastAPI-приложением.
client = TestClient(app)
