import datetime
import sys
import time
from pathlib import Path

import pandas as pd
import requests

from utils.ingestion import Ingestion
from utils.file_utils import FileUtils
from transformations.forecast import build_daily_forecast_dataframe


# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_ROOT = PROJECT_ROOT / "data"

BRONZE_DIR = DATA_ROOT / "bronze" / "open_meteo" / "forecast"
SILVER_DIR = DATA_ROOT / "silver" / "open_meteo" / "forecast"
GOLD_DIR = DATA_ROOT / "gold" / "open_meteo" / "forecast"

BASE_URL = "https://api.open-meteo.com/v1/forecast"

MAX_ATTEMPTS = 3
TIMEOUT_SECONDS = 45


# ============================================================
# BRONZE: COLETAR OS DADOS DA API
# ============================================================

def run_bronze(target_date: str) -> int:
    print("\n" + "=" * 55)
    print("ETAPA 1 — BRONZE")
    print("=" * 55)

    ingestion = Ingestion()
    configs = ingestion.load_config_json("cities", "metrics")

    cities = configs.get("cities", {})
    metrics = configs.get("metrics", {}).get("forecast", {})
    hourly_metrics = metrics.get("hourly", [])

    if not cities:
        raise RuntimeError("Nenhuma cidade encontrada em config/cities.json.")

    if not hourly_metrics:
        raise RuntimeError(
            "Nenhuma métrica horária encontrada em config/metrics.json."
        )

    output_dir = BRONZE_DIR / target_date
    output_dir.mkdir(parents=True, exist_ok=True)

    successful = 0
    errors = []

    for city, coordinates in cities.items():
        output_path = output_dir / f"{city}_{target_date}.json"

        print(f"\nColetando: {city}")

        params = {
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "hourly": ",".join(hourly_metrics),
            "forecast_days": 7,
            "timezone": "UTC",
        }

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = requests.get(
                    BASE_URL,
                    params=params,
                    timeout=TIMEOUT_SECONDS,
                )

                response.raise_for_status()
                data = response.json()

                hourly = data.get("hourly", {})
                times = hourly.get("time", [])

                if not times:
                    raise ValueError(
                        f"A API não retornou horários para {city}."
                    )

                # Salvar somente após validar a resposta.
                FileUtils.write_json(data, output_path)

                print(f"OK: {city} — {len(times)} horários")
                successful += 1
                break

            except (
                requests.exceptions.RequestException,
                ValueError,
            ) as error:
                if attempt == MAX_ATTEMPTS:
                    errors.append((city, str(error)))
                    print(f"ERRO: {city} — {error}")
                else:
                    wait_seconds = 2 ** attempt
                    print(
                        f"Tentativa {attempt}/{MAX_ATTEMPTS} falhou. "
                        f"Nova tentativa em {wait_seconds}s."
                    )
                    time.sleep(wait_seconds)

    print("\nResumo Bronze:")
    print(f"Cidades configuradas: {len(cities)}")
    print(f"Coletas bem-sucedidas: {successful}")
    print(f"Coletas com falha: {len(errors)}")

    if errors:
        for city, error in errors:
            print(f"  {city}: {error}")

        raise RuntimeError(
            "A coleta Bronze teve falhas. "
            "As etapas seguintes não serão executadas."
        )

    if successful != len(cities):
        raise RuntimeError("A quantidade de coletas não corresponde às cidades.")

    return len(cities)


# ============================================================
# SILVER: TRANSFORMAR JSON EM PARQUET
# ============================================================

def build_forecast_dataframe(path: Path) -> pd.DataFrame:
    raw = FileUtils.read_json(path)
    hourly = raw.get("hourly", {})

    times = hourly.get("time", [])

    if not times:
        return pd.DataFrame()

    field_mapping = {
        "temperature_2m": "temperature_celsius",
        "apparent_temperature": "feels_like_celsius",
        "relative_humidity_2m": "relative_humidity_pct",
        "precipitation_probability": "precipitation_probability",
        "precipitation": "precipitation_mm",
        "weather_code": "weather_code",
        "wind_speed_10m": "wind_speed_10m",
        "wind_direction_10m": "wind_direction_10m",
    }

    data = {
        "source_name": ["open_meteo"] * len(times),
        "source_type": ["forecast"] * len(times),
        "city_name": [path.stem.rsplit("_", 1)[0]] * len(times),
        "ingestion_date": [path.parent.name] * len(times),
        "observation_time": [f"{hour}Z" for hour in times],
    }

    for source_field, target_field in field_mapping.items():
        values = hourly.get(source_field, [])

        if not isinstance(values, list):
            values = []

        values = values[:len(times)]

        if len(values) < len(times):
            values.extend([None] * (len(times) - len(values)))

        data[target_field] = values

    return pd.DataFrame(data)


