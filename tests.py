from src.data_collection import (
    fetch_epa_pm25_by_month,
    fetch_openmeteo_weather,
    build_epa_daily_dataset,
    build_weather_dataset,
    merge_air_weather_data
)
import os
from dotenv import load_dotenv

load_dotenv()

def run_tests():
    email = os.getenv("EPA_EMAIL")
    key = os.getenv("EPA_KEY")

    print("Testing EPA API...")
    epa_df = fetch_epa_pm25_by_month(
        email=email,
        key=key,
        param_code="88101",
        state="06",
        county="037",
        bdate="20240101",
        edate="20240131"
    )
    print("EPA rows:", len(epa_df))
    assert not epa_df.empty, "EPA data download failed"

    print("Testing Open-Meteo API...")
    weather_df = fetch_openmeteo_weather(
        lat=34.0522,
        lon=-118.2437,
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    print("Weather rows:", len(weather_df))
    assert not weather_df.empty, "Weather data download failed"

    print("Testing merged dataset build...")
    epa_daily = build_epa_daily_dataset()
    weather_daily = build_weather_dataset()
    merged_df = merge_air_weather_data(epa_daily, weather_daily)

    print("Merged rows:", len(merged_df))
    assert not merged_df.empty, "Merged dataset build failed"

    print("All tests passed.")

if __name__ == "__main__":
    run_tests()