"""
Smoke tests: verify we can access each data source.

Requires EPA_EMAIL / EPA_KEY in src/.env and the EPA AirData CSV placed at
data/daily_aqi_by_county_2024.csv. Run:  python tests.py
"""

import os

from config import (
    PARAM_CODE_PM25,
    TEST_STATE,
    TEST_COUNTY,
    TEST_BDATE,
    TEST_EDATE,
    TEST_LAT,
    TEST_LON,
    TEST_START_DATE,
    TEST_END_DATE,
)
from load import (
    get_epa_pm25_daily,
    get_openmeteo_weather,
    load_epa_airdata_csv,
)
from process import (
    build_epa_daily_pm25,
    build_weather_daily,
    merge_air_weather,
    build_epa_airdata_daily,
)


def run_tests():
    email = os.getenv("EPA_EMAIL")
    key = os.getenv("EPA_KEY")

    print("Testing EPA API...")
    epa_df = get_epa_pm25_daily(
        email=email,
        key=key,
        param_code=PARAM_CODE_PM25,
        state=TEST_STATE,
        county=TEST_COUNTY,
        bdate=TEST_BDATE,
        edate=TEST_EDATE,
    )
    print("EPA rows:", len(epa_df))
    assert not epa_df.empty, "EPA data download failed"

    print("Testing Open-Meteo API...")
    weather_df = get_openmeteo_weather(
        lat=TEST_LAT,
        lon=TEST_LON,
        start_date=TEST_START_DATE,
        end_date=TEST_END_DATE,
    )
    print("Weather rows:", len(weather_df))
    assert not weather_df.empty, "Weather data download failed"

    print("Testing EPA AirData CSV load...")
    csv_df = load_epa_airdata_csv()
    assert not csv_df.empty, "CSV load failed"

    print("Testing merged dataset build...")
    epa_daily = build_epa_daily_pm25(email, key)
    weather_daily = build_weather_daily()
    merged = merge_air_weather(epa_daily, weather_daily)
    print("Merged rows:", len(merged))
    assert not merged.empty, "Merged dataset build failed"

    print("Testing EPA AirData daily filter...")
    airdata_daily = build_epa_airdata_daily()
    assert not airdata_daily.empty, "AirData filter failed"

    print("All tests passed.")


if __name__ == "__main__":
    run_tests()
