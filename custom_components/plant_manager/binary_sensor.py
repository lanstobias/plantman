"""Binary sensor platform for Plant Manager."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_TASK_ID, DOMAIN
from .entity import PlantEntity

if TYPE_CHECKING:
    from .coordinator import PlantCoordinator
    from .models import Task

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor platform."""
    coordinator: PlantCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[BinarySensorEntity] = []

    for plant in coordinator.data.values():
        for task in plant.tasks:
            entities.append(TaskOverdueSensor(coordinator, plant.id, task.id))

    async_add_entities(entities)


class TaskOverdueSensor(PlantEntity, BinarySensorEntity):
    """Binary sensor showing if task is overdue."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: PlantCoordinator,
        plant_id: str,
        task_id: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, plant_id)
        self._task_id = task_id
        self._attr_unique_id = f"{plant_id}_{task_id}_overdue"

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
        return f"{self.plant.name} {task.name} Overdue"

    @property
    def is_on(self) -> bool:
        """Return true if task is overdue."""
        task = self.task
        if not task:
            return False
        return task.is_overdue()

    @property
    def extra_state_attributes(self) -> dict[str, str]:
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
