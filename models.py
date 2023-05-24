from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey  # , JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]

    # event_metrics: Mapped[JSON] = mapped_column(JSON, nullable=False)

    metric_one: Mapped[Optional[int]]
    metric_two: Mapped[Optional[int]]
    metric_n: Mapped[Optional[int]]

    created_date: Mapped[datetime]
    recorded_date: Mapped[datetime]
    dimension_one_id: Mapped[int] = mapped_column(
        ForeignKey("first_dimensions.id"), index=True
    )
    dimension_two_id: Mapped[int] = mapped_column(ForeignKey("second_dimensions.id"))


class FirstDimension(Base):
    __tablename__ = "first_dimensions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    dimension_second_id: Mapped[int] = mapped_column(ForeignKey("second_dimensions.id"))


class SecondDimension(Base):
    __tablename__ = "second_dimensions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
