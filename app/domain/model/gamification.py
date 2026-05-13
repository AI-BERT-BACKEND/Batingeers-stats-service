from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Badge:
    badge_id: str
    name: str
    icon: str
    description: str


@dataclass
class GamificationProfile:
    user_id: str
    total_points: int
    current_level: int
    badges: list[Badge]
    progress_to_next: float  # 0.0 – 100.0 (100.0 means max level reached)
    generated_at: datetime = field(default_factory=datetime.utcnow)
