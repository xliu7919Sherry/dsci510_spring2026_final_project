import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("EPA_EMAIL")
key = os.getenv("EPA_KEY")

if not email or not key:
    raise ValueError("EPA credentials not found. Please check your .env file.")

start_date = "2024-01-01"
end_date = "2024-06-30"
param_code = "88101"

locations = {
    "Los Angeles": {"state": "06", "county": "037"},
    "Houston": {"state": "48", "county": "201"}
}

weather_locations = {
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
    "Houston": {"lat": 29.7604, "lon": -95.3698}
}

months = [
    ("20240101", "20240131"),
    ("20240201", "20240229"),
    ("20240301", "20240331"),
    ("20240401", "20240430"),
    ("20240501", "20240531"),
    ("20240601", "20240630")
]


def fetch_epa_pm25_by_month(email, key, param_code, state, county, bdate, edate):
    url = (
        "https://aqs.epa.gov/data/api/dailyData/byCounty"
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
        print(f"Request failed: {response.status_code}")
        return pd.DataFrame()

    data = response.json()

    if "Data" not in data:
        print("No 'Data' field found in response.")
        return pd.DataFrame()

    return pd.DataFrame(data["Data"])


def fetch_openmeteo_weather(lat, lon, start_date, end_date):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        "&daily=temperature_2m_mean,relative_humidity_2m_mean,wind_speed_10m_mean,precipitation_sum"
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


def build_epa_daily_dataset():
    all_data = []

    for city, info in locations.items():
        print(f"Downloading data for {city}...")

        city_monthly_data = []

        for bdate, edate in months:
            print(f"  {bdate} to {edate}")
            df_month = fetch_epa_pm25_by_month(
                email=email,
                key=key,
                param_code=param_code,
                state=info["state"],
                county=info["county"],
                bdate=bdate,
                edate=edate
            )

            if not df_month.empty:
                df_month["city"] = city
                city_monthly_data.append(df_month)

        if city_monthly_data:
            city_df = pd.concat(city_monthly_data, ignore_index=True)
            all_data.append(city_df)

    epa_raw = pd.concat(all_data, ignore_index=True)

    epa_pm25 = epa_raw[["date_local", "arithmetic_mean", "city"]].copy()
    epa_pm25["date_local"] = pd.to_datetime(epa_pm25["date_local"])
    epa_pm25["arithmetic_mean"] = pd.to_numeric(epa_pm25["arithmetic_mean"], errors="coerce")

    epa_daily = (
        epa_pm25
        .groupby(["city", "date_local"], as_index=False)["arithmetic_mean"]
        .mean()
        .rename(columns={"date_local": "date", "arithmetic_mean": "pm25"})
    )

    return epa_daily


def build_weather_dataset():
    weather_data = []

    for city, coord in weather_locations.items():
        print(f"Downloading weather data for {city}...")
        df_weather = fetch_openmeteo_weather(
            lat=coord["lat"],
            lon=coord["lon"],
            start_date=start_date,
            end_date=end_date
        )

        if not df_weather.empty:
            df_weather["city"] = city
            weather_data.append(df_weather)

    weather_raw = pd.concat(weather_data, ignore_index=True)

    weather_daily = weather_raw.copy()
    weather_daily["time"] = pd.to_datetime(weather_daily["time"])

    weather_daily = weather_daily.rename(columns={
        "time": "date",
        "temperature_2m_mean": "temperature",
        "relative_humidity_2m_mean": "humidity",
        "wind_speed_10m_mean": "wind_speed",
        "precipitation_sum": "precipitation"
    })

    return weather_daily


def merge_air_weather_data(epa_daily, weather_daily):
    merged_df = pd.merge(
        epa_daily,
        weather_daily,
        on=["city", "date"],
        how="inner"
    )

    merged_df = merged_df.sort_values(["city", "date"]).reset_index(drop=True)
    return merged_df


if __name__ == "__main__":
    epa_daily = build_epa_daily_dataset()
    weather_daily = build_weather_dataset()
    merged_df = merge_air_weather_data(epa_daily, weather_daily)

    print("EPA daily shape:", epa_daily.shape)
    print("Weather daily shape:", weather_daily.shape)
    print("Merged shape:", merged_df.shape)
    print(merged_df.head())