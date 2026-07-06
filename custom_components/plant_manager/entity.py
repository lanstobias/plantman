"""Base entity for Plant Manager."""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

if TYPE_CHECKING:
    from .coordinator import PlantCoordinator
    from .models import Plant


class PlantEntity(CoordinatorEntity[PlantCoordinator]):
    """Base entity for plant entities."""

    def __init__(
        self,
        coordinator: PlantCoordinator,
        plant_id: str,
    ) -> None:
        """Initialize entity."""
        super().__init__(coordinator)
        self._plant_id = plant_id

    @property
    def plant(self) -> Plant | None:
        """Get the plant object."""
        return self.coordinator.data.get(self._plant_id) if self.coordinator.data else None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        plant = self.plant
        if not plant:
            return DeviceInfo(identifiers={(DOMAIN, self._plant_id)})

        return DeviceInfo(
            identifiers={(DOMAIN, self._plant_id)},
            name=plant.name,
            manufacturer="Plant Manager",
            model=plant.profile.scientific_name,
            suggested_area="Garden",
        )
