from datetime import datetime

from pydantic import BaseModel, Field


class GradeCreate(BaseModel):
    enrollment_id: int
    assignment_name: str = Field(
        min_length=1,
        max_length=150,
    )
    score: float = Field(
        ge=0,
        le=100,
    )


class GradeUpdate(BaseModel):
    assignment_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class GradeResponse(BaseModel):
    id: int
    enrollment_id: int
    assignment_name: str
    score: float
    graded_at: datetime

    class Config:
        from_attributes = True