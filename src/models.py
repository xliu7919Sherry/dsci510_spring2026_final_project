"""
Modeling: predict daily PM2.5 from weather variables.

We fit two models on the same 80/20 train/test split so their test R² and
RMSE are directly comparable:

    * Linear regression — a simple baseline assuming PM2.5 is a linear
      function of the weather variables.
    * Random Forest     — captures nonlinear effects and variable
      interactions, and gives us a feature-importance ranking.
"""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

from config import (
    RESULTS_DIR,
    FEATURE_COLS,
    TARGET_COL,
    TEST_SIZE,
    RANDOM_STATE,
)


# --- 1. Prepare city-level feature / target arrays ---

def prepare_city_data(df, city, feature_cols=FEATURE_COLS, target_col=TARGET_COL):
    """
    Filter the merged dataset to one city and drop rows with missing values
    in the features or target.

    :return: (X DataFrame, y Series)
    """
    sub = df[df["city"] == city].dropna(subset=feature_cols + [target_col])
    X = sub[feature_cols].copy()
    y = sub[target_col].copy()
    return X, y


# --- 2. Shared train/test split + metric helper ---
# AI generated:

def _train_and_score(estimator, X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE):
    """
    Split (X, y) into 80/20, fit the estimator, and return a metrics dict.
    Used by both the linear and Random Forest pipelines so the numbers are
    directly comparable.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    estimator.fit(X_train, y_train)

    y_pred_train = estimator.predict(X_train)
    y_pred_test = estimator.predict(X_test)

    metrics = {
        "r2_train": r2_score(y_train, y_pred_train),
        "r2_test": r2_score(y_test, y_pred_test),
        "rmse_train": float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
        "rmse_test": float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
        "n_train": len(y_train),
        "n_test": len(y_test),
    }
    return estimator, metrics


# --- 3. Linear regression (baseline) ---

def run_linear_regression(X, y):
    """
    Baseline linear regression: sklearn LinearRegression on an 80/20 split.
    """
    model, metrics = _train_and_score(LinearRegression(), X, y)
    return {"model": model, "metrics": metrics}


# --- 4. Random Forest ---

def run_random_forest(X, y, n_estimators=100):
    """
    Random Forest regression on the same 80/20 split as the linear baseline.
    """
    rf = RandomForestRegressor(
        n_estimators=n_estimators, random_state=RANDOM_STATE
    )
    model, metrics = _train_and_score(rf, X, y)
    return {"model": model, "metrics": metrics}


def feature_importance_table(rf_model, feature_cols=FEATURE_COLS):
    """
    Turn the Random Forest's built-in feature_importances_ array into a
    tidy DataFrame sorted from most to least important.
    """
    return (
        pd.DataFrame({
            "feature": feature_cols,
            "importance": rf_model.feature_importances_,
        })
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
        .round(4)
    )


# --- 5. End-to-end per-city analysis ---

def analyze_city(df, city, feature_cols=FEATURE_COLS, target_col=TARGET_COL,
                 verbose=True):
    """
    For one city: fit linear regression and Random Forest, report metrics
    for both, and return the Random Forest feature importance.
    """
    X, y = prepare_city_data(df, city, feature_cols, target_col)

    lr = run_linear_regression(X, y)
    rf = run_random_forest(X, y)
    importance = feature_importance_table(rf["model"], feature_cols)

    if verbose:
        print(f"\n================ {city} ================")
        print(f"n_train = {lr['metrics']['n_train']}   "
              f"n_test = {lr['metrics']['n_test']}")
        print("Linear Regression:")
        print(f"  test R²   = {lr['metrics']['r2_test']:.3f}")
        print(f"  test RMSE = {lr['metrics']['rmse_test']:.3f}")
        print("Random Forest:")
        print(f"  test R²   = {rf['metrics']['r2_test']:.3f}")
        print(f"  test RMSE = {rf['metrics']['rmse_test']:.3f}")
        print("Feature importance (Random Forest):")
        print(importance.to_string(index=False))

    return {
        "city": city,
        "lr_metrics": lr["metrics"],
        "rf_metrics": rf["metrics"],
        "rf_model": rf["model"],
        "feature_importance": importance,
    }


# --- 6. Compare cities and produce summary tables ---
# AI generated:

def compare_cities(df, feature_cols=FEATURE_COLS, target_col=TARGET_COL,
                   result_dir=RESULTS_DIR, save=True):
    """
    Run analyze_city for every city and return three objects:
        1. `comparison`  — test R² / RMSE for LR and RF, side by side
        2. `importance`  — per-city feature importance (RF)
        3. `per_city`    — full per-city result dict
    """
    os.makedirs(result_dir, exist_ok=True)

    per_city = {}
    comparison_rows = []
    importance_frames = []

    for city in df["city"].unique():
        res = analyze_city(df, city, feature_cols, target_col, verbose=False)
        per_city[city] = res

        comparison_rows.append({
            "city": city,
            "n": res["lr_metrics"]["n_train"] + res["lr_metrics"]["n_test"],
            "lr_test_r2":   round(res["lr_metrics"]["r2_test"], 3),
            "rf_test_r2":   round(res["rf_metrics"]["r2_test"], 3),
            "lr_test_rmse": round(res["lr_metrics"]["rmse_test"], 3),
            "rf_test_rmse": round(res["rf_metrics"]["rmse_test"], 3),
        })

        imp = res["feature_importance"].copy()
        imp.columns = ["feature", f"{city} importance"]
        importance_frames.append(imp.set_index("feature"))

    comparison = pd.DataFrame(comparison_rows)
    importance = pd.concat(importance_frames, axis=1)

    if save:
        comparison.to_csv(f"{result_dir}/model_comparison.csv", index=False)
        importance.to_csv(f"{result_dir}/rf_feature_importance.csv")
        print("Saved model_comparison.csv and rf_feature_importance.csv")

    return comparison, importance, per_city


# --- 7. Bar chart of RF feature importance per city ---
# AI generated:

def plot_feature_importance(per_city_results, result_dir=RESULTS_DIR,
                            notebook_plot=False):
    """
    One horizontal bar chart per city showing Random Forest feature
    importances (most important on top).
    """
    os.makedirs(result_dir, exist_ok=True)

    cities = list(per_city_results.keys())
    fig, axes = plt.subplots(1, len(cities), figsize=(5 * len(cities), 4))
    if len(cities) == 1:
        axes = [axes]

    for ax, city in zip(axes, cities):
        imp = per_city_results[city]["feature_importance"]
        ax.barh(imp["feature"], imp["importance"])
        ax.invert_yaxis()
        ax.set_title(city)
        ax.set_xlabel("Importance")

    plt.suptitle("Random Forest Feature Importance", y=1.02)
    plt.tight_layout()

    if notebook_plot:
        plt.show()
    else:
        plt.savefig(f"{result_dir}/rf_feature_importance.png",
                    dpi=120, bbox_inches="tight")
        print("Saved rf_feature_importance.png")
        plt.close()


# --- 8. Linear Regression vs Random Forest test-R² comparison (for slides) ---
# AI generated: grouped bar chart comparing the held-out test R² of the

def plot_model_comparison(comparison, result_dir=RESULTS_DIR, notebook_plot=False):
    """
    Draw a grouped bar chart of Linear Regression vs Random Forest test R²
    for each city. Reads the `comparison` DataFrame produced by
    `compare_cities` (columns: city, lr_test_r2, rf_test_r2, ...).
    """
    import numpy as np
    os.makedirs(result_dir, exist_ok=True)

    cities = list(comparison["city"])
    lr_r2 = comparison["lr_test_r2"].values
    rf_r2 = comparison["rf_test_r2"].values

    x = np.arange(len(cities))
    width = 0.38

    fig, ax = plt.subplots(figsize=(8, 5))
    bars_lr = ax.bar(x - width / 2, lr_r2, width, label="Linear Regression",
                     color="#64748B")
    bars_rf = ax.bar(x + width / 2, rf_r2, width, label="Random Forest",
                     color="#065A82")

    # Annotate each bar with its R² value
    for bars in (bars_lr, bars_rf):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.005,
                    f"{b.get_height():.2f}", ha="center", va="bottom", fontsize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(cities)
    ax.set_ylabel("Test R² (held-out 20%)")
    ax.set_title("Linear Regression vs Random Forest: test R² by city")
    ax.set_ylim(0, max(max(lr_r2), max(rf_r2)) * 1.25)
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    plt.tight_layout()

    if notebook_plot:
        plt.show()
    else:
        plt.savefig(f"{result_dir}/model_comparison.png",
                    dpi=120, bbox_inches="tight")
        print("Saved model_comparison.png")
        plt.close()
