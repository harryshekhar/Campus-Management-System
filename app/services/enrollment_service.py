from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user import User


# def get_enrollments(
#     db: Session,
# ) -> list[Enrollment]:
#     return (
#         db.query(Enrollment)
#         .order_by(Enrollment.id)
#         .all()
#     )

def get_enrollments(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Enrollment]:
    return (
        db.query(Enrollment)
        .order_by(Enrollment.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_enrollment(
    db: Session,
    enrollment_id: int,
) -> Enrollment | None:
    return (
        db.query(Enrollment)
        .filter(
            Enrollment.id == enrollment_id
        )
        .first()
    )


def get_student_enrollments(
    db: Session,
    student_id: int,
) -> list[Enrollment]:
    return (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == student_id
        )
        .order_by(Enrollment.id)
        .all()
    )


def create_enrollment(
    db: Session,
    student_id: int,
    course_id: int,
) -> Enrollment:

    student = (
        db.query(User)
        .filter(User.id == student_id)
        .first()
    )

    if not student:
        raise ValueError("Student not found")

    if student.role != "student":
        raise ValueError(
            "Only students can be enrolled"
        )

    course = (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )

    if not course:
        raise ValueError("Course not found")

    existing = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
        )
        .first()
    )

    if existing:
        raise ValueError(
            "Student is already enrolled in this course"
        )

    enrollment_count = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course_id
        )
        .count()
    )

    if enrollment_count >= course.capacity:
        raise ValueError(
            "Course capacity has been reached"
        )

    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment


def delete_enrollment(
    db: Session,
    enrollment: Enrollment,
) -> None:

    db.delete(enrollment)
    db.commit()