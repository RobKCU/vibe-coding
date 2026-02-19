from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class StepRecord:
    name: str
    prompt: str
    options: list[str]
    choice: str
    notes: str = ""
    regen_count: int = 0


@dataclass
class SessionRecord:
    started_at: str
    model: str
    voice: str
    absurdity: str
    steps: list[StepRecord] = field(default_factory=list)
    final_joke: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))


def new_session(*, model: str, voice: str, absurdity: str) -> SessionRecord:
    timestamp = datetime.now().isoformat(timespec="seconds")
    return SessionRecord(
        started_at=timestamp,
        model=model,
        voice=voice,
        absurdity=absurdity,
    )
