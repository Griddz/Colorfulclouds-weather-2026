import datetime
import logging

from aiohttp import ClientError
from async_timeout import timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.unit_system import METRIC_SYSTEM
from homeassistant.util.json import json_loads

_LOGGER = logging.getLogger(__name__)
from .const import DOMAIN


class ColorfulcloudsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Colorfulclouds data API."""

    def __init__(
        self,
        hass,
        websession,
        api_key,
        api_version,
        location_key,
        longitude,
        latitude,
        dailysteps: int,
        hourlysteps: int,
        alert: bool,
        starttime: int,
        interval: int,
    ):
        """Initialize."""
        self.location_key = location_key
        self.longitude = longitude
        self.latitude = latitude
        self.dailysteps = dailysteps
        self.alert = alert
        self.interval = interval
        self.hourlysteps = hourlysteps
        self.api_version = api_version
        self.api_key = api_key
        self.starttime = starttime
        self.websession = websession
        self.is_metric = "metric"
        if hass.config.units is METRIC_SYSTEM:
            self.is_metric = "metric"
        else:
            self.is_metric = "imperial"

        update_interval = datetime.timedelta(minutes=self.interval)
        _LOGGER.debug("Data will be update every %s", update_interval)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with timeout(10):
                url = str.format(
                    "https://api.caiyunapp.com/{}/{}/{},{}/weather?dailysteps={}&hourlysteps={}&alert={}&unit={}",
                    self.api_version,
                    self.api_key,
                    self.longitude,
                    self.latitude,
                    self.dailysteps,
                    self.hourlysteps,
                    str(self.alert).lower(),
                    self.is_metric,
                )
                _LOGGER.warning("Colorfulclouds request URL: %s", url)
                async with self.websession.get(url) as response:
                    response.raise_for_status()
                    resdata = json_loads(await response.text())
                _LOGGER.warning("Colorfulclouds raw response: %s", resdata)

                if resdata.get("status") != "ok":
                    raise UpdateFailed(
                        f"Caiyun API returned non-ok status: {resdata.get('status')}"
                    )
        except (ClientError, TimeoutError, ValueError) as error:
            raise UpdateFailed(error)
        _LOGGER.debug("Requests remaining: %s", url)
        return {
            **resdata,
            "location_key": self.location_key,
            "is_metric": self.is_metric,
        }
