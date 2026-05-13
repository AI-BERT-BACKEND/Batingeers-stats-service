from datetime import datetime
from pydantic import BaseModel, Field


class BadgeDto(BaseModel):
    badge_id: str
    name: str
    icon: str
    description: str


class GamificationResponseDto(BaseModel):
    user_id: str
    total_points: int = Field(..., description="Total points accumulated by the student")
    current_level: int = Field(..., description="Current level (1–4) based on points thresholds")
    badges: list[BadgeDto] = Field(..., description="Badges earned by the student")
    progress_to_next: float = Field(
        ..., description="Percentage progress toward the next level (0.0 – 100.0)"
    )
    generated_at: datetime

    model_config = {"from_attributes": True}
