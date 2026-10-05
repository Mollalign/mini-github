from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampIdMixin

if TYPE_CHECKING:
    from app.modules.users.models import User


class Repository(Base, TimestampIdMixin):
    __tablename__ = "repositories"

    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "name",
            name="uq_repository_owner_name",
        ),
    )

 
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True, 
        default=uuid.uuid4  
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_private: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    default_branch: Mapped[str] = mapped_column(
        String(100),
        default="main",
        nullable=False,
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="repositories",
    )