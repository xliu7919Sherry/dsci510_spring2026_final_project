import os
import matplotlib.pyplot as plt
import seaborn as sns

from config import RESULTS_DIR


# --- 1. Basic descriptive statistics ---

def describe_dataset(df):
    """
    Print basic information about the merged dataset: shape, missing values,
    and summary statistics grouped by city.

    :param df: Merged dataset DataFrame
    """
    print("--- Dataset shape ---")
    print(df.shape)

    print("\n--- Missing values ---")
    print(df.isnull().sum())

    print("\n--- Summary statistics by city ---")
    print(df.groupby("city").describe().transpose())


# --- 2. Time-series plots ---

def plot_timeseries(df, column, ylabel, result_dir=RESULTS_DIR, notebook_plot=False):
    """
    Plot the daily time series of a variable for each city on the same axes.

    :param df: Merged dataset DataFrame
    :param column: Column name to plot (e.g., 'pm25', 'aqi', 'temperature')
    :param ylabel: Y-axis label
    :param result_dir: Where to save the plot
    :param notebook_plot: If True, show inline; if False, save to file
    """
    os.makedirs(result_dir, exist_ok=True)

    plt.figure(figsize=(12, 5))
    for city in df["city"].unique():
        city_df = df[df["city"] == city].sort_values("date")
        plt.plot(city_df["date"], city_df[column], label=city, alpha=0.8)

    plt.title(f"Daily {ylabel}: Los Angeles vs Houston (2024 H1)")
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if notebook_plot:
        plt.show()
    else:
        plt.savefig(f"{result_dir}/timeseries_{column}.png", dpi=120)
        print(f"Saved timeseries_{column}.png")
        plt.close()


# --- 3. Distribution comparison (histogram) ---

def plot_distribution_by_city(df, column, xlabel, result_dir=RESULTS_DIR, notebook_plot=False):
    """
    Plot overlaid histograms of a variable for each city.

    :param df: Merged dataset DataFrame
    :param column: Column to plot
    :param xlabel: X-axis label
    """
    os.makedirs(result_dir, exist_ok=True)

    plt.figure(figsize=(9, 5))
    sns.histplot(data=df, x=column, hue="city", kde=True, bins=30, alpha=0.5)
    plt.title(f"Distribution of {xlabel} by City")
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")
    plt.tight_layout()

    if notebook_plot:
        plt.show()
    else:
        plt.savefig(f"{result_dir}/distribution_{column}.png", dpi=120)
        print(f"Saved distribution_{column}.png")
        plt.close()


# --- 4. Boxplots (side-by-side comparison) ---

def plot_boxplot_by_city(df, columns, result_dir=RESULTS_DIR, notebook_plot=False):
    """
    Draw a row of boxplots, one per variable, comparing the two cities.

    :param df: Merged dataset DataFrame
    :param columns: List of columns to plot
    """
    os.makedirs(result_dir, exist_ok=True)

    n = len(columns)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 5))

    # If only one column, axes is not a list — wrap it so we can iterate
    if n == 1:
        axes = [axes]

    for ax, col in zip(axes, columns):
        sns.boxplot(data=df, x="city", y=col, ax=ax)
        ax.set_title(col)
        ax.set_xlabel("")

    plt.suptitle("Variable Comparison: Los Angeles vs Houston", y=1.02)
    plt.tight_layout()

    if notebook_plot:
        plt.show()
    else:
        plt.savefig(f"{result_dir}/boxplot_by_city.png", dpi=120, bbox_inches="tight")
        print("Saved boxplot_by_city.png")
        plt.close()


# --- 5. Scatter plots: weather vs PM2.5 ---

