from typing import Optional
# pyrefly: ignore [missing-import]
from sqlalchemy import select
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import joinedload
from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Data access repository for Task entities.

    Demonstrates:
    - SQL Joins with joinedload (Eager loading)
    - Filter queries utilizing B-Tree and Composite indexes
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Task, session)

    async def get_by_id_and_owner(self, task_id: int, owner_id: int) -> Optional[Task]:
        """Fetch a task ensuring it belongs to the given owner (uses idx_tasks_owner_id)."""
        stmt = select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_by_owner(
        self,
        owner_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Task]:
        """Retrieve tasks belonging to a specific owner with optional status filter.

        Utilizes the composite index (owner_id, status) for maximum query efficiency.
        """
        stmt = select(Task).where(Task.owner_id == owner_id)
        if status:
            stmt = stmt.where(Task.status == status)

        stmt = stmt.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_task_with_owner(self, task_id: int) -> Optional[Task]:
        """Fetch a task alongside its owner user information using an SQL JOIN.

        Generates:
        SELECT tasks.*, users.*
        FROM tasks
        LEFT OUTER JOIN users ON users.id = tasks.owner_id
        WHERE tasks.id = :task_id
        """
        stmt = (
            select(Task)
            .options(joinedload(Task.owner))
            .where(Task.id == task_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
