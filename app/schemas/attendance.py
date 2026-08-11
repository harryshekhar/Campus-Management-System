from datetime import datetime

from pydantic import BaseModel

from app.models.attendance import AttendanceStatus


class AttendanceCreate(BaseModel):
    enrollment_id: int
    status: AttendanceStatus
    date: datetime | None = None


class AttendanceUpdate(BaseModel):
    status: AttendanceStatus


class AttendanceResponse(BaseModel):
    id: int
    enrollment_id: int
    date: datetime
    status: AttendanceStatus

    class Config:
        from_attributes = True