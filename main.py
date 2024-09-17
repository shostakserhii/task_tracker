from datetime import timedelta
from logging import Logger
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import auth
import crud
import database
import models
import schemas

logger = Logger(name=__name__)
app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)


@app.on_event("startup")
async def startup():
    await database.database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.database.disconnect()


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    db: Session = Depends(database.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Generate a JWT token for user authentication.

    Parameters:
    - db: Session - The database session.
    - form_data: OAuth2PasswordRequestForm - The form data containing username and password.

    Returns:
    - A JWT token.
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    Create a new user.

    Parameters:
    - user: schemas.UserCreate - The user data to create.
    - db: Session - The database session.

    Returns:
    - The created user.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post(
    "/tasks/",
    response_model=schemas.Task,
    dependencies=[Depends(auth.get_current_admin_user)],
)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    """
    Create a new task.

    Parameters:
    - task: schemas.TaskCreate - The task data to create.
    - db: Session - The database session.

    Returns:
    - The created task.
    """
    return crud.create_task(db=db, task=task)


@app.get(
    "/tasks/",
    response_model=List[schemas.Task],
    dependencies=[Depends(auth.get_current_active_user)],
)
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    """
    Get a list of tasks.

    Parameters:
    - skip: int - The number of tasks to skip (default is 0).
    - limit: int - The maximum number of tasks to return (default is 10).
    - db: Session - The database session.

    Returns:
    - A list of tasks.
    """
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


@app.get(
    "/tasks/{task_id}",
    response_model=schemas.Task,
    dependencies=[Depends(auth.get_current_active_user)],
)
def read_task(task_id: int, db: Session = Depends(database.get_db)):
    """
    Get a task by its ID.

    Parameters:
    - task_id: int - The ID of the task to retrieve.
    - db: Session - The database session.

    Returns:
    - The task with the specified ID, or None if not found.
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.put(
    "/tasks/{task_id}",
    response_model=schemas.Task,
    dependencies=[Depends(auth.get_current_admin_user)],
)
def update_task(
    task_id: int, task: schemas.TaskUpdate, db: Session = Depends(database.get_db)
):
    """
    Update an existing task.

    Parameters:
    - task_id: int - The ID of the task to update.
    - task: schemas.TaskUpdate - The updated task data.
    - db: Session - The database session.

    Returns:
    - The updated task, or None if not found.
    """
    db_task = crud.update_task(db, task_id=task_id, task=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.delete(
    "/tasks/{task_id}",
    response_model=schemas.Task,
    dependencies=[Depends(auth.get_current_admin_user)],
)
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    """
    Delete a task by its ID.

    Parameters:
    - task_id: int - The ID of the task to delete.
    - db: Session - The database session.

    Returns:
    - The deleted task, or None if not found.
    """
    db_task = crud.delete_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)