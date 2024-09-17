from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from sqlalchemy.orm import Session

import crud
import database
import models
import schemas

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token.

    Parameters:
    - data: dict - The data to include in the token.
    - expires_delta: timedelta - The token expiration time.

    Returns:
    - The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)
):
    """
    Get the current authenticated user.

    Parameters:
    - db: Session - The database session.
    - token: str - The JWT token.

    Returns:
    - The current authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
):
    """
    Get the current active user.

    Parameters:
    - current_user: schemas.User - The current authenticated user.

    Returns:
    - The current active user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Get the current admin user.

    Parameters:
    - current_user: schemas.User - The current authenticated user.

    Returns:
    - The current admin user.
    """
    if current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


async def get_current_read_only_user(
    current_user: schemas.User = Depends(get_current_active_user),
):
    """
    Get the current read-only user.

    Parameters:
    - current_user: schemas.User - The current authenticated user.

    Returns:
    - The current read-only user.
    """
    if current_user.role not in models.RoleEnum:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
