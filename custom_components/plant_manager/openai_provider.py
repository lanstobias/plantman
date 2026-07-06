"""OpenAI implementation of plant info provider."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from .ai_provider import PlantInfoProvider
from .models import PlantProfile

_LOGGER = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a plant care expert. When given a plant name, return ONLY valid JSON with complete care information.

The JSON must have this exact structure:
{
  "common_name": "string",
  "scientific_name": "string",
  "variety": "string",
  "description": "string (2-3 sentences)",
  "light_requirements": "string (e.g., 'Full sun 6-8 hours daily')",
  "temperature": "string (e.g., '65-75°F (18-24°C)')",
  "humidity": "string (e.g., '40-60%')",
  "soil": "string (e.g., 'Well-draining potting mix, pH 6.0-7.0')",
  "harvest_info": "string (or 'Not applicable' for non-edible plants)",
  "common_issues": "string (list 2-3 common problems)",
  "tasks": [
    {
      "id": "water",
      "name": "Water",
      "interval_days": 3
    },
    {
      "id": "fertilize",
      "name": "Fertilize",
      "interval_days": 14
    }
  ],
  "growth_stages": [
    {
      "id": "seedling",
      "name": "Seedling",
      "task_overrides": {
        "water": 2,
        "fertilize": 21
      }
    },
    {
      "id": "mature",
      "name": "Mature",
      "task_overrides": {}
    }
  ]
}

Include tasks like: water, fertilize, prune, mist, rotate, repot, pest_check, etc.
Include appropriate growth stages for the plant type (seedling, vegetative, flowering, etc.).
Task overrides should adjust intervals for specific growth stages (e.g., seedlings need more frequent watering).

Return ONLY the JSON, no other text."""


class OpenAIPlantInfoProvider(PlantInfoProvider):
    """OpenAI implementation of plant info provider."""

    def __init__(self, api_key: str, endpoint: str, model: str) -> None:
        """Initialize provider.

        Args:
            api_key: API key for authentication
            endpoint: API endpoint URL
            model: Model name to use
        """
        self._client = AsyncOpenAI(api_key=api_key, base_url=endpoint)
        self._model = model

    async def get_plant_profile(self, plant_name: str) -> PlantProfile:
        """Get plant profile from OpenAI."""
        _LOGGER.debug("Querying OpenAI for plant: %s", plant_name)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Provide care information for: {plant_name}"},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from AI")

            _LOGGER.debug("Received AI response: %s", content[:200])

            data = json.loads(content)

            self._validate_response(data)

            return PlantProfile.from_dict(data)

        except json.JSONDecodeError as err:
            _LOGGER.error("Failed to parse AI response as JSON: %s", err)
            raise ValueError(f"Invalid JSON response from AI: {err}") from err
        except Exception as err:
            _LOGGER.error("Failed to get plant profile: %s", err)
            raise

    def _validate_response(self, data: dict[str, Any]) -> None:
        """Validate AI response structure."""
        required_fields = [
            "common_name",
            "scientific_name",
            "variety",
            "description",
            "light_requirements",
            "temperature",
            "humidity",
            "soil",
            "harvest_info",
            "common_issues",
            "tasks",
            "growth_stages",
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(data["tasks"], list) or len(data["tasks"]) == 0:
            raise ValueError("Tasks must be a non-empty list")

        for task in data["tasks"]:
            if not all(k in task for k in ["id", "name", "interval_days"]):
                raise ValueError(f"Invalid task structure: {task}")

        if not isinstance(data["growth_stages"], list):
            raise ValueError("Growth stages must be a list")

        for stage in data["growth_stages"]:
            if not all(k in stage for k in ["id", "name"]):
                raise ValueError(f"Invalid growth stage structure: {stage}")
