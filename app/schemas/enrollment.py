from datetime import datetime

from pydantic import BaseModel


class EnrollmentCreate(BaseModel):
    course_id: int
    student_id: int | None = None


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True