def run_silver(target_date: str, expected_cities: int) -> int:
    print("\n" + "=" * 55)
    print("ETAPA 2 — SILVER")
    print("=" * 55)

    source_dir = BRONZE_DIR / target_date
    output_dir = SILVER_DIR / target_date

    json_files = sorted(source_dir.glob("*.json"))

    if len(json_files) != expected_cities:
        raise RuntimeError(
            f"Esperados {expected_cities} JSONs na Bronze, "
            f"mas foram encontrados {len(json_files)}."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    total_rows = 0

    for path in json_files:
        df = build_forecast_dataframe(path)

        if df.empty:
            raise RuntimeError(
                f"O arquivo {path.name} não contém dados horários."
            )

        output_path = output_dir / f"{path.stem}.parquet"

        df.to_parquet(
            output_path,
            engine="pyarrow",
            index=False,
        )

        total_rows += len(df)
        print(f"OK: {path.name} — {len(df)} linhas")

    parquet_files = sorted(output_dir.glob("*.parquet"))

    if len(parquet_files) != expected_cities:
        raise RuntimeError(
            "A quantidade de arquivos Silver não corresponde "
            "à quantidade de cidades."
        )

    print(f"\nArquivos Silver: {len(parquet_files)}")
    print(f"Total de linhas horárias: {total_rows}")

    return len(parquet_files)


# ============================================================
# GOLD: AGREGAR OS DADOS POR DIA
# ============================================================

def run_gold(target_date: str, expected_cities: int) -> int:
    print("\n" + "=" * 55)
    print("ETAPA 3 — GOLD")
    print("=" * 55)

    source_dir = SILVER_DIR / target_date
    output_dir = GOLD_DIR / target_date

    silver_files = sorted(source_dir.glob("*.parquet"))

    if len(silver_files) != expected_cities:
        raise RuntimeError(
            f"Esperados {expected_cities} arquivos Silver, "
            f"mas foram encontrados {len(silver_files)}."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    total_daily_rows = 0

    for path in silver_files:
        df = pd.read_parquet(path, engine="pyarrow")
        daily_df = build_daily_forecast_dataframe(df)

        if daily_df.empty:
            raise RuntimeError(
                f"A transformação Gold não gerou dados para {path.name}."
            )

        output_path = output_dir / path.name

        daily_df.to_parquet(
            output_path,
            engine="pyarrow",
            index=False,
        )

        total_daily_rows += len(daily_df)
        print(f"OK: {path.name} — {len(daily_df)} linhas diárias")

    gold_files = sorted(output_dir.glob("*.parquet"))

    if len(gold_files) != expected_cities:
        raise RuntimeError(
            "A quantidade de arquivos Gold não corresponde "
            "à quantidade de cidades."
        )

    print(f"\nArquivos Gold: {len(gold_files)}")
    print(f"Total de linhas diárias: {total_daily_rows}")

    return len(gold_files)


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main() -> None:
    target_date = datetime.date.today().strftime("%Y%m%d")

    print("=" * 55)
    print("PIPELINE OPEN-METEO")
    print(f"Data da coleta: {target_date}")
    print(f"Projeto: {PROJECT_ROOT}")
    print("=" * 55)

    expected_cities = run_bronze(target_date)
    silver_count = run_silver(target_date, expected_cities)
    gold_count = run_gold(target_date, expected_cities)

    print("\n" + "=" * 55)
    print("PIPELINE CONCLUÍDO COM SUCESSO")
    print("=" * 55)
    print(f"Data: {target_date}")
    print(f"Bronze: {expected_cities} arquivos JSON")
    print(f"Silver: {silver_count} arquivos Parquet")
    print(f"Gold: {gold_count} arquivos Parquet")
    print(f"\nDados salvos em: {DATA_ROOT}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nPIPELINE INTERROMPIDO: {error}")
        sys.exit(1)
