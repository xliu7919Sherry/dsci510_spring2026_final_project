# Weather Effects on Urban Air Pollution: Los Angeles and Houston

## Project Description
This project examines how weather conditions affect urban air pollution in Los Angeles and Houston during the first half of 2024. The current progress focuses on collecting and merging PM2.5 data from the EPA AQS API and weather data from the Open-Meteo API.

## Data Sources
- EPA AQS API: daily PM2.5 data by county
- Open-Meteo Historical Weather API: daily temperature, humidity, wind speed, and precipitation
- EPA AirData Historical Dataset: planned for later integration

## Current Progress
- Retrieved EPA PM2.5 data for Los Angeles County and Harris County
- Retrieved weather data for Los Angeles and Houston
- Cleaned and aggregated PM2.5 data to daily city-level values
- Merged pollution and weather datasets

## Repository Structure
- `src/`: project Python scripts
- `doc/`: progress report PDF
- `tests.py`: test script for API data retrieval

## How to Run
1. Create a `.env` file with:
   - `EPA_EMAIL=your_email`
   - `EPA_KEY=your_key`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run tests:
   - `python tests.py`

## Notes
Do not upload `.env`, `data/`, or `results/` to the repository.