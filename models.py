import enum

from sqlalchemy import Boolean, Column, Enum, Integer, String, Table
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TaskStatus(enum.Enum):
    todo = "todo"
    in_progress = "in progress"
    done = "done"


class TaskPriority(enum.Enum):
    highest = "highest"
    high = "high"
    medium = "medium"
    low = "low"
    lowest = "lowest"


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    reporter = Column(String)
    assignee = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium)


class RoleEnum(str, enum.Enum):
    admin = "admin"
    read_only = "read_only"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.read_only)
