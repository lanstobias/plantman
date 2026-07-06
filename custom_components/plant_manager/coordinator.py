"""Data coordinator for Plant Manager."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_AI_API_KEY,
    CONF_AI_ENDPOINT,
    CONF_AI_MODEL,
    DEFAULT_AI_ENDPOINT,
    DEFAULT_AI_MODEL,
    DOMAIN,
    UPDATE_INTERVAL_SECONDS,
)
from .models import GrowthStage, Plant, Task
from .openai_provider import OpenAIPlantInfoProvider
from .storage import PlantStorage

if TYPE_CHECKING:
    from .models import PlantProfile

_LOGGER = logging.getLogger(__name__)


class PlantCoordinator(DataUpdateCoordinator[dict[str, Plant]]):
    """Coordinator to manage plant data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        storage: PlantStorage,
        entry: ConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self._storage = storage
        self._entry = entry

        api_key = entry.data.get(CONF_AI_API_KEY, "")
        endpoint = entry.data.get(CONF_AI_ENDPOINT, DEFAULT_AI_ENDPOINT)
        model = entry.data.get(CONF_AI_MODEL, DEFAULT_AI_MODEL)

        self._ai_provider = OpenAIPlantInfoProvider(api_key, endpoint, model)

    async def _async_update_data(self) -> dict[str, Plant]:
        """Fetch data from storage."""
        try:
            plants = self._storage.get_all_plants()
            return {plant.id: plant for plant in plants}
        except Exception as err:
            raise UpdateFailed(f"Error fetching plant data: {err}") from err

    async def async_add_plant(self, plant_name: str) -> Plant:
        """Add a new plant using AI to generate profile.

        Args:
            plant_name: Name of the plant

        Returns:
            Created Plant object

        Raises:
            Exception: If AI query or storage fails
        """
        _LOGGER.info("Adding new plant: %s", plant_name)

        profile = await self._ai_provider.get_plant_profile(plant_name)

        plant_id = str(uuid.uuid4())

        tasks = [
            Task(
                id=task_data["id"],
                name=task_data["name"],
                interval_days=task_data["interval_days"],
            )
            for task_data in profile.tasks
        ]

        growth_stages = [
            GrowthStage(
                id=stage_data["id"],
                name=stage_data["name"],
                task_overrides=stage_data.get("task_overrides", {}),
            )
            for stage_data in profile.growth_stages
        ]

        initial_stage_id = growth_stages[0].id if growth_stages else None

        plant = Plant(
            id=plant_id,
            name=plant_name,
            profile=profile,
            tasks=tasks,
            growth_stages=growth_stages,
            current_stage_id=initial_stage_id,
            created_at=datetime.now(),
        )

        await self._storage.async_add_plant(plant)
        await self.async_refresh()

        return plant

    async def async_remove_plant(self, plant_id: str) -> None:
        """Remove a plant.

        Args:
            plant_id: ID of plant to remove
        """
        await self._storage.async_remove_plant(plant_id)
        await self.async_refresh()

    async def async_complete_task(self, plant_id: str, task_id: str) -> None:
        """Mark a task as completed.

        Args:
            plant_id: ID of the plant
            task_id: ID of the task to complete
        """
        plant = self._storage.get_plant(plant_id)
        if not plant:
            _LOGGER.error("Plant not found: %s", plant_id)
            return

        task = plant.get_task(task_id)
        if not task:
            _LOGGER.error("Task not found: %s for plant %s", task_id, plant_id)
            return

        task.last_completed = datetime.now()

        await self._storage.async_update_plant(plant)
        await self.async_refresh()

        _LOGGER.info(
            "Completed task %s for plant %s (%s)",
            task.name,
            plant.name,
            plant_id,
        )

    async def async_set_growth_stage(self, plant_id: str, stage_id: str) -> None:
        """Change plant growth stage.

        Args:
            plant_id: ID of the plant
            stage_id: ID of the growth stage
        """
        plant = self._storage.get_plant(plant_id)
        if not plant:
            _LOGGER.error("Plant not found: %s", plant_id)
            return

        if not any(stage.id == stage_id for stage in plant.growth_stages):
            _LOGGER.error("Growth stage not found: %s for plant %s", stage_id, plant_id)
            return

        plant.current_stage_id = stage_id

        await self._storage.async_update_plant(plant)
        await self.async_refresh()

        _LOGGER.info(
            "Changed growth stage to %s for plant %s (%s)",
            stage_id,
            plant.name,
            plant_id,
        )
