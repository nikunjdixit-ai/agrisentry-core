"""
Central configuration for AgriSentry Member 3 modules.

Contains:
- Open-Meteo configuration
- Default agricultural coordinates
- NDVI thresholds
- LoRaWAN settings
- MQTT settings
- Supported languages and TTS voices
"""



DEFAULT_LATITUDE = 26.8467
DEFAULT_LONGITUDE = 80.9462

DEFAULT_LOCATION_NAME = "Lucknow-Barabanki Agricultural Region"




OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

OPEN_METEO_TIMEOUT = 10

OPEN_METEO_RETRIES = 3

OPEN_METEO_HOURLY_VARIABLES = [
    "soil_temperature_0_to_7cm",
    "soil_moisture_0_to_7cm",
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
]




NDVI_HEALTHY_THRESHOLD = 0.60
NDVI_MODERATE_THRESHOLD = 0.30

NDVI_HEALTHY_LABEL = "Dense / Healthy Canopy"
NDVI_MODERATE_LABEL = "Moderate / Developing Vegetation"
NDVI_STRESSED_LABEL = "Stressed / Sparse Canopy or Bare Soil"




LORAWAN_FREQUENCY_MIN = 865
LORAWAN_FREQUENCY_MAX = 867

SPREADING_FACTORS = [7, 8, 9, 10, 11, 12]

RSSI_MIN = -115
RSSI_MAX = -80

SNR_MIN = 6
SNR_MAX = 12




DEFAULT_GATEWAY_ID = "GW-UP-BARABANKI-01"

DEFAULT_SENSOR_NODES = [
    "FARM-NODE-01",
    "FARM-NODE-02",
    "FARM-NODE-03",
]



MQTT_HOST = "localhost"
MQTT_PORT = 1883

MQTT_TOPIC = "agrisentry/telemetry"

MQTT_CONNECT_TIMEOUT = 3



SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "mr": "Marathi",
    "bn": "Bengali",
    "en": "Indian English",
}



TTS_VOICES = {
    "hi": "hi-IN-MadhurNeural",
    "mr": "mr-IN-AarohiNeural",
    "bn": "bn-IN-BashkarNeural",
    "en": "en-IN-NeerjaNeural",
}


DEFAULT_LANGUAGE = "hi"
DEFAULT_TTS_VOICE = TTS_VOICES[DEFAULT_LANGUAGE]


SUPPORTED_AUDIO_FORMATS = [
    ".ogg",
    ".wav",
    ".mp3",
    ".m4a",
]

VOICE_OUTPUT_DIRECTORY = "voice_outputs"


SIMULATION_MODE = True

ENABLE_NETWORK_APIS = True

ENABLE_MQTT = True

ENABLE_WHISPER = True

ENABLE_EDGE_TTS = True