import enum

from pydantic import BaseModel, EmailStr


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in progress"
    done = "done"


class TaskPriority(str, enum.Enum):
    highest = "highest"
    high = "high"
    medium = "medium"
    low = "low"
    lowest = "lowest"


class TaskBase(BaseModel):
    title: str
    description: str
    reporter: str
    assignee: str
    status: TaskStatus
    priority: TaskPriority


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True


class RoleEnum(str, enum.Enum):
    admin = "admin"
    read_only = "read_only"


class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
