"""Notification manager for Plant Manager."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components import persistent_notification
from homeassistant.core import HomeAssistant, callback

from .const import NOTIFICATION_ID_PREFIX

if TYPE_CHECKING:
    from .coordinator import PlantCoordinator
    from .models import Plant, Task

_LOGGER = logging.getLogger(__name__)


class NotificationManager:
    """Manage overdue task notifications."""

    def __init__(self, hass: HomeAssistant, coordinator: PlantCoordinator) -> None:
        """Initialize notification manager."""
        self._hass = hass
        self._coordinator = coordinator
        self._active_notifications: set[str] = set()

        self._coordinator.async_add_listener(self._async_update_notifications)

    @callback
    def _async_update_notifications(self) -> None:
        """Update notifications based on current plant state."""
        if not self._coordinator.data:
            return

        current_overdue: set[str] = set()

        for plant in self._coordinator.data.values():
            for task in plant.tasks:
                if task.is_overdue():
                    notification_id = self._get_notification_id(plant.id, task.id)
                    current_overdue.add(notification_id)

                    if notification_id not in self._active_notifications:
                        self._create_notification(plant, task)
                        self._active_notifications.add(notification_id)

        to_remove = self._active_notifications - current_overdue

        for notification_id in to_remove:
            self._remove_notification(notification_id)
            self._active_notifications.discard(notification_id)

    def _create_notification(self, plant: Plant, task: Task) -> None:
        """Create a notification for an overdue task."""
        notification_id = self._get_notification_id(plant.id, task.id)

        days_overdue = 0
        if task.last_completed:
            days_since = task.days_since_completed()
            if days_since:
                days_overdue = days_since - task.interval_days

        message = f"**{plant.name}** needs {task.name.lower()}."
        if days_overdue > 0:
            message += f" Overdue by {days_overdue} day(s)."

        persistent_notification.async_create(
            self._hass,
            message=message,
            title=f"Plant Care: {task.name}",
            notification_id=notification_id,
        )

        _LOGGER.debug(
            "Created notification for %s - %s (%s)",
            plant.name,
            task.name,
            notification_id,
        )

    def _remove_notification(self, notification_id: str) -> None:
        """Remove a notification."""
        persistent_notification.async_dismiss(self._hass, notification_id)
        _LOGGER.debug("Removed notification: %s", notification_id)

    @staticmethod
    def _get_notification_id(plant_id: str, task_id: str) -> str:
        """Generate notification ID."""
        return f"{NOTIFICATION_ID_PREFIX}{plant_id}_{task_id}"

    async def async_cleanup(self) -> None:
        """Clean up all notifications on unload."""
        for notification_id in list(self._active_notifications):
            self._remove_notification(notification_id)
        self._active_notifications.clear()
