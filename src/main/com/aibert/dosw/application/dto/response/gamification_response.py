from datetime import date, datetime
from pydantic import BaseModel, Field


class BadgeDto(BaseModel):
    badge_id: str
    badge_name: str = Field(
        ..., description="Badge name (e.g., Constante, Cumplido, Enfoque)"
    )
    icon: str = Field(
        ..., description="URL, filename, or visual key for the badge icon"
    )
    description: str = Field(..., description="Explains how the badge is obtained")
    unlocked: bool = Field(..., description="true = unlocked, false = locked")
    unlocked_date: date | None = Field(
        None,
        description="Date when the badge was unlocked. Only populated when unlocked = true",
    )


class GamificationResponseDto(BaseModel):
    user_id: str
    total_points: int = Field(
        ..., description="Total points accumulated by the student (Integer)"
    )
    current_level: int = Field(
        ...,
        description="Current level (1–4) determined by the system's level table (Integer)",
    )
    badges: list[BadgeDto] = Field(
        ...,
        description="All system badges showing unlocked/locked state for the student",
    )
    progress_to_next: float = Field(
        ...,
        description="Points in current level / points needed for the next level (Float, 0.0 – 100.0)",
    )
    generated_at: datetime

    model_config = {"from_attributes": True}
