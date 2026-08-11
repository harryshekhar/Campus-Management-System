from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.roles import UserRole
from app.models.user import User
from app.models.enrollment import Enrollment
from app.schemas.grade import (
    GradeCreate,
    GradeResponse,
    GradeUpdate,
)
from app.services.grade_service import (
    create_grade,
    get_grade_by_id,
    get_grades,
    get_student_grades,
    update_grade,
)


router = APIRouter(
    prefix="/grades",
    tags=["Grades"],
)


@router.post(
    "",
    response_model=GradeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_grade(
    data: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    # Students cannot create grades.
    if current_user.role == UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot create grades",
        )

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.id == data.enrollment_id
        )
        .first()
    )

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )

    # Teacher can only grade students
    # enrolled in their own courses.
    if current_user.role == UserRole.TEACHER.value:
        if (
            enrollment.course.teacher_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only grade students in your courses",
            )

    # Admin is allowed.

    try:
        return create_grade(
            db=db,
            enrollment_id=data.enrollment_id,
            assignment_name=data.assignment_name,
            score=data.score,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[GradeResponse],
)
def list_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Student → own grades only
    if current_user.role == UserRole.STUDENT.value:
        return get_student_grades(
            db,
            current_user.id,
        )

    # Admin → all grades
    if current_user.role == UserRole.ADMIN.value:
        return get_grades(db)

    # Teacher → grades for their courses
    if current_user.role == UserRole.TEACHER.value:
        grades = get_grades(db)

        return [
            grade
            for grade in grades
            if grade.enrollment.course.teacher_id
            == current_user.id
        ]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission",
    )


@router.get(
    "/{grade_id}",
    response_model=GradeResponse,
)
def read_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grade = get_grade_by_id(
        db,
        grade_id,
    )

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found",
        )

    enrollment = grade.enrollment

    # Student → own grade only
    if current_user.role == UserRole.STUDENT.value:
        if enrollment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own grades",
            )

    # Teacher → own courses only
    elif current_user.role == UserRole.TEACHER.value:
        if (
            enrollment.course.teacher_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view grades for your courses",
            )

    return grade


@router.put(
    "/{grade_id}",
    response_model=GradeResponse,
)
def update_existing_grade(
    grade_id: int,
    data: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grade = get_grade_by_id(
        db,
        grade_id,
    )

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found",
        )

    enrollment = grade.enrollment

    # Students cannot update grades.
    if current_user.role == UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot update grades",
        )

    # Teacher → own courses only
    if current_user.role == UserRole.TEACHER.value:
        if (
            enrollment.course.teacher_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update grades for your courses",
            )

    return update_grade(
        db=db,
        grade=grade,
        assignment_name=data.assignment_name,
        score=data.score,
    )