from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user import User


# def get_courses(
#     db: Session,
# ) -> list[Course]:
#     return (
#         db.query(Course)
#         .order_by(Course.id)
#         .all()
#     )

def get_courses(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Course]:
    return (
        db.query(Course)
        .order_by(Course.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_course(
    db: Session,
    course_id: int,
) -> Course | None:
    return (
        db.query(Course)
        .filter(Course.id == course_id)
        .first()
    )


def create_course(
    db: Session,
    title: str,
    description: str | None,
    capacity: int,
    teacher_id: int,
) -> Course:

    teacher = (
        db.query(User)
        .filter(User.id == teacher_id)
        .first()
    )

    if not teacher:
        raise ValueError("Teacher not found")

    if teacher.role != "teacher":
        raise ValueError(
            "Selected user is not a teacher"
        )

    course = Course(
        title=title,
        description=description,
        capacity=capacity,
        teacher_id=teacher_id,
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


def update_course(
    db: Session,
    course: Course,
    title: str | None = None,
    description: str | None = None,
    capacity: int | None = None,
    teacher_id: int | None = None,
) -> Course:

    if title is not None:
        course.title = title

    if description is not None:
        course.description = description

    if capacity is not None:
        enrollment_count = (
            db.query(Enrollment)
            .filter(
                Enrollment.course_id == course.id
            )
            .count()
        )

        if capacity < enrollment_count:
            raise ValueError(
                "Capacity cannot be lower than "
                "current enrollment count"
            )

        course.capacity = capacity

    if teacher_id is not None:
        teacher = (
            db.query(User)
            .filter(User.id == teacher_id)
            .first()
        )

        if not teacher:
            raise ValueError("Teacher not found")

        if teacher.role != "teacher":
            raise ValueError(
                "Selected user is not a teacher"
            )

        course.teacher_id = teacher_id

    db.commit()
    db.refresh(course)

    return course


def delete_course(
    db: Session,
    course: Course,
) -> None:

    enrollment_count = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == course.id
        )
        .count()
    )

    if enrollment_count > 0:
        raise ValueError(
            "Cannot delete a course with active enrollments"
        )

    db.delete(course)
    db.commit()