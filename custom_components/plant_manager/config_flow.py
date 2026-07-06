"""Config flow for Plant Manager integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_AI_API_KEY,
    CONF_AI_ENDPOINT,
    CONF_AI_MODEL,
    CONF_GROWTH_STAGE,
    CONF_PLANT_NAME,
    DEFAULT_AI_ENDPOINT,
    DEFAULT_AI_MODEL,
    DOMAIN,
)
from .coordinator import PlantCoordinator
from .openai_provider import OpenAIPlantInfoProvider

_LOGGER = logging.getLogger(__name__)


class PlantManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plant Manager."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle initial setup."""
        entries = self._async_current_entries()

        if not entries:
            return await self.async_step_ai_setup()

        return await self.async_step_add_plant()

    async def async_step_ai_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure AI provider."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                provider = OpenAIPlantInfoProvider(
                    api_key=user_input[CONF_AI_API_KEY],
                    endpoint=user_input.get(CONF_AI_ENDPOINT, DEFAULT_AI_ENDPOINT),
                    model=user_input.get(CONF_AI_MODEL, DEFAULT_AI_MODEL),
                )

                await provider.get_plant_profile("test basil")

                return self.async_create_entry(
                    title="Plant Manager",
                    data=user_input,
                )

            except Exception as err:
                _LOGGER.error("Failed to validate AI provider: %s", err)
                errors["base"] = "cannot_connect"

        schema = vol.Schema(
            {
                vol.Required(CONF_AI_API_KEY): str,
                vol.Optional(CONF_AI_ENDPOINT, default=DEFAULT_AI_ENDPOINT): str,
                vol.Optional(CONF_AI_MODEL, default=DEFAULT_AI_MODEL): str,
            }
        )

        return self.async_show_form(
            step_id="ai_setup",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "endpoint_example": "https://api.openai.com/v1",
                "model_example": "gpt-4o-mini",
            },
        )

    async def async_step_add_plant(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a new plant."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                entry = self._async_current_entries()[0]
                coordinator: PlantCoordinator = self.hass.data[DOMAIN][entry.entry_id][
                    "coordinator"
                ]

                plant = await coordinator.async_add_plant(user_input[CONF_PLANT_NAME])

                return self.async_create_entry(
                    title=plant.name,
                    data={CONF_PLANT_NAME: plant.name},
                )

            except Exception as err:
                _LOGGER.error("Failed to add plant: %s", err)
                errors["base"] = "cannot_add"

        schema = vol.Schema(
            {
                vol.Required(CONF_PLANT_NAME): str,
            }
        )

        return self.async_show_form(
            step_id="add_plant",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "name_example": "Monstera Deliciosa",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> PlantManagerOptionsFlow:
        """Get the options flow for this handler."""
        return PlantManagerOptionsFlow(config_entry)


class PlantManagerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Plant Manager."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        coordinator: PlantCoordinator = self.hass.data[DOMAIN][
            self.config_entry.entry_id
        ]["coordinator"]

        plants = list(coordinator.data.values())

        if not plants:
            return self.async_abort(reason="no_plants")

        plant_options = {plant.id: plant.name for plant in plants}

        if user_input is not None:
            plant_id = user_input.get("plant")
            if plant_id:
                return await self.async_step_change_stage(plant_id)

        schema = vol.Schema(
            {
                vol.Required("plant"): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            {"value": pid, "label": name}
                            for pid, name in plant_options.items()
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )

    async def async_step_change_stage(
        self, plant_id: str, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Change growth stage for a plant."""
        coordinator: PlantCoordinator = self.hass.data[DOMAIN][
            self.config_entry.entry_id
        ]["coordinator"]

        plant = coordinator.data.get(plant_id)
        if not plant:
            return self.async_abort(reason="plant_not_found")

        if user_input is not None:
            stage_id = user_input[CONF_GROWTH_STAGE]
            await coordinator.async_set_growth_stage(plant_id, stage_id)
            return self.async_create_entry(title="", data={})

        stage_options = [
            {"value": stage.id, "label": stage.name} for stage in plant.growth_stages
        ]

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_GROWTH_STAGE, default=plant.current_stage_id
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=stage_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="change_stage",
            data_schema=schema,
            description_placeholders={"plant_name": plant.name},
        )
