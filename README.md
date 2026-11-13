# Open-Meteo Ingestion

A data ingestion project that collects weather data from the Open-Meteo API and organizes it into structured data layers for analysis.

## Project Overview

The project uses Python to ingest weather data and stores it in different layers following a Bronze, Silver, and Gold architecture.

## Architecture

```text
Open-Meteo API
       |
       v
Python Ingestion Pipeline
       |
       v
Bronze Layer - Raw JSON
       |
       v
Silver Layer - Processed Parquet
       |
       v
Gold Layer - Aggregated Parquet
       |
       v
Data Exploration with PySpark