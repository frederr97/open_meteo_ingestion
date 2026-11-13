# PostgreSQL bootstrap

This prototype creates the initial PostgreSQL structures for the bronze-to-silver pipeline:

- `bronze` schema for raw payload storage
- `silver` schema for curated hourly weather records

## Usage

Run the bootstrap script from the repository root:

```bash
python scripts/setup_postgres.py \
  --host localhost \
  --port 5432 \
  --dbname open_meteo \
  --user postgres \
  --password postgres
```

The script will create the `open_meteo` database automatically if it does not exist.

You can also use environment variables:

```bash
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=open_meteo
export POSTGRES_ADMIN_DB=postgres
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
python scripts/setup_postgres.py
```

If you have a `.env` file in the repository root, the script will load connection settings from it automatically.

Use `--dry-run` to preview the SQL files that would be executed.
