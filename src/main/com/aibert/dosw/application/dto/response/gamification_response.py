from datetime import date, datetime
from pydantic import BaseModel, Field


class BadgeDto(BaseModel):
    badge_id: str = Field(..., example="first_steps")
    badge_name: str = Field(
        ...,
        description="Badge name (e.g., Constante, Cumplido, Enfoque)",
        example="First Steps",
    )
    icon: str = Field(
        ...,
        description="URL, filename, or visual key for the badge icon",
        example="🎯",
    )
    description: str = Field(
        ...,
        description="Explains how the badge is obtained",
        example="Complete at least 1 task",
    )
    unlocked: bool = Field(
        ..., description="true = unlocked, false = locked", example=True
    )
    unlocked_date: date | None = Field(
        None,
        description="Date when the badge was unlocked. Only populated when unlocked = true",
        example="2026-03-10",
    )


class GamificationResponseDto(BaseModel):
    user_id: str = Field(..., example="a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    total_points: int = Field(
        ...,
        description="Total points accumulated by the student (Integer)",
        example=150,
    )
    current_level: int = Field(
        ...,
        description="Current level (1–4) determined by the system's level table (Integer)",
        example=2,
    )
    badges: list[BadgeDto] = Field(
        ...,
        description="All system badges showing unlocked/locked state for the student",
    )
    progress_to_next: float = Field(
        ...,
        description="Points in current level / points needed for the next level (Float, 0.0 – 100.0)",
        example=25.0,
    )
    generated_at: datetime = Field(..., example="2026-05-22T16:52:39.763Z")

    model_config = {"from_attributes": True}
