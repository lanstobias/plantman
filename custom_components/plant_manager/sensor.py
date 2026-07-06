"""Sensor platform for Plant Manager."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_LAST_COMPLETED, ATTR_NEXT_DUE, ATTR_TASK_ID, DOMAIN
from .entity import PlantEntity

if TYPE_CHECKING:
    from .coordinator import PlantCoordinator
    from .models import Plant, Task

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator: PlantCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[SensorEntity] = []

    for plant in coordinator.data.values():
        for task in plant.tasks:
            entities.append(TaskDaysSinceSensor(coordinator, plant.id, task.id))
            entities.append(TaskNextDueSensor(coordinator, plant.id, task.id))

    async_add_entities(entities)


class TaskDaysSinceSensor(PlantEntity, SensorEntity):
    """Sensor showing days since task completion."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(
        self,
        coordinator: PlantCoordinator,
        plant_id: str,
        task_id: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, plant_id)
        self._task_id = task_id
        self._attr_unique_id = f"{plant_id}_{task_id}_days_since"

    @property
    def task(self) -> Task | None:
        """Get the task object."""
        if not self.plant:
            return None
        return self.plant.get_task(self._task_id)

    @property
    def name(self) -> str:
        """Return name."""
        task = self.task
        if not task or not self.plant:
            return "Unknown"
        return f"{self.plant.name} {task.name} Days Since"

    @property
    def native_value(self) -> int | None:
        """Return days since last completion."""
        task = self.task
        if not task:
            return None
        return task.days_since_completed()

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Return additional attributes."""
        task = self.task
        if not task:
            return {}

        last_completed = None
        if task.last_completed:
            last_completed = task.last_completed.isoformat()

        return {
            ATTR_TASK_ID: task.id,
            ATTR_LAST_COMPLETED: last_completed,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.plant is not None and self.task is not None


class TaskNextDueSensor(PlantEntity, SensorEntity):
    """Sensor showing next due date for task."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: PlantCoordinator,
        plant_id: str,
        task_id: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, plant_id)
        self._task_id = task_id
        self._attr_unique_id = f"{plant_id}_{task_id}_next_due"

    @property
    def task(self) -> Task | None:
        """Get the task object."""
        if not self.plant:
            return None
        return self.plant.get_task(self._task_id)

    @property
    def name(self) -> str:
        """Return name."""
        task = self.task
        if not task or not self.plant:
            return "Unknown"
        return f"{self.plant.name} {task.name} Next Due"

    @property
    def native_value(self) -> datetime | None:
        """Return next due date."""
        task = self.task
        if not task:
            return None
        return task.next_due_date()

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Return additional attributes."""
        task = self.task
        if not task:
            return {}

        return {
            ATTR_TASK_ID: task.id,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.plant is not None and self.task is not None