def plot_weather_vs_pm25(df, weather_cols, result_dir=RESULTS_DIR, notebook_plot=False):
    """
    Draw a 2x2 grid of scatter plots showing PM2.5 against each weather variable,
    colored by city.

    :param df: Merged dataset DataFrame
    :param weather_cols: List of weather variable column names
    """
    os.makedirs(result_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    axes = axes.flatten()

    for ax, col in zip(axes, weather_cols):   # AI generated:
        sns.scatterplot(data=df, x=col, y="pm25", hue="city", alpha=0.6, ax=ax)
        ax.set_title(f"PM2.5 vs {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("PM2.5")

    plt.suptitle("PM2.5 vs Weather Variables", y=1.00, fontsize=14)
    plt.tight_layout()

    if notebook_plot:
        plt.show()
    else:
        plt.savefig(f"{result_dir}/scatter_weather_vs_pm25.png", dpi=120, bbox_inches="tight")
        print("Saved scatter_weather_vs_pm25.png")
        plt.close()


# --- 6. Correlation matrix ---

def correlation_matrix(df, columns, method="pearson"):
    """
    Compute the correlation matrix for the given columns.

    :param df: DataFrame
    :param columns: List of numeric column names
    :param method: 'pearson' or 'spearman'
    :return: Correlation matrix as a DataFrame
    """
    return df[columns].corr(method=method)


# --- 7. Correlation heatmap ---

def plot_correlation_heatmap(df, columns, city, method="pearson",
                             result_dir=RESULTS_DIR, notebook_plot=False):
    """
    Plot a correlation heatmap for a single city.

    :param df: Merged dataset DataFrame (must contain a 'city' column)
    :param columns: Numeric columns to include in the correlation
    :param city: City name to filter on
    :param method: 'pearson' or 'spearman'
    """
    os.makedirs(result_dir, exist_ok=True)

    corr = df[df["city"] == city][columns].corr(method=method)

    plt.figure(figsize=(7, 6))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm",
        center=0, vmin=-1, vmax=1, square=True,
    )
    plt.title(f"{method.title()} Correlation — {city}")
    plt.tight_layout()

    if notebook_plot:
        plt.show()
    else:
        safe_city = city.lower().replace(" ", "_")
        filename = f"correlation_{method}_{safe_city}.png"
        plt.savefig(f"{result_dir}/{filename}", dpi=120)
        print(f"Saved {filename}")
        plt.close()


# --- 8. Side-by-side correlation table for both cities ---

def correlation_table_by_city(df, feature_cols, target_col="pm25", method="pearson"):
    """
    For each city, compute the correlation between each predictor and the
    target variable. Returns one small DataFrame indexed by predictor, with
    one column per city.

    :param df: Merged dataset DataFrame (must have 'city' column)
    :param feature_cols: Predictor columns
    :param target_col: Target column (default 'pm25')
    :param method: 'pearson' or 'spearman'
    """
    import pandas as pd
    rows = {}
    for city in df["city"].unique():
        city_df = df[df["city"] == city]
        for col in feature_cols:    # AI generated:
            r = city_df[col].corr(city_df[target_col], method=method)
            rows.setdefault(col, {})[city] = round(r, 3)
    return pd.DataFrame.from_dict(rows, orient="index")


# --- 9. Cross-source validation: EPA API vs EPA AirData CSV ---
# AI generated:

def compare_epa_sources(epa_daily, airdata_daily, result_dir=RESULTS_DIR,
                        notebook_plot=False):
    """
    Validate the EPA AQS API values against the independently downloaded
    EPA AirData CSV by merging on (city, date) and computing the Pearson
    correlation between the two AQI series for each city. Also saves a
    per-city scatter plot with a y = x reference line.

    :param epa_daily: DataFrame with 'city', 'date', 'aqi' (from EPA API)
    :param airdata_daily: DataFrame with 'city', 'date', 'aqi_csv' (from EPA CSV)
    :return: (merged DataFrame, per-city summary DataFrame)
    """
    import pandas as pd
    os.makedirs(result_dir, exist_ok=True)

    merged = pd.merge(
        epa_daily[["city", "date", "aqi"]],
        airdata_daily[["city", "date", "aqi_csv"]],
        on=["city", "date"],
        how="inner",
    ).dropna(subset=["aqi", "aqi_csv"])

    summary_rows = []
    cities = merged["city"].unique()

    fig, axes = plt.subplots(1, len(cities), figsize=(5 * len(cities), 5))
    if len(cities) == 1:
        axes = [axes]

    for ax, city in zip(axes, cities):
        city_df = merged[merged["city"] == city]
        r = city_df["aqi"].corr(city_df["aqi_csv"])
        summary_rows.append({
            "city": city,
            "n_days": len(city_df),
            "pearson_r": round(r, 3),
        })

        sns.scatterplot(data=city_df, x="aqi", y="aqi_csv", ax=ax, alpha=0.6)
        lo = min(city_df["aqi"].min(), city_df["aqi_csv"].min())
        hi = max(city_df["aqi"].max(), city_df["aqi_csv"].max())
        ax.plot([lo, hi], [lo, hi], "r--", alpha=0.6, label="y = x")
        ax.set_title(f"{city}\nr = {r:+.3f}  (n = {len(city_df)})")
        ax.set_xlabel("AQI (EPA AQS API)")
        ax.set_ylabel("AQI (EPA AirData CSV)")
        ax.legend()

    plt.suptitle("Cross-Source AQI Validation: API vs CSV", y=1.02)
    plt.tight_layout()

    if notebook_plot:
        plt.show()
    else:
        plt.savefig(f"{result_dir}/cross_source_aqi.png",
                    dpi=120, bbox_inches="tight")
        print("Saved cross_source_aqi.png")
        plt.close()

    return merged, pd.DataFrame(summary_rows)


# --- 10. Side-by-side Pearson-r bar chart (used in the presentation) ---
# AI generated: grouped bar chart of Pearson r between each weather variable
# (temperature, humidity, wind_speed, precipitation) and daily PM2.5, with the
# variable dominates in which city.

def plot_correlation_bars(df, feature_cols, target_col="pm25",
                          result_dir=RESULTS_DIR, notebook_plot=False):
    """
    Draw a grouped bar chart of Pearson correlation between each weather
    variable and the target (PM2.5) for each city.

    :param df: Merged dataset DataFrame (must have 'city' column)
    :param feature_cols: Predictor columns
    :param target_col: Target column (default 'pm25')
    """
    import numpy as np
    os.makedirs(result_dir, exist_ok=True)

    corr_table = correlation_table_by_city(df, feature_cols, target_col=target_col)
    cities = list(corr_table.columns)

    x = np.arange(len(feature_cols))
    width = 0.38

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, city in enumerate(cities):
        offset = (i - (len(cities) - 1) / 2) * width
        ax.bar(x + offset, corr_table[city].values, width, label=city)

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", " ").title() for c in feature_cols])
    ax.set_ylabel(f"Pearson r with daily {target_col.upper()}")
    ax.set_title(f"Weather variables vs {target_col.upper()}: correlation by city")
    ax.set_ylim(-0.5, 0.5)
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    plt.tight_layout()

    if notebook_plot:
        plt.show()
    else:
        plt.savefig(f"{result_dir}/correlation_bars.png",
                    dpi=120, bbox_inches="tight")
        print("Saved correlation_bars.png")
        plt.close()
