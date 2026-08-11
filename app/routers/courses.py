from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_db,
    require_role,
)
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)
from app.services.course_service import (
    create_course,
    delete_course,
    get_course,
    get_courses,
    update_course,
)


router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
)


# @router.get(
#     "",
#     response_model=list[CourseResponse],
# )
# def list_courses(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     return get_courses(db)
@router.get(
    "",
    response_model=list[CourseResponse],
)
def list_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    courses = get_courses(db)

    start = (page - 1) * limit
    end = start + limit

    return courses[start:end]


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
)
def read_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = get_course(db, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([
            UserRole.ADMIN,
            UserRole.TEACHER,
        ])
    ),
):
    # Teacher can only create a course for themselves.
    if (
        current_user.role == UserRole.TEACHER.value
        and data.teacher_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher can only create their own courses",
        )

    try:
        return create_course(
            db=db,
            title=data.title,
            description=data.description,
            capacity=data.capacity,
            teacher_id=data.teacher_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.put(
    "/{course_id}",
    response_model=CourseResponse,
)
def update_existing_course(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([
            UserRole.ADMIN,
            UserRole.TEACHER,
        ])
    ),
):
    course = get_course(db, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Teacher can only update their own course.
    if (
        current_user.role == UserRole.TEACHER.value
        and course.teacher_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own courses",
        )

    if (
        current_user.role == UserRole.TEACHER.value
        and data.teacher_id is not None
        and data.teacher_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher cannot transfer course ownership",
        )

    try:
        return update_course(
            db=db,
            course=course,
            title=data.title,
            description=data.description,
            capacity=data.capacity,
            teacher_id=data.teacher_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role([UserRole.ADMIN])
    ),
):
    course = get_course(db, course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    try:
        delete_course(db, course)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )