"""Config and options flows."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, selector

from .api import JeedomApi, JeedomApiError, JeedomAuthenticationError
from .const import (
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_SELECTED_EQUIPMENT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .models import parse_full_data


class JeedomApiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set up Jeedom API."""

    VERSION = 1

    def __init__(self) -> None:
        self._connection: dict[str, Any] = {}
        self._equipment: dict[str, Any] = {}

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")
            api_key = user_input[CONF_API_KEY]
            api = JeedomApi(self.hass, url, api_key)
            try:
                self._equipment = parse_full_data(await api.async_get_full_data())
            except JeedomAuthenticationError:
                errors["base"] = "invalid_auth"
            except JeedomApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(url.lower())
                self._abort_if_unique_id_configured()
                self._connection = {CONF_URL: url, CONF_API_KEY: api_key}
                return await self.async_step_select()

        schema = vol.Schema(
            {
                vol.Required(CONF_URL, default="http://jeedom-master.local"): str,
                vol.Required(CONF_API_KEY): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_select(self, user_input=None):
        choices = {
            eq_id: equipment.label
            for eq_id, equipment in sorted(
                self._equipment.items(), key=lambda item: item[1].label.lower()
            )
            if equipment.commands
        }
        if user_input is not None:
            return self.async_create_entry(
                title="Jeedom",
                data=self._connection,
                options={
                    CONF_SELECTED_EQUIPMENT: user_input[CONF_SELECTED_EQUIPMENT],
                    CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_SELECTED_EQUIPMENT, default=[]):
                    cv.multi_select(choices)
            }
        )
        return self.async_show_form(step_id="select", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return JeedomOptionsFlow()


class JeedomOptionsFlow(config_entries.OptionsFlow):
    """Change imported equipment and polling interval."""

    async def async_step_init(self, user_input=None):
        errors = {}
        api = JeedomApi(
            self.hass,
            self.config_entry.data[CONF_URL],
            self.config_entry.data[CONF_API_KEY],
        )
        try:
            equipment = parse_full_data(await api.async_get_full_data())
        except JeedomApiError:
            equipment = {}
            errors["base"] = "cannot_connect"

        choices = {
            eq_id: item.label
            for eq_id, item in sorted(
                equipment.items(), key=lambda value: value[1].label.lower()
            )
            if item.commands
        }
        current = self.config_entry.options.get(CONF_SELECTED_EQUIPMENT, [])
        current = [eq_id for eq_id in current if eq_id in choices]

        if user_input is not None and not errors:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_SELECTED_EQUIPMENT, default=current):
                    cv.multi_select(choices),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        step=1,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="s",
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
