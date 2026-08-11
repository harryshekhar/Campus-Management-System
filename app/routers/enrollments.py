from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_db,
)
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
)
from app.services.enrollment_service import (
    create_enrollment,
    delete_enrollment,
    get_enrollment,
    get_enrollments,
    get_student_enrollments,
)


router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"],
)


@router.post(
    "",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_enrollment(
    data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    # Student can only enroll themselves.
    if current_user.role == UserRole.STUDENT.value:
        student_id = current_user.id

    # Admin can enroll a specific student.
    elif current_user.role == UserRole.ADMIN.value:
        if data.student_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id is required for admin",
            )

        student_id = data.student_id

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teachers cannot create enrollments",
        )

    try:
        return create_enrollment(
            db=db,
            student_id=student_id,
            course_id=data.course_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[EnrollmentResponse],
)
def list_all_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    # Student → only their own enrollments
    if current_user.role == UserRole.STUDENT.value:
        return get_student_enrollments(
            db,
            current_user.id,
        )

    # Admin → everything
    if current_user.role == UserRole.ADMIN.value:
        return get_enrollments(db)

    # Teacher → enrollments belonging to their courses
    if current_user.role == UserRole.TEACHER.value:
        enrollments = get_enrollments(db)

        return [
            enrollment
            for enrollment in enrollments
            if enrollment.course.teacher_id
            == current_user.id
        ]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission",
    )


@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentResponse,
)
def read_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    enrollment = get_enrollment(
        db,
        enrollment_id,
    )

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )

    # Student → only own enrollment
    if current_user.role == UserRole.STUDENT.value:
        if enrollment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own enrollment",
            )

    # Teacher → only enrollment in own course
    elif current_user.role == UserRole.TEACHER.value:
        if enrollment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view enrollments in your courses",
            )

    return enrollment


@router.delete(
    "/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    enrollment = get_enrollment(
        db,
        enrollment_id,
    )

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )

    # Student → can remove own enrollment
    if current_user.role == UserRole.STUDENT.value:
        if enrollment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only remove your own enrollment",
            )

    # Teacher → can remove enrollment from own course
    elif current_user.role == UserRole.TEACHER.value:
        if enrollment.course.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage your course enrollments",
            )

    # Admin → allowed

    elif current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission",
        )

    delete_enrollment(
        db,
        enrollment,
    )