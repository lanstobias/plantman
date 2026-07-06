"""Data models for Plant Manager."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class Task:
    """Represents a plant care task."""

    id: str
    name: str
    interval_days: int
    last_completed: datetime | None = None

    def days_since_completed(self) -> int | None:
        """Calculate days since last completion."""
        if self.last_completed is None:
            return None
        delta = datetime.now() - self.last_completed
        return delta.days

    def next_due_date(self) -> datetime | None:
        """Calculate next due date."""
        if self.last_completed is None:
            return None
        return self.last_completed + timedelta(days=self.interval_days)

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        next_due = self.next_due_date()
        if next_due is None:
            return False
        return datetime.now() > next_due

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "interval_days": self.interval_days,
            "last_completed": self.last_completed.isoformat() if self.last_completed else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Create from dictionary."""
        last_completed = None
        if data.get("last_completed"):
            last_completed = datetime.fromisoformat(data["last_completed"])

        return cls(
            id=data["id"],
            name=data["name"],
            interval_days=data["interval_days"],
            last_completed=last_completed,
        )


@dataclass
class GrowthStage:
    """Represents a plant growth stage."""

    id: str
    name: str
    task_overrides: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "task_overrides": self.task_overrides,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GrowthStage:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            task_overrides=data.get("task_overrides", {}),
        )


@dataclass
class PlantProfile:
    """Represents AI-generated plant information."""

    common_name: str
    scientific_name: str
    variety: str
    description: str
    light_requirements: str
    temperature: str
    humidity: str
    soil: str
    harvest_info: str
    common_issues: str
    tasks: list[dict[str, Any]]
    growth_stages: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "common_name": self.common_name,
            "scientific_name": self.scientific_name,
            "variety": self.variety,
            "description": self.description,
            "light_requirements": self.light_requirements,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "soil": self.soil,
            "harvest_info": self.harvest_info,
            "common_issues": self.common_issues,
            "tasks": self.tasks,
            "growth_stages": self.growth_stages,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlantProfile:
        """Create from dictionary."""
        return cls(
            common_name=data["common_name"],
            scientific_name=data["scientific_name"],
            variety=data["variety"],
            description=data["description"],
            light_requirements=data["light_requirements"],
            temperature=data["temperature"],
            humidity=data["humidity"],
            soil=data["soil"],
            harvest_info=data["harvest_info"],
            common_issues=data["common_issues"],
            tasks=data["tasks"],
            growth_stages=data["growth_stages"],
        )


@dataclass
class Plant:
    """Represents a managed plant."""

    id: str
    name: str
    profile: PlantProfile
    tasks: list[Task]
    growth_stages: list[GrowthStage]
    current_stage_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def get_current_stage(self) -> GrowthStage | None:
        """Get current growth stage."""
        if not self.current_stage_id:
            return None
        for stage in self.growth_stages:
            if stage.id == self.current_stage_id:
                return stage
        return None

    def get_task(self, task_id: str) -> Task | None:
        """Get task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_effective_interval(self, task_id: str) -> int | None:
        """Get effective interval for task considering growth stage overrides."""
        task = self.get_task(task_id)
        if not task:
            return None

        current_stage = self.get_current_stage()
        if current_stage and task_id in current_stage.task_overrides:
            return current_stage.task_overrides[task_id]

        return task.interval_days

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "profile": self.profile.to_dict(),
            "tasks": [task.to_dict() for task in self.tasks],
            "growth_stages": [stage.to_dict() for stage in self.growth_stages],
            "current_stage_id": self.current_stage_id,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Plant:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            profile=PlantProfile.from_dict(data["profile"]),
            tasks=[Task.from_dict(t) for t in data["tasks"]],
            growth_stages=[GrowthStage.from_dict(s) for s in data["growth_stages"]],
            current_stage_id=data.get("current_stage_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
