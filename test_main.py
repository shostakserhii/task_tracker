from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import models, schemas, main, database

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

main.app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(main.app)


@pytest.fixture(scope="module")
def setup_database():
    # Create the database and tables
    models.Base.metadata.create_all(bind=engine)
    yield
    # Drop the database and tables
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture
def admin_token(setup_database):
    """
    Fixture to create an admin user and return a JWT token.
    """
    client.post(
        "/users/",
        json={"email": "admin@example.com", "password": "password", "role": "admin"}
    )
    response = client.post(
        "/token",
        data={"username": "admin@example.com", "password": "password"}
    )
    return response.json()["access_token"]


@pytest.fixture
def read_only_token(setup_database):
    """
    Fixture to create a read-only user and return a JWT token.
    """
    client.post(
        "/users/",
        json={"email": "readonly@example.com", "password": "password", "role": "read_only"}
    )
    response = client.post(
        "/token",
        data={"username": "readonly@example.com", "password": "password"}
    )
    return response.json()["access_token"]


def test_create_user(setup_database):
    """
    Test creating a new user.
    """
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "password", "role": "admin"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_login_user(setup_database):
    """
    Test logging in a user and obtaining a JWT token.
    """
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_create_task(admin_token):
    """
    Test creating a new task.
    """
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "reporter": "admin@example.com",
            "assignee": "admin@example.com",
            "status": "todo",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_read_tasks(admin_token):
    """
    Test reading tasks.
    """
    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0


@patch("crud.send_status_change_email")
def test_update_task(mock_send_email, admin_token):
    """
    Test updating a task.
    """
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "reporter": "admin@example.com",
            "assignee": "admin@example.com",
            "status": "todo",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    task_id = response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

    response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Updated Test Task",
            "description": "This is an updated test task",
            "reporter": "admin@example.com",
            "assignee": "admin@example.com",
            "status": "done",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    updated_task = response.json()
    assert updated_task["title"] == "Updated Test Task"
    assert updated_task["description"] == "This is an updated test task"
    assert updated_task["reporter"] == "admin@example.com"
    assert updated_task["assignee"] == "admin@example.com"
    assert updated_task["status"] == "done"
    assert updated_task["priority"] == "medium"
    mock_send_email.assert_called_once()

def test_delete_task(admin_token):
    """
    Test deleting a task.
    """
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "reporter": "admin@example.com",
            "assignee": "admin@example.com",
            "status": "todo",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    task_id = response.json()["id"]
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_read_only_user_cannot_create_task(read_only_token):
    """
    Test that a read-only user cannot create a task.
    """
    response = client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "reporter": "readonly@example.com",
            "assignee": "readonly@example.com",
            "status": "todo",
            "priority": "medium"
        },
        headers={"Authorization": f"Bearer {read_only_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
