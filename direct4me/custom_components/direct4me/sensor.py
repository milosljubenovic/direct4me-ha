"""Platform for sensor integration."""

from datetime import datetime
import logging

from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Direct4me sensor platform."""
    client = hass.data.get("direct4me")
    if not client:
        _LOGGER.error("No Direct4me client found.")
        return

    # Fetch initial data
    await client.ensure_logged_in()
    deliveries = await client.get_deliveries()

    if deliveries:
        upcoming_deliveries = []
        received_deliveries = []
        today_deliveries = []
        logs = []  # Assuming logs are part of the delivery data or a separate API call

        current_date = datetime.utcnow().date()

        for delivery in deliveries.get("Data", []):
            delivery_date = datetime.fromisoformat(
                delivery.get("Date").split("T")[0]
            ).date()

            if delivery.get("FlagPackageHandled"):
                received_deliveries.append(delivery)
            else:
                upcoming_deliveries.append(delivery)

            if delivery_date == current_date:
                today_deliveries.append(delivery)

            # Assuming logs are stored in delivery or fetched separately
            logs.append(delivery)  # Modify as needed if logs are separate

        async_add_entities(
            [
                Direct4meDeliverySensor(
                    client, "Upcoming Packages", upcoming_deliveries
                ),
                Direct4meDeliverySensor(
                    client, "Received Packages", received_deliveries
                ),
                Direct4meDeliverySensor(client, "Today's Arrivals", today_deliveries),
                Direct4meLogSensor(client, "Delivery Logs", logs),
            ],
            True,
        )


class Direct4meDeliverySensor(Entity):
    """Representation of a Direct4me sensor."""

    def __init__(self, client, name, deliveries) -> None:
        """Initialize the sensor."""
        self._client = client
        self._name = name
        self._deliveries = deliveries

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"Direct4me {self._name}"

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        return len(self._deliveries)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            "Deliveries": [
                {
                    "Box Name": delivery["BoxName"],
                    "Company": delivery["CompanyName"],
                    "Delivery Date": delivery["Date"],
                    "To User": delivery["ToUserDisplayName"],
                    "From User": delivery["FromUserDisplayName"],
                    "Location": f"{delivery['BoxArrayAddress']}, {delivery['BoxArrayCity']}",
                    "Tracking Number": delivery["TrackingNumber"],
                    "Reserved To": delivery["ReservedTo"],
                    "Authorised From": delivery["AuthorisedFrom"],
                    "Authorised To": delivery["AuthorisedTo"],
                    "Last Access": delivery["LastAccess"],
                }
                for delivery in self._deliveries
            ]
        }

    async def async_update(self) -> None:
        """Update the sensor."""
        deliveries = await self._client.get_deliveries()
        if deliveries:
            self._deliveries = [
                d for d in deliveries.get("Data", []) if self._filter_delivery(d)
            ]

    def _filter_delivery(self, delivery):
        """Filter deliveries based on the sensor type."""
        current_date = datetime.utcnow().date()
        delivery_date = datetime.fromisoformat(
            delivery.get("Date").split("T")[0]
        ).date()

        if self._name == "Upcoming Packages" and not delivery.get("FlagPackageHandled"):
            return True
        if self._name == "Received Packages" and delivery.get("FlagPackageHandled"):
            return True
        if self._name == "Today's Arrivals" and delivery_date == current_date:
            return True
        return False


class Direct4meLogSensor(Entity):
    """Representation of a Direct4me sensor for logs."""

    def __init__(self, client, name, logs) -> None:
        """Initialize the sensor."""
        self._client = client
        self._name = name
        self._logs = logs

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"Direct4me {self._name}"

    @property
    def state(self) -> int:
        """Return the state of the sensor."""
        return len(self._logs)

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {"Logs": self._logs}

    async def async_update(self) -> None:
        """Update the sensor."""
        # Update logs - modify as needed to reflect log handling
        logs = (
            await self._client.get_deliveries()
        )  # Or another API call if logs are separate
        if logs:
            self._logs = logs.get("Data", [])
