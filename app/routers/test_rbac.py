from fastapi import APIRouter, Depends

from app.core.dependencies import require_role
from app.core.roles import UserRole
from app.models.user import User

router = APIRouter(
    prefix="/test",
    tags=["RBAC Test"],
)


@router.get("/admin")
def admin_test(
    current_user: User = Depends(
        require_role([UserRole.ADMIN])
    ),
):
    return {
        "message": "Admin access granted",
        "user": current_user.email,
        "role": current_user.role,
    }


@router.get("/teacher")
def teacher_test(
    current_user: User = Depends(
        require_role([UserRole.TEACHER])
    ),
):
    return {
        "message": "Teacher access granted",
        "user": current_user.email,
        "role": current_user.role,
    }


@router.get("/student")
def student_test(
    current_user: User = Depends(
        require_role([UserRole.STUDENT])
    ),
):
    return {
        "message": "Student access granted",
        "user": current_user.email,
        "role": current_user.role,
    }