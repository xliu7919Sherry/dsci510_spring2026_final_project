"""
End-to-end pipeline for the Weather vs Air Pollution project.

Run from the src/ directory:

    python main.py

Outputs:
    - results/*.png   EDA, correlation, and modeling plots
    - results/*.csv   correlation and model summaries
"""

import os

from config import (
    RESULTS_DIR,
    FEATURE_COLS,
    TARGET_COL,
)
from process import (
    build_epa_daily_pm25,
    build_weather_daily,
    merge_air_weather,
    build_epa_airdata_daily,
)
from analyze import (
    describe_dataset,
    plot_timeseries,
    plot_distribution_by_city,
    plot_boxplot_by_city,
    plot_weather_vs_pm25,
    plot_correlation_heatmap,
    correlation_table_by_city,
    compare_epa_sources,
    plot_correlation_bars,
)
from models import (
    compare_cities,
    plot_feature_importance,
    plot_model_comparison,
)


# AI generated:
def main():
    # --- Step 1: Download and merge data ---
    email = os.getenv("EPA_EMAIL")
    key = os.getenv("EPA_KEY")
    if not email or not key:
        raise RuntimeError("EPA_EMAIL / EPA_KEY not set. Put them in src/.env.")

    print("\n========== Step 1: Downloading data ==========")
    epa_daily = build_epa_daily_pm25(email, key)
    weather_daily = build_weather_daily()

    print(f"\nEPA rows:     {len(epa_daily)}")
    print(f"Weather rows: {len(weather_daily)}")
    if epa_daily.empty:
        raise RuntimeError(
            "EPA API returned no rows. Check src/.env (EPA_EMAIL / EPA_KEY), "
            "or scroll up for 'EPA request failed' messages."
        )
    if weather_daily.empty:
        raise RuntimeError("Open-Meteo API returned no rows.")

    merged = merge_air_weather(epa_daily, weather_daily)
    airdata = build_epa_airdata_daily()

    # --- Step 2: EDA ---
    print("\n========== Step 2: EDA ==========")
    describe_dataset(merged)
    plot_timeseries(merged, "pm25", "PM2.5 (µg/m³)")
    plot_timeseries(merged, "temperature", "Temperature (°C)")
    plot_distribution_by_city(merged, "pm25", "PM2.5 (µg/m³)")
    plot_boxplot_by_city(
        merged,
        ["pm25", "temperature", "humidity", "wind_speed", "precipitation"],
    )
    plot_weather_vs_pm25(merged, FEATURE_COLS)

    # --- Step 3: Correlation analysis + cross-source validation ---
    print("\n========== Step 3: Correlation ==========")
    corr_cols = [TARGET_COL] + FEATURE_COLS
    for city in merged["city"].unique():
        plot_correlation_heatmap(merged, corr_cols, city)

    corr_table = correlation_table_by_city(merged, FEATURE_COLS, target_col=TARGET_COL)
    corr_table.to_csv(f"{RESULTS_DIR}/correlation_by_city.csv")
    print("\nCorrelation with PM2.5 by city:")
    print(corr_table)
    plot_correlation_bars(merged, FEATURE_COLS, target_col=TARGET_COL)

    if not airdata.empty:
        epa_slim = merged[["city", "date", "aqi"]]
        _, summary = compare_epa_sources(epa_slim, airdata)
        print("\nCross-source validation summary:")
        print(summary)

    # --- Step 4: Modeling (LR baseline + Random Forest) ---
    print("\n========== Step 4: Modeling ==========")
    comparison, importance, per_city = compare_cities(merged)
    print("\nLinear Regression vs Random Forest:")
    print(comparison)
    print("\nFeature importance (Random Forest):")
    print(importance)
    plot_feature_importance(per_city)
    plot_model_comparison(comparison)

    print("\n========== Pipeline finished ==========")
    print(f"Plots and tables saved to {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
