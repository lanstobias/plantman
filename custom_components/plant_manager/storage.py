"""Storage management for Plant Manager."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .models import Plant

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.storage"


class PlantStorage:
    """Manage plant data persistence."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""
        self._hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._plants: dict[str, Plant] = {}

    async def async_load(self) -> None:
        """Load plants from storage."""
        data = await self._store.async_load()

        if data is None:
            _LOGGER.debug("No stored data found, starting fresh")
            return

        plants_data = data.get("plants", {})

        for plant_id, plant_data in plants_data.items():
            try:
                self._plants[plant_id] = Plant.from_dict(plant_data)
            except Exception as err:
                _LOGGER.error("Failed to load plant %s: %s", plant_id, err)

    async def async_save(self) -> None:
        """Save plants to storage."""
        data = {
            "plants": {
                plant_id: plant.to_dict()
                for plant_id, plant in self._plants.items()
            }
        }

        await self._store.async_save(data)
        _LOGGER.debug("Saved %d plants to storage", len(self._plants))

    async def async_add_plant(self, plant: Plant) -> None:
        """Add a plant to storage."""
        self._plants[plant.id] = plant
        await self.async_save()
        _LOGGER.info("Added plant: %s (%s)", plant.name, plant.id)

    async def async_remove_plant(self, plant_id: str) -> None:
        """Remove a plant from storage."""
        if plant_id in self._plants:
            plant = self._plants.pop(plant_id)
            await self.async_save()
            _LOGGER.info("Removed plant: %s (%s)", plant.name, plant_id)

    async def async_update_plant(self, plant: Plant) -> None:
        """Update a plant in storage."""
        self._plants[plant.id] = plant
        await self.async_save()
        _LOGGER.debug("Updated plant: %s (%s)", plant.name, plant.id)

    def get_plant(self, plant_id: str) -> Plant | None:
        """Get a plant by ID."""
        return self._plants.get(plant_id)

    def get_all_plants(self) -> list[Plant]:
        """Get all plants."""
        return list(self._plants.values())
