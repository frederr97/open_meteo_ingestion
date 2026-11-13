import pandas as pd


def build_daily_forecast_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Converter o horário da observação e extrair a data
    df["observation_date"] = pd.to_datetime(
        df["observation_time"],
        utc=True
    ).dt.strftime("%Y-%m-%d")

    # Definir as agregações diárias
    aggregations = {
        "temperature_celsius": ["mean", "min", "max"],
        "feels_like_celsius": "mean",
        "relative_humidity_pct": "mean",
        "precipitation_probability": ["mean", "max"],
        "precipitation_mm": "sum",
        "wind_speed_10m": "mean",
    }

    daily_df = (
        df.groupby(
            [
                "source_name",
                "source_type",
                "city_name",
                "ingestion_date",
                "observation_date",
            ],
            as_index=False,
        )
        .agg(aggregations)
    )

    # Simplificar os nomes das colunas resultantes
    daily_df.columns = [
        "_".join(column).strip("_")
        if isinstance(column, tuple)
        else column
        for column in daily_df.columns
    ]

    # Renomear as colunas para facilitar a interpretação
    daily_df = daily_df.rename(
        columns={
            "temperature_celsius_mean": "temperature_mean_celsius",
            "temperature_celsius_min": "temperature_min_celsius",
            "temperature_celsius_max": "temperature_max_celsius",
            "feels_like_celsius_mean": "feels_like_mean_celsius",
            "relative_humidity_pct_mean": "relative_humidity_mean_pct",
            "precipitation_probability_mean": "precipitation_probability_mean_pct",
            "precipitation_probability_max": "precipitation_probability_max_pct",
            "precipitation_mm_sum": "precipitation_total_mm",
            "wind_speed_10m_mean": "wind_speed_mean_kmh",
        }
    )

    return daily_df