"""The Direct4me component."""

from datetime import timedelta

import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import aiohttp
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.storage import Store
from homeassistant.util.dt import parse_time

from .api_client import Direct4meApiClient
from .const import (
    _LOGGER,
    CONF_DEVICE_ID,
    CONF_PASSWORD,
    CONF_UPDATE_INTERVAL,
    CONF_USERNAME,
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
)


def validate_time(value):
    """Validate that the input is in hh:mm:ss format."""
    try:
        return parse_time(value).strftime("%H:%M:%S")
    except ValueError:
        raise vol.Invalid("Invalid time format, expected hh:mm:ss")  # noqa: B904


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_DEVICE_ID, default="HomeAssistant"): cv.string,
                vol.Optional(CONF_UPDATE_INTERVAL, default="01:00:00"): vol.All(
                    cv.string, validate_time
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the Direct4me component."""
    conf = config[DOMAIN]

    username = conf[CONF_USERNAME]
    password = conf[CONF_PASSWORD]
    device_id = conf[CONF_DEVICE_ID]
    update_interval_str = conf[CONF_UPDATE_INTERVAL]

    # Parse the update interval
    update_interval = timedelta(
        hours=parse_time(update_interval_str).hour,
        minutes=parse_time(update_interval_str).minute,
        seconds=parse_time(update_interval_str).second,
    )

    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    stored_data = await store.async_load()

    session = aiohttp.ClientSession()

    client = Direct4meApiClient(
        username, password, device_id, session, store, stored_data
    )

    if not await client.ensure_logged_in():
        _LOGGER.error("Failed to authenticate with Direct4me API")
        return False

    hass.data[DOMAIN] = client

    # Load the sensor platform
    hass.async_create_task(async_load_platform(hass, "sensor", DOMAIN, {}, config))

    # Schedule the periodic update
    async def async_update_data(_):
        await client.get_deliveries()

    hass.helpers.event.async_track_time_interval(async_update_data, update_interval)

    return True
