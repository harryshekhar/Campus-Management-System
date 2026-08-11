from datetime import datetime

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    description: str | None = None
    capacity: int = Field(gt=0, le=1000)
    teacher_id: int


class CourseUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    description: str | None = None
    capacity: int | None = Field(
        default=None,
        gt=0,
        le=1000,
    )
    teacher_id: int | None = None


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str | None
    capacity: int
    teacher_id: int
    created_at: datetime

    class Config:
        from_attributes = True