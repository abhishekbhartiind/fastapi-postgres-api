from typing import TYPE_CHECKING, Optional
# pyrefly: ignore [missing-import]
from sqlalchemy import ForeignKey, Index, Integer, String, Text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Task(Base, TimestampMixin):
    """Task database model linked to a User via foreign key.

    Indexes:
    - idx_tasks_owner_id: Fast lookups for all tasks owned by a user
    - idx_tasks_owner_status: Composite index for fast filtering (WHERE owner_id = X AND status = Y)
    - idx_tasks_title: B-Tree index for title searches
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)

    # Foreign Key with CASCADE delete
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relationship back to User
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="tasks"
    )

    __table_args__ = (
        Index("idx_tasks_owner_status", "owner_id", "status"),
        Index("idx_tasks_status_priority", "status", "priority"),
    )
