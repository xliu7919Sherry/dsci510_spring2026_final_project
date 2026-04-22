import os
import zipfile
import requests
import pandas as pd
from config import (
    EPA_API_URL,
    OPENMETEO_API_URL,
    WEATHER_DAILY_VARS,
    EPA_CSV_FILE,
    EPA_CSV_ZIP_FILE,
    EPA_AIRDATA_ZIP_URL,
    DATA_DIR,
)

# --- 1. EPA AQS API: daily pollutant data by county ---

def get_epa_pm25_daily(email, key, param_code, state, county, bdate, edate):
    """
    Download one month of daily pollutant data from the EPA AQS API.

    :param email: EPA account email
    :param key: EPA API key
    :param param_code: AQS parameter code (e.g., 88101 for PM2.5)
    :param state: State FIPS code (e.g., '06' for California)
    :param county: County FIPS code
    :param bdate: Begin date in YYYYMMDD format
    :param edate: End date in YYYYMMDD format
    :return: pandas DataFrame (empty if request failed)
    """
    url = (
        f"{EPA_API_URL}"
        f"?email={email}"
        f"&key={key}"
        f"&param={param_code}"
        f"&bdate={bdate}"
        f"&edate={edate}"
        f"&state={state}"
        f"&county={county}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"EPA request failed: {response.status_code}")
        print(f"  response body: {response.text[:500]}")
        return pd.DataFrame()

    data = response.json()

    if "Data" not in data:
        print(f"No 'Data' field in EPA response. Header: {data.get('Header')}")
        return pd.DataFrame()

    return pd.DataFrame(data["Data"])


# --- 2. Open-Meteo API: daily historical weather ---

def get_openmeteo_weather(lat, lon, start_date, end_date):
    """
    Download daily weather variables for a location from the Open-Meteo
    Historical Weather API.

    :param lat: Latitude
    :param lon: Longitude
    :param start_date: Start date in YYYY-MM-DD format
    :param end_date: End date in YYYY-MM-DD format
    :return: pandas DataFrame (empty if request failed)
    """
    url = (
        f"{OPENMETEO_API_URL}"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        f"&daily={WEATHER_DAILY_VARS}"
        "&timezone=auto"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Weather request failed: {response.status_code}")
        return pd.DataFrame()

    data = response.json()

    if "daily" not in data:
        print("No daily weather data found.")
        return pd.DataFrame()

    return pd.DataFrame(data["daily"])

# --- 3. Ensure EPA AirData CSV exists locally ---

def ensure_epa_airdata_csv(csv_path=EPA_CSV_FILE, zip_path=EPA_CSV_ZIP_FILE):
    """
    Make sure the EPA AirData CSV exists locally.
    If not, download the ZIP from EPA and extract it into the data folder.

    :param csv_path: Local path to the target CSV
    :param zip_path: Local path to the downloaded ZIP
    :return: Path to the CSV file
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(csv_path):
        print("EPA AirData CSV already exists.")
        return csv_path

    print("EPA AirData CSV not found locally.")
    print("Downloading EPA AirData ZIP...")

    response = requests.get(EPA_AIRDATA_ZIP_URL)
    response.raise_for_status()

    with open(zip_path, "wb") as f:
        f.write(response.content)

    print("Download complete. Extracting ZIP...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(DATA_DIR)

    print("EPA AirData CSV downloaded and extracted.")
    return csv_path

# --- 4. EPA AirData historical CSV file ---

def load_epa_airdata_csv(path=EPA_CSV_FILE):
    """
    Load the EPA AirData 'daily AQI by county' CSV file from disk.
    If it does not exist locally, download and extract it automatically.

    :param path: Path to the CSV file
    :return: pandas DataFrame (empty if file read failed)
    """
    try:
        ensure_epa_airdata_csv(path)
        df = pd.read_csv(path)
        print(f"Loaded EPA AirData CSV: {len(df)} rows")
        return df
    except Exception as e:
        print(f"Error loading EPA CSV: {e}")
        return pd.DataFrame()
