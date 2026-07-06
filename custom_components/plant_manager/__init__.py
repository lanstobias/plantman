"""Plant Manager integration for Home Assistant."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import ATTR_PLANT_ID, ATTR_TASK_ID, DOMAIN
from .coordinator import PlantCoordinator
from .notification_manager import NotificationManager
from .storage import PlantStorage

if TYPE_CHECKING:
    pass

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON]

SERVICE_COMPLETE_TASK = "complete_task"
SERVICE_SET_GROWTH_STAGE = "set_growth_stage"

SERVICE_COMPLETE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PLANT_ID): cv.string,
        vol.Required(ATTR_TASK_ID): cv.string,
    }
)

SERVICE_SET_GROWTH_STAGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PLANT_ID): cv.string,
        vol.Required("stage_id"): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Plant Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    storage = PlantStorage(hass)
    await storage.async_load()

    coordinator = PlantCoordinator(hass, storage, entry)
    await coordinator.async_config_entry_first_refresh()

    notification_manager = NotificationManager(hass, coordinator)

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "storage": storage,
        "notification_manager": notification_manager,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    async def handle_complete_task(call: ServiceCall) -> None:
        """Handle complete task service call."""
        plant_id = call.data[ATTR_PLANT_ID]
        task_id = call.data[ATTR_TASK_ID]

        for entry_data in hass.data[DOMAIN].values():
            coordinator = entry_data.get("coordinator")
            if coordinator and plant_id in coordinator.data:
                await coordinator.async_complete_task(plant_id, task_id)
                return

        _LOGGER.error("Plant not found: %s", plant_id)

    async def handle_set_growth_stage(call: ServiceCall) -> None:
        """Handle set growth stage service call."""
        plant_id = call.data[ATTR_PLANT_ID]
        stage_id = call.data["stage_id"]

        for entry_data in hass.data[DOMAIN].values():
            coordinator = entry_data.get("coordinator")
            if coordinator and plant_id in coordinator.data:
                await coordinator.async_set_growth_stage(plant_id, stage_id)
                return

        _LOGGER.error("Plant not found: %s", plant_id)

    hass.services.async_register(
        DOMAIN,
        SERVICE_COMPLETE_TASK,
        handle_complete_task,
        schema=SERVICE_COMPLETE_TASK_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_GROWTH_STAGE,
        handle_set_growth_stage,
        schema=SERVICE_SET_GROWTH_STAGE_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        notification_manager: NotificationManager = data["notification_manager"]
        await notification_manager.async_cleanup()

        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_COMPLETE_TASK)
            hass.services.async_remove(DOMAIN, SERVICE_SET_GROWTH_STAGE)

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: ConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    coordinator: PlantCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    plant_id = None
    for identifier in device_entry.identifiers:
        if identifier[0] == DOMAIN:
            plant_id = identifier[1]
            break

    if plant_id:
        await coordinator.async_remove_plant(plant_id)

    return True
