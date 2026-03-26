# Open Meteo Ingestion
Weather data ingestion via Open Meteo API.

Architecture flow:

    Weather API
        │
        ▼
    Python ingestion pipeline
        │
        ▼
    Raw JSON storage
        │
        ▼
    PostgreSQL database
        │
        ▼
    SQL transformations
        │
        ▼
    Analytics tables
        │
        ▼
    Dashboard (Metabase)
