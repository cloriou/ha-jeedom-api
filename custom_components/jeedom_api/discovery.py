"""Shared discovery rules for Jeedom entities."""
from __future__ import annotations

LIGHT_TYPES = {"LIGHT_ON", "LIGHT_OFF", "LIGHT_STATE", "LIGHT_BRIGHTNESS", "LIGHT_SLIDER", "LIGHT_COLOR", "LIGHT_COLOR_TEMP"}
SWITCH_ON = {"ENERGY_ON", "SWITCH_ON", "GENERIC_ON", "HEATING_ON"}
SWITCH_OFF = {"ENERGY_OFF", "SWITCH_OFF", "GENERIC_OFF", "HEATING_OFF"}
SWITCH_STATE = {"ENERGY_STATE", "SWITCH_STATE", "GENERIC_STATE", "HEATING_STATE"}
COVER_OPEN = {"FLAP_OPEN", "FLAP_UP", "SHUTTER_OPEN", "SHUTTER_UP", "GARAGE_OPEN"}
COVER_CLOSE = {"FLAP_CLOSE", "FLAP_DOWN", "SHUTTER_CLOSE", "SHUTTER_DOWN", "GARAGE_CLOSE"}
COVER_STOP = {"FLAP_STOP", "SHUTTER_STOP", "GARAGE_STOP"}
COVER_POSITION = {"FLAP_STATE", "SHUTTER_STATE", "GARAGE_STATE"}
COVER_SET_POSITION = {"FLAP_SLIDER", "SHUTTER_SLIDER", "GARAGE_SLIDER"}
COVER_TYPES = COVER_OPEN | COVER_CLOSE | COVER_STOP | COVER_POSITION | COVER_SET_POSITION


def generic_types(equipment):
    return {cmd.generic_type for cmd in equipment.commands if cmd.generic_type}


def command_by_types(equipment, types):
    return next((cmd for cmd in equipment.commands if cmd.generic_type in types), None)


def is_light(equipment):
    types = generic_types(equipment)
    return bool(types & LIGHT_TYPES) and bool(types & {"LIGHT_ON", "LIGHT_OFF"})


def is_cover(equipment):
    return bool(generic_types(equipment) & COVER_TYPES)


def is_switch(equipment):
    if is_light(equipment) or is_cover(equipment):
        return False
    types = generic_types(equipment)
    return bool(types & SWITCH_ON) and bool(types & SWITCH_OFF)


def button_commands(equipment):
    consumed = LIGHT_TYPES | SWITCH_ON | SWITCH_OFF | SWITCH_STATE | COVER_TYPES
    ignored_names = {"lock", "unlock"}
    return [
        cmd
        for cmd in equipment.commands
        if cmd.type == "action"
        and cmd.subtype == "other"
        and cmd.generic_type not in consumed
        and cmd.name.strip().lower() not in ignored_names
    ]
