import logging
from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceEntryType

from .const import ATTRIBUTION, COORDINATOR, DOMAIN, MANUFACTURER

PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)

FORECAST_TIME = "datetime"
FORECAST_CONDITION = "condition"
FORECAST_TEMP = "temperature"
FORECAST_TEMP_LOW = "templow"
FORECAST_WIND_BEARING = "wind_bearing"
FORECAST_WIND_SPEED = "wind_speed"
FORECAST_PRECIPITATION = "precipitation"
FORECAST_HUMIDITY = "humidity"
FORECAST_CLOUD_COVERAGE = "cloud_coverage"
FORECAST_PRESSURE = "pressure"
FORECAST_VISIBILITY = "visibility"

CONDITION_MAP = {
    "CLEAR_DAY": "sunny",
    "CLEAR_NIGHT": "clear-night",
    "PARTLY_CLOUDY_DAY": "partlycloudy",
    "PARTLY_CLOUDY_NIGHT": "partlycloudy",
    "CLOUDY": "cloudy",
    "LIGHT_HAZE": "fog",
    "MODERATE_HAZE": "fog",
    "HEAVY_HAZE": "fog",
    "LIGHT_RAIN": "rainy",
    "MODERATE_RAIN": "rainy",
    "HEAVY_RAIN": "pouring",
    "STORM_RAIN": "pouring",
    "FOG": "fog",
    "LIGHT_SNOW": "snowy",
    "MODERATE_SNOW": "snowy",
    "HEAVY_SNOW": "snowy",
    "STORM_SNOW": "snowy",
    "DUST": "fog",
    "SAND": "fog",
    "THUNDER_SHOWER": "lightning-rainy",
    "HAIL": "hail",
    "SLEET": "snowy-rainy",
    "WIND": "windy",
    "HAZE": "fog",
    "RAIN": "rainy",
    "SNOW": "snowy",
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a Colorfulclouds weather entity from a config_entry."""
    name = config_entry.data[CONF_NAME]

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    # _LOGGER.debug("metric: %s", coordinator.data["is_metric"])

    async_add_entities([ColorfulCloudsEntity(name, coordinator)], True)


class ColorfulCloudsEntity(WeatherEntity):
    """Representation of a weather condition."""

    # _attr_translation_key = "nmc"
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_DAILY
        # | WeatherEntityFeature.FORECAST_TWICE_DAILY
    )

    def __init__(self, name, coordinator):
        self.coordinator = coordinator
        _LOGGER.debug("coordinator: %s", coordinator.data["server_time"])
        self._name = name
        self._attrs = {}
        self._unit_system = (
            "Metric"
            if self.coordinator.data["is_metric"] == "metric"
            else "Imperial"
        )

    @property
    def name(self):
        return self._name

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        _LOGGER.debug("weather_unique_id: %s", self.coordinator.data["location_key"])
        return self.coordinator.data["location_key"]

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.data["location_key"])},
            "name": self._name,
            "manufacturer": MANUFACTURER,
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def state(self):
        """Return the weather condition."""
        skycon = self.coordinator.data["result"]["realtime"]["skycon"]
        return CONDITION_MAP.get(skycon)

    @property
    def cloud_coverage(self):
        return self.coordinator.data["result"]["realtime"]["cloudrate"]

    @property
    def condition(self):
        """Return the weather condition."""
        skycon = self.coordinator.data["result"]["realtime"]["skycon"]
        return CONDITION_MAP.get(skycon)

    @property
    def humidity(self):
        return float(self.coordinator.data["result"]["realtime"]["humidity"]) * 100

    @property
    def native_apparent_temperature(self):
        return self.coordinator.data["result"]["realtime"]["apparent_temperature"]

    @property
    def native_precipitation_unit(self):
        return "mm" if self.coordinator.data["is_metric"] == "metric" else "in"

    @property
    def native_pressure(self):
        return self.coordinator.data["result"]["realtime"]["pressure"]

    @property
    def native_pressure_unit(self):
        return "Pa"

    @property
    def native_temperature(self):
        return self.coordinator.data["result"]["realtime"]["temperature"]

    @property
    def native_temperature_unit(self):
        return "°C" if self.coordinator.data["is_metric"] == "metric" else "°F"

    @property
    def native_visibility(self):
        """能见度"""
        return self.coordinator.data["result"]["realtime"]["visibility"]

    @property
    def native_visibility_unit(self):
        return "km" if self.coordinator.data["is_metric"] == "metric" else "mi"

    @property
    def native_wind_speed(self):
        """风速"""
        return self.coordinator.data["result"]["realtime"]["wind"]["speed"]

    @property
    def wind_bearing(self):
        """风向"""
        return self.coordinator.data["result"]["realtime"]["wind"]["direction"]

    @property
    def native_wind_speed_unit(self):
        return "km/h" if self.coordinator.data["is_metric"] == "metric" else "mi/h"

    @property
    def uv_index(self):
        """紫外线"""
        return self.coordinator.data["result"]["realtime"]["life_index"]["ultraviolet"][
            "index"
        ]

    @property
    def extra_state_attributes(self):
        self._attrs = {
            "skycon": self.coordinator.data["result"]["realtime"]["skycon"],
            "forecast_hourly": self.coordinator.data["result"]["hourly"]["description"],
            "forecast_minutely": self.coordinator.data["result"]["minutely"][
                "description"
            ]
            if "minutely" in self.coordinator.data["result"]
            else "",
            "forecast_probability": self.coordinator.data["result"]["minutely"][
                "probability"
            ]
            if "minutely" in self.coordinator.data["result"]
            else "",
            "forecast_keypoint": self.coordinator.data["result"]["forecast_keypoint"],
            "forecast_alert": self.coordinator.data["result"]["alert"]
            if "alert" in self.coordinator.data["result"]
            else "",
            "pm25": self.coordinator.data["result"]["realtime"]["air_quality"]["pm25"],
            "pm10": self.coordinator.data["result"]["realtime"]["air_quality"]["pm10"],
            "o3": self.coordinator.data["result"]["realtime"]["air_quality"]["o3"],
            "no2": self.coordinator.data["result"]["realtime"]["air_quality"]["no2"],
            "so2": self.coordinator.data["result"]["realtime"]["air_quality"]["so2"],
            "co": self.coordinator.data["result"]["realtime"]["air_quality"]["co"],
            "aqi": self.coordinator.data["result"]["realtime"]["air_quality"]["aqi"][
                "chn"
            ],
            "aqi_description": self.coordinator.data["result"]["realtime"][
                "air_quality"
            ]["description"]["chn"],
            "aqi_usa": self.coordinator.data["result"]["realtime"]["air_quality"][
                "aqi"
            ]["usa"],
            "aqi_usa_description": self.coordinator.data["result"]["realtime"][
                "air_quality"
            ]["description"]["usa"],
        }
        return self._attrs

    def get_nested_attr(obj, attr, default_value=None):
        attrs = attr.split(".")
        for a in attrs:
            obj = getattr(obj, a, default_value)
            if obj == default_value:
                break
        return obj

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
        # await self.async_update_listeners({"daily", "hourly"})

    async def update_from_client(self):
        self.async_write_ha_state()

    async def async_update(self):
        """Update Colorfulclouds entity."""
        await self.coordinator.async_request_refresh()
        # self.async_write_ha_state()

    async def async_forecast_daily(self) -> list[Forecast] | None:
        daily = self.coordinator.data["result"]["daily"]
        forecast_data = []
        for i in range(len(daily["temperature"])):
            time_str = daily["temperature"][i]["date"]
            data_dict = {
                FORECAST_TIME: time_str,
                "skycon": daily["skycon"][i]["value"],
                FORECAST_CONDITION: CONDITION_MAP.get(daily["skycon"][i]["value"]),
                FORECAST_TEMP: daily["temperature"][i]["max"],
                FORECAST_TEMP_LOW: daily["temperature"][i]["min"],
                FORECAST_WIND_BEARING: daily["wind"][i]["avg"]["direction"],
                FORECAST_WIND_SPEED: daily["wind"][i]["avg"]["speed"],
                FORECAST_PRECIPITATION: daily["precipitation"][i]["avg"],
                FORECAST_HUMIDITY: daily["humidity"][i]["avg"],
                FORECAST_CLOUD_COVERAGE: daily["cloudrate"][i]["avg"],
                FORECAST_PRESSURE: daily["pressure"][i]["avg"],
                FORECAST_VISIBILITY: daily["visibility"][i]["avg"],
            }
            forecast_data.append(data_dict)

        return forecast_data

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        hourly = self.coordinator.data["result"]["hourly"]
        forecast_data = []
        for i in range(len(hourly["temperature"])):
            time_str = hourly["temperature"][i]["datetime"]
            data_dict = {
                FORECAST_TIME: time_str,
                "skycon": hourly["skycon"][i]["value"],
                FORECAST_CONDITION: CONDITION_MAP.get(hourly["skycon"][i]["value"]),
                FORECAST_TEMP: hourly["temperature"][i]["value"],
                FORECAST_WIND_BEARING: hourly["wind"][i]["direction"],
                FORECAST_WIND_SPEED: hourly["wind"][i]["speed"],
                FORECAST_PRECIPITATION: hourly["precipitation"][i]["value"],
                FORECAST_HUMIDITY: hourly["humidity"][i]["value"],
                FORECAST_CLOUD_COVERAGE: hourly["cloudrate"][i]["value"],
                FORECAST_PRESSURE: hourly["pressure"][i]["value"],
                FORECAST_VISIBILITY: hourly["visibility"][i]["value"],
            }
            forecast_data.append(data_dict)
        return forecast_data
