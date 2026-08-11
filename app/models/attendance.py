from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Index,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    enrollment_id = Column(
        Integer,
        ForeignKey("enrollments.id"),
        nullable=False,
    )

    date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    status = Column(
        SQLEnum(AttendanceStatus),
        nullable=False,
    )

    enrollment = relationship(
        "Enrollment",
        back_populates="attendance_records",
    )

    __table_args__ = (
        Index(
            "uq_attendance_enrollment_day",
            "enrollment_id",
            func.date(date),
            unique=True,
        ),
    )