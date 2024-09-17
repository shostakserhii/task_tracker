from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_task(db: Session, task_id: int):
    """
    Get a task by its ID.

    Parameters:
    - db: Session - The database session.
    - task_id: int - The ID of the task to retrieve.

    Returns:
    - The task with the specified ID, or None if not found.
    """
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    """
    Get a list of tasks.

    Parameters:
    - db: Session - The database session.
    - skip: int - The number of tasks to skip (default is 0).
    - limit: int - The maximum number of tasks to return (default is 10).

    Returns:
    - A list of tasks.
    """
    return db.query(models.Task).offset(skip).limit(limit).all()


def create_task(db: Session, task: schemas.TaskCreate):
    """
    Create a new task.

    Parameters:
    - db: Session - The database session.
    - task: schemas.TaskCreate - The task data to create.

    Returns:
    - The created task.
    """
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
    """
    Update an existing task.

    Parameters:
    - db: Session - The database session.
    - task_id: int - The ID of the task to update.
    - task: schemas.TaskUpdate - The updated task data.

    Returns:
    - The updated task, or None if not found.
    """
    db_task = get_task(db, task_id)
    old_status = db_task.status
    if db_task:
        for key, value in task.dict().items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
        if old_status != db_task.status:
            send_status_change_email(db_task.reporter, db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    """
    Delete a task by its ID.

    Parameters:
    - db: Session - The database session.
    - task_id: int - The ID of the task to delete.

    Returns:
    - The deleted task, or None if not found.
    """
    db_task = get_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task


def get_user_by_email(db: Session, email: str):
    """
    Get a user by their email.

    Parameters:
    - db: Session - The database session.
    - email: str - The email of the user to retrieve.

    Returns:
    - The user with the specified email, or None if not found.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user.

    Parameters:
    - db: Session - The database session.
    - user: schemas.UserCreate - The user data to create.

    Returns:
    - The created user.
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email, hashed_password=hashed_password, role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user by their email and password.

    Parameters:
    - db: Session - The database session.
    - email: str - The email of the user to authenticate.
    - password: str - The password of the user to authenticate.

    Returns:
    - The authenticated user, or False if authentication failed.
    """
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def send_status_change_email(reporter: str, task: models.Task):
    """
    Mock function to send an email notification when the task status changes.

    Parameters:
    - reporter: str - The email of the reporter.
    - task: models.Task - The task that was updated.
    """
    print(
        f"Sending email to {reporter}: The status of task '{task.title}' has been changed to `{task.status.value}`."
    )
