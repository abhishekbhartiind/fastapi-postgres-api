from typing import Optional
from app.core.exceptions import EntityNotFoundError
from app.models.task import Task
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Business logic for task lifecycle and authorization rules."""

    def __init__(self, task_repo: TaskRepository) -> None:
        self.task_repo = task_repo

    async def create_task(self, user: User, task_in: TaskCreate) -> Task:
        """Create a new task owned by the authenticated user."""
        task = Task(
            title=task_in.title,
            description=task_in.description,
            status=task_in.status,
            priority=task_in.priority,
            owner_id=user.id,
        )
        return await self.task_repo.create(task)

    async def get_tasks_for_user(
        self,
        user: User,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Task]:
        """Fetch tasks owned by the user with optional status filter."""
        return await self.task_repo.get_all_by_owner(
            owner_id=user.id,
            status=status,
            skip=skip,
            limit=limit
        )

    async def get_task_by_id(self, user: User, task_id: int) -> Task:
        """Fetch a specific task ensuring ownership authorization."""
        task = await self.task_repo.get_by_id_and_owner(task_id=task_id, owner_id=user.id)
        if not task:
            raise EntityNotFoundError("Task", task_id)
        return task

    async def update_task(self, user: User, task_id: int, task_in: TaskUpdate) -> Task:
        """Update an existing task owned by the user."""
        task = await self.get_task_by_id(user, task_id)

        update_data = task_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await self.task_repo.session.flush()
        await self.task_repo.session.refresh(task)
        return task

    async def delete_task(self, user: User, task_id: int) -> None:
        """Delete a task owned by the user."""
        task = await self.get_task_by_id(user, task_id)
        await self.task_repo.delete(task)

    async def get_task_with_owner(self, task_id: int) -> Task:
        """Fetch task and joined owner details using eager loading SQL JOIN."""
        task = await self.task_repo.get_task_with_owner(task_id)
        if not task:
            raise EntityNotFoundError("Task", task_id)
        return task
