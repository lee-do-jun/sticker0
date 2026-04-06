# src/sticker0/sticker.py
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

BORDER_STYLES: list[str] = [
    "solid",
    "heavy",
    "round",
    "double",
    "ascii",
    "inner",
    "outer",
    "dashed",
]
DEFAULT_BORDER_LINE = "solid"


@dataclass
class StickerColors:
    border: str = "white"
    text: str = "white"
    area: str = "transparent"


@dataclass
class StickerPosition:
    x: int = 0
    y: int = 0


@dataclass
class StickerSize:
    width: int = 30
    height: int = 10


@dataclass
class Sticker:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    colors: StickerColors = field(default_factory=StickerColors)
    line: str = DEFAULT_BORDER_LINE
    minimized: bool = False
    position: StickerPosition = field(default_factory=StickerPosition)
    size: StickerSize = field(default_factory=StickerSize)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "colors": {
                "border": self.colors.border,
                "text": self.colors.text,
                "area": self.colors.area,
            },
            "line": self.line,
            "minimized": self.minimized,
            "position": {"x": self.position.x, "y": self.position.y},
            "size": {"width": self.size.width, "height": self.size.height},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Sticker:
        now = datetime.now(timezone.utc).isoformat()
        colors_data = data.get("colors")
        if colors_data is not None:
            colors = StickerColors(
                border=colors_data.get("border", "white"),
                text=colors_data.get("text", "white"),
                area=colors_data.get("area", "transparent"),
            )
        else:
            # Legacy v0.2.0 migration: 기존 color 필드 무시, 기본 Snow 적용
            colors = StickerColors()
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            content=data.get("content", ""),
            colors=colors,
            line=data.get("line", DEFAULT_BORDER_LINE),
            minimized=data.get("minimized", False),
            position=StickerPosition(**data.get("position", {})),
            size=StickerSize(**data.get("size", {})),
            created_at=datetime.fromisoformat(data.get("created_at", now)),
            updated_at=datetime.fromisoformat(data.get("updated_at", now)),
        )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
