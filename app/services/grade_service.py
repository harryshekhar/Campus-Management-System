from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.grade import Grade


def get_grades(
    db: Session,
) -> list[Grade]:
    return (
        db.query(Grade)
        .order_by(Grade.graded_at.desc())
        .all()
    )


def get_grade_by_id(
    db: Session,
    grade_id: int,
) -> Grade | None:
    return (
        db.query(Grade)
        .filter(Grade.id == grade_id)
        .first()
    )


def get_student_grades(
    db: Session,
    student_id: int,
) -> list[Grade]:
    return (
        db.query(Grade)
        .join(Enrollment)
        .filter(
            Enrollment.student_id == student_id
        )
        .order_by(Grade.graded_at.desc())
        .all()
    )


def create_grade(
    db: Session,
    enrollment_id: int,
    assignment_name: str,
    score: float,
) -> Grade:

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.id == enrollment_id
        )
        .first()
    )

    if not enrollment:
        raise ValueError(
            "Enrollment not found"
        )

    grade = Grade(
        enrollment_id=enrollment_id,
        assignment_name=assignment_name,
        score=score,
    )

    db.add(grade)
    db.commit()
    db.refresh(grade)

    return grade


def update_grade(
    db: Session,
    grade: Grade,
    assignment_name: str | None = None,
    score: float | None = None,
) -> Grade:

    if assignment_name is not None:
        grade.assignment_name = assignment_name

    if score is not None:
        grade.score = score

    db.commit()
    db.refresh(grade)

    return grades