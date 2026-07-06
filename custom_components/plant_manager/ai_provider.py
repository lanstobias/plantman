"""Abstract AI provider interface for Plant Manager."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .models import PlantProfile


class PlantInfoProvider(ABC):
    """Abstract interface for AI plant information providers."""

    @abstractmethod
    async def get_plant_profile(self, plant_name: str) -> PlantProfile:
        """Get plant profile from AI.

        Args:
            plant_name: Name of the plant to query

        Returns:
            PlantProfile with complete information

        Raises:
            Exception: If AI query fails
        """
