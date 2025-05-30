# How to Demo the Salt Lake City (SLC) Data API Showcase

This guide provides step-by-step instructions to demonstrate the Salt Lake City air quality data showcase using the DataSpaces API.

## Prerequisites

1.  **Docker (Recommended for API Server):** Ensure Docker and Docker Compose are installed if you plan to run the API server via Docker.
2.  **Python Environment:** Python 3.7+ is required.
3.  **Git:** For cloning the repository if you haven't already.
4.  **Project Files:** You should have the `dspaces-api` project directory, including the `salt_lake_showcase.py` and related files.

## Demo Steps

### 1. Start the DataSpaces API Server

The API server needs to be running to serve the data.

**Using Docker (Recommended)**

Navigate to the root of the `dspaces-api` project directory in your terminal and run:

```bash
docker-compose up -d
```

This will build and start the API server in the background. It typically listens on `http://localhost:8001`.

*Verification:* Open your browser and go to `http://localhost:8001/docs`. You should see the API documentation.

### 2. Install Python Dependencies for the Showcase

The showcase script has its own set of Python dependencies. Open a new terminal window, navigate to the `dspaces-api` project directory, and run:
```bash
pip install -r showcase_requirements.txt
```
*(If you use `uv`, you can run `uv pip install -r showcase_requirements.txt`)*

### 3. Ingest the Salt Lake County Data

The Salt Lake County air quality data needs to be loaded into the DataSpaces API. Run the ingestion script:
```bash
python ingest_salt_lake_data.py
```
You should see output indicating successful ingestion, including the namespace (`salt_lake_demo`) and the number of rows/columns processed.

### 4. Run the Salt Lake Showcase Script

Now you can run the main showcase script. This script will:
*   Connect to the API.
*   Perform various data analyses (exploration, temporal, seasonal).
*   Generate visualizations using `matplotlib`.

Execute the script:
```bash
python salt_lake_showcase.py
```

**During the Demo:**
*   The script will print analysis results to the console.
*   `matplotlib` plot windows will appear one by one.
    *   **Explain each graph** as it appears (e.g., hourly NO2 patterns, monthly trends).
    *   **Close each plot window** to allow the script to proceed to the next analysis and visualization.
*   The script currently shows the first two sets of graphs (Temporal and Seasonal analysis) as per the latest modification.

### 5. (Optional) Run the Test Script

To demonstrate that the underlying `SaltLakeDataAPI` client is functioning correctly and can interact with the API endpoints, you can run the test script:
```bash
python test_showcase.py
```
This script will output results for several tests, such as API connection, filter retrieval, and basic data fetching.

## Key Talking Points for the Demo

*   **DataSpaces API:** Emphasize how the API allows for easy retrieval, filtering, and aggregation of the dataset.
*   **Data Analysis:** Showcase the types of insights that can be derived (e.g., pollution peaks during certain hours/days, seasonal variations).
*   **Visualization:** Highlight how `matplotlib` is used to visualize these patterns.
*   **Extensibility:** Briefly mention that the showcase can be extended with more complex analyses or different datasets.
*   **Reproducibility:** The scripts and defined environment allow for reproducible data analysis.

## Troubleshooting Common Issues

*   **API Connection Failed:**
    *   Ensure the API server Docker container is running (check with `docker ps`).
    *   Check that the `BASE_URL` in `salt_lake_showcase.py` (default: `http://localhost:8001`) matches where the API is being served.
*   **Data Not Found / Empty Plots:**
    *   Make sure `ingest_salt_lake_data.py` was run successfully and the data was ingested into the `salt_lake_demo` namespace.
*   **`ModuleNotFoundError`:**
    *   Ensure `pip install -r showcase_requirements.txt` was completed successfully in your active Python environment.

---

For more detailed information about the showcase script itself, refer to `SALT_LAKE_SHOWCASE_README.md`.
