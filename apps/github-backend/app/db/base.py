from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, declarative_mixin, DeclarativeBase

class Base(DeclarativeBase):
    """SQLAlchemy Base class."""
    pass

@declarative_mixin
class TimestampIdMixin:
    """Mixin to inject created_at, and updated_at columns automatically."""  

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# Import all models here for Alembic
from app.modules.users.models import User
# from app.modules.repositories.models import Repository
