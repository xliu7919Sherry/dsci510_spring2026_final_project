# Weather Effects on Urban Air Pollution: Los Angeles vs Houston
This project examines how weather conditions relate to urban air pollution in Los Angeles and Houston during the first half of 2024. The current progress focuses on collecting, cleaning, and merging PM2.5 and weather data for later analysis and modeling.

# Data sources

| Data source # | Name / short description | Source URL | Type | List of fields | Format | Have tried to access/collect data with python? | Estimated data size |
|---|---|---|---|---|---|---|---|
| 1 | **EPA Air Quality System (AQS) API**. Provides air pollution monitoring data such as PM2.5, O3, NO2, and AQI for cities in the United States. | https://aqs.epa.gov/aqsweb/documents/data_api.html | API | `date_local`, `city`, `state`, `parameter_name`, `arithmetic_mean`, `units_of_measure`, `AQI` | JSON | Yes | ~700–800 daily observations per city |
| 2 | **Open-Meteo Historical Weather API**. Provides weather observations such as temperature, humidity, wind speed, and precipitation for specific geographic coordinates. | https://open-meteo.com/en/docs/historical-weather-api | API | `time`, `temperature_2m`, `relative_humidity_2m`, `wind_speed_10m`, `precipitation` | JSON | Yes | ~700–800 weather observations per city |
| 3 | **EPA AirData Historical Dataset**. Downloadable historical air pollution measurements across monitoring stations in the United States. | https://aqs.epa.gov/aqsweb/airdata/download_files.html | File | `date`, `pollutant`, `concentration`, `AQI`, `site_number`, `city`, `state` | CSV | Yes | ~1000 pollution records |

# Results
So far, the project has successfully:
- collected daily PM2.5 data from the EPA AQS API
- collected daily weather data from the Open-Meteo API
- cleaned and aggregated EPA station-level data into daily city-level PM2.5 values
- merged air pollution and weather data by city and date

The current merged dataset contains complete daily records for Los Angeles and Houston from January 1, 2024 to June 30, 2024.

# Installation
- Create a `.env` file in the project root with:
  - `EPA_EMAIL=your_email`
  - `EPA_KEY=your_key`
- Install required packages with:
  - `pip install -r requirements.txt`

Main packages used in this project:
- `requests`
- `pandas`
- `python-dotenv`

# Running analysis
To test the current workflow, run:

`python tests.py`

This will test:
- EPA API data access
- Open-Meteo API data access
- merged dataset construction

Project code is stored in the `src/` folder.  
The progress report PDF is stored in the `doc/` folder.