# Weather Effects on Urban Air Pollution: Los Angeles vs Houston

**DSCI 510 Final Project**  
**Xingtong Liu**

## Introduction

This project examines how daily weather conditions relate to PM2.5 air pollution in Los Angeles and Houston during the first half of 2024. The study focuses on four weather variables: temperature, humidity, wind speed, and precipitation. It compares whether these factors are associated with PM2.5 in similar or different ways across the two cities. In addition, the project compares a Linear Regression baseline with a Random Forest model to determine whether a nonlinear model can better predict PM2.5.

## Data sources

| # | Name / short description | Source URL | Type | Key fields | Format | Size |
|---|---|---|---|---|---|---|
| 1 | EPA Air Quality System (AQS) API — daily pollutant observations by county | https://aqs.epa.gov/aqsweb/documents/data_api.html | API | `date_local`, `arithmetic_mean`, `aqi`, `state`, `county` | JSON | About 180 daily observations × 2 cities |
| 2 | Open-Meteo Historical Weather API — daily historical weather by latitude and longitude | https://open-meteo.com/en/docs/historical-weather-api | API | `time`, `temperature_2m_mean`, `relative_humidity_2m_mean`, `wind_speed_10m_mean`, `precipitation_sum` | JSON | About 180 daily observations × 2 cities |
| 3 | EPA AirData historical CSV — daily AQI by county | https://aqs.epa.gov/aqsweb/airdata/download_files.html | CSV file | `Date`, `State Name`, `county Name`, `AQI` | CSV | Large national file filtered to Los Angeles County and Harris County |

The EPA AirData CSV is used as an independent reference source to cross-check the AQI values from the EPA AQS API.

## Analysis

This project includes several stages of analysis.

First, the pipeline downloads daily PM2.5 data from the EPA AQS API and daily weather data from the Open-Meteo API. It also loads the EPA AirData CSV file for cross-source validation.

Second, the raw data are cleaned and processed into city-level daily datasets. EPA monitoring site records are aggregated into daily mean PM2.5 and AQI values for each city. Weather variables are standardized and merged with the air pollution data by city and date.

Third, the project performs exploratory data analysis using time-series plots, histograms, boxplots, and scatter plots. These visualizations are used to compare the distributions and trends of PM2.5 and weather variables between Los Angeles and Houston.

Fourth, the project computes correlation matrices and city-level correlation tables to examine the relationships between PM2.5 and weather variables.

Finally, the project builds two predictive models for each city. A Linear Regression model is used as a baseline, and a Random Forest model is used to capture possible nonlinear relationships. Model performance is compared using R² and RMSE, and Random Forest feature importance is also reported.

## Summary of the results

The analysis shows that weather variables are related to PM2.5 in both Los Angeles and Houston, but the relationships are not identical across the two cities. Correlation patterns differ between the two locations, which suggests that local environmental conditions may influence air pollution in different ways. The Random Forest model provides a useful nonlinear comparison to the Linear Regression baseline, and the feature importance results help identify which weather variables are most influential in each city.

## Repository structure

```text
.
├── data/                              # empty in repository; used locally for downloaded/input data
├── docs/
│   ├── Xingtong_Liu_progress_report.pdf
│   └── Xingtong_Liu_presentation.pdf
├── results/                           # generated plots and summary CSV files
├── src/
│   ├── config.py
│   ├── load.py
│   ├── process.py
│   ├── analyze.py
│   ├── models.py
│   ├── main.py
│   └── tests.py
├── results.ipynb
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

1. Clone the repository.

2. Create and activate a Python environment.

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Get a free EPA AQS API key from:

```text
https://aqs.epa.gov/data/api/signup
```

5. Create a `.env` file in the `src/` folder with the following variables:

```text
EPA_EMAIL=your_email
EPA_KEY=your_key
```

6. No API key is required for the Open-Meteo Historical Weather API for normal non-commercial use.

7. The EPA AirData CSV file is downloaded automatically by the code if it is not already present in the local `data/` folder.

Download the file named:

```text
daily_aqi_by_county_2024.zip
```

Unzip it and place:

```text
daily_aqi_by_county_2024.csv
```

inside the local `data/` folder.

## How to run

From the `src/` directory, run the full pipeline:

```bash
cd src
python main.py
```

This command downloads data, processes the datasets, runs the analysis, and saves plots and summary files into the `results/` folder.

To run the smoke tests, from the same `src/` directory run:

```bash
python tests.py
```

To open the notebook with the final narrated analysis, run:

```bash
jupyter notebook results.ipynb
```

## AI usage disclosure

OpenAI ChatGPT was used for limited coding assistance, including code structure suggestions, debugging help, and refinement of selected functions. Any code sections that received substantial AI assistance are labeled with a `# AI generated:` comment directly above the relevant code block.

## Notes

- No raw data files are included in the repository.
- No API keys or `.env` file are included in the repository.
- The `data/` folder should remain empty in the submitted GitHub repository.
- The `.env.example` file should list required environment variable names without values.
