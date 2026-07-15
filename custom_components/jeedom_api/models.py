"""Small data models and discovery helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class JeedomCommand:
    """A Jeedom command."""

    id: str
    name: str
    type: str
    subtype: str
    generic_type: str | None
    logical_id: str | None
    unit: str | None
    state: Any
    value: str | None
    configuration: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JeedomCommand":
        return cls(
            id=str(data["id"]),
            name=str(data.get("name") or data["id"]),
            type=str(data.get("type") or ""),
            subtype=str(data.get("subType") or ""),
            generic_type=data.get("generic_type") or None,
            logical_id=data.get("logicalId"),
            unit=data.get("unite") or None,
            state=data.get("state"),
            value=str(data["value"]) if data.get("value") not in (None, "") else None,
            configuration=data.get("configuration") or {},
        )


@dataclass(slots=True)
class JeedomEquipment:
    """A Jeedom eqLogic."""

    id: str
    name: str
    object_id: str | None
    object_name: str
    plugin: str
    enabled: bool
    visible: bool
    commands: list[JeedomCommand]
    raw: dict[str, Any]

    @property
    def label(self) -> str:
        return f"{self.object_name} / {self.name} [{self.plugin}]"

    def command_by_generic(self, *generic_types: str) -> JeedomCommand | None:
        wanted = set(generic_types)
        return next((cmd for cmd in self.commands if cmd.generic_type in wanted), None)

    def info_commands(self) -> list[JeedomCommand]:
        return [cmd for cmd in self.commands if cmd.type == "info"]

    @classmethod
    def from_dict(cls, data: dict[str, Any], object_name: str) -> "JeedomEquipment":
        return cls(
            id=str(data["id"]),
            name=str(data.get("name") or data["id"]),
            object_id=str(data["object_id"]) if data.get("object_id") is not None else None,
            object_name=object_name,
            plugin=str(data.get("eqType_name") or "unknown"),
            enabled=str(data.get("isEnable", "1")) == "1",
            visible=str(data.get("isVisible", "1")) == "1",
            commands=[JeedomCommand.from_dict(cmd) for cmd in data.get("cmds", [])],
            raw=data,
        )


def parse_full_data(payload: list[dict[str, Any]]) -> dict[str, JeedomEquipment]:
    """Flatten Jeedom fullData objects into equipment indexed by id."""
    equipment: dict[str, JeedomEquipment] = {}
    for obj in payload:
        object_name = str(obj.get("name") or "Sans objet")
        for eq in obj.get("eqLogics", []):
            parsed = JeedomEquipment.from_dict(eq, object_name)
            if parsed.enabled:
                equipment[parsed.id] = parsed
    return equipment
