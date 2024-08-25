"""Holding Constants for Direct4Me."""

import logging

_LOGGER = logging.getLogger(__package__)
DOMAIN = "direct4me"
STORAGE_KEY = f"{DOMAIN}_token"
STORAGE_VERSION = 1

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DEVICE_ID = "device_id"
CONF_UPDATE_INTERVAL = "update_interval"
