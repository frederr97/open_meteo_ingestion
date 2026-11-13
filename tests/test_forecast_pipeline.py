from pathlib import Path

import pandas as pd

from transformations.forecast import build_daily_forecast_dataframe


# Caminho da camada Gold da coleta de 15/10/2026
PROJECT_ROOT = Path(__file__).resolve().parent.parent

GOLD_DIR = (
    PROJECT_ROOT
    / "data"
    / "gold"
    / "open_meteo"
    / "forecast"
    / "20261015"
)


def test_gold_files_exist():
    """Verifica se existem arquivos Parquet na camada Gold."""
    files = list(GOLD_DIR.glob("*.parquet"))

    assert len(files) == 14, (
        f"Esperados 14 arquivos Gold, mas foram encontrados {len(files)}."
    )


def test_gold_files_have_expected_structure():
    """Verifica a quantidade de linhas e colunas dos arquivos Gold."""
    files = list(GOLD_DIR.glob("*.parquet"))

    assert len(files) == 14, "A quantidade de arquivos Gold está incorreta."

    for file in files:
        df = pd.read_parquet(file)

        assert len(df) == 7, (
            f"{file.name}: esperadas 7 linhas, mas foram encontradas {len(df)}."
        )

        assert len(df.columns) == 14, (
            f"{file.name}: esperadas 14 colunas, mas foram encontradas "
            f"{len(df.columns)}."
        )

def test_gold_files_have_no_null_values():
    """Verifica se os arquivos Gold não possuem valores nulos."""
    files = list(GOLD_DIR.glob("*.parquet"))

    assert len(files) == 14, "A quantidade de arquivos Gold está incorreta."

    for file in files:
        df = pd.read_parquet(file)

        null_count = int(df.isna().sum().sum())

        assert null_count == 0, (
            f"{file.name}: encontrados {null_count} valores nulos."
        )


def test_gold_files_have_no_duplicate_daily_records():
    """Verifica se existem registros diários duplicados."""
    files = list(GOLD_DIR.glob("*.parquet"))

    assert len(files) == 14, "A quantidade de arquivos Gold está incorreta."

    key_columns = [
        "source_name",
        "source_type",
        "city_name",
        "ingestion_date",
        "observation_date",
    ]

    for file in files:
        df = pd.read_parquet(file)

        duplicate_count = int(
            df.duplicated(subset=key_columns).sum()
        )

        assert duplicate_count == 0, (
            f"{file.name}: encontrados {duplicate_count} registros duplicados."
        )       

def test_daily_forecast_aggregation():
    """Verifica se as agregações diárias calculam os valores esperados."""
    from pipelines.forecast_silver_to_gold import build_daily_forecast_dataframe

    sample_df = pd.DataFrame({
        "source_name": ["open_meteo"] * 3,
        "source_type": ["forecast"] * 3,
        "city_name": ["amsterdam"] * 3,
        "ingestion_date": ["20261015"] * 3,
        "observation_time": [
            "2026-10-15T00:00:00Z",
            "2026-10-15T01:00:00Z",
            "2026-10-15T02:00:00Z",
        ],
        "temperature_celsius": [20.0, 22.0, 24.0],
        "feels_like_celsius": [19.0, 21.0, 23.0],
        "relative_humidity_pct": [60, 70, 80],
        "precipitation_probability": [10, 30, 20],
        "precipitation_mm": [0.0, 1.5, 2.5],
        "wind_speed_10m": [10.0, 20.0, 30.0],
    })

    result = build_daily_forecast_dataframe(sample_df)

    # Deve gerar somente um registro diário
    assert len(result) == 1

    row = result.iloc[0]

    # Temperatura
    assert row["temperature_mean_celsius"] == 22.0
    assert row["temperature_min_celsius"] == 20.0
    assert row["temperature_max_celsius"] == 24.0

    # Sensação térmica e umidade
    assert row["feels_like_mean_celsius"] == 21.0
    assert row["relative_humidity_mean_pct"] == 70.0

    # Probabilidade de precipitação
    assert row["precipitation_probability_mean_pct"] == 20.0
    assert row["precipitation_probability_max_pct"] == 30

    # Precipitação acumulada e vento médio
    assert row["precipitation_total_mm"] == 4.0
    assert row["wind_speed_mean_kmh"] == 20.0

    # Data de observação
    assert row["observation_date"] == "2026-10-15"

def test_daily_forecast_aggregation():
    """Verifica se os cálculos diários da camada Gold estão corretos."""

    sample_df = pd.DataFrame({
        "source_name": ["open_meteo"] * 3,
        "source_type": ["forecast"] * 3,
        "city_name": ["amsterdam"] * 3,
        "ingestion_date": ["20261015"] * 3,
        "observation_time": [
            "2026-10-15T00:00:00Z",
            "2026-10-15T01:00:00Z",
            "2026-10-15T02:00:00Z",
        ],
        "temperature_celsius": [20.0, 22.0, 24.0],
        "feels_like_celsius": [19.0, 21.0, 23.0],
        "relative_humidity_pct": [60, 70, 80],
        "precipitation_probability": [10, 30, 20],
        "precipitation_mm": [0.0, 1.5, 2.5],
        "wind_speed_10m": [10.0, 20.0, 30.0],
    })

    result = build_daily_forecast_dataframe(sample_df)

    assert len(result) == 1

    row = result.iloc[0]

    assert row["temperature_mean_celsius"] == 22.0
    assert row["temperature_min_celsius"] == 20.0
    assert row["temperature_max_celsius"] == 24.0
    assert row["feels_like_mean_celsius"] == 21.0
    assert row["relative_humidity_mean_pct"] == 70.0
    assert row["precipitation_probability_mean_pct"] == 20.0
    assert row["precipitation_probability_max_pct"] == 30
    assert row["precipitation_total_mm"] == 4.0
    assert row["wind_speed_mean_kmh"] == 20.0
    assert row["observation_date"] == "2026-10-15"