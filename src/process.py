import pandas as pd
from config import (
    LOCATIONS,
    WEATHER_LOCATIONS,
    MONTHS,
    START_DATE,
    END_DATE,
    PARAM_CODE_PM25,
    CSV_COUNTY_FILTERS,
)
from load import get_epa_pm25_daily, get_openmeteo_weather, load_epa_airdata_csv


# --- 1. Build daily PM2.5 dataset from EPA API ---
# AI generated:

def build_epa_daily_pm25(email, key):
    """
    Download EPA PM2.5 data for all cities and months in config, then
    aggregate station-level records into daily city-level averages.

    :param email: EPA account email
    :param key: EPA API key
    :return: DataFrame with columns ['city', 'date', 'pm25', 'aqi']
    """
    all_raw = []

    for city, info in LOCATIONS.items():
        print(f"Downloading EPA data for {city}...")

        for bdate, edate in MONTHS:
            print(f"  {bdate} to {edate}")
            df_month = get_epa_pm25_daily(
                email=email,
                key=key,
                param_code=PARAM_CODE_PM25,
                state=info["state"],
                county=info["county"],
                bdate=bdate,
                edate=edate,
            )
            if not df_month.empty:
                df_month["city"] = city
                all_raw.append(df_month)

    if not all_raw:
        return pd.DataFrame(columns=["city", "date", "pm25", "aqi"])

    epa_raw = pd.concat(all_raw, ignore_index=True)

    # Keep PM2.5 measurement, AQI, and metadata
    epa_clean = epa_raw[["date_local", "city", "arithmetic_mean", "aqi"]].copy()
    epa_clean["date_local"] = pd.to_datetime(epa_clean["date_local"])
    epa_clean["arithmetic_mean"] = pd.to_numeric(epa_clean["arithmetic_mean"], errors="coerce")
    epa_clean["aqi"] = pd.to_numeric(epa_clean["aqi"], errors="coerce")

    # Multiple monitoring sites per city per day → take the mean per city/date
    epa_daily = (
        epa_clean
        .groupby(["city", "date_local"], as_index=False)
        .agg(pm25=("arithmetic_mean", "mean"), aqi=("aqi", "mean"))
        .rename(columns={"date_local": "date"})
    )

    return epa_daily


# --- 2. Build daily weather dataset from Open-Meteo API ---

def build_weather_daily():
    """
    Download daily weather data for all cities in config and standardize
    column names for later merging.

    :return: DataFrame with columns ['city', 'date', 'temperature', 'humidity', 'wind_speed', 'precipitation']
    """
    all_weather = []

    for city, coord in WEATHER_LOCATIONS.items():
        print(f"Downloading weather data for {city}...")
        df_weather = get_openmeteo_weather(
            lat=coord["lat"],
            lon=coord["lon"],
            start_date=START_DATE,
            end_date=END_DATE,
        )
        if not df_weather.empty:
            df_weather["city"] = city
            all_weather.append(df_weather)

    if not all_weather:
        return pd.DataFrame(
            columns=["city", "date", "temperature", "humidity", "wind_speed", "precipitation"]
        )

    weather = pd.concat(all_weather, ignore_index=True)
    weather["time"] = pd.to_datetime(weather["time"])
    weather = weather.rename(columns={
        "time": "date",
        "temperature_2m_mean": "temperature",
        "relative_humidity_2m_mean": "humidity",
        "wind_speed_10m_mean": "wind_speed",
        "precipitation_sum": "precipitation",
    })

    return weather


# --- 3. Merge air and weather datasets ---

def merge_air_weather(epa_daily, weather_daily):
    """
    Inner-join PM2.5 and weather data on city and date.

    :param epa_daily: DataFrame with ['city', 'date', 'pm25', 'aqi']
    :param weather_daily: DataFrame with ['city', 'date', 'temperature', 'humidity', 'wind_speed', 'precipitation']
    :return: Merged DataFrame sorted by city and date
    """
    merged = pd.merge(epa_daily, weather_daily, on=["city", "date"], how="inner")
    merged = merged.sort_values(["city", "date"]).reset_index(drop=True)
    return merged


# --- 4. Build daily AQI dataset from EPA AirData CSV (third data source) ---

def build_epa_airdata_daily():
    """
    Filter the EPA AirData historical CSV to the cities and date range we study.
    Acts as an independent cross-check against the EPA API values.

    :return: DataFrame with columns ['city', 'date', 'aqi_csv']
    """
    df = load_epa_airdata_csv()
    if df.empty:
        return df

    # Keep only rows for our target cities
    kept = []
    for city, f in CSV_COUNTY_FILTERS.items():
        city_df = df[
            (df["State Name"] == f["state_name"]) &
            (df["county Name"] == f["county_name"])
        ].copy()
        city_df["city"] = city
        kept.append(city_df)

    if not kept:
        return pd.DataFrame()

    out = pd.concat(kept, ignore_index=True)
    out["Date"] = pd.to_datetime(out["Date"])
    out = out[(out["Date"] >= START_DATE) & (out["Date"] <= END_DATE)]

    out = out.rename(columns={"Date": "date", "AQI": "aqi_csv"})
    return out[["city", "date", "aqi_csv"]].sort_values(["city", "date"]).reset_index(drop=True)
