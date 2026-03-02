"""Data models for extracted content."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ExtractionResult:
    url: str
    content: str  # clean markdown/text
    title: str = ""
    method: str = ""  # "trafilatura" | "playwright" | "failed"
    content_length: int = 0
    extracted_at: datetime = field(default_factory=_utcnow)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        self.content_length = len(self.content)
