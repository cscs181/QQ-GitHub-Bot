import json
from typing import Any
from typing_extensions import Self
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Entity:
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(**data)

    @classmethod
    def from_json(cls, data: str | bytes) -> Self:
        return cls.from_dict(json.loads(data))

    def dict(self) -> dict[str, Any]:
        return asdict(self)

    def json(self) -> str:
        return json.dumps(asdict(self))
