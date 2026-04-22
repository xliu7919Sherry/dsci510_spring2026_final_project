from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (EPA_EMAIL, EPA_KEY) from .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- Project directories ---
DATA_DIR = "../data"
RESULTS_DIR = "../results"
EPA_CSV_FILE = "../data/daily_aqi_by_county_2024.csv"
EPA_CSV_ZIP_FILE = "../data/daily_aqi_by_county_2024.zip"

# --- Study period ---
START_DATE = "2024-01-01"
END_DATE = "2024-06-30"

# --- EPA AQS API ---
EPA_API_URL = "https://aqs.epa.gov/data/api/dailyData/byCounty"
PARAM_CODE_PM25 = "88101"

# EPA uses FIPS codes: state + county
LOCATIONS = {
    "Los Angeles": {"state": "06", "county": "037"},
    "Houston":     {"state": "48", "county": "201"},
}

# Monthly chunks (EPA API is slow on long ranges, so we split the half-year into months)
MONTHS = [
    ("20240101", "20240131"),
    ("20240201", "20240229"),
    ("20240301", "20240331"),
    ("20240401", "20240430"),
    ("20240501", "20240531"),
    ("20240601", "20240630"),
]

# --- Open-Meteo Historical Weather API ---
OPENMETEO_API_URL = "https://archive-api.open-meteo.com/v1/archive"
WEATHER_DAILY_VARS = (
    "temperature_2m_mean,"
    "relative_humidity_2m_mean,"
    "wind_speed_10m_mean,"
    "precipitation_sum"
)

WEATHER_LOCATIONS = {
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
    "Houston":     {"lat": 29.7604, "lon": -95.3698},
}

# --- EPA AirData download URL ---
# AI generated:
EPA_AIRDATA_ZIP_URL = "https://aqs.epa.gov/aqsweb/airdata/daily_aqi_by_county_2024.zip"

# --- EPA AirData CSV (third data source, filtering) ---
# State/county names as they appear in the CSV file
CSV_COUNTY_FILTERS = {
    "Los Angeles": {"state_name": "California", "county_name": "Los Angeles"},
    "Houston":     {"state_name": "Texas",      "county_name": "Harris"},
}

# --- Modeling ---
TEST_SIZE = 0.2
RANDOM_STATE = 42
FEATURE_COLS = ["temperature", "humidity", "wind_speed", "precipitation"]
TARGET_COL = "pm25"

# --- Test configuration ---
TEST_STATE = "06"
TEST_COUNTY = "037"
TEST_BDATE = "20240101"
TEST_EDATE = "20240131"

TEST_LAT = 34.0522
TEST_LON = -118.2437
TEST_START_DATE = "2024-01-01"
TEST_END_DATE = "2024-01-31"