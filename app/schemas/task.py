from datetime import datetime
from typing import Literal, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse

TaskStatus = Literal["pending", "in_progress", "completed", "cancelled"]
TaskPriority = Literal["low", "medium", "high", "critical"]


class TaskBase(BaseModel):
    """Common Task attributes."""
    title: str = Field(..., min_length=1, max_length=200, examples=["Deploy Database Migration"])
    description: Optional[str] = Field(default=None, max_length=2000, examples=["Run Alembic upgrade head in Docker"])
    status: TaskStatus = Field(default="pending", examples=["pending"])
    priority: TaskPriority = Field(default="medium", examples=["high"])


class TaskCreate(TaskBase):
    """Payload schema for creating a new Task."""
    pass


class TaskUpdate(BaseModel):
    """Optional payload for updating a Task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskResponse(TaskBase):
    """Response schema representing a stored Task."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskWithUserResponse(TaskResponse):
    """Task response including joined owner information (demonstrating SQL joins)."""
    owner: UserResponse

    model_config = ConfigDict(from_attributes=True)
