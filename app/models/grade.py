from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship

from app.database import Base


class Grade(Base):
    __tablename__ = "grades"

    __table_args__ = (
        UniqueConstraint(
            "enrollment_id",
            "assignment_name",
            name="uq_enrollment_assignment",
        ),
    )

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

    assignment_name = Column(
        String,
        nullable=False,
    )

    score = Column(
        Float,
        nullable=False,
    )

    graded_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    enrollment = relationship(
        "Enrollment",
        back_populates="grades",
    )