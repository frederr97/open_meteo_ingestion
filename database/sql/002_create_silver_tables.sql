CREATE TABLE IF NOT EXISTS silver.archive_weather_hourly (
    id BIGSERIAL PRIMARY KEY,
    source_name TEXT,
    source_type TEXT,
    city_name TEXT NOT NULL,
    ingestion_date DATE NOT NULL,
    observation_time TIMESTAMPTZ NOT NULL,
    temperature_celsius NUMERIC(5, 2),
    feels_like_celsius NUMERIC(5, 2),
    relative_humidity_pct NUMERIC(5, 2),
    dew_point_2m NUMERIC(5, 2),
    precipitation_mm NUMERIC(5, 2),
    rain NUMERIC(5, 2),
    snowfall NUMERIC(5, 2),
    snow_depth NUMERIC(5, 2),
    weather_code INTEGER,
    wind_speed_10m NUMERIC(5, 2),
    wind_direction_10m NUMERIC(5, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_silver_archive_weather_hourly_city_time
    ON silver.archive_weather_hourly (city_name, observation_time);

CREATE TABLE IF NOT EXISTS silver.forecast_weather_hourly (
    id BIGSERIAL PRIMARY KEY,
    source_name TEXT,
    source_type TEXT,
    city_name TEXT NOT NULL,
    ingestion_date DATE NOT NULL,
    observation_time TIMESTAMPTZ NOT NULL,
    temperature_celsius NUMERIC(5, 2),
    feels_like_celsius NUMERIC(5, 2),
    relative_humidity_pct NUMERIC(5, 2),
    precipitation_probability NUMERIC(5, 2),
    precipitation_mm NUMERIC(5, 2),
    weather_code INTEGER,
    wind_speed_10m NUMERIC(5, 2),
    wind_direction_10m NUMERIC(5, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_silver_forecast_weather_hourly_city_time
    ON silver.forecast_weather_hourly (city_name, observation_time);