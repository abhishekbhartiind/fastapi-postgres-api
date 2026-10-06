from typing import Annotated, Optional
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import CurrentUser, get_task_service
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
    TaskWithUserResponse,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task for the current user"
)
async def create_task(
    task_in: TaskCreate,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service)]
) -> TaskResponse:
    """Create a task owned by the authenticated user."""
    return await task_service.create_task(user=current_user, task_in=task_in)


@router.get(
    "/",
    response_model=list[TaskResponse],
    summary="List all tasks owned by current user"
)
async def get_my_tasks(
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    status: Optional[TaskStatus] = Query(None, description="Filter by status (uses composite index)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> list[TaskResponse]:
    """Retrieve tasks with optional status filter and pagination."""
    return await task_service.get_tasks_for_user(
        user=current_user,
        status=status,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a specific task by ID"
)
async def get_task(
    task_id: Annotated[int, Path(ge=1)],
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service)]
) -> TaskResponse:
    """Retrieve a single task owned by the authenticated user."""
    return await task_service.get_task_by_id(user=current_user, task_id=task_id)


@router.get(
    "/{task_id}/with-owner",
    response_model=TaskWithUserResponse,
    summary="Get task details with joined owner profile (SQL JOIN demonstration)"
)
async def get_task_with_owner_details(
    task_id: Annotated[int, Path(ge=1)],
    _: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service)]
) -> TaskWithUserResponse:
    """Retrieve task alongside owner profile loaded via SQL JOIN (eager loading)."""
    return await task_service.get_task_with_owner(task_id=task_id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task"
)
async def update_task(
    task_id: Annotated[int, Path(ge=1)],
    task_in: TaskUpdate,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service)]
) -> TaskResponse:
    """Update fields of an existing task owned by the user."""
    return await task_service.update_task(
        user=current_user,
        task_id=task_id,
        task_in=task_in
    )


@router.delete(
    "/{task_id}",
    summary="Delete a task"
)
async def delete_task(
    task_id: Annotated[int, Path(ge=1)],
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends(get_task_service)]
):
    """Delete a task owned by the authenticated user."""
    await task_service.delete_task(user=current_user, task_id=task_id)
    return {
        "success": True,
        "message": f"Task {task_id} successfully deleted."
    }
