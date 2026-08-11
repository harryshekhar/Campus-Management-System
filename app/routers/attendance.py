from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.roles import UserRole
from app.models.user import User
from app.models.enrollment import Enrollment
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
)
from app.services.attendance_service import (
    create_attendance,
    get_attendance,
    get_attendance_by_id,
    get_student_attendance,
    update_attendance,
)


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)


@router.post(
    "",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    # Students cannot mark attendance.
    if current_user.role == UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot mark attendance",
        )

    # Teacher can only mark attendance
    # for students enrolled in their own course.
    if current_user.role == UserRole.TEACHER.value:
        if (
            enrollment.course.teacher_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark attendance for your courses",
            )

    # Admin is allowed.

    try:
        return create_attendance(
            db=db,
            enrollment_id=data.enrollment_id,
            status=data.status,
            date=data.date,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[AttendanceResponse],
)
def list_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Student → own attendance only
    if current_user.role == UserRole.STUDENT.value:
        return get_student_attendance(
            db,
            current_user.id,
        )

    # Admin → all attendance
    if current_user.role == UserRole.ADMIN.value:
        return get_attendance(db)

    # Teacher → attendance for their courses
    if current_user.role == UserRole.TEACHER.value:
        records = get_attendance(db)

        return [
            record
            for record in records
            if record.enrollment.course.teacher_id
            == current_user.id
        ]

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission",
    )


@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse,
)
def read_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendance = get_attendance_by_id(
        db,
        attendance_id,
    )

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found",
        )

    enrollment = attendance.enrollment

    # Student → own attendance only
    if current_user.role == UserRole.STUDENT.value:
        if enrollment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own attendance",
            )

    # Teacher → own courses only
    elif current_user.role == UserRole.TEACHER.value:
        if (
            enrollment.course.teacher_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view attendance for your courses",
            )

    return attendance


@router.put(
    "/{attendance_id}",
    response_model=AttendanceResponse,
)
def update_existing_attendance(
    attendance_id: int,
    data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendance = get_attendance_by_id(
        db,
        attendance_id,
    )

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found",
        )

    enrollment = attendance.enrollment

    # Students cannot update attendance.
    if current_user.role == UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot update attendance",
        )

    # Teacher → own courses only
    if current_user.role == UserRole.TEACHER.value:
        if (
            enrollment.course.teacher_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update attendance for your courses",
            )

    return update_attendance(
        db=db,
        attendance=attendance,
        status=data.status,
    )