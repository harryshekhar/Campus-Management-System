from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceStatus
from app.models.enrollment import Enrollment


def get_attendance(
    db: Session,
) -> list[Attendance]:
    return (
        db.query(Attendance)
        .order_by(Attendance.date.desc())
        .all()
    )


def get_attendance_by_id(
    db: Session,
    attendance_id: int,
) -> Attendance | None:
    return (
        db.query(Attendance)
        .filter(Attendance.id == attendance_id)
        .first()
    )


def get_student_attendance(
    db: Session,
    student_id: int,
) -> list[Attendance]:
    return (
        db.query(Attendance)
        .join(Enrollment)
        .filter(
            Enrollment.student_id == student_id
        )
        .order_by(Attendance.date.desc())
        .all()
    )


def create_attendance(
    db: Session,
    enrollment_id: int,
    status: AttendanceStatus,
    date: datetime | None = None,
) -> Attendance:

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.id == enrollment_id
        )
        .first()
    )

    if not enrollment:
        raise ValueError("Enrollment not found")

    attendance_date = date or datetime.utcnow()

    # Start and end of the selected calendar day
    start_of_day = attendance_date.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    end_of_day = start_of_day + timedelta(days=1)

    # Check if attendance already exists
    existing = (
        db.query(Attendance)
        .filter(
            Attendance.enrollment_id == enrollment_id,
            Attendance.date >= start_of_day,
            Attendance.date < end_of_day,
        )
        .first()
    )

    if existing:
        raise ValueError(
            "Attendance already exists for this date"
        )

    attendance = Attendance(
        enrollment_id=enrollment_id,
        status=status,
        date=attendance_date,
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance


def update_attendance(
    db: Session,
    attendance: Attendance,
    status: AttendanceStatus,
) -> Attendance:

    attendance.status = status

    db.commit()
    db.refresh(attendance)

    return attendance