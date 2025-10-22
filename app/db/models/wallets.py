from datetime import datetime
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy import (
    UUID,
    DECIMAL,
    DateTime,
    func,
    text,
)

from decimal import Decimal

import uuid

from app.db.models.base import Base


class Wallet(Base):
    id: Mapped[str] = mapped_column(
        UUID,
        primary_key=True,
        nullable=False,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    balance: Mapped[Decimal] = mapped_column(
        DECIMAL,
        nullable=False,
        default=Decimal("0.0"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        default=func.now(),
    )
