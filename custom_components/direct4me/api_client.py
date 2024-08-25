import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)


class Direct4meApiClient:
    def __init__(self, username, password, device_id, session, store, stored_data):
        self.base_url = "https://api.direct4.me/MobileApp/v3/api"
        self.username = username
        self.password = password
        self.device_id = device_id
        self._session = session
        self._store = store
        self.auth_token = stored_data.get("auth_token") if stored_data else None

    async def ensure_logged_in(self):
        """Ensure the user is logged in. Re-login if the token is invalid or missing."""
        if self.auth_token:
            if await self.is_token_valid():
                return True
            _LOGGER.info("Token invalid, re-logging in.")

        return await self.login()

    async def is_token_valid(self):
        """Check if the current token is valid."""
        url = "https://api.direct4.me/main/v1/signin/token"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "DeviceId": self.device_id,
            "Version-Code": "464",
            "Version-Name": "1.51.10",
            "User-Agent": "Direct4.me/464 CFNetwork/1496.0.7 Darwin/23.5.0",
            "Content-Type": "application/json",
        }

        async with self._session.post(url, headers=headers, json={}) as response:
            if response.status == 200:
                _LOGGER.debug("Token is still valid.")
                return True
            _LOGGER.warning("Token is invalid, status code: %s", response.status)
            return False

    async def login(self):
        """Login and obtain a new token."""
        url = f"{self.base_url}/user/SignOn"
        headers = {
            "Content-Type": "application/json",
            "Host": "api.direct4.me",
            "DeviceId": self.device_id,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "User-Agent": "Direct4.me/464 CFNetwork/1496.0.7 Darwin/23.5.0",
            "Version": "1.51.10",
        }
        payload = {"Username": self.username, "Password": self.password}

        _LOGGER.debug("Attempting to log in to Direct4me API")
        async with self._session.post(url, headers=headers, json=payload) as response:
            if response.status != 200:
                _LOGGER.error("Login failed with status code: %s", response.status)
                return False

            response_json = await response.json()
            if response_json.get("Result") != 0:
                _LOGGER.error(
                    "Login failed: %s", response_json.get("Message", "Unknown error")
                )
                return False

            self.auth_token = response_json.get("Data")
            _LOGGER.debug("Login successful, token: %s", self.auth_token)

            # Store the new token
            await self._store.async_save({"auth_token": self.auth_token})

            return True

    async def get_deliveries(self):
        """Fetch deliveries from the API."""
        if not self.auth_token:
            _LOGGER.error("Not authenticated. Please call login() first.")
            return None

        url = f"{self.base_url}/delivery/GetDeliveries"
        headers = {
            "Language": "sr",
            "BundleId": "me.direct4.customer",
            "Platform": "iOS",
            "Version-Name": "1.51.10",
            "Version-Code": "464",
            "Authorization": f"Bearer {self.auth_token}",
            "Version": "1.51.10",
            "User-Agent": "Direct4.me/464 CFNetwork/1496.0.7 Darwin/23.5.0",
            "DeviceId": self.device_id,
            "Accept": "*/*",
            "Host": "api.direct4.me",
            "VersionSDK": "0.0.1",
            "Accept-Language": "sr",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
        }

        _LOGGER.debug("Fetching deliveries from Direct4me API")
        async with self._session.get(
            url, headers=headers, params={"includeTransporterDeliveries": "True"}
        ) as response:
            if response.status != 200:
                _LOGGER.error(
                    "Failed to fetch deliveries with status code: %s", response.status
                )
                return None

            deliveries = await response.json()
            _LOGGER.debug("Deliveries received: %s", deliveries)
            return deliveries
