from datetime import datetime

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy import (
    UUID,
    String,
    DECIMAL,
    DateTime,
    func,
)

import uuid

from decimal import Decimal

from app.db.models.base import Base


class Transaction(Base):
    id: Mapped[str] = mapped_column(
        UUID,
        primary_key=True,
        nullable=False,
        default=uuid.uuid4,
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
    )
